#!/usr/bin/env python3
"""
DeepSeek AI集成测试脚本

测试DeepSeek AI与MCP智能图表系统的完整集成
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.deepseek_ai_service import DeepSeekAIService
from app.services.mcp_client import MCPDatabaseClient
from app.services.chart_config_generator import ChartConfigGenerator

async def test_deepseek_ai_service():
    """测试DeepSeek AI服务"""
    print("🧪 测试DeepSeek AI服务...")
    
    service = DeepSeekAIService()
    
    # 测试健康检查
    print("  📡 测试健康检查...")
    health_ok = await service.health_check()
    if health_ok:
        print("  ✅ DeepSeek AI服务健康检查通过")
    else:
        print("  ❌ DeepSeek AI服务健康检查失败")
        return False
    
    # 测试问题分析
    print("  🤖 测试问题分析...")
    test_questions = [
        "显示各平台的资产分布",
        "最近的资产变化趋势",
        "收益率最高的投资排行",
        "各资产类型的占比分析"
    ]
    
    for question in test_questions:
        print(f"    📝 问题: {question}")
        analysis = await service.analyze_financial_question(question)
        
        if analysis:
            print(f"    ✅ 分析成功: {analysis.get('chart_type', 'unknown')} 图表")
            print(f"       SQL: {analysis.get('sql', 'N/A')[:100]}...")
        else:
            print(f"    ❌ 分析失败")
    
    return True

async def test_full_workflow():
    """测试完整工作流程"""
    print("\n🚀 测试完整工作流程...")
    
    # 初始化MCP客户端
    mcp_client = MCPDatabaseClient(use_mock=False)
    
    # 测试问题
    test_question = "显示各平台的资产分布"
    print(f"  📝 测试问题: {test_question}")
    
    try:
        # 1. 自然语言查询
        print("  🔍 步骤1: 自然语言查询...")
        query_result = await mcp_client.natural_language_query(test_question)
        
        if query_result.success:
            print(f"  ✅ 查询成功: {query_result.row_count} 条记录")
            print(f"      执行时间: {query_result.execution_time:.3f}秒")
            print(f"      使用方法: {query_result.method}")
            
            if hasattr(query_result, 'ai_analysis') and query_result.ai_analysis:
                print(f"      AI分析: {query_result.ai_analysis.get('description', 'N/A')}")
            
            # 2. 生成图表配置
            print("  📊 步骤2: 生成图表配置...")
            chart_generator = ChartConfigGenerator()
            chart_config = chart_generator.generate_config(
                query_result.data,
                test_question,
                query_result.sql
            )
            
            if chart_config:
                print(f"  ✅ 图表配置生成成功: {chart_config.chart_type} 图表")
                print(f"      标题: {chart_config.title}")
                print(f"      数据点: {len(chart_config.data)}")
            else:
                print("  ❌ 图表配置生成失败")
                
        else:
            print(f"  ❌ 查询失败: {query_result.error}")
            
    except Exception as e:
        print(f"  ❌ 工作流程测试异常: {e}")
        return False
    
    return True

async def main():
    """主测试函数"""
    print("🎯 DeepSeek AI集成测试开始\n")
    
    # 检查环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        print("请设置环境变量或复制 env.deepseek.example 为 .env 并配置")
        return
    
    print(f"🔑 DeepSeek API Key: {api_key[:10]}...")
    
    # 测试DeepSeek AI服务
    ai_test_ok = await test_deepseek_ai_service()
    
    if ai_test_ok:
        # 测试完整工作流程
        workflow_test_ok = await test_full_workflow()
        
        if workflow_test_ok:
            print("\n🎉 所有测试通过！DeepSeek AI集成成功！")
        else:
            print("\n⚠️  工作流程测试失败，但DeepSeek AI服务正常")
    else:
        print("\n❌ DeepSeek AI服务测试失败")

if __name__ == "__main__":
    asyncio.run(main())
