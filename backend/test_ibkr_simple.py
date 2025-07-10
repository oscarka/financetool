#!/usr/bin/env python3
"""
简单的IBKR测试脚本
用于验证接口和数据存储逻辑
"""

import requests
import json
from datetime import datetime, timezone

# 配置
API_BASE_URL = "http://localhost:8000"
IBKR_API_KEY = "ibkr_sync_key_2024_test"

def test_ibkr_health():
    """测试IBKR健康检查"""
    print("🏥 测试IBKR健康检查...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ibkr/health", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"服务状态: {data.get('data', {}).get('status')}")
            print(f"配置有效: {data.get('data', {}).get('config_valid')}")
            print(f"数据库正常: {data.get('data', {}).get('database_ok')}")
            print(f"数据库信息: {data.get('data', {}).get('database_info')}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

def test_ibkr_sync():
    """测试IBKR数据同步"""
    print("\n🔄 测试IBKR数据同步...")
    
    # 构造测试数据
    test_data = {
        "account_id": "U13638726",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "balances": {
            "total_cash": 1000.50,
            "net_liquidation": 15000.75,
            "buying_power": 5000.25,
            "currency": "USD"
        },
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "market_value": 1500.00,
                "average_cost": 145.50,
                "unrealized_pnl": 45.00,
                "realized_pnl": 0.00,
                "currency": "USD",
                "asset_class": "STK"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": IBKR_API_KEY
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/ibkr/sync",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 同步成功!")
            print(f"   同步ID: {result.get('sync_id')}")
            print(f"   更新记录: {result.get('records_updated')}")
        else:
            print(f"❌ 同步失败")
            
    except Exception as e:
        print(f"错误: {e}")

def test_ibkr_data():
    """测试获取IBKR数据"""
    print("\n📊 测试获取IBKR数据...")
    
    # 测试余额
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ibkr/balances", timeout=10)
        print(f"余额接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"余额记录数: {data.get('count', 0)}")
        else:
            print(f"余额接口响应: {response.text}")
    except Exception as e:
        print(f"余额接口错误: {e}")
    
    # 测试持仓
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ibkr/positions", timeout=10)
        print(f"持仓接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"持仓记录数: {data.get('count', 0)}")
        else:
            print(f"持仓接口响应: {response.text}")
    except Exception as e:
        print(f"持仓接口错误: {e}")
    
    # 测试同步日志
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ibkr/logs?limit=5", timeout=10)
        print(f"日志接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"日志记录数: {data.get('count', 0)}")
        else:
            print(f"日志接口响应: {response.text}")
    except Exception as e:
        print(f"日志接口错误: {e}")

if __name__ == "__main__":
    print("🚀 开始IBKR简单测试...")
    print("=" * 50)
    
    # 1. 健康检查
    test_ibkr_health()
    
    # 2. 数据同步测试
    test_ibkr_sync()
    
    # 3. 查看数据
    test_ibkr_data()
    
    print("\n✅ 测试完成!") 