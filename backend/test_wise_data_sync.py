#!/usr/bin/env python3
"""
测试Wise数据落库功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_wise_data_sync():
    """测试Wise数据同步功能"""
    
    try:
        from app.services.wise_api_service import WiseAPIService
        from app.utils.database import SessionLocal
        from app.models.database import WiseBalance, WiseTransaction, WiseExchangeRate
        
        print("=== 测试Wise数据落库功能 ===")
        
        # 初始化Wise服务
        wise_service = WiseAPIService()
        
        # 测试1: 同步余额数据
        print("\n1. 测试余额数据同步...")
        balance_result = await wise_service.sync_balances_to_db()
        print(f"   结果: {balance_result}")
        
        # 测试2: 同步交易数据
        print("\n2. 测试交易数据同步...")
        transaction_result = await wise_service.sync_all_transactions_to_db(days=30)
        print(f"   结果: {transaction_result}")
        
        # 测试3: 检查数据库中的数据
        print("\n3. 检查数据库中的数据...")
        db = SessionLocal()
        try:
            # 检查余额数据
            balance_count = db.query(WiseBalance).count()
            print(f"   余额记录数: {balance_count}")
            
            # 检查交易数据
            transaction_count = db.query(WiseTransaction).count()
            print(f"   交易记录数: {transaction_count}")
            
            # 检查汇率数据
            rate_count = db.query(WiseExchangeRate).count()
            print(f"   汇率记录数: {rate_count}")
            
            # 显示一些示例数据
            if balance_count > 0:
                print(f"\n   示例余额数据:")
                sample_balance = db.query(WiseBalance).first()
                print(f"     账户ID: {sample_balance.account_id}")
                print(f"     货币: {sample_balance.currency}")
                print(f"     可用余额: {sample_balance.available_balance}")
                print(f"     总价值: {sample_balance.total_worth}")
            
            if transaction_count > 0:
                print(f"\n   示例交易数据:")
                sample_transaction = db.query(WiseTransaction).first()
                print(f"     交易ID: {sample_transaction.transaction_id}")
                print(f"     类型: {sample_transaction.type}")
                print(f"     金额: {sample_transaction.amount} {sample_transaction.currency}")
                print(f"     日期: {sample_transaction.date}")
            
        finally:
            db.close()
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_wise_api_endpoints():
    """测试Wise API端点"""
    
    try:
        import httpx
        
        print("\n=== 测试Wise API端点 ===")
        
        base_url = "http://localhost:8000"
        
        # 测试1: 获取配置
        print("\n1. 测试获取配置...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/wise/config")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   响应: {response.json()}")
        
        # 测试2: 同步余额
        print("\n2. 测试同步余额...")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/api/v1/wise/sync-balances")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   响应: {response.json()}")
        
        # 测试3: 获取存储的余额
        print("\n3. 测试获取存储的余额...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/wise/stored-balances")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   记录数: {data.get('count', 0)}")
        
        # 测试4: 同步交易
        print("\n4. 测试同步交易...")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/api/v1/wise/sync-transactions")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   响应: {response.json()}")
        
        # 测试5: 获取存储的交易
        print("\n5. 测试获取存储的交易...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/wise/stored-transactions?limit=10")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   记录数: {data.get('count', 0)}")
        
        print("\n=== API端点测试完成 ===")
        
    except Exception as e:
        print(f"API端点测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试Wise数据落库功能...")
    
    # 运行数据同步测试
    asyncio.run(test_wise_data_sync())
    
    # 运行API端点测试
    asyncio.run(test_wise_api_endpoints())
    
    print("\n所有测试完成！")