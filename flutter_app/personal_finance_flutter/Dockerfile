# Flutter Web 应用的多阶段构建
FROM debian:latest AS build

# 安装必要的依赖
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
USER flutter

# 设置Flutter环境
ENV FLUTTER_HOME="/home/flutter/flutter"
ENV PATH="$FLUTTER_HOME/bin:$PATH"

# 克隆Flutter SDK
RUN git clone --depth 1 -b stable https://github.com/flutter/flutter.git $FLUTTER_HOME
RUN $FLUTTER_HOME/bin/flutter --version
RUN $FLUTTER_HOME/bin/flutter doctor

# 设置工作目录
WORKDIR /app

# 复制pubspec文件
COPY --chown=flutter:flutter pubspec.yaml pubspec.lock ./

# 获取Flutter依赖 (使用flutter命令而不是dart)
RUN $FLUTTER_HOME/bin/flutter pub get

# 复制项目源码
COPY --chown=flutter:flutter . .

# 构建Flutter Web应用
RUN $FLUTTER_HOME/bin/flutter build web --release --no-tree-shake-icons

# 生产阶段 - nginx静态文件服务器
FROM nginx:alpine

# 安装envsubst用于环境变量替换
RUN apk add --no-cache gettext

# 复制构建的web文件
COPY --from=build /app/build/web /usr/share/nginx/html

# 复制nginx配置模板
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# 设置默认端口
ENV PORT=80

# 暴露端口
EXPOSE $PORT

# 启动命令：替换环境变量并启动nginx
CMD envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'