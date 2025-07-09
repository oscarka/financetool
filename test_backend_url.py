#!/usr/bin/env python3
"""
测试Railway后端URL脚本
"""

import requests
import json

# 可能的Railway后端URL列表
possible_urls = [
    "https://backend-production-e90f.up.railway.app",
    "https://backend-production-xxxx.up.railway.app",  # 需要替换
    "https://your-backend-domain.railway.app",  # 需要替换
]

def test_url(base_url):
    """测试单个URL"""
    try:
        # 测试健康检查
        health_url = f"{base_url}/api/v1/ibkr/health"
        print(f"🔍 测试: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功! 响应: {result}")
            return True
        else:
            print(f"❌ 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("🔍 测试Railway后端URL...")
    print("=" * 50)
    
    for url in possible_urls:
        print(f"\n测试URL: {url}")
        if test_url(url):
            print(f"🎉 找到正确的后端URL: {url}")
            break
        print("-" * 30)
    
    print("\n" + "=" * 50)
    print("💡 提示: 请检查您的Railway仪表板获取正确的后端URL")

if __name__ == "__main__":
    main()