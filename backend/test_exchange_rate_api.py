import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_exchange_rate_api():
    """测试汇率API接口"""
    print("=== 测试汇率API接口 ===")
    
    # 1. 测试获取货币列表
    print("\n1. 测试获取货币列表:")
    try:
        response = requests.get(f"{BASE_URL}/exchange-rates/currencies")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取所有汇率
    print("\n2. 测试获取所有汇率:")
    try:
        response = requests.get(f"{BASE_URL}/exchange-rates/rates")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试获取指定货币汇率
    print("\n3. 测试获取美元汇率:")
    try:
        response = requests.get(f"{BASE_URL}/exchange-rates/rates/USD")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试货币转换
    print("\n4. 测试货币转换:")
    try:
        response = requests.get(f"{BASE_URL}/exchange-rates/convert?amount=100&from_currency=USD&to_currency=CNY")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_exchange_rate_api() 