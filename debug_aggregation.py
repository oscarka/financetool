#!/usr/bin/env python3
"""
调试聚合计算过程
"""

import os
import sys
from decimal import Decimal
from sqlalchemy import create_engine, text
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from backend.app.models.database import AssetPosition, WiseBalance, IBKRBalance, OKXBalance
from backend.app.services.asset_aggregation_service import aggregate_asset_data, get_latest_rate
from backend.app.database import get_db

def debug_aggregation_calculation():
    """调试聚合计算过程"""
    print("🔍 开始调试聚合计算过程...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 1. 获取所有原始数据
        print("\n📊 1. 获取原始数据:")
        
        # AssetPosition
        asset_positions = db.query(AssetPosition).all()
        print(f"   基金资产: {len(asset_positions)} 条")
        for p in asset_positions:
            print(f"     {p.platform} - {p.asset_type} - {p.asset_name}: {p.current_value} {p.currency}")
        
        # WiseBalance
        wise_balances = db.query(WiseBalance).all()
        print(f"   Wise外汇: {len(wise_balances)} 条")
        for w in wise_balances:
            print(f"     账户 {w.account_id}: {w.available_balance} {w.currency}")
        
        # IBKRBalance
        ibkr_balances = db.query(IBKRBalance).all()
        print(f"   IBKR证券: {len(ibkr_balances)} 条")
        for i in ibkr_balances:
            print(f"     账户 {i.account_id}: {i.net_liquidation} {i.currency}")
        
        # OKXBalance
        okx_balances = db.query(OKXBalance).all()
        print(f"   OKX数字货币: {len(okx_balances)} 条")
        for o in okx_balances:
            print(f"     账户 {o.account_id}: {o.total_balance} {o.currency}")
        
        # 2. 测试汇率转换
        print("\n💱 2. 测试汇率转换:")
        currencies = ['JPY', 'AUD', 'EUR', 'CNY', 'HKD', 'USD', 'ETH', 'BTC', 'USDT', 'POL', 'SOL', 'RIO', 'USDC', 'MXC', 'TRUMP']
        
        for currency in currencies:
            rate = get_latest_rate(db, currency, 'CNY')
            print(f"   {currency} -> CNY: {rate}")
        
        # 3. 手动计算每个资产的价值
        print("\n🧮 3. 手动计算每个资产价值:")
        total_value = Decimal('0')
        
        # 基金资产
        for p in asset_positions:
            if p.currency == 'CNY':
                value = Decimal(str(p.current_value))
            else:
                rate = get_latest_rate(db, p.currency, 'CNY')
                value = Decimal(str(p.current_value)) * rate if rate else Decimal('0')
            
            total_value += value
            print(f"   {p.platform} - {p.asset_type} - {p.asset_name}: {p.current_value} {p.currency} -> {value} CNY")
        
        # Wise资产
        for w in wise_balances:
            if w.currency == 'CNY':
                value = Decimal(str(w.available_balance))
            else:
                rate = get_latest_rate(db, w.currency, 'CNY')
                value = Decimal(str(w.available_balance)) * rate if rate else Decimal('0')
            
            total_value += value
            print(f"   Wise 账户 {w.account_id}: {w.available_balance} {w.currency} -> {value} CNY")
        
        # IBKR资产
        for i in ibkr_balances:
            if i.currency == 'CNY':
                value = Decimal(str(i.net_liquidation))
            else:
                rate = get_latest_rate(db, i.currency, 'CNY')
                value = Decimal(str(i.net_liquidation)) * rate if rate else Decimal('0')
            
            total_value += value
            print(f"   IBKR 账户 {i.account_id}: {i.net_liquidation} {i.currency} -> {value} CNY")
        
        # OKX资产
        for o in okx_balances:
            if o.currency == 'CNY':
                value = Decimal(str(o.total_balance))
            else:
                rate = get_latest_rate(db, o.currency, 'CNY')
                value = Decimal(str(o.total_balance)) * rate if rate else Decimal('0')
            
            total_value += value
            print(f"   OKX 账户 {o.account_id}: {o.total_balance} {o.currency} -> {value} CNY")
        
        print(f"\n📈 手动计算总价值: {total_value} CNY")
        
        # 4. 对比聚合服务的结果
        print("\n🔄 4. 对比聚合服务结果:")
        from backend.app.services.asset_aggregation_service import calculate_aggregated_stats
        result = calculate_aggregated_stats(db, 'CNY')
        print(f"   聚合服务总价值: {result['total_value']} CNY")
        print(f"   差异: {abs(total_value - Decimal(str(result['total_value'])))} CNY")
        
        if abs(total_value - Decimal(str(result['total_value']))) > Decimal('0.01'):
            print("   ⚠️ 发现计算差异！")
        else:
            print("   ✅ 计算结果一致")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_aggregation_calculation()