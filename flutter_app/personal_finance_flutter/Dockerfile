# 使用官方Flutter镜像
FROM debian:latest AS build-env

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -s /bin/bash flutter
USER flutter

# 设置Flutter环境变量
ENV FLUTTER_HOME="/home/flutter/flutter"
ENV PATH="$FLUTTER_HOME/bin:$PATH"

# 下载并安装Flutter (指定较新版本)
RUN git clone https://github.com/flutter/flutter.git $FLUTTER_HOME
RUN cd $FLUTTER_HOME && git checkout stable
RUN cd $FLUTTER_HOME && git pull origin stable
RUN $FLUTTER_HOME/bin/flutter channel stable
RUN $FLUTTER_HOME/bin/flutter upgrade --force
RUN $FLUTTER_HOME/bin/flutter doctor

# 设置工作目录
WORKDIR /app

# 复制pubspec文件
COPY --chown=flutter:flutter pubspec.yaml pubspec.lock ./

# 获取依赖
RUN flutter pub get

# 复制源代码
COPY --chown=flutter:flutter . .

# 构建Web版本（禁用图标树摇）
RUN flutter build web --release --no-tree-shake-icons

# 使用nginx提供静态文件服务
FROM nginx:alpine

# 安装envsubst工具（用于环境变量替换）
RUN apk add --no-cache gettext

# 复制构建的文件到nginx目录
COPY --from=build-env /app/build/web /usr/share/nginx/html

# 复制nginx配置模板
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# 设置默认端口
ENV PORT=80

# 暴露端口
EXPOSE $PORT

# 启动时替换环境变量并启动nginx
CMD envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
