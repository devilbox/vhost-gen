#!/usr/bin/env bash

set -e
set -u
set -o pipefail

GIT_PATH="$( cd "$(dirname "$0")/../" && pwd -P )"
BIN_PATH="${GIT_PATH}/bin"

echo "------------------------------------------------------------"
echo "- Test: ${0}"
echo "------------------------------------------------------------"

"${BIN_PATH}/vhost-gen" -r http://127.0.0.1:3000 -l / -n name -t etc/templates/ | grep -v '__'
"${BIN_PATH}/vhost-gen" -r http://127.0.0.1:3000 -l / -n name -t etc/templates/ -c etc/conf.yml | grep -v '__'
"${BIN_PATH}/vhost-gen" -r http://127.0.0.1:3000 -l / -n name -t etc/templates/ -c examples/conf.nginx.yml | grep -v '__'
"${BIN_PATH}/vhost-gen" -r http://127.0.0.1:3000 -l / -n name -t etc/templates/ -c examples/conf.apache22.yml | grep -v '__'
"${BIN_PATH}/vhost-gen" -r http://127.0.0.1:3000 -l / -n name -t etc/templates/ -c examples/conf.apache24.yml | grep -v '__'
