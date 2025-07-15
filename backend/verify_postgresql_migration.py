#!/usr/bin/env python3
"""
PostgreSQL迁移验证脚本
验证数据迁移是否成功，比较SQLite和PostgreSQL的数据
"""

import os
import sys
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_sqlite_connection():
    """获取SQLite连接"""
    sqlite_path = "data/personalfinance.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite数据库文件不存在: {sqlite_path}")
        return None
    
    return sqlite3.connect(sqlite_path)

def get_postgresql_engine():
    """获取PostgreSQL引擎"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 未设置DATABASE_URL环境变量")
        return None
    
    try:
        engine = create_engine(database_url, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return None

def get_table_names(conn, is_sqlite=True):
    """获取表名列表"""
    if is_sqlite:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row[0] for row in cursor.fetchall()]
    else:
        with conn.connect() as pg_conn:
            result = pg_conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            return [row[0] for row in result]

def get_table_count(conn, table_name, is_sqlite=True):
    """获取表的记录数"""
    try:
        if is_sqlite:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        else:
            with conn.connect() as pg_conn:
                result = pg_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.fetchone()[0]
    except Exception as e:
        print(f"❌ 获取表 {table_name} 记录数失败: {e}")
        return -1

def compare_table_data(sqlite_conn, pg_engine, table_name):
    """比较单个表的数据"""
    try:
        # 获取SQLite数据
        sqlite_df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
        sqlite_count = len(sqlite_df)
        
        # 获取PostgreSQL数据
        pg_df = pd.read_sql_query(f"SELECT * FROM {table_name}", pg_engine)
        pg_count = len(pg_df)
        
        # 比较记录数
        if sqlite_count == pg_count:
            print(f"✅ {table_name}: {sqlite_count} 条记录 (匹配)")
            return True
        else:
            print(f"❌ {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count} (不匹配)")
            return False
            
    except Exception as e:
        print(f"❌ 比较表 {table_name} 失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🔍 PostgreSQL迁移验证")
    print("=" * 50)
    
    # 1. 连接数据库
    print("\n📋 步骤1: 连接数据库")
    sqlite_conn = get_sqlite_connection()
    if not sqlite_conn:
        return False
    
    pg_engine = get_postgresql_engine()
    if not pg_engine:
        sqlite_conn.close()
        return False
    
    # 2. 获取表列表
    print("\n📋 步骤2: 获取表列表")
    sqlite_tables = get_table_names(sqlite_conn, is_sqlite=True)
    pg_tables = get_table_names(pg_engine, is_sqlite=False)
    
    print(f"SQLite表数量: {len(sqlite_tables)}")
    print(f"PostgreSQL表数量: {len(pg_tables)}")
    
    # 3. 比较表结构
    print("\n📋 步骤3: 比较表结构")
    sqlite_set = set(sqlite_tables)
    pg_set = set(pg_tables)
    
    if sqlite_set == pg_set:
        print("✅ 表结构完全匹配")
    else:
        print("❌ 表结构不匹配")
        missing_in_pg = sqlite_set - pg_set
        extra_in_pg = pg_set - sqlite_set
        if missing_in_pg:
            print(f"PostgreSQL缺少的表: {missing_in_pg}")
        if extra_in_pg:
            print(f"PostgreSQL多余的表: {extra_in_pg}")
    
    # 4. 比较数据量
    print("\n📋 步骤4: 比较数据量")
    common_tables = sqlite_set & pg_set
    success_count = 0
    total_count = len(common_tables)
    
    for table_name in sorted(common_tables):
        if compare_table_data(sqlite_conn, pg_engine, table_name):
            success_count += 1
    
    # 5. 总结
    sqlite_conn.close()
    
    print("\n" + "=" * 50)
    print("🎯 验证结果")
    print(f"✅ 数据匹配的表: {success_count}/{total_count}")
    
    if success_count == total_count and sqlite_set == pg_set:
        print("🎉 迁移验证成功! 所有数据都正确迁移到PostgreSQL")
        return True
    else:
        print("⚠️  迁移验证失败，请检查数据")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 