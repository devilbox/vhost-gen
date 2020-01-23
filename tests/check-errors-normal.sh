#!/usr/bin/env bash

set -e
set -u
set -o pipefail

GIT_PATH="$( cd "$(dirname "$0")/../" && pwd -P )"
BIN_PATH="${GIT_PATH}/bin"

echo "------------------------------------------------------------"
echo "- Test: ${0}"
echo "------------------------------------------------------------"

"${BIN_PATH}/vhost-gen" -p ./ -n name -t etc/templates/ >/dev/null
"${BIN_PATH}/vhost-gen" -p ./ -n name -t etc/templates/ -c etc/conf.yml >/dev/null
"${BIN_PATH}/vhost-gen" -p ./ -n name -t etc/templates/ -c examples/conf.nginx.yml >/dev/null
"${BIN_PATH}/vhost-gen" -p ./ -n name -t etc/templates/ -c examples/conf.apache22.yml >/dev/null
"${BIN_PATH}/vhost-gen" -p ./ -n name -t etc/templates/ -c examples/conf.apache24.yml >/dev/null
