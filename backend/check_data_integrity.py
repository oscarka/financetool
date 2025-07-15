#!/usr/bin/env python3
"""
数据完整性检查脚本
用于验证Railway数据持久化是否正常工作
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

def check_database_file():
    """检查数据库文件是否存在"""
    db_path = "./data/personalfinance.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    file_size = os.path.getsize(db_path)
    print(f"✅ 数据库文件存在: {db_path} ({file_size/1024/1024:.2f}MB)")
    return True

def check_database_tables():
    """检查数据库表是否存在"""
    db_path = "./data/personalfinance.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ 数据库表数量: {len(tables)}")
        
        # 检查关键表
        key_tables = [
            'user_operations',
            'fund_info', 
            'fund_nav',
            'wise_transactions',
            'ibkr_accounts',
            'asset_positions',
            'dca_plans'
        ]
        
        for table in key_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库表失败: {e}")
        return False

def check_data_volume_mount():
    """检查数据卷挂载"""
    data_path = "/app/data"
    
    if os.path.exists(data_path):
        print(f"✅ 数据目录存在: {data_path}")
        
        # 检查目录权限
        stat = os.stat(data_path)
        print(f"  - 权限: {oct(stat.st_mode)[-3:]}")
        print(f"  - 所有者: {stat.st_uid}")
        
        # 检查是否可写
        if os.access(data_path, os.W_OK):
            print("  - 可写: ✅")
        else:
            print("  - 可写: ❌")
            
        return True
    else:
        print(f"❌ 数据目录不存在: {data_path}")
        return False

def check_backup_files():
    """检查备份文件"""
    backup_dir = "./backups"
    
    if not os.path.exists(backup_dir):
        print(f"❌ 备份目录不存在: {backup_dir}")
        return False
    
    backup_files = []
    for file in os.listdir(backup_dir):
        if file.endswith('.db') or file.endswith('.json'):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backup_files.append((file, file_size, file_time))
    
    if backup_files:
        print(f"✅ 找到 {len(backup_files)} 个备份文件:")
        for file, size, time in sorted(backup_files, key=lambda x: x[2], reverse=True):
            print(f"  - {file} ({size/1024/1024:.2f}MB) - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    else:
        print("❌ 没有找到备份文件")
        return False

def check_environment_variables():
    """检查环境变量"""
    env_vars = [
        'DATABASE_URL',
        'DATABASE_PERSISTENT_PATH',
        'DATABASE_BACKUP_ENABLED',
        'APP_ENV'
    ]
    
    print("🔧 环境变量检查:")
    for var in env_vars:
        value = os.getenv(var, '未设置')
        print(f"  - {var}: {value}")
    
    return True

def check_data_integrity():
    """检查数据完整性"""
    db_path = "./data/personalfinance.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查关键数据的完整性
        checks = [
            ("用户操作记录", "SELECT COUNT(*) FROM user_operations"),
            ("基金信息", "SELECT COUNT(*) FROM fund_info"),
            ("基金净值", "SELECT COUNT(*) FROM fund_nav"),
            ("Wise交易", "SELECT COUNT(*) FROM wise_transactions"),
            ("资产持仓", "SELECT COUNT(*) FROM asset_positions"),
            ("定投计划", "SELECT COUNT(*) FROM dca_plans")
        ]
        
        print("📊 数据完整性检查:")
        total_records = 0
        
        for name, query in checks:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"  - {name}: {count} 条记录")
                total_records += count
            except sqlite3.OperationalError:
                print(f"  - {name}: 表不存在")
        
        print(f"  - 总记录数: {total_records}")
        
        # 检查最近的数据
        try:
            cursor.execute("SELECT MAX(created_at) FROM user_operations")
            latest_operation = cursor.fetchone()[0]
            if latest_operation:
                print(f"  - 最新操作时间: {latest_operation}")
        except:
            pass
        
        conn.close()
        return total_records > 0
        
    except Exception as e:
        print(f"❌ 数据完整性检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 开始数据完整性检查...")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    checks = [
        ("数据库文件", check_database_file),
        ("数据库表", check_database_tables),
        ("数据卷挂载", check_data_volume_mount),
        ("备份文件", check_backup_files),
        ("环境变量", check_environment_variables),
        ("数据完整性", check_data_integrity)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}检查:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查异常: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  - {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 数据完整性检查全部通过！")
        return 0
    else:
        print("⚠️  数据完整性检查发现问题，请检查上述失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())