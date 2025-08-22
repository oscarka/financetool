#!/usr/bin/env python3
"""
测试Claude + MCP方案
验证工具调用和AI服务选择功能
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.mcp_tools import MCPTools
from app.services.claude_ai_service import ClaudeAIService

async def test_mcp_tools():
    """测试MCP工具功能"""
    print("🔧 测试MCP工具...")
    
    # 模拟数据库配置
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'financetool_test'),
        'user': os.getenv('DB_USER', 'financetool_user'),
        'password': os.getenv('DB_PASSWORD', 'financetool_pass')
    }
    
    try:
        # 初始化MCP工具
        mcp_tools = MCPTools(db_config)
        print(f"✅ MCP工具初始化成功，可用工具数量: {len(mcp_tools.get_tools())}")
        
        # 显示可用工具
        tools = mcp_tools.get_tools()
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        return mcp_tools
        
    except Exception as e:
        print(f"❌ MCP工具初始化失败: {e}")
        return None

async def test_claude_ai_service(mcp_tools):
    """测试Claude AI服务"""
    print("\n🤖 测试Claude AI服务...")
    
    try:
        # 初始化Claude AI服务
        claude_ai = ClaudeAIService(mcp_tools)
        
        if not claude_ai.api_key:
            print("⚠️  Claude API Key未配置，跳过测试")
            return None
        
        print(f"✅ Claude AI服务初始化成功")
        print(f"  - 模型: {claude_ai.model}")
        print(f"  - 可用工具: {len(claude_ai.tools)}")
        
        return claude_ai
        
    except Exception as e:
        print(f"❌ Claude AI服务初始化失败: {e}")
        return None

async def test_ai_analysis(claude_ai):
    """测试AI分析功能"""
    print("\n🧠 测试AI分析功能...")
    
    if not claude_ai:
        print("⚠️  跳过AI分析测试")
        return
    
    test_questions = [
        "查看我的资产分布情况",
        "分析最近一个月的资产趋势",
        "按平台分组显示资产占比"
    ]
    
    for question in test_questions:
        print(f"\n📝 测试问题: {question}")
        try:
            result = claude_ai.analyze_with_tools(question)
            print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"  ❌ 分析失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始测试Claude + MCP方案...\n")
    
    # 测试MCP工具
    mcp_tools = await test_mcp_tools()
    
    # 测试Claude AI服务
    claude_ai = await test_claude_ai_service(mcp_tools)
    
    # 测试AI分析
    await test_ai_analysis(claude_ai)
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    # 设置环境变量（测试用）
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '5432')
    os.environ.setdefault('DB_NAME', 'financetool_test')
    os.environ.setdefault('DB_USER', 'financetool_user')
    os.environ.setdefault('DB_PASSWORD', 'financetool_pass')
    
    # 运行测试
    asyncio.run(main())
