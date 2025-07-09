#!/usr/bin/env python3
"""
测试增强日志API功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.v1.enhanced_logs import read_detailed_logs_from_files, get_detailed_log_categories
import json

def test_enhanced_logs_api():
    """测试增强日志API功能"""
    print("🧪 测试增强日志API功能...")
    
    # 测试获取日志分类
    print("\n1. 测试获取日志分类:")
    try:
        import asyncio
        categories = asyncio.run(get_detailed_log_categories())
        print("✅ 日志分类获取成功")
        print(f"分类数量: {len(categories['categories'])}")
        print("分类列表:")
        for category in categories['categories']:
            desc = categories['category_descriptions'].get(category, '未知')
            print(f"  - {category}: {desc}")
    except Exception as e:
        print(f"❌ 获取日志分类失败: {e}")
    
    # 测试读取所有日志
    print("\n2. 测试读取所有日志:")
    try:
        logs = read_detailed_logs_from_files(limit=10)
        print(f"✅ 成功读取 {len(logs)} 条日志")
        
        if logs:
            print("\n第一条日志详情:")
            log = logs[0]
            print(f"  时间: {log.timestamp}")
            print(f"  级别: {log.level}")
            print(f"  分类: {log.category}")
            print(f"  消息: {log.message}")
            if log.details:
                print(f"  详细信息: {json.dumps(log.details, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 读取日志失败: {e}")
    
    # 测试按分类过滤日志
    print("\n3. 测试按分类过滤日志:")
    try:
        api_logs = read_detailed_logs_from_files(category="api", limit=5)
        print(f"✅ API分类日志: {len(api_logs)} 条")
        
        business_logs = read_detailed_logs_from_files(category="business", limit=5)
        print(f"✅ 业务分类日志: {len(business_logs)} 条")
        
        fund_api_logs = read_detailed_logs_from_files(category="fund_api", limit=5)
        print(f"✅ 基金API分类日志: {len(fund_api_logs)} 条")
    except Exception as e:
        print(f"❌ 按分类过滤失败: {e}")
    
    # 测试搜索功能
    print("\n4. 测试搜索功能:")
    try:
        search_logs = read_detailed_logs_from_files(search="API", limit=5)
        print(f"✅ 搜索'API'关键词: {len(search_logs)} 条")
        
        if search_logs:
            print("搜索结果:")
            for log in search_logs[:3]:
                print(f"  - [{log.category}] {log.message}")
    except Exception as e:
        print(f"❌ 搜索功能失败: {e}")
    
    print("\n✅ 增强日志API测试完成！")

if __name__ == "__main__":
    test_enhanced_logs_api()