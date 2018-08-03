Hi everybody,


**TL;DR**

Is **[vhost-gen](https://github.com/devilbox/vhost-gen)** outputting best-practise directives for Nginx for

* PHP-FPM
* Aliases
* Denies
* and server status?


**Long version:**

I have crafted an initial version of a **[vhost generator](https://github.com/devilbox/vhost-gen)** for Apache 2.2, Apache 2.4 and Nginx based on Python (compatible with [2.6 - 3.6](https://travis-ci.org/devilbox/vhost-gen) and least possible dependencies). It is still an ongoing process and far from finished.

This is going to be an actively maintained project, as [other projects](https://github.com/devilbox/docker-nginx-stable) of mine also rely on it. That said, I wanted to check with you guys for some improvements, possible pitfalls that might have already been made and some review of the generated Nginx configuration.

**What is the current state?**

* Be able to create web server vhost configurations for Apache 2.2, Apache 2.4 and Nginx with the same behavior/outcome
* Normal vhosts and Reverse Proxy vhosts are suppored
* PHP-FPM directives
* Alias directives (optoinal with cross-domain requests)
* Deny directives
* Server status directive
* Set the default vhost
* Logging to file or stderr/stdout for use in Docker

As I am not too skilled with Nginx, I wanted to double check with you guys if the general directives are chosen well or are in need of improvement.

**So what do I need to verify?**

1. Nginx PHP-FPM directive

`phphost` and `9000` will be replaced as defined in the configuration file.

```shell
    # PHP-FPM Definition
    location / {
        try_files $uri $uri/ /index.php$is_args$args;
    }
    location ~ \.php?$ {
        try_files $uri = 404;
        include fastcgi_params;

        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_split_path_info ^(.+\.php)(.*)$;

        fastcgi_pass phphost:9000;

        fastcgi_index index.php;
        fastcgi_intercept_errors on;
    }
```

2. Deny location
`/\.git` will be replaced into this directive.
```shell
    # Deny Definition
    location ~ /\.git {
        deny all;
    }
```

3. Server status

`/server-status/` will be replaced into this directive.
```shell
    # Status Page
    location ~ /server-status/ {
        stub_status on;
        access_log off;
    }
```

4. Alias location

The following three values will be replaced into this directive:

* `/my-api/`
* `/var/www/default/api`
* `http(s)?://(.*)`

(Cross Domain requests can be enabled or disabled)

```shell
   # Alias Definition
    location ~ /my-api/ {
        root  /var/www/default/api;
        # Allow cross domain request from these hosts
        if ( $http_origin ~* (http(s)?://(.*)$) ) {
            add_header "Access-Control-Allow-Origin" "$http_origin";
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range';
            add_header 'Access-Control-Expose-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range';
            add_header 'Access-Control-Max-Age' 0;
            return 200;
        }
    }
```


**Links:**

* [https://github.com/devilbox/vhost-gen](https://github.com/devilbox/vhost-gen)
