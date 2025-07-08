#!/usr/bin/env python3
"""
IBKR API集成测试脚本

此脚本用于测试IBKR API的各项功能，包括：
1. 配置验证
2. 数据同步
3. 数据查询
4. 错误处理

使用方法：
python test_ibkr_api.py
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional


class IBKRAPITester:
    """IBKR API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "test_key"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
    async def test_config(self) -> Dict[str, Any]:
        """测试配置获取"""
        print("🔧 测试配置获取...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/config")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 配置获取成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 配置获取失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 配置获取异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        print("🔗 测试连接状态...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/test")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 连接测试成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 连接测试失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 连接测试异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_sync_data(self, test_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """测试数据同步"""
        print("📊 测试数据同步...")
        
        # 默认测试数据
        if not test_data:
            test_data = {
                "account_id": "U13638726",
                "timestamp": datetime.now().isoformat() + "Z",
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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/ibkr/sync",
                    headers=self.headers,
                    json=test_data
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 数据同步成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 数据同步失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 数据同步异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_get_balances(self) -> Dict[str, Any]:
        """测试获取余额"""
        print("💰 测试获取余额...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/balances")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 余额获取成功: 找到 {data['count']} 条记录")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 余额获取失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 余额获取异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_get_positions(self) -> Dict[str, Any]:
        """测试获取持仓"""
        print("📈 测试获取持仓...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/positions")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 持仓获取成功: 找到 {data['count']} 条记录")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 持仓获取失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 持仓获取异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_get_logs(self) -> Dict[str, Any]:
        """测试获取同步日志"""
        print("📝 测试获取同步日志...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/logs?limit=10")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 日志获取成功: 找到 {data['count']} 条记录")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 日志获取失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 日志获取异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_get_summary(self) -> Dict[str, Any]:
        """测试获取汇总信息"""
        print("📊 测试获取汇总信息...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/summary")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 汇总信息获取成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 汇总信息获取失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 汇总信息获取异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_health_check(self) -> Dict[str, Any]:
        """测试健康检查"""
        print("🏥 测试健康检查...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/ibkr/health")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 健康检查成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 健康检查失败: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
            except Exception as e:
                print(f"❌ 健康检查异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def test_invalid_api_key(self) -> Dict[str, Any]:
        """测试无效API密钥"""
        print("🔒 测试API密钥验证...")
        invalid_headers = {
            "X-API-Key": "invalid_key",
            "Content-Type": "application/json"
        }
        
        test_data = {
            "account_id": "U13638726",
            "timestamp": datetime.now().isoformat() + "Z",
            "balances": {
                "total_cash": 1.0,
                "net_liquidation": 1.0,
                "buying_power": 1.0,
                "currency": "USD"
            },
            "positions": []
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/ibkr/sync",
                    headers=invalid_headers,
                    json=test_data
                )
                if response.status_code == 401:
                    print("✅ API密钥验证正常工作")
                    return {"status": "success", "message": "API key validation working"}
                else:
                    print(f"❌ API密钥验证失败: 应该返回401，实际返回 {response.status_code}")
                    return {"status": "error", "error": f"Expected 401, got {response.status_code}"}
            except Exception as e:
                print(f"❌ API密钥测试异常: {e}")
                return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """运行所有测试"""
        print("🚀 开始IBKR API全面测试...")
        print("=" * 60)
        
        results = {}
        
        # 基础功能测试
        results["config"] = await self.test_config()
        results["connection"] = await self.test_connection()
        results["health"] = await self.test_health_check()
        
        # 数据同步测试
        results["sync"] = await self.test_sync_data()
        
        # 数据查询测试
        results["balances"] = await self.test_get_balances()
        results["positions"] = await self.test_get_positions()
        results["logs"] = await self.test_get_logs()
        results["summary"] = await self.test_get_summary()
        
        # 安全测试
        results["invalid_api_key"] = await self.test_invalid_api_key()
        
        print("=" * 60)
        
        # 生成测试报告
        total_tests = len(results)
        passed_tests = len([r for r in results.values() if r["status"] == "success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📋 测试报告:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests}")
        print(f"   失败: {failed_tests}")
        print(f"   成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for test_name, result in results.items():
                if result["status"] == "error":
                    print(f"   - {test_name}: {result.get('error', 'Unknown error')}")
        
        return results


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="IBKR API集成测试")
    parser.add_argument("--host", default="http://localhost:8000", help="API服务地址")
    parser.add_argument("--api-key", default="ibkr_sync_key_2024_test", help="API密钥")
    parser.add_argument("--test", help="指定单个测试: config|connection|sync|balances|positions|logs|summary|health|auth")
    
    args = parser.parse_args()
    
    tester = IBKRAPITester(base_url=args.host, api_key=args.api_key)
    
    if args.test:
        # 运行单个测试
        test_method = getattr(tester, f"test_{args.test}", None)
        if test_method:
            result = await test_method()
            print(f"\n测试结果: {result}")
        else:
            print(f"❌ 未知测试: {args.test}")
    else:
        # 运行所有测试
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())