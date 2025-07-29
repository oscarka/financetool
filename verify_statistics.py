#!/usr/bin/env python3
"""
验证统计计算准确性的脚本
"""
import os
import sys
from decimal import Decimal

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.database import get_db
from app.models.database import AssetPosition, WiseBalance, IBKRBalance, OKXBalance
from app.services.asset_aggregation_service import calculate_aggregated_stats, aggregate_asset_data

def verify_database_data():
    """验证数据库中的实际数据"""
    print("🔍 开始验证数据库中的资产数据...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 1. 检查基金资产
        print("\n📊 1. 基金资产 (AssetPosition):")
        asset_positions = db.query(AssetPosition).all()
        print(f"   总数: {len(asset_positions)} 条")
        
        total_fund_value = Decimal('0')
        for i, asset in enumerate(asset_positions, 1):
            value = Decimal(str(asset.current_value))
            total_fund_value += value
            print(f"   {i}. {asset.platform} - {asset.asset_type} - {asset.asset_name}")
            print(f"      价值: {value:,.2f} {asset.currency}")
            print(f"      代码: {asset.asset_code}")
        
        print(f"   基金总价值: {total_fund_value:,.2f}")
        
        # 2. 检查Wise外汇资产
        print("\n💱 2. Wise外汇资产 (WiseBalance):")
        wise_balances = db.query(WiseBalance).all()
        print(f"   总数: {len(wise_balances)} 条")
        
        total_wise_value = Decimal('0')
        for i, balance in enumerate(wise_balances, 1):
            value = Decimal(str(balance.available_balance))
            total_wise_value += value
            print(f"   {i}. 账户: {balance.account_id}")
            print(f"      余额: {value:,.2f} {balance.currency}")
        
        print(f"   Wise总价值: {total_wise_value:,.2f}")
        
        # 3. 检查IBKR证券资产
        print("\n📈 3. IBKR证券资产 (IBKRBalance):")
        ibkr_balances = db.query(IBKRBalance).all()
        print(f"   总数: {len(ibkr_balances)} 条")
        
        total_ibkr_value = Decimal('0')
        for i, balance in enumerate(ibkr_balances, 1):
            value = Decimal(str(balance.net_liquidation))
            total_ibkr_value += value
            print(f"   {i}. 账户: {balance.account_id}")
            print(f"      净值: {value:,.2f} {balance.currency}")
        
        print(f"   IBKR总价值: {total_ibkr_value:,.2f}")
        
        # 4. 检查OKX数字货币资产
        print("\n🪙 4. OKX数字货币资产 (OKXBalance):")
        okx_balances = db.query(OKXBalance).all()
        print(f"   总数: {len(okx_balances)} 条")
        
        total_okx_value = Decimal('0')
        for i, balance in enumerate(okx_balances, 1):
            value = Decimal(str(balance.total_balance))
            total_okx_value += value
            print(f"   {i}. 账户: {balance.account_id}")
            print(f"      余额: {value:,.8f} {balance.currency}")
        
        print(f"   OKX总价值: {total_okx_value:,.8f}")
        
        # 5. 原始数据汇总
        print("\n📋 5. 原始数据汇总:")
        print(f"   基金资产: {total_fund_value:,.2f}")
        print(f"   Wise外汇: {total_wise_value:,.2f}")
        print(f"   IBKR证券: {total_ibkr_value:,.2f}")
        print(f"   OKX数字货币: {total_okx_value:,.8f}")
        print(f"   总计: {total_fund_value + total_wise_value + total_ibkr_value + total_okx_value:,.2f}")
        
        # 6. 测试聚合统计
        print("\n🧮 6. 聚合统计测试:")
        try:
            stats = calculate_aggregated_stats(db, 'CNY')
            print(f"   聚合统计总价值: {stats['total_value']:,.2f} CNY")
            print(f"   资产数量: {stats['asset_count']}")
            print(f"   平台数量: {stats['platform_count']}")
            print(f"   资产类型数: {stats['asset_type_count']}")
            
            print("\n   平台分布:")
            for platform, value in stats['platform_stats'].items():
                print(f"     {platform}: {value:,.2f} CNY")
            
            print("\n   资产类型分布:")
            for asset_type, value in stats['asset_type_stats'].items():
                print(f"     {asset_type}: {value:,.2f} CNY")
                
        except Exception as e:
            print(f"   聚合统计失败: {e}")
        
        # 7. 汇率问题检查
        print("\n💱 7. 汇率问题检查:")
        all_assets = aggregate_asset_data(db, 'CNY')
        cny_assets = [a for a in all_assets if a['currency'] == 'CNY']
        usd_assets = [a for a in all_assets if a['currency'] == 'USD']
        eur_assets = [a for a in all_assets if a['currency'] == 'EUR']
        
        print(f"   CNY资产数量: {len(cny_assets)}")
        print(f"   USD资产数量: {len(usd_assets)}")
        print(f"   EUR资产数量: {len(eur_assets)}")
        
        if usd_assets or eur_assets:
            print("   ⚠️  发现非CNY资产，需要检查汇率转换")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_database_data()