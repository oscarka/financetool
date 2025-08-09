# Flutter Web 应用 - Railway 部署专用
FROM debian:latest AS flutter-build

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# 创建flutter用户
RUN useradd -m -s /bin/bash flutter

# 切换到flutter用户
USER flutter

# 设置Flutter环境变量
ENV FLUTTER_HOME="/home/flutter/flutter"
ENV PATH="$FLUTTER_HOME/bin:$PATH"

# 下载并安装Flutter SDK
RUN git clone --depth 1 -b stable https://github.com/flutter/flutter.git $FLUTTER_HOME

# 初始化Flutter
RUN flutter doctor

# 创建工作目录
WORKDIR /app

# 复制Flutter配置文件 (重命名以避免Railway自动检测)
COPY --chown=flutter:flutter personal_finance_flutter/flutter_pubspec.yaml pubspec.yaml
COPY --chown=flutter:flutter personal_finance_flutter/pubspec.lock ./

# 安装Flutter依赖 - 明确使用flutter pub get
RUN flutter pub get

# 复制所有源代码
COPY --chown=flutter:flutter personal_finance_flutter/ .

# 构建Flutter Web应用
RUN flutter build web --release --no-tree-shake-icons

# 生产环境 - 使用nginx提供静态文件服务
FROM nginx:alpine AS production

# 安装gettext用于环境变量替换，net-tools用于调试
RUN apk add --no-cache gettext net-tools

# 从构建阶段复制web文件
COPY --from=flutter-build /app/build/web /usr/share/nginx/html

# 内联创建nginx配置模板（使用printf避免Dockerfile语法冲突）
RUN printf 'server {\n    listen $PORT;\n    server_name localhost;\n\n    location / {\n        root /usr/share/nginx/html;\n        index index.html;\n        try_files $uri $uri/ /index.html;\n    }\n\n    location /health {\n        return 200 "healthy\\n";\n        add_header Content-Type text/plain;\n    }\n\n    location /debug {\n        return 200 "Container running on port $PORT\\n";\n        add_header Content-Type text/plain;\n    }\n}\n' > /etc/nginx/conf.d/default.conf.template

# 创建备用index.html（使用printf避免heredoc问题）
RUN printf '<!DOCTYPE html>\n<html>\n<head><title>Flutter App - Container Running</title></head>\n<body style="font-family: Arial; text-align: center; padding: 50px;">\n<h1>🎉 Flutter App Container is Running!</h1>\n<p>✅ Docker build successful</p>\n<p>✅ Nginx configured</p>\n<p>✅ Container started</p>\n<p><a href="/health">Health Check</a> | <a href="/debug">Debug Info</a></p>\n</body>\n</html>\n' > /backup-index.html

# 验证创建的文件
RUN echo "=== Created files ===" && \
    ls -la /etc/nginx/conf.d/default.conf.template && \
    ls -la /backup-index.html && \
    echo "=== Template content ===" && \
    cat /etc/nginx/conf.d/default.conf.template

# 设置环境变量
ENV PORT=80

# 暴露端口
EXPOSE $PORT

# 完全自包含的启动命令
CMD ["/bin/bash", "-c", "\
    export PORT=${PORT:-80} && \
    echo '=== Container Starting on port:' $PORT '===' && \
    if [ ! -f '/usr/share/nginx/html/index.html' ] || [ ! -s '/usr/share/nginx/html/index.html' ]; then \
    echo 'Flutter index.html missing, using backup' && \
    cp /backup-index.html /usr/share/nginx/html/index.html; \
    fi && \
    echo 'Processing nginx template...' && \
    envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && \
    echo 'Generated nginx config:' && \
    cat /etc/nginx/conf.d/default.conf && \
    echo 'Testing nginx config...' && \
    nginx -t && \
    echo 'Starting nginx...' && \
    exec nginx -g 'daemon off;'\
    "]
