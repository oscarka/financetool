#!/bin/bash

echo "🚀 启动Flutter投资组合应用..."

# 设置Flutter路径
export PATH="$PATH:/workspace/flutter/bin"

# 切换到Flutter项目目录
cd /workspace/flutter_app/personal_finance_flutter

# 检查Flutter是否正常工作
echo "检查Flutter版本..."
flutter --version

# 获取依赖
echo "获取依赖包..."
flutter pub get

# 启动Web服务器
echo "启动Web服务器在端口8080..."
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0

echo "应用启动完成！访问 http://localhost:8080 查看效果"