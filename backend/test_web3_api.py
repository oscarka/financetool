#!/usr/bin/env python3
"""
Web3 API 测试脚本
测试所有的 Web3 API 功能
"""

import asyncio
import os
import sys
import httpx
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append('.')

async def test_web3_endpoints():
    """测试所有Web3 API端点"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 测试端点列表
    endpoints = [
        {
            "name": "Web3配置信息",
            "url": f"{base_url}/api/v1/okx/web3/config",
            "method": "GET"
        },
        {
            "name": "Web3连接测试",
            "url": f"{base_url}/api/v1/okx/web3/test",
            "method": "GET"
        },
        {
            "name": "Web3账户余额",
            "url": f"{base_url}/api/v1/okx/web3/balance",
            "method": "GET"
        },
        {
            "name": "Web3代币列表",
            "url": f"{base_url}/api/v1/okx/web3/tokens",
            "method": "GET"
        },
        {
            "name": "Web3交易记录",
            "url": f"{base_url}/api/v1/okx/web3/transactions?limit=10",
            "method": "GET"
        }
    ]
    
    print("=" * 60)
    print("Web3 API 测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试端点数量: {len(endpoints)}")
    print("=" * 60)
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            try:
                print(f"测试: {endpoint['name']}")
                print(f"URL: {endpoint['url']}")
                
                if endpoint['method'] == 'GET':
                    response = await client.get(endpoint['url'])
                else:
                    response = await client.post(endpoint['url'])
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 成功 - 状态码: {response.status_code}")
                    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    results.append({
                        "name": endpoint['name'],
                        "status": "成功",
                        "status_code": response.status_code,
                        "data": data
                    })
                else:
                    print(f"❌ 失败 - 状态码: {response.status_code}")
                    print(f"错误信息: {response.text}")
                    results.append({
                        "name": endpoint['name'],
                        "status": "失败",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                
            except Exception as e:
                print(f"❌ 异常: {str(e)}")
                results.append({
                    "name": endpoint['name'],
                    "status": "异常",
                    "error": str(e)
                })
            
            print("-" * 60)
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    success_count = len([r for r in results if r['status'] == '成功'])
    fail_count = len([r for r in results if r['status'] != '成功'])
    
    print(f"总测试数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/len(results)*100:.1f}%")
    
    if fail_count > 0:
        print("\n失败的测试:")
        for result in results:
            if result['status'] != '成功':
                print(f"  - {result['name']}: {result.get('error', '未知错误')}")
    
    return results

if __name__ == "__main__":
    # 设置环境变量
    os.environ['WEB3_API_KEY'] = '2e0bcec7-1673-4ca7-8623-37eae00b199d'
    os.environ['WEB3_API_SECRET'] = '6AD13C181D27AA31216A7075F7636313'
    os.environ['WEB3_PROJECT_ID'] = '0b9c8f048d24ded4fbf885b243bdcf69'
    os.environ['WEB3_ACCOUNT_ID'] = '17ad7785-ff25-4c5a-ab32-0f3bc63597df'
    os.environ['WEB3_PASSPHRASE'] = 'Oscar3579～'
    
    # 运行测试
    asyncio.run(test_web3_endpoints()) 