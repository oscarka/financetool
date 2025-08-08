#!/bin/bash

# 替换nginx配置中的环境变量
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# 启动nginx
nginx -g "daemon off;"
