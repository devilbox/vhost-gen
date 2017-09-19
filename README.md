# vhost-gen

[![Build Status](https://travis-ci.org/devilbox/vhost-gen.svg?branch=master)](https://travis-ci.org/devilbox/vhost-gen)

[vhost_gen.py](bin/vhost_gen.py) will dynamically generate vhost configuration files for Nginx, Apache 2.2 or Apache 2.4 depending on what you have set in [conf.yml](etc/conf.yml).

---

### Supported Webserver

If you are not satisfied with the default definitions for the webserver configuration files, feel free to open an issue or a pull request.

| Name       | Template with default definitions          |
|------------|--------------------------------------------|
| Nginx      | [nginx.yml](etc/templates/nginx.yml)       |
| Apache 2.2 | [apache22.yml](etc/templates/apache22.yml) |
| Apache 2.4 | [apache24.yml](etc/templates/apache24.yml) |


### Supported Features

* Custom server name
* Custom document root
* Custom access log name
* Custom error log name
* Enable cross domain requests with regex support for origins
* Enable PHP-FPM
* Add Aliases with regex support
* Add Deny locations with regex support
* Enable webserver status page


### How does it work?

**General information:**

* vHost name is specified as a command line argument
* vHost templates for major webservers are defined in etc/templates
* vHost templates contain variables that must be replaced
* Webserver type/version is defined in etc/conf.yml
* Variable replacer are defined in etc/conf.yml
* Additional variable replacer can also be defined (`-o`)

**The following describes the program flow:**

1. [vhost_gen.py](bin/vhost_gen.py) will read /etc/conf.yml to get defines and webserver type/version
2. Base on the webserver version/type, it will read etc/templates/<HTTPD_VERSION>.yml template
3. Variables in the chosen template are replaced
4. The vHost name (`-n`) is also placed into the template
5. Template is written to webserver's config location (defined in etc/conf.yml)


### Installation

The Makefile will simply copy everything to their correct location.
```shell
$ sudo make install
```

To uninstall type:
```shell
$ sudo make uninstall
```

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
