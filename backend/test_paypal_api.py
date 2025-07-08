#!/usr/bin/env python3
"""
PayPal API集成测试脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.paypal_api_service import PayPalAPIService
from loguru import logger


async def test_paypal_config():
    """测试PayPal配置"""
    print("\n" + "="*60)
    print("🔧 测试PayPal API配置")
    print("="*60)
    
    service = PayPalAPIService()
    config = await service.get_config()
    
    print(f"API已配置: {config['api_configured']}")
    print(f"Base URL: {config['base_url']}")
    print(f"Client ID: {config['client_id_prefix']}")
    print(f"环境: {config['environment']}")
    
    return config['api_configured']


async def test_paypal_connection():
    """测试PayPal连接"""
    print("\n" + "="*60)
    print("🔗 测试PayPal API连接")
    print("="*60)
    
    service = PayPalAPIService()
    result = await service.test_connection()
    
    print(f"Token认证: {'✅' if result['token_auth'] else '❌'}")
    print(f"余额API: {'✅' if result['balance_api'] else '❌'}")
    print(f"交易API: {'✅' if result['transaction_api'] else '❌'}")
    
    if not result['token_auth']:
        print(f"❌ 错误: {result.get('error', '未知错误')}")
    
    if result['balance_error']:
        print(f"余额API错误: {result['balance_error']}")
    
    if result['transaction_error']:
        print(f"交易API错误: {result['transaction_error']}")
    
    return result['token_auth']


async def test_paypal_balance_accounts():
    """测试PayPal余额账户"""
    print("\n" + "="*60)
    print("💰 测试PayPal余额账户")
    print("="*60)
    
    service = PayPalAPIService()
    
    try:
        # 测试原始余额账户API
        raw_balance = await service.get_balance_accounts()
        if raw_balance:
            print("✅ 原始余额账户API调用成功")
            print(f"📊 原始数据: {raw_balance}")
        else:
            print("❌ 原始余额账户API调用失败")
        
        # 测试格式化后的余额数据
        balances = await service.get_all_balances()
        if balances:
            print(f"✅ 获取到 {len(balances)} 个余额账户")
            for balance in balances:
                print(f"  💳 {balance['currency']}: 可用 {balance['available_balance']}, 冻结 {balance['reserved_balance']}")
        else:
            print("❌ 没有获取到余额数据")
        
        return bool(balances)
    except Exception as e:
        print(f"❌ 余额账户测试异常: {e}")
        return False


async def test_paypal_transactions():
    """测试PayPal交易记录"""
    print("\n" + "="*60)
    print("📊 测试PayPal交易记录")
    print("="*60)
    
    service = PayPalAPIService()
    
    try:
        # 测试最近7天的交易
        transactions = await service.get_recent_transactions(7)
        if transactions:
            print(f"✅ 获取到 {len(transactions)} 条最近7天的交易记录")
            for transaction in transactions[:3]:  # 只显示前3条
                print(f"  📝 {transaction['date']}: {transaction['type']} {transaction['amount']} {transaction['currency']} - {transaction['description'][:50]}")
        else:
            print("ℹ️ 最近7天没有交易记录")
        
        # 测试最近30天的交易
        transactions_30 = await service.get_recent_transactions(30)
        if transactions_30:
            print(f"✅ 获取到 {len(transactions_30)} 条最近30天的交易记录")
        else:
            print("ℹ️ 最近30天没有交易记录")
        
        return True
    except Exception as e:
        print(f"❌ 交易记录测试异常: {e}")
        return False


async def test_paypal_summary():
    """测试PayPal账户汇总"""
    print("\n" + "="*60)
    print("📈 测试PayPal账户汇总")
    print("="*60)
    
    service = PayPalAPIService()
    
    try:
        summary = await service.get_account_summary()
        if summary:
            print(f"✅ 账户汇总获取成功")
            print(f"  🏦 总账户数: {summary['total_accounts']}")
            print(f"  💱 支持货币数: {summary['total_currencies']}")
            print(f"  💰 总余额: ${summary['total_balance']:.2f}")
            print(f"  📊 最近交易数: {summary['recent_transactions_count']}")
            
            if summary.get('balance_by_currency'):
                print("  💵 按货币分组:")
                for currency, amount in summary['balance_by_currency'].items():
                    print(f"    {currency}: {amount:.2f}")
        else:
            print("❌ 账户汇总获取失败")
        
        return bool(summary)
    except Exception as e:
        print(f"❌ 账户汇总测试异常: {e}")
        return False


async def test_paypal_debug_info():
    """测试PayPal调试信息"""
    print("\n" + "="*60)
    print("🔍 PayPal调试信息")
    print("="*60)
    
    service = PayPalAPIService()
    
    print(f"Client ID: {service.client_id[:20]}...")
    print(f"Client Secret: {service.client_secret[:20]}...")
    print(f"Base URL: {service.base_url}")
    print(f"当前Token: {'有' if service.access_token else '无'}")
    print(f"Token过期时间: {service.token_expires_at}")


async def main():
    """主测试函数"""
    print("🚀 PayPal API集成测试开始")
    print("当前工作目录:", os.getcwd())
    
    # 测试配置
    config_ok = await test_paypal_config()
    if not config_ok:
        print("\n❌ PayPal配置不完整，无法继续测试")
        return
    
    # 测试连接
    connection_ok = await test_paypal_connection()
    if not connection_ok:
        print("\n❌ PayPal连接失败，无法继续测试")
        return
    
    # 测试各个功能
    await test_paypal_balance_accounts()
    await test_paypal_transactions()
    await test_paypal_summary()
    await test_paypal_debug_info()
    
    print("\n" + "="*60)
    print("✅ PayPal API集成测试完成")
    print("="*60)


if __name__ == "__main__":
    # 配置日志
    logger.add("./logs/paypal_test.log", rotation="10 MB", level="DEBUG")
    
    # 运行测试
    asyncio.run(main())