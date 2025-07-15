#!/usr/bin/env python3
"""
修复PostgreSQL表冲突问题
"""

import os
import sys
from sqlalchemy import create_engine, text
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_postgresql_tables():
    """修复PostgreSQL表冲突"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 未设置DATABASE_URL环境变量")
        return False
    
    try:
        engine = create_engine(database_url, echo=True)
        
        with engine.connect() as conn:
            # 检查现有表
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            existing_tables = [row[0] for row in result]
            print(f"📋 现有表: {existing_tables}")
            
            # 检查序列
            result = conn.execute(text("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
                ORDER BY sequence_name
            """))
            existing_sequences = [row[0] for row in result]
            print(f"📋 现有序列: {existing_sequences}")
            
            if existing_tables:
                print("⚠️  发现现有表，需要清理后重新创建")
                
                # 删除所有表（这会同时删除序列）
                print("🗑️  删除所有现有表...")
                for table in reversed(existing_tables):
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        print(f"✅ 删除表: {table}")
                    except Exception as e:
                        print(f"❌ 删除表 {table} 失败: {e}")
                
                conn.commit()
                print("✅ 所有表已删除")
                
                # 重新创建表
                print("🏗️  重新创建表结构...")
                from app.models.database import Base
                Base.metadata.create_all(bind=engine)
                print("✅ 表结构重新创建成功")
                
                # 验证表创建
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                new_tables = [row[0] for row in result]
                print(f"📋 新创建的表: {new_tables}")
                
            else:
                print("✅ 没有现有表，直接创建")
                from app.models.database import Base
                Base.metadata.create_all(bind=engine)
                print("✅ 表结构创建成功")
            
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 修复PostgreSQL表冲突")
    print("=" * 50)
    success = fix_postgresql_tables()
    if success:
        print("🎉 修复完成！")
    else:
        print("❌ 修复失败")
    sys.exit(0 if success else 1) 