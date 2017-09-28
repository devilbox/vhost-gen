# vhost-gen

[![Build Status](https://travis-ci.org/devilbox/vhost-gen.svg?branch=master)](https://travis-ci.org/devilbox/vhost-gen) ![Version](https://img.shields.io/github/tag/devilbox/vhost-gen.svg)

[vhost_gen.py](bin/vhost_gen.py) will dynamically generate vhost configuration files for Nginx, Apache 2.2 or Apache 2.4 depending on what you have set in [conf.yml](etc/conf.yml).

---

## What is all the fuzz?

**`vhost_gen.py`** alone simply creates a new virtual host every time you execute it. The goal however is to also automate the execution of the vhost generator itself. Here enters **[watcherd](https://github.com/devilbox/watcherd)** the game. **[watcherd](https://github.com/devilbox/watcherd)** listens for directory changes and triggers a command for each added and deletd directory. Combining these two tools, you could automate mass virtual hosting with one command:

```shell
# %n will be replaced by watcherd with the new directory name
# %p will be replaced by watcherd with the new directory path
watcherd -v \
  -p /shared/httpd \
  -a "vhost_gen.py -p %p -n %n -s" \
  -d "rm /etc/nginx/conf.d/%n.conf" \
  -t "nginx -s reload"
```
**More customization**

Now it might look much more interesting. With the above command every vhost will have the exact same definition (except server name, document root and log file names). It is however also possible that every vhost could be customized depending on their needs. **`vhost_gen.py`** allows for additional overwriting its template. So inside each newly created folder you could have a sub-directory (e.g. `templates/`) with folder specific defines. Those custom templates would only be sourced if they exist:

```shell
# Note: Adding -o %p/templates
watcherd -v \
  -p /shared/httpd \
  -a "vhost_gen.py -p %p -n %n -o %p/templates -s" \
  -d "rm /etc/nginx/conf.d/%n.conf" \
  -t "nginx -s reload"
```

**Dockerizing**

If you don't want to implement it yourself, there are already four fully functional dockerized containers available that offer mass virtual hosting based on the above commands:

| Base Image | Web server | Repository |
|------------|------------|------------|
| Nginx stable (official) | nginx | https://github.com/devilbox/docker-nginx-stable |
| Nginx mainline (official) | nginx | https://github.com/devilbox/docker-nginx-mainline |
| Apache 2.2 (official) | Apache 2.2 | https://github.com/devilbox/docker-apache-2.2 |
| Apache 2.2 (official) | Apache 2.4 | https://github.com/devilbox/docker-apache-2.4 |


## Insights

#### Supported Webserver

If you are not satisfied with the default definitions for the webserver configuration files, feel free to open an issue or a pull request.

| Name       | Template with default definitions          |
|------------|--------------------------------------------|
| Nginx      | [nginx.yml](etc/templates/nginx.yml)       |
| Apache 2.2 | [apache22.yml](etc/templates/apache22.yml) |
| Apache 2.4 | [apache24.yml](etc/templates/apache24.yml) |


#### Supported Features

* Custom server name
* Custom document root
* Custom access log name
* Custom error log name
* Enable cross domain requests with regex support for origins
* Enable PHP-FPM
* Add Aliases with regex support
* Add Deny locations with regex support
* Enable webserver status page


#### How does it work?

**General information:**

* vHost name is specified as a command line argument
* vHost templates for major webservers are defined in etc/templates
* vHost templates contain variables that must be replaced
* Webserver type/version is defined in /etc/vhost-gen/conf.yml
* Variable replacer are defined in /etc/vhost-gen/conf.yml
* Additional variable replacer can also be defined (`-o`)

**The following describes the program flow:**

1. [vhost_gen.py](bin/vhost_gen.py) will read /etc/vhost-gen/conf.yml to get defines and webserver type/version
2. Base on the webserver version/type, it will read etc/templates/<HTTPD_VERSION>.yml template
3. Variables in the chosen template are replaced
4. The vHost name (`-n`) is also placed into the template
5. Template is written to webserver's config location (defined in /etc/vhost-gen/conf.yml)


#### Installation

The Makefile will simply copy everything to their correct location.
```shell
$ sudo make install
```

To uninstall type:
```shell
$ sudo make uninstall
```

#### Usage

```shell
Usage: vhost_gen.py -p <str> -n <str> [-c <str> -t <str> -o <str> -s -d -v]
       vhost_gen.py --help
       vhost_gen.py --version

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
  -d          Make this vhost the default virtual host.
              Note, this will also change the server_name directive of nginx to '_'
              as well as discarding any prefix or suffix's specified for the name.
              Apache does not have any specialities, the first vhost takes precedence.
  -s          If specified, the generated vhost will be saved in the location found in
              conf.yml. If not specified, vhost will be printed to stdout.
  -v          Be verbose.

Misc arguments:
  --help      Show this help.
  --version   Show version.
```
