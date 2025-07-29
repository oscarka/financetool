#!/usr/bin/env python3
"""
检查汇率表数据
"""
import os
import sys
from decimal import Decimal

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.database import get_db
from app.models.database import ExchangeRate, WiseExchangeRate

def check_exchange_rates():
    """检查汇率表数据"""
    print("💱 检查汇率表数据...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 检查ExchangeRate表
        print("\n📊 1. ExchangeRate表:")
        exchange_rates = db.query(ExchangeRate).all()
        print(f"   总数: {len(exchange_rates)} 条")
        
        if exchange_rates:
            for i, rate in enumerate(exchange_rates[:10], 1):  # 只显示前10条
                print(f"   {i}. {rate.from_currency} -> {rate.to_currency}: {rate.rate} (日期: {rate.rate_date})")
        else:
            print("   ⚠️  表中没有汇率数据")
        
        # 检查WiseExchangeRate表
        print("\n📊 2. WiseExchangeRate表:")
        wise_rates = db.query(WiseExchangeRate).all()
        print(f"   总数: {len(wise_rates)} 条")
        
        if wise_rates:
            for i, rate in enumerate(wise_rates[:10], 1):  # 只显示前10条
                print(f"   {i}. {rate.source_currency} -> {rate.target_currency}: {rate.rate} (时间: {rate.time})")
        else:
            print("   ⚠️  表中没有汇率数据")
        
        # 检查需要的汇率对
        print("\n🔍 3. 需要的汇率对:")
        needed_pairs = [
            ('JPY', 'CNY'), ('AUD', 'CNY'), ('EUR', 'CNY'), 
            ('USD', 'CNY'), ('HKD', 'CNY'), ('ETH', 'CNY'),
            ('BTC', 'CNY'), ('USDT', 'CNY'), ('USDC', 'CNY')
        ]
        
        for from_cur, to_cur in needed_pairs:
            # 检查ExchangeRate表
            rate1 = db.query(ExchangeRate).filter(
                ExchangeRate.from_currency == from_cur,
                ExchangeRate.to_currency == to_cur
            ).first()
            
            # 检查WiseExchangeRate表
            rate2 = db.query(WiseExchangeRate).filter(
                WiseExchangeRate.source_currency == from_cur,
                WiseExchangeRate.target_currency == to_cur
            ).first()
            
            status = "❌ 缺失"
            if rate1:
                status = f"✅ ExchangeRate: {rate1.rate}"
            elif rate2:
                status = f"✅ WiseExchangeRate: {rate2.rate}"
            
            print(f"   {from_cur} -> {to_cur}: {status}")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_exchange_rates()