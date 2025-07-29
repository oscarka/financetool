#!/usr/bin/env python3
"""
检查数据库数据安全性的脚本
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 设置环境变量
os.environ.setdefault('DATABASE_URL', 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test')

def check_database_data():
    """检查数据库数据情况"""
    try:
        # 创建数据库连接
        engine = create_engine(os.environ['DATABASE_URL'])
        
        with engine.connect() as conn:
            print("🔍 检查数据库数据安全性...")
            print("=" * 50)
            
            # 1. 检查当前Alembic版本
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar()
            print(f"📋 当前Alembic版本: {current_version}")
            
            # 2. 检查所有表的数据量
            print("\n📊 各表数据量统计:")
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    n_tup_ins as total_rows
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY relname
            """))
            
            total_tables = 0
            total_rows = 0
            for row in result:
                table_name = row.tablename
                row_count = row.total_rows or 0
                print(f"  📈 {table_name}: {row_count} 条记录")
                total_tables += 1
                total_rows += row_count
            
            print(f"\n📋 总计: {total_tables} 个表, {total_rows} 条记录")
            
            # 3. 检查关键业务表的数据
            print("\n🔍 关键业务表数据检查:")
            key_tables = [
                'user_operations', 'asset_positions', 'fund_info', 
                'wise_transactions', 'okx_transactions', 'ibkr_accounts'
            ]
            
            for table in key_tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✅ {table}: {count} 条记录")
                except Exception as e:
                    print(f"  ❌ {table}: 表不存在或查询失败 - {e}")
            
            # 4. 检查缺失的表
            print("\n🔍 检查缺失的表:")
            missing_tables = []
            expected_tables = [
                'asset_snapshot', 'exchange_rate_snapshot'
            ]
            
            for table in expected_tables:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = '{table}'
                    )
                """))
                exists = result.scalar()
                if not exists:
                    missing_tables.append(table)
                    print(f"  ❌ {table}: 表不存在")
                else:
                    print(f"  ✅ {table}: 表存在")
            
            # 5. 数据安全评估
            print("\n🛡️ 数据安全评估:")
            if total_rows > 0:
                print(f"  ✅ 数据库包含 {total_rows} 条业务数据，需要保护")
                if missing_tables:
                    print(f"  ⚠️  缺失 {len(missing_tables)} 个表: {', '.join(missing_tables)}")
                    print("  💡 建议: 只创建缺失的表，不删除现有数据")
                else:
                    print("  ✅ 所有表都存在，数据完整")
            else:
                print("  ℹ️  数据库为空，可以安全重建")
            
            print("\n" + "=" * 50)
            return {
                'current_version': current_version,
                'total_tables': total_tables,
                'total_rows': total_rows,
                'missing_tables': missing_tables
            }
            
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return None

if __name__ == "__main__":
    check_database_data()