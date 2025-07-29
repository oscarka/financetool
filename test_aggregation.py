#!/usr/bin/env python3
"""
测试聚合功能
"""
import requests
import json
import time

def test_aggregation_api():
    """测试聚合API"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 开始测试聚合API...")
    
    # 测试健康检查
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ 健康检查: {response.status_code}")
        if response.status_code == 200:
            print(f"📊 健康数据: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 测试聚合统计数据
    try:
        response = requests.get(f"{base_url}/aggregation/stats?base_currency=CNY", timeout=10)
        print(f"✅ 聚合统计API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 聚合统计API失败: {response.text}")
    except Exception as e:
        print(f"❌ 聚合统计API异常: {e}")
    
    # 测试趋势数据
    try:
        response = requests.get(f"{base_url}/aggregation/trend?days=30&base_currency=CNY", timeout=10)
        print(f"✅ 趋势数据API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📈 趋势数据: {len(data.get('data', []))} 条记录")
        else:
            print(f"❌ 趋势数据API失败: {response.text}")
    except Exception as e:
        print(f"❌ 趋势数据API异常: {e}")
    
    # 测试资产类型分布
    try:
        response = requests.get(f"{base_url}/aggregation/distribution/asset-type?base_currency=CNY", timeout=10)
        print(f"✅ 资产类型分布API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 资产类型分布: {len(data.get('data', []))} 种类型")
        else:
            print(f"❌ 资产类型分布API失败: {response.text}")
    except Exception as e:
        print(f"❌ 资产类型分布API异常: {e}")
    
    # 测试平台分布
    try:
        response = requests.get(f"{base_url}/aggregation/distribution/platform?base_currency=CNY", timeout=10)
        print(f"✅ 平台分布API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"🏦 平台分布: {len(data.get('data', []))} 个平台")
        else:
            print(f"❌ 平台分布API失败: {response.text}")
    except Exception as e:
        print(f"❌ 平台分布API异常: {e}")
    
    # 测试完整仪表板数据
    try:
        response = requests.get(f"{base_url}/aggregation/dashboard?base_currency=CNY&days=30", timeout=15)
        print(f"✅ 仪表板数据API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 仪表板数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 仪表板数据API失败: {response.text}")
    except Exception as e:
        print(f"❌ 仪表板数据API异常: {e}")
    
    print("🎉 聚合API测试完成!")

if __name__ == "__main__":
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    test_aggregation_api()