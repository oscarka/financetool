#!/bin/bash

# MCP服务部署脚本

echo "🚀 开始部署MCP服务..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $? -ne 0 ]]; then
    echo "❌ Python3未安装"
    exit 1
fi

echo "✅ Python版本: $python_version"

# 检查依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt

if [[ $? -ne 0 ]]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 检查环境变量
echo "🔧 检查环境变量..."

required_vars=("DEEPSEEK_API_KEY" "DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo "⚠️  缺少环境变量: ${missing_vars[*]}"
    echo "请设置这些环境变量或使用 .env 文件"
    
    # 检查.env文件
    if [[ -f ".env" ]]; then
        echo "📁 发现.env文件，正在加载..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "📝 创建.env.example文件作为参考"
        cp env.example .env.example
    fi
fi

# 启动服务
echo "🚀 启动MCP服务..."
echo "📍 服务地址: http://localhost:3001"
echo "📊 健康检查: http://localhost:3001/health"
echo "📚 API文档: http://localhost:3001/docs"

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
