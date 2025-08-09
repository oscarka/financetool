#!/bin/bash
set -e

echo "=== Container Starting ===" | tee /tmp/startup.log
echo "Date: $(date)" | tee -a /tmp/startup.log

# 设置端口
export PORT=${PORT:-80}
echo "Using PORT: $PORT" | tee -a /tmp/startup.log

# 显示环境变量
echo "Environment variables:" | tee -a /tmp/startup.log
env | grep -E "PORT|RAILWAY" | tee -a /tmp/startup.log

# 生成nginx配置
echo "Generating nginx config..." | tee -a /tmp/startup.log
envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Generated nginx config:" | tee -a /tmp/startup.log
cat /etc/nginx/conf.d/default.conf | tee -a /tmp/startup.log

# 测试nginx配置
echo "Testing nginx configuration..." | tee -a /tmp/startup.log
if nginx -t 2>&1 | tee -a /tmp/startup.log; then
    echo "Nginx config test PASSED" | tee -a /tmp/startup.log
else
    echo "Nginx config test FAILED" | tee -a /tmp/startup.log
    cat /tmp/startup.log
    exit 1
fi

# 检查端口是否被占用
echo "Checking if port $PORT is available..." | tee -a /tmp/startup.log
if netstat -ln | grep ":$PORT " >/dev/null 2>&1; then
    echo "WARNING: Port $PORT is already in use!" | tee -a /tmp/startup.log
    netstat -ln | grep ":$PORT " | tee -a /tmp/startup.log
fi

# 启动nginx
echo "Starting nginx..." | tee -a /tmp/startup.log
exec nginx -g 'daemon off;'
