#!/usr/bin/env python3
"""
OKX 接口管理测试脚本
测试所有的 OKX API 功能
"""

import asyncio
import os
import sys
import httpx
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append('.')

async def test_okx_endpoints():
    """测试所有OKX API端点"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 测试端点列表
    endpoints = [
        {
            "name": "配置信息",
            "url": f"{base_url}/api/v1/funds/okx/config",
            "method": "GET"
        },
        {
            "name": "连接测试",
            "url": f"{base_url}/api/v1/funds/okx/test",
            "method": "GET"
        },
        {
            "name": "行情数据",
            "url": f"{base_url}/api/v1/funds/okx/ticker?inst_id=BTC-USDT",
            "method": "GET"
        },
        {
            "name": "所有行情",
            "url": f"{base_url}/api/v1/funds/okx/tickers?inst_type=SPOT",
            "method": "GET"
        },
        {
            "name": "交易产品",
            "url": f"{base_url}/api/v1/funds/okx/instruments?inst_type=SPOT",
            "method": "GET"
        },
        {
            "name": "账户资产",
            "url": f"{base_url}/api/v1/funds/okx/account",
            "method": "GET"
        },
        {
            "name": "持仓信息",
            "url": f"{base_url}/api/v1/funds/okx/positions",
            "method": "GET"
        },
        {
            "name": "账单流水",
            "url": f"{base_url}/api/v1/funds/okx/bills?limit=10",
            "method": "GET"
        }
    ]
    
    print("=" * 60)
    print("OKX 接口管理测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试端点数量: {len(endpoints)}")
    print("=" * 60)
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, endpoint in enumerate(endpoints, 1):
            print(f"\n[{i}/{len(endpoints)}] 测试: {endpoint['name']}")
            print(f"URL: {endpoint['url']}")
            
            try:
                if endpoint['method'] == 'GET':
                    response = await client.get(endpoint['url'])
                else:
                    response = await client.post(endpoint['url'])
                
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        success = data.get('success', False)
                        message = data.get('message', 'No message')
                        
                        print(f"业务状态: {'✅ 成功' if success else '❌ 失败'}")
                        print(f"响应消息: {message}")
                        
                        # 显示部分数据
                        if data.get('data'):
                            data_info = data['data']
                            if isinstance(data_info, dict):
                                if 'data' in data_info and isinstance(data_info['data'], list):
                                    print(f"数据数量: {len(data_info['data'])}")
                                elif 'api_configured' in data_info:
                                    print(f"API配置状态: {data_info['api_configured']}")
                                    print(f"沙盒模式: {data_info.get('sandbox_mode', 'N/A')}")
                                elif 'public_api' in data_info:
                                    print(f"公共API: {data_info['public_api']}")
                                    print(f"私有API: {data_info['private_api']}")
                                    if data_info.get('private_error'):
                                        print(f"私有API错误: {data_info['private_error']}")
                        
                        results.append({
                            'name': endpoint['name'],
                            'status': 'SUCCESS' if success else 'BUSINESS_FAIL',
                            'message': message
                        })
                        
                    except json.JSONDecodeError:
                        print("❌ JSON解析失败")
                        print(f"响应内容: {response.text[:200]}...")
                        results.append({
                            'name': endpoint['name'],
                            'status': 'JSON_ERROR',
                            'message': 'JSON解析失败'
                        })
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                    print(f"错误内容: {response.text[:200]}...")
                    results.append({
                        'name': endpoint['name'],
                        'status': 'HTTP_ERROR',
                        'message': f'HTTP {response.status_code}'
                    })
                    
            except Exception as e:
                print(f"❌ 异常: {str(e)}")
                results.append({
                    'name': endpoint['name'],
                    'status': 'EXCEPTION',
                    'message': str(e)
                })
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    success_count = len([r for r in results if r['status'] == 'SUCCESS'])
    business_fail_count = len([r for r in results if r['status'] == 'BUSINESS_FAIL'])
    error_count = len([r for r in results if r['status'] not in ['SUCCESS', 'BUSINESS_FAIL']])
    
    print(f"总计: {len(results)} 个端点")
    print(f"✅ 成功: {success_count}")
    print(f"⚠️  业务失败: {business_fail_count}")
    print(f"❌ 错误: {error_count}")
    
    if error_count > 0:
        print("\n错误详情:")
        for result in results:
            if result['status'] not in ['SUCCESS', 'BUSINESS_FAIL']:
                print(f"  - {result['name']}: {result['status']} - {result['message']}")
    
    if business_fail_count > 0:
        print("\n业务失败详情:")
        for result in results:
            if result['status'] == 'BUSINESS_FAIL':
                print(f"  - {result['name']}: {result['message']}")
    
    print(f"\n测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    print("启动OKX接口管理测试...")
    print("确保后端服务正在运行在 http://localhost:8000")
    print()
    
    try:
        asyncio.run(test_okx_endpoints())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试发生未预期错误: {e}")
        import traceback
        traceback.print_exc() 