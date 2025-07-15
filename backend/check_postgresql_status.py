#!/usr/bin/env python3
"""
检查PostgreSQL数据库状态
"""

import os
import sys
from sqlalchemy import create_engine, text
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_postgresql_status():
    """检查PostgreSQL状态"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 未设置DATABASE_URL环境变量")
        return False
    
    try:
        engine = create_engine(database_url, echo=True)
        
        with engine.connect() as conn:
            # 检查连接
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL连接成功")
            print(f"📊 版本: {version}")
            
            # 检查当前用户
            result = conn.execute(text("SELECT current_user, current_database()"))
            user, db = result.fetchone()
            print(f"👤 当前用户: {user}")
            print(f"🗄️  当前数据库: {db}")
            
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"📋 现有表: {tables}")
            
            # 检查用户权限
            result = conn.execute(text("""
                SELECT privilege_type 
                FROM information_schema.role_table_grants 
                WHERE grantee = current_user 
                AND table_schema = 'public'
            """))
            privileges = [row[0] for row in result]
            print(f"🔑 用户权限: {privileges}")
            
            # 尝试创建测试表
            try:
                conn.execute(text("""
                    CREATE TABLE test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50)
                    )
                """))
                print("✅ 可以创建表")
                
                # 删除测试表
                conn.execute(text("DROP TABLE test_table"))
                print("✅ 可以删除表")
                
            except Exception as e:
                print(f"❌ 无法创建表: {e}")
            
            conn.commit()
            
    except Exception as e:
        print(f"❌ PostgreSQL检查失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_postgresql_status() 