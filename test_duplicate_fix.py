#!/usr/bin/env python3
"""
测试修复后的聚合逻辑，验证是否解决了重复计算问题
"""

import os
import sys
from decimal import Decimal
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.database import AssetPosition, WiseBalance, IBKRBalance, OKXBalance
from app.services.asset_aggregation_service import aggregate_asset_data, calculate_aggregated_stats
from app.utils.database import get_db

def test_duplicate_fix():
    """测试修复后的聚合逻辑"""
    print("🔍 测试修复后的聚合逻辑...")

    # 获取数据库会话
    db = next(get_db())

    try:
        # 1. 检查当前数据情况
        print("\n📊 1. 检查当前数据情况:")

        # 检查Wise余额数据
        wise_balances = db.query(WiseBalance).all()
        print(f"   Wise余额记录总数: {len(wise_balances)}")
        
        if wise_balances:
            # 按账户分组检查
            account_groups = {}
            for w in wise_balances:
                key = f"{w.account_id}_{w.currency}"
                if key not in account_groups:
                    account_groups[key] = []
                account_groups[key].append(w)
            
            print(f"   账户+货币组合数: {len(account_groups)}")
            
            # 检查是否有重复记录
            for key, records in account_groups.items():
                if len(records) > 1:
                    print(f"   ⚠️ 发现重复记录: {key} ({len(records)} 条)")
                    for r in records:
                        print(f"      {r.account_id} - {r.currency} - {r.available_balance} - {r.created_at}")
                else:
                    print(f"   ✅ 正常记录: {key} (1 条)")

        # 2. 测试聚合逻辑
        print("\n🧮 2. 测试聚合逻辑:")
        
        # 获取聚合数据
        all_assets = aggregate_asset_data(db, 'CNY')
        print(f"   聚合后的资产数量: {len(all_assets)}")
        
        # 检查是否有重复的资产
        asset_keys = set()
        duplicate_count = 0
        
        for asset in all_assets:
            # 创建唯一标识符
            asset_key = f"{asset['platform']}_{asset['asset_code']}_{asset['currency']}"
            
            if asset_key in asset_keys:
                duplicate_count += 1
                print(f"   ⚠️ 发现重复资产: {asset_key}")
            else:
                asset_keys.add(asset_key)
        
        print(f"   重复资产数量: {duplicate_count}")
        
        # 3. 测试统计计算
        print("\n📈 3. 测试统计计算:")
        result = calculate_aggregated_stats(db, 'CNY')
        print(f"   总价值: {result['total_value']} CNY")
        print(f"   资产数量: {result['asset_count']}")
        print(f"   使用默认汇率: {result['has_default_rates']}")
        
        # 4. 验证逻辑
        print("\n✅ 4. 验证修复效果:")
        if duplicate_count == 0:
            print("   ✅ 没有发现重复计算问题")
        else:
            print("   ⚠️ 仍然存在重复计算问题")
            
        # 检查时间过滤是否生效
        print("\n⏰ 5. 检查时间过滤:")
        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)
        print(f"   当前时间: {now}")
        print(f"   过滤时间: {cutoff_time}")
        
        # 检查最近的记录
        recent_wise = db.query(WiseBalance).filter(WiseBalance.created_at >= cutoff_time).all()
        print(f"   最近24小时Wise记录: {len(recent_wise)} 条")
        
        if len(recent_wise) < len(wise_balances):
            print("   ✅ 时间过滤生效，只计算最近记录")
        else:
            print("   ⚠️ 时间过滤可能未生效")

    finally:
        db.close()

if __name__ == "__main__":
    test_duplicate_fix()