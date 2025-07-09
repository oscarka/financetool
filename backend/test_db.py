#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def test_database():
    print("🔍 数据库连接测试")
    print("=" * 50)
    
    # 获取数据库URL
    db_url = settings.database_url
    print(f"📊 数据库URL: {db_url}")
    
    try:
        # 创建引擎
        engine = create_engine(db_url)
        print("✅ 数据库引擎创建成功")
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接测试成功")
            
            # 检查表是否存在
            tables = ['ibkr_accounts', 'ibkr_balances', 'ibkr_positions', 'ibkr_sync_logs']
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"📊 {table}: {count} 条记录")
                except Exception as e:
                    print(f"❌ {table}: 表不存在或查询失败 - {e}")
                    
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

if __name__ == "__main__":
    test_database()