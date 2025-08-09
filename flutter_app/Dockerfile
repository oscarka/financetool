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
RUN apk add --no-cache gettext net-tools bash

# 调试信息：显示当前时间和构建信息
RUN echo "=== Docker Image Build Info ===" && \
    echo "Build time: $(date)" && \
    echo "Alpine version: $(cat /etc/alpine-release)" && \
    echo "Nginx version: $(nginx -v 2>&1)"

# 从构建阶段复制web文件
COPY --from=flutter-build /app/build/web /usr/share/nginx/html

# 复制nginx配置模板、启动脚本和备用页面
COPY personal_finance_flutter/nginx.conf.server /etc/nginx/conf.d/default.conf.template
COPY start.sh /start.sh
COPY simple-index.html /simple-index.html

# 调试：检查文件是否复制成功
RUN echo "=== Checking copied files ===" && \
    ls -la /start.sh && \
    ls -la /simple-index.html && \
    ls -la /etc/nginx/conf.d/default.conf.template && \
    echo "=== Web files in /usr/share/nginx/html ===" && \
    ls -la /usr/share/nginx/html/

# 设置脚本权限并创建健康检查
RUN chmod +x /start.sh && \
    echo '#!/bin/bash' > /health.sh && \
    echo 'curl -f http://localhost:$PORT/ || exit 1' >> /health.sh && \
    chmod +x /health.sh

# 设置环境变量
ENV PORT=80

# 暴露端口
EXPOSE $PORT

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /health.sh

# 使用启动脚本
CMD ["/start.sh"]
