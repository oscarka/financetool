#!/usr/bin/env python3
"""
Wise API测试脚本
用于测试Wise API的各种功能
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.wise_api_service import WiseAPIService
from loguru import logger


async def test_wise_config():
    """测试Wise配置"""
    print("\n=== 测试Wise配置 ===")
    wise_service = WiseAPIService()
    config = await wise_service.get_config()
    print(f"配置信息: {config}")


async def test_wise_connection():
    """测试Wise连接"""
    print("\n=== 测试Wise连接 ===")
    wise_service = WiseAPIService()
    result = await wise_service.test_connection()
    print(f"连接测试结果: {result}")


async def test_wise_profiles():
    """测试获取用户资料"""
    print("\n=== 测试获取用户资料 ===")
    wise_service = WiseAPIService()
    profiles = await wise_service.get_profile()
    if profiles:
        print(f"用户资料: {profiles}")
    else:
        print("获取用户资料失败")


async def test_wise_accounts():
    """测试获取账户列表"""
    print("\n=== 测试获取账户列表 ===")
    wise_service = WiseAPIService()
    
    # 先获取用户资料
    profiles = await wise_service.get_profile()
    if not profiles:
        print("无法获取用户资料")
        return
    
    for profile in profiles.get('data', []):
        profile_id = profile.get('id')
        print(f"用户ID: {profile_id}")
        
        accounts = await wise_service.get_accounts(profile_id)
        if accounts:
            print(f"账户列表: {accounts}")
        else:
            print("获取账户列表失败")


async def test_wise_balances():
    """测试获取账户余额"""
    print("\n=== 测试获取账户余额 ===")
    wise_service = WiseAPIService()
    
    balances = await wise_service.get_all_account_balances()
    if balances:
        print(f"所有账户余额: {balances}")
        print(f"账户数量: {len(balances)}")
    else:
        print("获取账户余额失败")


async def test_wise_transactions():
    """测试获取交易记录"""
    print("\n=== 测试获取交易记录 ===")
    wise_service = WiseAPIService()
    
    transactions = await wise_service.get_recent_transactions(7)
    if transactions:
        print(f"最近7天交易记录: {transactions}")
        print(f"交易数量: {len(transactions)}")
    else:
        print("获取交易记录失败")


async def test_wise_exchange_rates():
    """测试获取汇率"""
    print("\n=== 测试获取汇率 ===")
    wise_service = WiseAPIService()
    
    # 测试USD到CNY的汇率
    rates = await wise_service.get_exchange_rates("USD", "CNY")
    if rates:
        print(f"USD到CNY汇率: {rates}")
    else:
        print("获取汇率失败")
    
    # 测试EUR到CNY的汇率
    rates = await wise_service.get_exchange_rates("EUR", "CNY")
    if rates:
        print(f"EUR到CNY汇率: {rates}")
    else:
        print("获取EUR汇率失败")


async def test_wise_historical_rates():
    """测试获取历史汇率"""
    print("\n=== 测试获取历史汇率 ===")
    wise_service = WiseAPIService()
    
    # 获取最近7天的历史汇率
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    rates = await wise_service.get_historical_rates("USD", "CNY", start_date, end_date)
    if rates:
        print(f"USD到CNY历史汇率: {rates}")
    else:
        print("获取历史汇率失败")


async def test_wise_currencies():
    """测试获取货币列表"""
    print("\n=== 测试获取货币列表 ===")
    wise_service = WiseAPIService()
    
    currencies = await wise_service.get_available_currencies()
    if currencies:
        print(f"可用货币列表: {currencies}")
    else:
        print("获取货币列表失败")


async def test_wise_summary():
    """测试获取汇总信息"""
    print("\n=== 测试获取汇总信息 ===")
    wise_service = WiseAPIService()
    
    # 获取所有余额
    balances = await wise_service.get_all_account_balances()
    if balances:
        # 计算汇总信息
        total_balance_by_currency = {}
        for balance in balances:
            currency = balance['currency']
            if currency not in total_balance_by_currency:
                total_balance_by_currency[currency] = 0
            total_balance_by_currency[currency] += balance['available_balance']
        
        summary = {
            "total_accounts": len(set(b['account_id'] for b in balances)),
            "total_currencies": len(total_balance_by_currency),
            "balance_by_currency": total_balance_by_currency,
            "last_updated": datetime.now().isoformat()
        }
        print(f"汇总信息: {summary}")
    else:
        print("获取汇总信息失败")


async def main():
    """主测试函数"""
    print("开始测试Wise API...")
    
    # 设置日志级别
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    try:
        await test_wise_config()
        await test_wise_connection()
        await test_wise_profiles()
        await test_wise_accounts()
        await test_wise_balances()
        await test_wise_transactions()
        await test_wise_exchange_rates()
        await test_wise_historical_rates()
        await test_wise_currencies()
        await test_wise_summary()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        print(f"测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 