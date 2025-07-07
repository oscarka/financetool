#!/bin/bash

# 快速调试脚本 - 一键获取错误日志
# 使用方法: ./quick_debug.sh

echo "🔍 Railway 快速调试工具"
echo "=========================="

# 检查 Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI 未安装，请运行: npm install -g @railway/cli"
    exit 1
fi

# 获取项目状态
echo "📊 检查项目状态..."
railway status

echo ""
echo "🚨 获取错误日志 (最近50条):"
echo "----------------------------"
railway logs --deployment | grep -i "error\|exception\|fail\|panic\|fatal" | tail -50

echo ""
echo "⚠️  获取警告日志 (最近20条):"
echo "----------------------------"  
railway logs --deployment | grep -i "warn\|warning" | tail -20

echo ""
echo "📈 获取最新日志 (最近30条):"
echo "----------------------------"
railway logs --deployment | tail -30

echo ""
echo "💡 复制以上输出给AI助手进行调试分析"