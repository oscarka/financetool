#!/bin/bash
set -e

# 添加详细的调试输出
echo "=== Flutter App Container Startup Debug ==="
echo "Script: $0"
echo "Current directory: $(pwd)"
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Environment variables:"
env | sort
echo "=== File System Check ==="
echo "Root directory contents:"
ls -la /
echo "Nginx directory contents:"
ls -la /usr/share/nginx/ || echo "Nginx directory not found"
echo "Nginx html directory contents:"
ls -la /usr/share/nginx/html/ || echo "Nginx html directory not found"
echo "=== Script continues ==="

# 创建调试信息HTML页面
create_debug_page() {
    local debug_file="/usr/share/nginx/html/debug.html"
    cat > "$debug_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Debug Information</title>
    <style>
        body { font-family: monospace; background: #1e1e1e; color: #fff; padding: 20px; }
        .section { margin: 20px 0; padding: 10px; border: 1px solid #555; }
        .success { color: #4CAF50; }
        .error { color: #f44336; }
        .warning { color: #ff9800; }
    </style>
</head>
<body>
    <h1>Flutter App Debug Information</h1>
    
    <div class="section">
        <h2>Container Startup</h2>
        <p>Date: $(date)</p>
        <p>Status: <span class="success">Container Started Successfully</span></p>
    </div>
    
    <div class="section">
        <h2>Environment Variables</h2>
        <pre>PORT: ${PORT:-"NOT SET"}
$(env | grep -E "PORT|RAILWAY" || echo "No RAILWAY vars found")</pre>
    </div>
    
    <div class="section">
        <h2>Generated nginx config</h2>
        <pre>$(cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo "Config not generated yet")</pre>
    </div>
    
    <div class="section">
        <h2>Nginx Configuration Test</h2>
        <pre id="nginx-test">Testing...</pre>
    </div>
    
    <div class="section">
        <h2>Port Status</h2>
        <pre id="port-status">Checking...</pre>
    </div>
    
    <div class="section">
        <h2>Process Status</h2>
        <pre>$(ps aux | grep nginx || echo "No nginx processes")</pre>
    </div>
    
    <div class="section">
        <h2>Quick Links</h2>
        <p><a href="/" style="color: #2196F3;">Main App</a></p>
        <p><a href="/health" style="color: #2196F3;">Health Check</a></p>
    </div>
</body>
</html>
EOF
}

echo "=== Container Starting ==="
echo "Date: $(date)"

# 设置端口
export PORT=${PORT:-80}
echo "Using PORT: $PORT"

# 生成nginx配置
echo "Generating nginx config..."
envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Generated nginx config:"
cat /etc/nginx/conf.d/default.conf

# 创建调试页面
create_debug_page

# 如果Flutter的index.html有问题，复制备用的简单页面
if [ ! -f "/usr/share/nginx/html/index.html" ] || [ ! -s "/usr/share/nginx/html/index.html" ]; then
    echo "Flutter index.html missing or empty, using simple fallback"
    cp /simple-index.html /usr/share/nginx/html/index.html
fi

# 测试nginx配置
echo "Testing nginx configuration..."
if nginx -t 2>&1; then
    echo "Nginx config test PASSED"
    config_status="PASSED"
else
    echo "Nginx config test FAILED"
    config_status="FAILED"
    exit 1
fi

# 检查端口
echo "Checking if port $PORT is available..."
port_status=$(netstat -ln | grep ":$PORT " || echo "Port available")

# 更新调试页面中的测试结果
sed -i "s/Testing.../$config_status/" /usr/share/nginx/html/debug.html
sed -i "s/Checking.../$port_status/" /usr/share/nginx/html/debug.html

# 启动nginx
echo "Starting nginx..."
exec nginx -g 'daemon off;'
