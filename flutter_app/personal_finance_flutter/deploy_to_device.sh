#!/bin/bash

echo "🚀 个人金融Flutter应用 - 真机部署脚本"
echo "=================================="

# 检查Flutter环境
echo "📱 检查Flutter环境..."
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter未安装，请先安装Flutter"
    exit 1
fi

# 检查设备连接
echo "🔍 检查连接的设备..."
flutter devices

echo ""
echo "📋 部署步骤："
echo "1. 确保iPhone已连接到Mac"
echo "2. 在iPhone上启用开发者模式："
echo "   设置 > 隐私与安全性 > 开发者模式 > 开启"
echo "3. 重启iPhone"
echo "4. 在iPhone上信任这台Mac"
echo "5. 运行以下命令部署到真机："
echo ""
echo "   flutter run -d <您的iPhone设备ID>"
echo ""
echo "💡 提示：如果看不到iPhone，请检查："
echo "   - USB连接是否正常"
echo "   - iPhone是否已解锁"
echo "   - 是否已信任Mac"
echo "   - 开发者模式是否已开启"
echo ""
echo "🎯 准备就绪！请在iPhone上完成设置后运行部署命令"
