#!/usr/bin/env python3
"""
测试增强日志系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.enhanced_logger import (
    log_api_detailed, log_database_detailed, log_business_detailed,
    log_fund_api_detailed, log_okx_api_detailed, log_error_detailed,
    log_fund_operation, log_database_operation, log_api_request
)
import time

def test_enhanced_logging():
    """测试增强日志系统"""
    print("🧪 开始测试增强日志系统...")
    
    # 测试API日志
    log_api_detailed("测试API请求", extra_data={
        "method": "GET",
        "path": "/api/v1/funds/operations",
        "user_agent": "test-client",
        "ip_address": "127.0.0.1"
    })
    
    # 测试数据库日志
    log_database_operation(
        operation="SELECT",
        table="fund_operations",
        data={"fund_code": "000001", "limit": 10},
        execution_time=0.15
    )
    
    # 测试业务日志
    log_business_detailed("测试业务操作", extra_data={
        "user_id": 123,
        "action": "create_fund_operation",
        "result": "success"
    })
    
    # 测试基金API日志
    log_fund_api_detailed("测试基金API调用", extra_data={
        "endpoint": "/api/fund/nav",
        "fund_code": "000001",
        "response_time": 0.5,
        "status_code": 200
    })
    
    # 测试OKX API日志
    log_okx_api_detailed("测试OKX API调用", extra_data={
        "endpoint": "/api/v5/account/balance",
        "response_data": {"total_balance": "1000.00"},
        "execution_time": 0.3
    })
    
    # 测试基金操作日志
    log_fund_operation(
        operation_type="buy",
        fund_code="000001",
        amount=1000.0,
        quantity=100.0,
        price=10.0,
        platform="蚂蚁财富",
        operation_id=456
    )
    
    # 测试API请求日志
    log_api_request(
        method="POST",
        path="/api/v1/funds/operations",
        params={"fund_code": "000001"},
        response_status=200,
        execution_time=0.25
    )
    
    # 测试错误日志
    try:
        raise ValueError("这是一个测试错误")
    except Exception as e:
        log_error_detailed("测试错误日志", extra_data={
            "error_type": "ValueError",
            "error_message": str(e),
            "stack_trace": "测试堆栈跟踪"
        })
    
    print("✅ 增强日志系统测试完成！")
    print("📁 请检查 logs/ 目录下的日志文件")

if __name__ == "__main__":
    test_enhanced_logging()