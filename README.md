# vhost-gen

[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/vhost-gen)](https://pypi.org/project/vhost-gen/)
[![PyPI - Status](https://img.shields.io/pypi/status/vhost-gen)](https://pypi.org/project/vhost-gen/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vhost-gen)](https://pypi.org/project/vhost-gen/)
[![PyPI - Format](https://img.shields.io/pypi/format/vhost-gen)](https://pypi.org/project/vhost-gen/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/vhost-gen)](https://pypi.org/project/vhost-gen/)
[![PyPI - License](https://img.shields.io/pypi/l/vhost-gen)](https://pypi.org/project/vhost-gen/)

**Continuous Integration**

[![testing](https://github.com/devilbox/vhost-gen/workflows/testing/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Atesting)
[![fuzzing](https://github.com/devilbox/vhost-gen/workflows/fuzzing/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Afuzzing)

[![linting](https://github.com/devilbox/vhost-gen/workflows/linting/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Alinting)
[![pylint](https://github.com/devilbox/vhost-gen/workflows/pylint/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Apylint)
[![black](https://github.com/devilbox/vhost-gen/workflows/black/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Ablack)
[![mypy](https://github.com/devilbox/vhost-gen/workflows/mypy/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Amypy)
[![pycode](https://github.com/devilbox/vhost-gen/workflows/pycode/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Apycode)
[![pydoc](https://github.com/devilbox/vhost-gen/workflows/pydoc/badge.svg)](https://github.com/devilbox/vhost-gen/actions?query=workflow%3Apydoc)


**[vhost-gen](bin/vhost-gen)** will dynamically generate **vhost** or **reverse proxy** configuration files for Apache 2.2, Apache 2.4 and Nginx depending on what you have set in [conf.yml](etc/conf.yml). This makes it easy to switch between different web servers while keeping the exact same functionality.

---

## Installation

#### Via pip
```bash
pip install vhost-gen
```

#### From git
**Note:** When using the Makefile, ensure that `pyyaml` is installed (`pip install pyyaml`).
```bash
git clone https://github.com/devilbox/vhost-gen
cd vhost-gen
sudo make install
```


## What is all the fuzz?

Imagine you have to create virtual hosts for your web server over and over again. The only things that might change are document root, log files and server names and possibly some other minor changes. Instead of having to copy and adjust the server's vhost config file each time, you can use `vhost-gen` to generate them for you. By supporting different web server versions, it makes it also easy for you to switch back and forth between Apache 2.2, Apache 2.4 and Nginx.

```bash
# vHost
$ vhost-gen -p /shared/httpd/www.example.com -n www.example.com
# Reverse Proxy
$ vhost-gen -r http://127.0.0.1:8080 -l / -n api.example.com
```

**`vhost-gen`** alone simply creates a new virtual host every time you execute it. The goal however is to also automate the execution of the vhost generator itself.

#### 1. Reverse Proxy automation: [watcherp](https://github.com/devilbox/watcherp)

Here enters **[watcherp](https://github.com/devilbox/watcherp)** the game. **[watcherp](https://github.com/devilbox/watcherp)** listens for changes of port bindings and triggers a command whenever a new port has been bound or a binding has been removed. By combining these two tools, you could automate the creating of reverse proxies with one command:

```bash
# %n will be replaced by watcherp with the address a port has binded
# %p will be replaced by watcherp with the the actual port number that started binding
# -p argument from watcherp specifies ports to ignore for changes
$ watcherp -v \
  -p 80,443 \
  -a "vhost-gen -r 'http://%n:%p' -l '/' -n '%n.example.com' -s" \
  -d "rm /etc/nginx/conf.d/%n.example.com.conf" \
  -t "nginx -s reload"
```

#### 2. Virtual Host automation: [watcherd](https://github.com/devilbox/watcherd)

Here enters **[watcherd](https://github.com/devilbox/watcherd)** the game. **[watcherd](https://github.com/devilbox/watcherd)** listens for directory changes and triggers a command whenever a directory has been created or deleted. By combining these two tools, you could automate mass virtual hosting with one command:

```bash
# %n will be replaced by watcherd with the new directory name
# %p will be replaced by watcherd with the new directory path
$ watcherd -v \
  -p /shared/httpd \
  -a "vhost-gen -p %p -n %n -s" \
  -d "rm /etc/nginx/conf.d/%n.conf" \
  -t "nginx -s reload"
```

##### More customization

Now it might look much more interesting. With the above command every vhost will have the exact same definition (except server name, document root and log file names). It is however also possible that every vhost could be customized depending on their needs. **`vhost-gen`** allows for additional overwriting its template. So inside each newly created folder you could have a sub-directory (e.g. `templates/`) with folder specific defines. Those custom templates would only be sourced if they exist:

```bash
# Note: Adding -o %p/templates
$ watcherd -v \
  -p /shared/httpd \
  -a "vhost-gen -p %p -n %n -o %p/templates -s" \
  -d "rm /etc/nginx/conf.d/%n.conf" \
  -t "nginx -s reload"
```

##### Making it robust

If you don't trust the stability of **[watcherd](https://github.com/devilbox/watcherd)** or want other means of controlling this daemon, you can utilize **[supervisord](http://supervisord.org/)**:
```ini
[program:watcherd]
command=watcherd -v -p /shared/httpd -a "vhost-gen -p %%p -n %%n -s" -d "rm /etc/nginx/custom.d/%%n.conf" -t "nginx -s reload"
startsecs = 0
autorestart = true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
stdout_events_enabled=true
stderr_events_enabled=true
```

#### 3. Dockerizing

If you don't want to implement it yourself, there are already four fully functional dockerized containers available that offer automated mass virtual hosting based on `vhost-gen` and `watcherd`:

| Base Image | Web server | Repository |
|------------|------------|------------|
| Nginx stable (official) | nginx | https://github.com/devilbox/docker-nginx-stable |
| Nginx mainline (official) | nginx | https://github.com/devilbox/docker-nginx-mainline |
| Apache 2.2 (official) | Apache 2.2 | https://github.com/devilbox/docker-apache-2.2 |
| Apache 2.4 (official) | Apache 2.4 | https://github.com/devilbox/docker-apache-2.4 |


## Insights

#### Supported Webserver

If you are not satisfied with the default definitions for the webserver configuration files, feel free to open an issue or a pull request.

| Name       | Template with default definitions          |
|------------|--------------------------------------------|
| Nginx      | [nginx.yml](etc/templates/nginx.yml)       |
| Apache 2.2 | [apache22.yml](etc/templates/apache22.yml) |
| Apache 2.4 | [apache24.yml](etc/templates/apache24.yml) |

#### Supported Features

* Document serving vHost or Reverse Proxy
* Custom server name
* Custom document root
* Custom access log name
* Custom error log name
* Enable cross domain requests with regex support for origins
* Enable PHP-FPM
* Add Aliases with regex support
* Add Deny locations with regex support
* Enable webserver status page
* Add custom directives from the configuration file

#### How does it work?

**General information:**

* vHost name is specified as a command line argument
* vHost templates for major webservers are defined in etc/templates
* vHost templates contain variables that must be replaced
* Webserver type/version is defined in /etc/vhost-gen/conf.yml
* Variable replacer are defined in /etc/vhost-gen/conf.yml
* Additional variable replacer can also be defined (`-o`)

**The following describes the program flow:**

1. [vhost-gen](bin/vhost-gen) will read /etc/vhost-gen/conf.yml to get defines and webserver type/version
2. Base on the webserver version/type, it will read etc/templates/<HTTPD_VERSION>.yml template
3. Variables in the chosen template are replaced
4. The vHost name (`-n`) is also placed into the template
5. Template is written to webserver's config location (defined in /etc/vhost-gen/conf.yml)


## Usage

#### Using different configurations

The [configuration file](etc/conf.yml) should give you a lot of flexibility to generate a customized virtual host that fits your needs. Go and check out the [example](examples/) section to see different configuration files for different web servers. If however the customization available in the configuration file is not sufficient, you can also adjust the [templates](etc/template) itself. Read on to find out more in the next section.

#### Adding custom directives

The [configuration file](etc/conf.yml) also contains a `custom:` directive. This is to add customized directives into your vhost definition that are not yet included in the feature sections. An example for Nginx would be:

`conf.yml`:
```yml
custom: |
  if (-f $request_filename) {
      break;
  }
```
This would then be added to your generated vhost:
```nginx
server {
    ...
    if (-f $request_filename) {
        break;
    }
}
```

If the current vHost definition does not suit your needs, you could also disable all available features in the configuration file and only use the `custom:` directive to specify your required definitions.

#### Using different templates

Each [template](etc/templates) consists of two sections:

1. `vhost`
2. `features`

The `vhost` section is the actual vhost that is being built. All placeholders (In the form of: `__*__`) will be substituted from either the configuration file or the feature section of the template.

The `features` section contains definitions of features that can be enabled or disabled (via the config file). If those features do not seem suitable, you can adjust them to better fit your needs. You can also re-arrange their position in the `vhost` section.

Whenever you edit the template, make sure not to misspell any placeholders. They will not get replaced when spellt wrong.


Let's take for example the `features.server_status` section from Apache 2.2:
```yml
  server_status: |
    # Status Page
    <Location __REGEX__>
        SetHandler server-status
        Order allow,deny
        Allow from all
    </Location>
```

If you are not satisfied with the `Allow from all` permissions, simply rewrite this template to your needs:
```yml
  server_status: |
    # Status Page
    <Location __REGEX__>
        SetHandler server-status
        Order allow,deny
        Allow from 160.120.25.65
    </Location>
```

#### Available command line options

```bash
Usage: vhost-gen -p|r <str> -n <str> [-l <str> -c <str> -t <str> -o <str> -d -s -v]
       vhost-gen --help
       vhost-gen --version

vhost-gen will dynamically generate vhost configuration files
for Nginx, Apache 2.2 or Apache 2.4 depending on what you have set
in /etc/vhost-gen/conf.yml

Required arguments:
  -p|r <str>  You need to choose one of the mutually exclusive arguments.
              -p: Path to document root/
              -r: http(s)://Host:Port for reverse proxy.
              Depening on the choice, it will either generate a document serving
              vhost or a reverse proxy vhost.
              Note, when using -p, this can also have a suffix directory to be set
              in conf.yml
  -l <str>    Location path when using reverse proxy.
              Note, this is not required for normal document root server (-p)
  -n <str>    Name of vhost
              Note, this can also have a prefix and/or suffix to be set in conf.yml

Optional arguments:
  -m <str>    Vhost generation mode. Possible values are:
              -m plain: Only generate http version (default)
              -m ssl:   Only generate https version
              -m both:  Generate http and https version
              -m redir: Generate https version and make http redirect to https
  -c <str>    Path to global configuration file.
              If not set, the default location is /etc/vhost-gen/conf.yml
              If no config is found, a default is used with all features turned off.
  -t <str>    Path to global vhost template directory.
              If not set, the default location is /etc/vhost-gen/templates/
              If vhost template files are not found in this directory, the program will
              abort.
  -o <str>    Path to local override vhost template directory.
              This is used as a secondary template directory and definitions found here
              will be merged with the ones found in the global template directory.
              Note, definitions in local vhost teplate directory take precedence over
              the ones found in the global template directory.
  -d          Make this vhost the default virtual host.
              Note, this will also change the server_name directive of nginx to '_'
              as well as discarding any prefix or suffix specified for the name.
              Apache does not have any specialities, the first vhost takes precedence.
  -s          If specified, the generated vhost will be saved in the location found in
              conf.yml. If not specified, vhost will be printed to stdout.
  -v          Be verbose. Use twice for debug output.

Misc arguments:
  --help      Show this help.
  --version   Show version.
```


## Contributing

This is an open source project and done in spare time. If you want to help out you are warmly welcome. You could do one or more of the following things:

* Validate web server templates
* Submit template examples
* Create templates for other web servers
* Whatever else you can imagine of


## License

**[MIT License](LICENSE.md)**

Copyright (c) 2017 [cytopia](https://github.com/cytopia)
