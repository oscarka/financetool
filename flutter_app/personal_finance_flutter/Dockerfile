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

# 下载并安装Flutter
RUN git clone https://github.com/flutter/flutter.git $FLUTTER_HOME
RUN $FLUTTER_HOME/bin/flutter channel stable
RUN $FLUTTER_HOME/bin/flutter upgrade
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

# 复制构建的文件到nginx目录
COPY --from=build-env /app/build/web /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
