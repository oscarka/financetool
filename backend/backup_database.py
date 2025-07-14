#!/usr/bin/env python3
"""
数据库备份脚本
用于在Railway部署前备份重要数据
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """备份数据库文件和数据"""
    db_path = "./data/personalfinance.db"
    backup_dir = "./backups"
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/personalfinance_backup_{timestamp}.db"
    
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        # 复制数据库文件
        shutil.copy2(db_path, backup_file)
        print(f"✅ 数据库文件备份成功: {backup_file}")
        
        # 导出重要数据为JSON格式
        export_important_data(db_path, backup_dir, timestamp)
        
        return True
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False

def export_important_data(db_path, backup_dir, timestamp):
    """导出重要数据为JSON格式"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 定义要导出的重要表
        important_tables = [
            'ibkr_accounts',
            'ibkr_balances', 
            'ibkr_positions',
            'ibkr_sync_logs',
            'wise_transactions',
            'wise_balances',
            'user_operations',
            'asset_positions',
            'fund_info',
            'fund_nav',
            'dca_plans'
        ]
        
        exported_data = {}
        
        for table in important_tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # 获取列名
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # 转换为字典列表
                table_data = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # 处理datetime对象
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    table_data.append(row_dict)
                
                exported_data[table] = table_data
                print(f"✅ 导出表 {table}: {len(table_data)} 条记录")
                
            except sqlite3.OperationalError as e:
                print(f"⚠️  表 {table} 不存在或无法访问: {e}")
                continue
        
        # 保存为JSON文件
        json_file = f"{backup_dir}/data_export_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(exported_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据导出成功: {json_file}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据导出失败: {e}")

def restore_database(backup_file):
    """从备份文件恢复数据库"""
    db_path = "./data/personalfinance.db"
    
    try:
        # 确保数据目录存在
        os.makedirs("./data", exist_ok=True)
        
        # 恢复数据库文件
        shutil.copy2(backup_file, db_path)
        print(f"✅ 数据库恢复成功: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def list_backups():
    """列出所有备份文件"""
    backup_dir = "./backups"
    
    if not os.path.exists(backup_dir):
        print("❌ 备份目录不存在")
        return
    
    backup_files = []
    for file in os.listdir(backup_dir):
        if file.endswith('.db') and file.startswith('personalfinance_backup_'):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backup_files.append((file, file_size, file_time))
    
    if not backup_files:
        print("❌ 没有找到备份文件")
        return
    
    print("📋 可用备份文件:")
    for file, size, time in sorted(backup_files, key=lambda x: x[2], reverse=True):
        print(f"  {file} ({size/1024/1024:.1f}MB) - {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            backup_database()
        elif command == "restore" and len(sys.argv) > 2:
            restore_database(sys.argv[2])
        elif command == "list":
            list_backups()
        else:
            print("用法:")
            print("  python backup_database.py backup    # 创建备份")
            print("  python backup_database.py restore <file>  # 恢复备份")
            print("  python backup_database.py list      # 列出备份")
    else:
        print("🔧 数据库备份工具")
        print("用法:")
        print("  python backup_database.py backup    # 创建备份")
        print("  python backup_database.py restore <file>  # 恢复备份")
        print("  python backup_database.py list      # 列出备份")