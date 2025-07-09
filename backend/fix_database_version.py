#!/usr/bin/env python3
"""
修复数据库迁移版本记录
"""

import sqlite3
import os

def fix_database_version():
    """修复数据库中的迁移版本"""
    db_path = "data/personalfinance.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前版本
        cursor.execute("SELECT version_num FROM alembic_version")
        current_version = cursor.fetchone()
        print(f"当前数据库版本: {current_version[0] if current_version else 'None'}")
        
        # 当前版本是已删除的迁移，需要更新为最新的有效版本
        # 根据迁移链，最新版本应该是 a1b2c3d4e5f6
        new_version = "a1b2c3d4e5f6"
        
        if current_version and current_version[0] != new_version:
            cursor.execute("UPDATE alembic_version SET version_num = ?", (new_version,))
            conn.commit()
            print(f"数据库版本已更新: {current_version[0]} -> {new_version}")
        else:
            print("数据库版本已经是正确的")
        
        conn.close()
        
    except Exception as e:
        print(f"修复数据库版本时出错: {e}")

def verify_database_schema():
    """验证数据库结构"""
    db_path = "data/personalfinance.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查关键表是否存在
        tables_to_check = [
            'user_operations',
            'fund_nav', 
            'dca_plans',
            'wise_transactions',
            'ibkr_accounts',
            'ibkr_balances',
            'ibkr_positions'
        ]
        
        print("\n数据库表结构验证:")
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            print(f"  {table}: {'✓' if exists else '✗'}")
        
        # 检查 user_operations 表的 nav 字段
        cursor.execute("PRAGMA table_info(user_operations)")
        columns = cursor.fetchall()
        nav_exists = any(col[1] == 'nav' for col in columns)
        print(f"  user_operations.nav 字段: {'✓' if nav_exists else '✗'}")
        
        conn.close()
        
    except Exception as e:
        print(f"验证数据库结构时出错: {e}")

def main():
    """主函数"""
    print("=== 修复数据库迁移版本 ===\n")
    
    # 修复版本
    print("1. 修复数据库版本...")
    fix_database_version()
    
    # 验证结构
    print("\n2. 验证数据库结构...")
    verify_database_schema()
    
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    main()