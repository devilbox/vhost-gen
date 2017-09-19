# vhost-gen

[![Build Status](https://travis-ci.org/devilbox/vhost-gen.svg?branch=master)](https://travis-ci.org/devilbox/vhost-gen)

[vhost_gen.py](bin/vhost_gen.py) will dynamically generate vhost configuration files for Nginx, Apache 2.2 or Apache 2.4 depending on what you have set in [conf.yml](etc/conf.yml).

### How does it work?



### Usage

```shell
Usage: vhost_gen.py -p <str> -n <str> [-c <str> -t <str> -o <str> -s]
       vhost_gen.py -h
       vhost_gen.py -v

vhost_gen.py will dynamically generate vhost configuration files
for Nginx, Apache 2.2 or Apache 2.4 depending on what you have set
in /etc/vhot-gen/conf.yml

Required arguments:
  -p <str>    Path to document root
              Note, this can also have a suffix directory to be set in conf.yml
  -n <str>    Name of vhost
              Note, this can also have a prefix and/or suffix to be set in conf.yml

Optional arguments:
  -c <str>    Path to global configuration file.
              If not set, the default location is /etc/vhost-gen/conf.yml
              If no config is found, a default is used with all features turned off.
  -t <str>    Path to global vhost template directory.
              If not set, the default location is /etc/vhost-gen/templates/
              If vhost template files are not found in this directory, the program will
              abort.
  -o <str>    Path to local vhost template directory.
              This is used as a secondary template directory and definitions found here
              will be merged with the ones found in the global template directory.
              Note, definitions in local vhost teplate directory take precedence over
              the ones found in the global template directory.

  -s          If specified, the generated vhost will be saved in the location found in
              conf.yml. If not specified, vhost will be printed to stdout.

Misc arguments:
  -h          Show this help.
  -v          Show version.
```
