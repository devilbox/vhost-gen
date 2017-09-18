#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2017 cytopia <cytopia@everythingcli.org>

'''
vHost creator for Apache 2.2, Apache 2.4 and Nginx
'''

############################################################
# Imports
############################################################

import os
import sys
import getopt
import itertools
import yaml


############################################################
# Globals
############################################################

# Default paths
CONFIG_PATH = '/etc/vhost-gen/config.yml'
TEMPLATE_DIR = '/etc/vhost-gen/templates'

# Default configuration
CONFIG = {
    'httpd': {
        'server': 'nginx',
        'conf_dir': '/etc/nginx/conf.d',
        'vhost': {
            'name': {
                'prefix': '',
                'suffix': ''
            },
            'docroot': {
                'suffix': ''
            },
            'log': {
                'dir': '/var/log/nginx'
            },
            'xdomain_request': {
                'enable': False,
                'origin': ''
            },
            'php_fpm': {
                'enable': False,
                'address': '',
                'port': 9000
            },
            'alias': [],
            'deny': [],
            'status': {
                'enable': False,
                'alias': ''
            }
        }
    }
}

# Available templates
TEMPLATE = {
    'apache22': 'apache22.yml',
    'apache24': 'apache24.yml',
    'nginx':    'nginx.yml'
}


############################################################
# System Functions
############################################################

def print_help():
    ''' Show program help '''
    print 'help'


def print_version():
    ''' Show program version '''
    print 'vhost_gen v0.1 (2017-09-18)'
    print 'cytopia <cytopia@everythingcli.org>'
    print 'https://github.com/devilbox/vhost-gen'
    print 'The MIT License (MIT)'


############################################################
# Wrapper Functions
############################################################

def str_replace(string, replacer):
    ''' Generic string replace '''

    # Replace all 'keys' with 'values'
    for key, val in replacer.items():
        string = string.replace(key, val)

    return string


def str_indent(text, amount, char=' '):
    ''' Indent every newline inside str by specified value '''
    padding = amount * char
    return ''.join(padding+line for line in text.splitlines(True))


def to_str(string):
    ''' Dummy string retriever '''
    if string is None:
        return ''
    return str(string)


def load_yaml(path):
    ''' Wrapper to load yaml file safely '''

    with open(path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            if data is None:
                data = dict()
            return (True, data)
        except yaml.YAMLError as err:
            return (False, err)


############################################################
# Argument Functions
############################################################

def parse_args(argv):
    ''' Parse command line arguments '''

    # Config location, can be overwritten with -c
    l_config_path = CONFIG_PATH
    l_template_dir = TEMPLATE_DIR

    # Define command line options
    try:
        opts, argv = getopt.getopt(argv, 'vhc:p:n:t:')
    except getopt.GetoptError, err:
        print '[ERR]', str(err)
        print 'Type -h for help'
        sys.exit(2)

    # Get command line options
    for opt, arg in opts:
        if opt == '-v':
            print_version()
            sys.exit()
        elif opt == '-h':
            print_help()
            sys.exit()
        # Config file overwrite
        elif opt == '-c':
            l_config_path = arg
        # Vhost document root path
        elif opt == '-p':
            path = arg
        # Vhost name
        elif opt == '-n':
            name = arg
        # Template dir
        elif opt == '-t':
            l_template_dir = arg

    # Validate required command line options are set
    try:
        path
    except NameError:
        print '[ERR] -p is required'
        print 'Type -h for help'
        sys.exit(1)

    try:
        name
    except NameError:
        print '[ERR] -n is required'
        print 'Type -h for help'
        sys.exit(1)

    return (l_config_path, l_template_dir, path, name)


def validate_args(config, tpl_dir):
    ''' Validate command line arguments '''

    if not os.path.isfile(config):
        print '[WARN] Config file not found:', config
    if not os.path.isdir(tpl_dir):
        print '[ERR] Template path does not exist:', tpl_dir
        print 'Type -h for help'
        sys.exit(1)

    tpl_file = os.path.join(tpl_dir, TEMPLATE['apache22'])
    if not os.path.isfile(tpl_file):
        print '[ERR] Apache 2.2 template file does not exist:', tpl_file
        print 'Type -h for help'
        sys.exit(1)

    tpl_file = os.path.join(tpl_dir, TEMPLATE['apache24'])
    if not os.path.isfile(tpl_file):
        print '[ERR] Apache 2.4 template file does not exist:', tpl_file
        print 'Type -h for help'
        sys.exit(1)

    tpl_file = os.path.join(tpl_dir, TEMPLATE['nginx'])
    if not os.path.isfile(tpl_file):
        print '[ERR] Nginx template file does not exist:', tpl_file
        print 'Type -h for help'
        sys.exit(1)


############################################################
# Config File Functions
############################################################

def validate_config(settings):
    ''' Validate some important keys in config dict '''

    valid_hosts = list(TEMPLATE.keys())
    if settings['httpd']['server'] not in valid_hosts:
        print '[ERR] httpd.server must be \'apache22\', \'apache24\' or \'nginx\''
        print '[ERR] Your configuration is:', settings['httpd']['server']
        sys.exit(1)


############################################################
# vHost Functions
############################################################

def get_vhost(settings, tpl_dir, docroot, name):
    ''' Create the vhost '''

    server = settings['httpd']['server']
    tpl_path = os.path.join(tpl_dir, TEMPLATE[server])

    succ, data = load_yaml(tpl_path)
    if not succ:
        return (False, data)

    # Configs
    cfg_vhost = settings['httpd']['vhost']

    # Template
    tpl_vhost = data['structure']
    tpl_feature = data['features']

    # Replacer
    repl = {}
    repl['name'] = to_str(cfg_vhost['name']['prefix']) + name + to_str(cfg_vhost['name']['suffix'])
    repl['docroot'] = os.path.join(docroot, to_str(cfg_vhost['docroot']['suffix']))
    repl['index'] = 'index.php' if cfg_vhost['php_fpm']['enable'] else 'index.html'
    repl['access_log'] = os.path.join(cfg_vhost['log']['dir'], repl['name']+'-access.log')
    repl['error_log'] = os.path.join(cfg_vhost['log']['dir'], repl['name']+'-error.log')

    # Get cross-domain request
    repl['xdomain_request'] = ''
    if cfg_vhost['xdomain_request']['enable']:
        repl['xdomain_request'] = str_replace(tpl_feature['xdomain_request'], {
            '__REGEX__': cfg_vhost['xdomain_request']['origin']
        })

    # Get PHP-FPM
    repl['php_fpm'] = ''
    if cfg_vhost['php_fpm']['enable']:
        repl['php_fpm'] = str_replace(tpl_feature['php_fpm'], {
            '__PHP_ADDR__': cfg_vhost['php_fpm']['address'],
            '__PHP_PORT__': to_str(cfg_vhost['php_fpm']['port'])
        })

    # Get location aliases
    tmp = []
    for item in cfg_vhost['alias']:
        tmp.append(str_replace(tpl_feature['alias'], {
            '__REGEX__': item['alias'],
            '__PATH__': item['path']
        }))
    repl['alias'] = '\n'.join(tmp)

    # Get deny aliases
    tmp = []
    for item in cfg_vhost['deny']:
        tmp.append(str_replace(tpl_feature['deny'], {
            '__REGEX__': item['alias']
        }))
    repl['deny'] = '\n'.join(tmp)

    # Get status alias
    repl['status'] = ''
    if cfg_vhost['status']['enable']:
        repl['status'] = str_replace(tpl_feature['status'], {
            '__REGEX__': cfg_vhost['status']['alias']
        })

    # Get final vhost
    tpl_vhost = str_replace(tpl_vhost, {
        '__VHOST_NAME__':    repl['name'],
        '__DOCUMENT_ROOT__': repl['docroot'],
        '__INDEX__':         repl['index'],
        '__ACCESS_LOG__':    repl['access_log'],
        '__ERROR_LOG__':     repl['error_log'],
        '__PHP_FPM__':       str_indent(repl['php_fpm'], 4),
        '__XDOMAIN_REQ__':   str_indent(repl['xdomain_request'], 4),
        '__ALIASES__':       str_indent(repl['alias'], 4),
        '__DENIES__':        str_indent(repl['deny'], 4),
        '__STATUS__':        str_indent(repl['status'], 4)
    })
    return (True, tpl_vhost)


############################################################
# Main Function
############################################################

def main(argv):
    ''' Main entrypoint '''

    # Get command line arguments
    config_path, template_dir, docroot, name = parse_args(argv)

    # Validate command line arguments
    # This will abort the program on error
    validate_args(config_path, template_dir)

    # Load configuration file
    if os.path.isfile(config_path):
        succ, data = load_yaml(config_path)
        if not succ:
            print data
            sys.exit(1)
    else:
        data = dict()

    # Merge config with defaults (config takes precedence over defaults)
    data = dict(itertools.chain(CONFIG.iteritems(), data.iteritems()))

    # Validate configuration file
    # This will abort the program on error
    validate_config(data)

    # Create vhost
    succ, vhost = get_vhost(data, template_dir, docroot, name)
    if not succ:
        print vhost
        sys.exit(1)

    print vhost


############################################################
# Main Entry Point
############################################################

if __name__ == '__main__':
    main(sys.argv[1:])
