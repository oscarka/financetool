#!/usr/bin/env python3
"""
IBKR连接测试脚本 - 简化版本
用于快速测试Railway后端连接和数据推送
"""

import requests
import json
from datetime import datetime, timezone

# 配置
RAILWAY_BACKEND_URL = "https://backend-production-e90f.up.railway.app"  # 请替换为您的Railway后端URL
API_KEY = "ibkr_sync_key_2024_test"

# 测试数据
test_data = {
    "account_id": "U13638726",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "balances": {
        "total_cash": 2.74,
        "net_liquidation": 5.70,
        "buying_power": 2.74,
        "currency": "USD"
    },
    "positions": [
        {
            "symbol": "TSLA",
            "quantity": 0.01,
            "market_value": 2.96,
            "average_cost": 0.0,
            "currency": "USD"
        }
    ]
}

def test_health():
    """测试健康检查"""
    try:
        url = f"{RAILWAY_BACKEND_URL}/api/v1/ibkr/health"
        print(f"🔍 测试健康检查: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 健康检查成功: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_sync():
    """测试数据同步"""
    try:
        url = f"{RAILWAY_BACKEND_URL}/api/v1/ibkr/sync"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print(f"🔍 测试数据同步: {url}")
        print(f"📤 发送数据: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 数据同步成功: {result}")
        return True
        
    except requests.RequestException as e:
        print(f"❌ 数据同步失败: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ 数据同步失败: {e}")
        return False

def main():
    print("=" * 50)
    print("IBKR Railway连接测试")
    print("=" * 50)
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    health_ok = test_health()
    
    # 测试数据同步
    print("\n2. 测试数据同步...")
    sync_ok = test_sync()
    
    print("\n" + "=" * 50)
    if health_ok and sync_ok:
        print("🎉 所有测试通过！IBKR集成工作正常！")
    else:
        print("⚠️ 部分测试失败，请检查配置")
    print("=" * 50)

if __name__ == "__main__":
    main()