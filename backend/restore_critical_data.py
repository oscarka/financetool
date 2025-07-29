#!/usr/bin/env python3
"""
关键数据恢复脚本
在整合迁移后恢复重要数据
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

class CriticalDataRestore:
    def __init__(self):
        self.service_url = os.getenv('RAILWAY_SERVICE_URL')
        
    def restore_table_data(self, table_name, endpoint, data):
        """恢复单个表的数据"""
        try:
            if not self.service_url:
                print(f"⚠️  未设置RAILWAY_SERVICE_URL，跳过 {table_name}")
                return True
            
            restored_count = 0
            for record in data:
                # 移除自动生成字段
                for field in ['id', 'created_at', 'updated_at']:
                    if field in record:
                        del record[field]
                
                response = requests.post(f"{self.service_url}{endpoint}", json=record, timeout=30)
                if response.status_code in [200, 201]:
                    restored_count += 1
                else:
                    print(f"⚠️  恢复记录失败: {response.status_code} - {response.text}")
            
            print(f"✅ 恢复 {table_name}: {restored_count}/{len(data)} 条记录")
            return True
        except Exception as e:
            print(f"⚠️  恢复 {table_name} 异常: {e}")
            return False
    
    def restore_from_backup(self, backup_file):
        """从备份文件恢复数据"""
        print(f"🔄 从备份文件恢复数据: {backup_file}")
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            endpoint_map = {
                "user_operations": "/api/v1/operations",
                "asset_positions": "/api/v1/positions",
                "fund_info": "/api/v1/funds",
                "dca_plans": "/api/v1/dca-plans",
                "wise_transactions": "/api/v1/wise/transactions",
                "wise_balances": "/api/v1/wise/balances",
                "ibkr_accounts": "/api/v1/ibkr/accounts",
                "ibkr_balances": "/api/v1/ibkr/balances",
                "ibkr_positions": "/api/v1/ibkr/positions",
                "okx_balances": "/api/v1/okx/balances",
                "okx_transactions": "/api/v1/okx/transactions",
                "okx_positions": "/api/v1/okx/positions",
                "web3_balances": "/api/v1/web3/balances",
                "web3_tokens": "/api/v1/web3/tokens",
                "asset_snapshots": "/api/v1/snapshots",
                "exchange_rates": "/api/v1/exchange-rates",
                "system_config": "/api/v1/system/config"
            }
            
            total_restored = 0
            for table_name, data in backup_data.items():
                if table_name in ['backup_time', 'consolidation_type', 'total_tables', 'total_records']:
                    continue
                
                if table_name in endpoint_map and data:
                    endpoint = endpoint_map[table_name]
                    if self.restore_table_data(table_name, endpoint, data):
                        total_restored += len(data)
            
            print(f"✅ 数据恢复完成，总计恢复: {total_restored} 条记录")
            return True
            
        except Exception as e:
            print(f"❌ 数据恢复失败: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("❌ 请指定备份文件路径")
        print("用法: python restore_critical_data.py <backup_file>")
        return
    
    backup_file = sys.argv[1]
    restore = CriticalDataRestore()
    restore.restore_from_backup(backup_file)

if __name__ == "__main__":
    main()