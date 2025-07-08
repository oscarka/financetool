#!/bin/bash
# API接口快速测试脚本

echo "🚀 API接口管理工具"
echo "===================="

# 检查Python3是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3命令"
    exit 1
fi

# 检查工具文件是否存在
if [[ ! -f "api_tester_simple.py" ]]; then
    echo "❌ 错误: 未找到 api_tester_simple.py 文件"
    echo "请确保在 backend 目录下运行此脚本"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 显示菜单
while true; do
    echo "请选择操作:"
    echo "  1. 🏥 快速健康检查 (推荐)"
    echo "  2. 🧪 批量测试所有接口"
    echo "  3. 🚀 交互式测试"
    echo "  4. 📄 生成健康报告"
    echo "  5. 🔧 自定义服务器地址"
    echo "  6. 📚 启用API文档"
    echo "  0. 退出"
    echo ""
    
    read -p "请输入选择 (0-6): " choice
    
    case $choice in
        1)
            echo ""
            echo "🏥 执行快速健康检查..."
            python3 api_tester_simple.py --mode health
            ;;
        2)
            echo ""
            echo "🧪 执行批量接口测试..."
            python3 api_tester_simple.py --mode batch
            ;;
        3)
            echo ""
            echo "🚀 启动交互式测试..."
            python3 api_tester_simple.py --mode interactive
            ;;
        4)
            echo ""
            echo "📄 生成健康报告..."
            python3 api_tester_simple.py --mode report
            ;;
        5)
            echo ""
            read -p "请输入服务器地址 (例: http://localhost:8000): " server_url
            if [[ -n "$server_url" ]]; then
                echo "🔧 测试服务器: $server_url"
                python3 api_tester_simple.py --url "$server_url" --mode health
            else
                echo "❌ 地址不能为空"
            fi
            ;;
        6)
            echo ""
            echo "📚 启用API文档..."
            if [[ -f "enable_docs.py" ]]; then
                echo "🔓 启动带文档的服务器..."
                echo "文档将在以下地址可用:"
                echo "  - Swagger: http://localhost:8000/docs"
                echo "  - ReDoc: http://localhost:8000/redoc"
                echo ""
                echo "按 Ctrl+C 停止服务器"
                python3 enable_docs.py
            else
                echo "❌ 未找到 enable_docs.py 文件"
            fi
            ;;
        0)
            echo "👋 再见!"
            exit 0
            ;;
        *)
            echo "❌ 无效选择，请重新输入"
            ;;
    esac
    
    echo ""
    echo "按Enter继续..."
    read
    echo ""
done