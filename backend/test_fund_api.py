#!/usr/bin/env python3
"""
基金API测试脚本
"""

import asyncio
import httpx
import json
from datetime import date, datetime
from decimal import Decimal


class FundAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        response = await self.client.get(f"{self.base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_create_fund_info(self):
        """测试创建基金信息"""
        print("📝 测试创建基金信息...")
        fund_data = {
            "fund_code": "000001",
            "fund_name": "华夏成长混合",
            "fund_type": "混合型",
            "management_fee": 0.015,
            "purchase_fee": 0.015,
            "redemption_fee": 0.005,
            "min_purchase": 100.0,
            "risk_level": "中风险"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/funds/info",
            json=fund_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_get_all_funds(self):
        """测试获取所有基金"""
        print("📋 测试获取所有基金...")
        response = await self.client.get(f"{self.base_url}/api/v1/funds/info")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_create_fund_operation(self):
        """测试创建基金操作"""
        print("💰 测试创建基金操作...")
        operation_data = {
            "operation_date": datetime.now().isoformat(),
            "operation_type": "buy",
            "asset_code": "000001",
            "asset_name": "华夏成长混合",
            "amount": 1000.0,
            "strategy": "定投策略",
            "emotion_score": 7,
            "notes": "测试买入操作"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/funds/operations",
            json=operation_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_get_fund_operations(self):
        """测试获取基金操作记录"""
        print("📊 测试获取基金操作记录...")
        response = await self.client.get(f"{self.base_url}/api/v1/funds/operations")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_create_fund_nav(self):
        """测试创建基金净值"""
        print("📈 测试创建基金净值...")
        nav_data = {
            "fund_code": "000001",
            "nav_date": date.today().isoformat(),
            "nav": 1.2345,
            "accumulated_nav": 2.3456,
            "growth_rate": 0.015,
            "source": "manual"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/funds/nav",
            json=nav_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_get_fund_positions(self):
        """测试获取基金持仓"""
        print("💼 测试获取基金持仓...")
        response = await self.client.get(f"{self.base_url}/api/v1/funds/positions")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_get_position_summary(self):
        """测试获取持仓汇总"""
        print("📊 测试获取持仓汇总...")
        response = await self.client.get(f"{self.base_url}/api/v1/funds/positions/summary")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_create_dca_plan(self):
        """测试创建定投计划"""
        print("🔄 测试创建定投计划...")
        dca_data = {
            "plan_name": "华夏成长定投",
            "asset_code": "000001",
            "asset_name": "华夏成长混合",
            "amount": 500.0,
            "currency": "CNY",
            "frequency": "monthly",
            "frequency_value": 30,
            "start_date": date.today().isoformat(),
            "strategy": "每月定投500元"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/funds/dca/plans",
            json=dca_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def test_get_dca_plans(self):
        """测试获取定投计划"""
        print("📋 测试获取定投计划...")
        response = await self.client.get(f"{self.base_url}/api/v1/funds/dca/plans")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始基金API测试...")
        print("=" * 50)
        
        try:
            await self.test_health_check()
            await self.test_create_fund_info()
            await self.test_get_all_funds()
            await self.test_create_fund_nav()
            await self.test_create_fund_operation()
            await self.test_get_fund_operations()
            await self.test_get_fund_positions()
            await self.test_get_position_summary()
            await self.test_create_dca_plan()
            await self.test_get_dca_plans()
            
            print("✅ 所有测试完成！")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")


async def main():
    """主函数"""
    async with FundAPITester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 