#!/usr/bin/env python3
"""
关键数据备份脚本
在整合迁移前备份重要数据
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

class CriticalDataBackup:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.service_url = os.getenv('RAILWAY_SERVICE_URL')
        
    def backup_table_data(self, table_name, endpoint):
        """备份单个表的数据"""
        try:
            if not self.service_url:
                print(f"⚠️  未设置RAILWAY_SERVICE_URL，跳过 {table_name}")
                return []
            
            response = requests.get(f"{self.service_url}{endpoint}?limit=10000", timeout=30)
            if response.status_code == 200:
                data = response.json()
                records = data.get('data', [])
                print(f"✅ 备份 {table_name}: {len(records)} 条记录")
                return records
            else:
                print(f"⚠️  备份 {table_name} 失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️  备份 {table_name} 异常: {e}")
            return []
    
    def backup_all_critical_data(self):
        """备份所有关键数据"""
        print("🔄 开始备份关键数据...")
        
        critical_tables = [
            ("user_operations", "/api/v1/operations"),
            ("asset_positions", "/api/v1/positions"),
            ("fund_info", "/api/v1/funds"),
            ("dca_plans", "/api/v1/dca-plans"),
            ("wise_transactions", "/api/v1/wise/transactions"),
            ("wise_balances", "/api/v1/wise/balances"),
            ("ibkr_accounts", "/api/v1/ibkr/accounts"),
            ("ibkr_balances", "/api/v1/ibkr/balances"),
            ("ibkr_positions", "/api/v1/ibkr/positions"),
            ("okx_balances", "/api/v1/okx/balances"),
            ("okx_transactions", "/api/v1/okx/transactions"),
            ("okx_positions", "/api/v1/okx/positions"),
            ("web3_balances", "/api/v1/web3/balances"),
            ("web3_tokens", "/api/v1/web3/tokens"),
            ("asset_snapshots", "/api/v1/snapshots"),
            ("exchange_rates", "/api/v1/exchange-rates"),
            ("system_config", "/api/v1/system/config")
        ]
        
        backup_data = {
            "backup_time": datetime.now().isoformat(),
            "consolidation_type": "migration_consolidation",
            "total_tables": len(critical_tables)
        }
        
        total_records = 0
        for table_name, endpoint in critical_tables:
            records = self.backup_table_data(table_name, endpoint)
            backup_data[table_name] = records
            total_records += len(records)
        
        backup_data["total_records"] = total_records
        
        # 保存备份文件
        backup_file = self.backup_dir / f"critical_data_backup_{self.timestamp}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 关键数据备份完成: {backup_file}")
        print(f"📊 总计备份: {len(critical_tables)} 个表, {total_records} 条记录")
        return str(backup_file)

def main():
    backup = CriticalDataBackup()
    backup.backup_all_critical_data()

if __name__ == "__main__":
    main()