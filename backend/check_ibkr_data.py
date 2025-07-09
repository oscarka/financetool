#!/usr/bin/env python3
"""
检查IBKR数据库数据脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.database import IBKRBalance, IBKRPosition, IBKRSyncLog
from sqlalchemy import desc
import json

def check_ibkr_data():
    """检查IBKR数据库数据"""
    db = next(get_db())
    
    print('🔍 检查IBKR数据库数据...')
    print('=' * 50)
    
    # 检查同步日志
    print('📋 最近同步日志:')
    logs = db.query(IBKRSyncLog).order_by(desc(IBKRSyncLog.created_at)).limit(5).all()
    if logs:
        for log in logs:
            print(f'时间: {log.created_at}')
            print(f'账户: {log.account_id}')
            print(f'状态: {log.status}')
            print(f'处理记录: {log.records_processed}')
            print(f'插入记录: {log.records_inserted}')
            print(f'来源IP: {log.source_ip}')
            print('---')
    else:
        print('❌ 没有找到同步日志')
    
    # 检查余额数据
    print('💰 余额数据:')
    balances = db.query(IBKRBalance).order_by(desc(IBKRBalance.snapshot_time)).limit(3).all()
    if balances:
        for balance in balances:
            print(f'账户: {balance.account_id}')
            print(f'总现金: ${balance.total_cash}')
            print(f'净清算: ${balance.net_liquidation}')
            print(f'购买力: ${balance.buying_power}')
            print(f'货币: {balance.currency}')
            print(f'时间: {balance.snapshot_time}')
            print('---')
    else:
        print('❌ 没有找到余额数据')
    
    # 检查持仓数据
    print('📈 持仓数据:')
    positions = db.query(IBKRPosition).order_by(desc(IBKRPosition.snapshot_time)).limit(3).all()
    if positions:
        for position in positions:
            print(f'账户: {position.account_id}')
            print(f'股票: {position.symbol}')
            print(f'数量: {position.quantity}')
            print(f'市值: ${position.market_value}')
            print(f'成本: ${position.average_cost}')
            print(f'时间: {position.snapshot_time}')
            print('---')
    else:
        print('❌ 没有找到持仓数据')
    
    print('=' * 50)
    print('✅ 数据库检查完成')
    
    # 返回数据统计
    total_logs = db.query(IBKRSyncLog).count()
    total_balances = db.query(IBKRBalance).count()
    total_positions = db.query(IBKRPosition).count()
    
    print(f'📊 数据统计:')
    print(f'- 同步日志: {total_logs} 条')
    print(f'- 余额记录: {total_balances} 条')
    print(f'- 持仓记录: {total_positions} 条')

if __name__ == "__main__":
    check_ibkr_data()