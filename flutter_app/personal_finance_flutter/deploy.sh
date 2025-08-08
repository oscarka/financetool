#!/bin/bash

# Flutter Web部署脚本

echo "🚀 开始部署Flutter Web应用..."

# 检查Flutter环境
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter未安装，请先安装Flutter SDK"
    exit 1
fi

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
flutter clean

# 获取依赖
echo "📦 安装依赖..."
flutter pub get

# 构建Web版本
echo "🔨 构建Web版本..."
flutter build web --release

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "✅ 构建成功！"
    echo "📁 构建文件位于: build/web/"
    echo "🌐 可以通过以下命令启动本地服务器:"
    echo "   cd build/web && python3 -m http.server 8080"
else
    echo "❌ 构建失败！"
    exit 1
fi

echo "🎉 部署准备完成！"
