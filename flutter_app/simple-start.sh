#!/bin/bash
echo "=== Simple Start Script Running ==="
echo "Date: $(date)"
echo "PWD: $(pwd)"
echo "USER: $(whoami)"

# 设置端口
export PORT=${PORT:-80}
echo "Using PORT: $PORT"

# 检查文件
echo "=== Checking files ==="
ls -la /usr/share/nginx/html/
ls -la /etc/nginx/conf.d/

# 创建基本nginx配置
cat > /etc/nginx/conf.d/default.conf << EOF
server {
    listen $PORT;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /debug {
        return 200 "debug: container running\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo "=== Generated nginx config ==="
cat /etc/nginx/conf.d/default.conf

# 测试nginx配置
echo "=== Testing nginx config ==="
nginx -t

# 启动nginx
echo "=== Starting nginx ==="
exec nginx -g 'daemon off;'
