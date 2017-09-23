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

from __future__ import print_function
import os
import sys
import re
import getopt
import itertools
import yaml


############################################################
# Globals
############################################################

# Default paths
CONFIG_PATH = '/etc/vhost-gen/conf.yml'
TEMPLATE_DIR = '/etc/vhost-gen/templates'

# Default configuration
DEFAULT_CONFIG = {
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
            'prefix': '',
            'dir': {
                'create': False,
                'path': '/var/log/nginx'
            },
            'mode': {
                'set': False,
                'mode': '0755'
            },
            'user': {
                'set': False,
                'user': ''
            },
            'group': {
                'set': False,
                'group': ''
            }
        },
        'listen': {
            'enable': False,
        },
        'php_fpm': {
            'enable': False,
            'address': '',
            'port': 9000
        },
        'alias': [],
        'deny': [],
        'server_status': {
            'enable': False,
            'alias': ''
        }
    }
}

# Available templates
TEMPLATES = {
    'apache22': 'apache22.yml',
    'apache24': 'apache24.yml',
    'nginx':    'nginx.yml'
}


############################################################
# System Functions
############################################################

def print_help():
    ''' Show program help '''
    print('Usage: vhost_gen.py -p <str> -n <str> [-c <str> -t <str> -o <str> -s]')
    print('       vhost_gen.py -h')
    print('       vhost_gen.py -v')
    print('')
    print('vhost_gen.py will dynamically generate vhost configuration files')
    print('for Nginx, Apache 2.2 or Apache 2.4 depending on what you have set')
    print('in /etc/vhot-gen/conf.yml')
    print('')
    print('Required arguments:')
    print('  -p <str>    Path to document root')
    print('              Note, this can also have a suffix directory to be set in conf.yml')
    print('  -n <str>    Name of vhost')
    print('              Note, this can also have a prefix and/or suffix to be set in conf.yml')
    print('')
    print('Optional arguments:')
    print('  -c <str>    Path to global configuration file.')
    print('              If not set, the default location is /etc/vhost-gen/conf.yml')
    print('              If no config is found, a default is used with all features turned off.')
    print('  -t <str>    Path to global vhost template directory.')
    print('              If not set, the default location is /etc/vhost-gen/templates/')
    print('              If vhost template files are not found in this directory, the program will')
    print('              abort.')
    print('  -o <str>    Path to local vhost template directory.')
    print('              This is used as a secondary template directory and definitions found here')
    print('              will be merged with the ones found in the global template directory.')
    print('              Note, definitions in local vhost teplate directory take precedence over')
    print('              the ones found in the global template directory.')
    print('  -s          If specified, the generated vhost will be saved in the location found in')
    print('              conf.yml. If not specified, vhost will be printed to stdout.')
    print('')
    print('Misc arguments:')
    print('  -h          Show this help.')
    print('  -v          Show version.')


def print_version():
    ''' Show program version '''
    print('vhost_gen v0.1 (2017-09-18)')
    print('cytopia <cytopia@everythingcli.org>')
    print('https://github.com/devilbox/vhost-gen')
    print('The MIT License (MIT)')


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

    try:
        with open(path, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                if data is None:
                    data = dict()
                return (True, data, '')
            except yaml.YAMLError as err:
                return (False, dict(), err)
    except IOError:
        return (False, dict(), 'File does not exist:'+path)


def merge_yaml(yaml1, yaml2):
    ''' Merge two yaml strings. The secondary takes precedence '''
    return dict(itertools.chain(yaml1.items(), yaml2.items()))


############################################################
# Argument Functions
############################################################

def parse_args(argv):
    ''' Parse command line arguments '''

    # Config location, can be overwritten with -c
    l_config_path = CONFIG_PATH
    l_template_dir = TEMPLATE_DIR
    o_template_dir = None
    save = None

    # Define command line options
    try:
        opts, argv = getopt.getopt(argv, 'vhc:p:n:t:o:s')
    except getopt.GetoptError as err:
        print('[ERR]', str(err), file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
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
        # Global template dir
        elif opt == '-t':
            l_template_dir = arg
        # Local template dir
        elif opt == '-o':
            o_template_dir = arg
        # Save?
        elif opt == '-s':
            save = True

    # Validate required command line options are set
    try:
        path
    except NameError:
        print('[ERR] -p is required', file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
        sys.exit(1)

    try:
        name
    except NameError:
        print('[ERR] -n is required', file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
        sys.exit(1)

    return (l_config_path, l_template_dir, o_template_dir, path, name, save)


def validate_args(config, tpl_dir, name):
    ''' Validate command line arguments '''

    regex = re.compile('(^[-_.a-zA-Z0-9]+$)', re.IGNORECASE)
    if not regex.match(name):
        print('[ERR] Invalid name:', name, file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(config):
        print('[WARN] Config file not found:', config, file=sys.stderr)

    if not os.path.isdir(tpl_dir):
        print('[ERR] Template path does not exist:', tpl_dir, file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
        sys.exit(1)

    # Validate global templates
    tpl_file = os.path.join(tpl_dir, TEMPLATES['apache22'])
    if not os.path.isfile(tpl_file):
        print('[ERR] Apache 2.2 template file does not exist:', tpl_file, file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
        sys.exit(1)

    tpl_file = os.path.join(tpl_dir, TEMPLATES['apache24'])
    if not os.path.isfile(tpl_file):
        print('[ERR] Apache 2.4 template file does not exist:', tpl_file, file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
        sys.exit(1)

    tpl_file = os.path.join(tpl_dir, TEMPLATES['nginx'])
    if not os.path.isfile(tpl_file):
        print('[ERR] Nginx template file does not exist:', tpl_file, file=sys.stderr)
        print('Type -h for help', file=sys.stderr)
        sys.exit(1)


############################################################
# Config File Functions
############################################################

def validate_config(config):
    ''' Validate some important keys in config dict '''

    # Validate server type
    valid_hosts = list(TEMPLATES.keys())
    if config['server'] not in valid_hosts:
        print('[ERR] httpd.server must be \'apache22\', \'apache24\' or \'nginx\'', file=sys.stderr)
        print('[ERR] Your configuration is:', config['server'], file=sys.stderr)
        sys.exit(1)

    # Validate if log dir can be created
    log_dir = config['vhost']['log']['dir']['path']
    if config['vhost']['log']['dir']['create']:
        if not os.path.isdir(log_dir):
            if not os.access(os.path.dirname(log_dir), os.W_OK):
                print('[ERR] log directory does not exist and cannot be created:', log_dir,
                      file=sys.stderr)
                sys.exit(1)


############################################################
# vHost build Functions
############################################################

def vhost_get_server_name(config, server_name):
    ''' Get server name '''

    prefix = str(config['vhost']['name']['prefix'])
    suffix = str(config['vhost']['name']['suffix'])
    return prefix + server_name + suffix


def vhost_get_document_root(config, docroot):
    ''' Get document root '''

    suffix = str(config['vhost']['docroot']['suffix'])
    path = os.path.join(docroot, suffix)
    return path


def vhost_get_index(config):
    ''' Get index '''

    index = 'index.html'
    if config['vhost']['php_fpm']['enable']:
        index = 'index.php'

    return index


def vhost_get_listen(config, template):
    ''' Get listen directive '''

    listen = ''
    if config['vhost']['listen']['enable']:
        listen = template['features']['listen']

    return listen


def vhost_get_access_log(config, server_name):
    ''' Get access log directive '''

    name = config['vhost']['log']['prefix'] + server_name + '-access.log'
    path = os.path.join(config['vhost']['log']['dir']['path'], name)
    return path


def vhost_get_error_log(config, server_name):
    ''' Get error log directive '''

    name = config['vhost']['log']['prefix'] + server_name + '-error.log'
    path = os.path.join(config['vhost']['log']['dir']['path'], name)
    return path


def vhost_get_php_fpm(config, template):
    ''' Get PHP FPM directive '''

    # Get PHP-FPM
    php_fpm = ''
    if config['vhost']['php_fpm']['enable']:
        php_fpm = str_replace(template['features']['php_fpm'], {
            '__PHP_ADDR__': config['vhost']['php_fpm']['address'],
            '__PHP_PORT__': to_str(config['vhost']['php_fpm']['port'])
        })
    return php_fpm


def vhost_get_aliases(config, template):
    ''' Get virtual host alias directives '''

    # Get location aliases
    aliases = []
    for item in config['vhost']['alias']:
        # Add optional xdomain request if enabled
        xdomain_request = ''
        if 'xdomain_request' in item:
            if item['xdomain_request']['enable']:
                xdomain_request = str_replace(template['features']['xdomain_request'], {
                    '__REGEX__': item['xdomain_request']['origin']
                })
        # Replace everything
        aliases.append(str_replace(template['features']['alias'], {
            '__REGEX__': item['alias'],
            '__PATH__': item['path'],
            '__XDOMAIN_REQ__': str_indent(xdomain_request, 4)
        }))
    return '\n'.join(aliases)


def vhost_get_denies(config, template):
    ''' Get virtual host deny alias directives '''

    # Get deny aliases
    denies = []
    for item in config['vhost']['deny']:
        denies.append(str_replace(template['features']['deny'], {
            '__REGEX__': item['alias']
        }))
    return '\n'.join(denies)


def vhost_get_server_status(config, template):
    ''' Get virtual host server status directive '''
    status = ''
    if config['vhost']['server_status']['enable']:
        status = template['features']['server_status']

    return str_replace(status, {
        '__REGEX__': config['vhost']['server_status']['alias']
    })


############################################################
# vHost create
############################################################

def get_vhost(config, tpl_dir, o_tpl_dir, docroot, name):
    ''' Create the vhost '''

    # Server type
    server = config['server']

    # Load global template file
    succ, template, err = load_yaml(os.path.join(tpl_dir, TEMPLATES[server]))
    if not succ:
        return (False, err)

    # Load optional template file (if specified file and merge it)
    if o_tpl_dir is not None:
        succ, template2, err = load_yaml(os.path.join(o_tpl_dir, TEMPLATES[server]))
        template = merge_yaml(template, template2)

    # Get final vhost
    return (True, str_replace(template['vhost'], {
        '__VHOST_NAME__':    vhost_get_server_name(config, name),
        '__LISTEN__':        vhost_get_listen(config, template),
        '__DOCUMENT_ROOT__': vhost_get_document_root(config, docroot),
        '__INDEX__':         vhost_get_index(config),
        '__ACCESS_LOG__':    vhost_get_access_log(config, name),
        '__ERROR_LOG__':     vhost_get_error_log(config, name),
        '__PHP_FPM__':       str_indent(vhost_get_php_fpm(config, template), 4),
        '__ALIASES__':       str_indent(vhost_get_aliases(config, template), 4),
        '__DENIES__':        str_indent(vhost_get_denies(config, template), 4),
        '__SERVER_STATUS__': str_indent(vhost_get_server_status(config, template), 4)
    }))


############################################################
# Main Function
############################################################

def main(argv):
    ''' Main entrypoint '''

    # Get command line arguments
    config_path, template_dir, o_template_dir, docroot, name, save = parse_args(argv)

    # Validate command line arguments
    # This will abort the program on error
    validate_args(config_path, template_dir, name)

    # Load configuration file
    if os.path.isfile(config_path):
        succ, data, err = load_yaml(config_path)
        if not succ:
            print(err, file=sys.stderr)
            sys.exit(1)
    else:
        data = dict()

    # Merge config with defaults (config takes precedence over defaults)
    data = merge_yaml(DEFAULT_CONFIG, data)

    # Validate configuration file
    # This will abort the program on error
    validate_config(data)

    # Create vhost
    succ, vhost = get_vhost(data, template_dir, o_template_dir, docroot, name)
    if not succ:
        print(vhost, file=sys.stderr)
        sys.exit(1)

    if save:
        if not os.path.isdir(data['conf_dir']):
            print('[ERR] output conf_dir does not exist:', data['conf_dir'],
                  file=sys.stderr)
            sys.exit(1)
        if not os.access(data['conf_dir'], os.W_OK):
            print('[ERR] directory does not have write permissions', data['conf_dir'],
                  file=sys.stderr)
            sys.exit(1)

        vhost_path = os.path.join(data['conf_dir'], name+'.conf')
        with open(vhost_path, 'w') as outfile:
            outfile.write(vhost)
    else:
        print(vhost)


############################################################
# Main Entry Point
############################################################

if __name__ == '__main__':
    main(sys.argv[1:])
