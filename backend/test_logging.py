#!/usr/bin/env python3
"""
测试日志系统
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.logger import (
    log_api, log_database, log_scheduler, log_business, log_error, log_system, log_security,
    log_fund_api, log_okx_api, log_wise_api, log_paypal_api, log_exchange_api, log_external_other
)
from app.utils.auto_logger import auto_log, log_context, quick_log

@auto_log("fund")
async def test_fund_api():
    """测试基金API日志"""
    return {"fund_code": "000001", "nav": 1.2345}

@auto_log("okx")
async def test_okx_api():
    """测试OKX API日志"""
    return {"balance": 1000.50, "currency": "USDT"}

@auto_log("wise")
async def test_wise_api():
    """测试Wise API日志"""
    return {"account_id": "12345", "balance": 500.75}

@auto_log("paypal")
async def test_paypal_api():
    """测试PayPal API日志"""
    return {"account_id": "paypal_123", "balance": 250.00}

@auto_log("exchange")
async def test_exchange_api():
    """测试汇率API日志"""
    return {"from": "USD", "to": "CNY", "rate": 7.2}

@auto_log("database")
async def test_database():
    """测试数据库日志"""
    return {"query": "SELECT * FROM users", "rows": 10}

@auto_log("system")
async def test_system():
    """测试系统日志"""
    return {"status": "healthy", "uptime": 3600}

async def test_all_logs():
    """测试所有类型的日志"""
    print("开始测试日志系统...")
    
    # 测试基础日志函数
    log_api("测试API请求", extra_data={"endpoint": "/api/test", "method": "GET"})
    log_database("测试数据库查询", extra_data={"table": "users", "operation": "SELECT"})
    log_scheduler("测试定时任务", extra_data={"task": "sync_data", "interval": "1h"})
    log_business("测试业务逻辑", extra_data={"user_id": 123, "action": "login"})
    log_error("测试错误日志", extra_data={"error_code": 500, "details": "Internal error"})
    log_system("测试系统日志", extra_data={"component": "auth", "status": "running"})
    log_security("测试安全日志", extra_data={"ip": "192.168.1.1", "event": "login_attempt"})
    
    # 测试外部API日志
    log_fund_api("测试基金API", extra_data={"fund_code": "000001", "source": "tiantian"})
    log_okx_api("测试OKX API", extra_data={"endpoint": "/balance", "response_time": 150})
    log_wise_api("测试Wise API", extra_data={"profile_id": "123", "currency": "USD"})
    log_paypal_api("测试PayPal API", extra_data={"transaction_id": "txn_123", "amount": 100})
    log_exchange_api("测试汇率API", extra_data={"from": "USD", "to": "CNY", "rate": 7.2})
    log_external_other("测试其他外部API", extra_data={"service": "weather", "location": "Beijing"})
    
    # 测试自动化日志装饰器
    print("\n测试自动化日志装饰器...")
    await test_fund_api()
    await test_okx_api()
    await test_wise_api()
    await test_paypal_api()
    await test_exchange_api()
    await test_database()
    await test_system()
    
    # 测试上下文管理器
    print("\n测试上下文管理器...")
    with log_context("fund", "批量获取基金净值"):
        log_fund_api("获取基金000001净值")
        log_fund_api("获取基金000002净值")
        log_fund_api("获取基金000003净值")
    
    with log_context("database", "批量插入数据"):
        log_database("插入用户数据")
        log_database("插入订单数据")
        log_database("插入日志数据")
    
    # 测试快速日志
    print("\n测试快速日志...")
    quick_log("快速信息日志", "business")
    quick_log("快速错误日志", "error", level="ERROR")
    
    print("\n日志测试完成！")
    print("请访问 /logs-viewer 查看日志")

if __name__ == "__main__":
    asyncio.run(test_all_logs())