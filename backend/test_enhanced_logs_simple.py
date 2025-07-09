#!/usr/bin/env python3
"""
简单测试增强日志系统核心功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.enhanced_logger import (
    log_api_detailed, log_business_detailed, log_fund_api_detailed,
    log_okx_api_detailed, log_error_detailed, log_database_detailed
)
import json
from pathlib import Path

def test_enhanced_logging():
    """测试增强日志系统"""
    print("🧪 测试增强日志系统核心功能...")
    
    # 生成各种类型的测试日志
    print("\n1. 生成测试日志...")
    
    # API日志
    log_api_detailed("用户登录API调用", extra_data={
        "endpoint": "/api/v1/auth/login",
        "method": "POST",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.100",
        "response_time": 0.15
    })
    
    # 业务日志
    log_business_detailed("用户登录成功", extra_data={
        "user_id": 12345,
        "action": "login",
        "result": "success",
        "login_time": "2025-07-09T14:00:00"
    })
    
    # 基金API日志
    log_fund_api_detailed("获取基金净值", extra_data={
        "endpoint": "/api/fund/nav",
        "fund_code": "000001",
        "nav_date": "2025-07-09",
        "nav_value": 1.2345,
        "response_time": 0.5
    })
    
    # OKX API日志
    log_okx_api_detailed("获取OKX账户余额", extra_data={
        "endpoint": "/api/v5/account/balance",
        "total_balance": "10000.00",
        "currency": "USDT",
        "response_time": 0.3
    })
    
    # 数据库日志
    log_database_detailed("查询用户信息", extra_data={
        "operation": "SELECT",
        "table": "users",
        "query": "SELECT * FROM users WHERE id = 12345",
        "execution_time": 0.02,
        "rows_returned": 1
    })
    
    # 错误日志
    log_error_detailed("数据库连接失败", extra_data={
        "error_type": "ConnectionError",
        "error_message": "无法连接到数据库服务器",
        "retry_count": 3,
        "last_attempt": "2025-07-09T14:00:05"
    })
    
    print("✅ 测试日志生成完成")
    
    # 检查日志文件
    print("\n2. 检查日志文件...")
    log_dir = Path("./logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"找到 {len(log_files)} 个日志文件:")
        
        for log_file in log_files:
            file_size = log_file.stat().st_size
            print(f"  - {log_file.name}: {file_size} bytes")
            
            # 显示文件内容示例
            if file_size > 0:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            last_line = lines[-1].strip()
                            print(f"    最新日志: {last_line[:100]}...")
                except Exception as e:
                    print(f"    读取失败: {e}")
    else:
        print("❌ 日志目录不存在")
    
    # 验证JSON格式
    print("\n3. 验证JSON格式...")
    try:
        with open("./logs/LogCategory.API.log", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                log_data = json.loads(last_line)
                print("✅ API日志JSON格式正确")
                print(f"  分类: {log_data.get('category')}")
                print(f"  级别: {log_data.get('level')}")
                print(f"  消息: {log_data.get('message')}")
                if 'details' in log_data:
                    print(f"  详细信息: {json.dumps(log_data['details'], indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ JSON格式验证失败: {e}")
    
    print("\n✅ 增强日志系统测试完成！")

if __name__ == "__main__":
    test_enhanced_logging()