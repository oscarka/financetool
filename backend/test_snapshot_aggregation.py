#!/usr/bin/env python3
"""
测试快照聚合逻辑的脚本
验证按天/半天/小时聚合时是否正确取最新数据而不是累加
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from app.models.asset_snapshot import AssetSnapshot
from app.models.database import get_db_url

def test_snapshot_aggregation():
    """测试快照聚合逻辑"""
    
    # 创建数据库连接
    engine = create_engine(get_db_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("=== 测试快照聚合逻辑 ===\n")
        
        # 1. 查看最近的快照数据
        print("1. 查看最近的资产快照数据:")
        recent_snapshots = db.query(AssetSnapshot).order_by(
            AssetSnapshot.snapshot_time.desc()
        ).limit(10).all()
        
        for snapshot in recent_snapshots:
            print(f"  - {snapshot.snapshot_time}: {snapshot.platform} {snapshot.asset_code} "
                  f"{snapshot.balance} {snapshot.currency} (CNY: {snapshot.balance_cny})")
        
        print()
        
        # 2. 测试按天聚合
        print("2. 测试按天聚合 (取每天最新):")
        end = datetime.now()
        start = end - timedelta(days=7)
        
        # 使用窗口函数获取每天最新的快照
        daily_latest = db.query(
            func.date_trunc('day', AssetSnapshot.snapshot_time).label('day'),
            func.max(AssetSnapshot.snapshot_time).label('latest_time')
        ).filter(
            AssetSnapshot.snapshot_time >= start,
            AssetSnapshot.snapshot_time <= end
        ).group_by('day').order_by('day').all()
        
        for row in daily_latest:
            print(f"  - {row.day.date()}: 最新快照时间 {row.latest_time}")
            
            # 获取该天最新的快照详情
            latest_snapshot = db.query(AssetSnapshot).filter(
                AssetSnapshot.snapshot_time == row.latest_time
            ).first()
            
            if latest_snapshot:
                print(f"    总资产: {latest_snapshot.balance_cny} CNY")
        
        print()
        
        # 3. 测试按半天聚合
        print("3. 测试按半天聚合:")
        half_day_latest = db.query(
            func.case(
                (func.extract('hour', AssetSnapshot.snapshot_time) < 12,
                 func.date_trunc('day', AssetSnapshot.snapshot_time)),
                else_=func.date_trunc('day', AssetSnapshot.snapshot_time) + func.interval('12 hours')
            ).label('half_day'),
            func.max(AssetSnapshot.snapshot_time).label('latest_time')
        ).filter(
            AssetSnapshot.snapshot_time >= start,
            AssetSnapshot.snapshot_time <= end
        ).group_by('half_day').order_by('half_day').all()
        
        for row in half_day_latest:
            period = "上午" if row.half_day.hour == 0 else "下午"
            print(f"  - {row.half_day.date()} {period}: 最新快照时间 {row.latest_time}")
        
        print()
        
        # 4. 对比累加 vs 取最新的差异
        print("4. 对比累加 vs 取最新的差异:")
        
        # 累加方式（错误的方式）
        sum_query = db.query(
            func.date_trunc('day', AssetSnapshot.snapshot_time).label('day'),
            func.sum(AssetSnapshot.balance_cny).label('total_sum')
        ).filter(
            AssetSnapshot.snapshot_time >= start,
            AssetSnapshot.snapshot_time <= end
        ).group_by('day').order_by('day')
        
        print("  累加方式 (错误):")
        for row in sum_query.all():
            print(f"    {row.day.date()}: {row.total_sum} CNY (累加所有快照)")
        
        print()
        print("  取最新方式 (正确):")
        for row in daily_latest:
            latest_snapshot = db.query(AssetSnapshot).filter(
                AssetSnapshot.snapshot_time == row.latest_time
            ).first()
            
            if latest_snapshot:
                print(f"    {row.day.date()}: {latest_snapshot.balance_cny} CNY (当天最新)")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_snapshot_aggregation()