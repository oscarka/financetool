#!/usr/bin/env python3
"""
SQLite到PostgreSQL数据迁移脚本
将本地SQLite数据库的所有数据迁移到PostgreSQL
"""

import os
import sys
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import json
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import Base
from app.settings import settings

def get_sqlite_connection():
    """获取SQLite连接"""
    sqlite_path = "data/personalfinance.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite数据库文件不存在: {sqlite_path}")
        return None
    
    return sqlite3.connect(sqlite_path)

def get_postgresql_engine():
    """获取PostgreSQL引擎"""
    # 检查是否有DATABASE_URL环境变量
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 未设置DATABASE_URL环境变量")
        return None
    
    if not database_url.startswith("postgresql://"):
        print(f"❌ DATABASE_URL不是PostgreSQL连接串: {database_url}")
        return None
    
    try:
        engine = create_engine(database_url, echo=False)
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL连接成功")
        return engine
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return None

def get_table_names(sqlite_conn):
    """获取SQLite中的所有表名"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def get_table_data(sqlite_conn, table_name):
    """获取表的所有数据"""
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
        return df
    except Exception as e:
        print(f"❌ 读取表 {table_name} 失败: {e}")
        return None

def create_postgresql_tables(engine):
    """在PostgreSQL中创建表结构"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL表结构创建成功")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL表结构创建失败: {e}")
        return False

def migrate_table_data(engine, table_name, df):
    """迁移单个表的数据"""
    if df is None or df.empty:
        print(f"⚠️  表 {table_name} 无数据，跳过")
        return True
    
    try:
        # 处理数据类型转换
        for col in df.columns:
            if df[col].dtype == 'object':
                # 检查是否是JSON字符串
                if df[col].iloc[0] and isinstance(df[col].iloc[0], str) and df[col].iloc[0].startswith('{'):
                    try:
                        # 尝试解析JSON
                        df[col] = df[col].apply(lambda x: json.dumps(json.loads(x)) if pd.notna(x) else None)
                    except:
                        pass
        
        # 写入PostgreSQL
        df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
        print(f"✅ 表 {table_name} 迁移成功: {len(df)} 条记录")
        return True
    except Exception as e:
        print(f"❌ 表 {table_name} 迁移失败: {e}")
        return False

def backup_sqlite_data():
    """备份SQLite数据"""
    backup_dir = "backups"
    Path(backup_dir).mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/sqlite_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2("data/personalfinance.db", backup_file)
        print(f"✅ SQLite数据已备份到: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ SQLite数据备份失败: {e}")
        return None

def main():
    """主迁移函数"""
    print("🚀 开始SQLite到PostgreSQL数据迁移")
    print("=" * 50)
    
    # 1. 备份SQLite数据
    print("\n📋 步骤1: 备份SQLite数据")
    backup_file = backup_sqlite_data()
    
    # 2. 连接SQLite
    print("\n📋 步骤2: 连接SQLite数据库")
    sqlite_conn = get_sqlite_connection()
    if not sqlite_conn:
        return False
    
    # 3. 连接PostgreSQL
    print("\n📋 步骤3: 连接PostgreSQL数据库")
    pg_engine = get_postgresql_engine()
    if not pg_engine:
        sqlite_conn.close()
        return False
    
    # 4. 创建PostgreSQL表结构
    print("\n📋 步骤4: 创建PostgreSQL表结构")
    if not create_postgresql_tables(pg_engine):
        sqlite_conn.close()
        return False
    
    # 5. 获取所有表名
    print("\n📋 步骤5: 获取表列表")
    tables = get_table_names(sqlite_conn)
    print(f"发现 {len(tables)} 个表: {', '.join(tables)}")
    
    # 6. 迁移数据
    print("\n📋 步骤6: 开始数据迁移")
    success_count = 0
    total_count = len(tables)
    
    for table_name in tables:
        print(f"\n📊 迁移表: {table_name}")
        
        # 获取表数据
        df = get_table_data(sqlite_conn, table_name)
        if df is not None:
            # 迁移数据
            if migrate_table_data(pg_engine, table_name, df):
                success_count += 1
    
    # 7. 清理和总结
    sqlite_conn.close()
    
    print("\n" + "=" * 50)
    print("🎉 迁移完成!")
    print(f"✅ 成功迁移: {success_count}/{total_count} 个表")
    
    if success_count == total_count:
        print("🎯 所有数据迁移成功!")
        print(f"💾 SQLite备份文件: {backup_file}")
        print("💡 建议: 验证数据完整性后可以删除SQLite文件")
    else:
        print("⚠️  部分表迁移失败，请检查错误信息")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 