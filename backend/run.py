#!/usr/bin/env python3
"""
启动脚本
"""
import sys
import os
from pathlib import Path
import subprocess
import logging
from sqlalchemy import create_engine, inspect
from app.settings import settings

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接在run.py检测wise_balances唯一约束
try:
    engine = create_engine(settings.database_url, echo=False)
    insp = inspect(engine)
    constraints = insp.get_unique_constraints('wise_balances')
    if constraints:
        print(f"[WISE_BALANCES] 检测到唯一约束: {constraints}")
        logging.warning(f"[WISE_BALANCES] 检测到唯一约束: {constraints}")
    else:
        print("[WISE_BALANCES] 未检测到唯一约束")
        logging.info("[WISE_BALANCES] 未检测到唯一约束")
except Exception as e:
    print(f"[WISE_BALANCES] 检查唯一约束失败: {e}")
    logging.error(f"[WISE_BALANCES] 检查唯一约束失败: {e}")

def check_railway_environment():
    """检查Railway环境配置"""
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    
    print(f"🚀 启动个人财务管理系统")
    print(f"📍 运行环境: {'Railway' if is_railway else '本地/其他'}")
    print(f"📁 数据目录: {data_path}")
    
    # 确保数据目录存在
    Path(data_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ 数据目录已确保存在")
    
    # 在Railway环境中修复volume权限
    if is_railway:
        try:
            import pwd
            
            # 获取当前用户ID
            current_uid = os.getuid()
            current_gid = os.getgid()
            
            print(f"🔧 修复volume权限...")
            print(f"   当前用户ID: {current_uid}")
            print(f"   当前组ID: {current_gid}")
            
            # 修复数据目录权限
            subprocess.run(["chown", "-R", f"{current_uid}:{current_gid}", data_path], check=True)
            subprocess.run(["chmod", "-R", "755", data_path], check=True)
            print(f"✅ 数据目录权限已修复")
            
            # 检查数据库文件权限
            db_file = os.path.join(data_path, "personalfinance.db")
            if os.path.exists(db_file):
                subprocess.run(["chown", f"{current_uid}:{current_gid}", db_file], check=True)
                subprocess.run(["chmod", "644", db_file], check=True)
                print(f"✅ 数据库文件权限已修复")
                
        except Exception as e:
            print(f"⚠️  权限修复失败: {e}")
            print(f"   继续启动，但可能遇到权限问题")
    
    # 检查数据库文件
    db_file = os.path.join(data_path, "personalfinance.db")
    if os.path.exists(db_file):
        size_mb = os.path.getsize(db_file) / (1024 * 1024)
        print(f"📊 数据库文件: {db_file} (大小: {size_mb:.2f}MB)")
    else:
        print(f"📊 数据库文件: {db_file} (不存在，将创建新文件)")
    
    # 在Railway环境中设置PostgreSQL数据库
    if is_railway:
        setup_postgresql_database(data_path)

def setup_postgresql_database(data_path):
    """设置PostgreSQL数据库"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.startswith("postgresql://"):
        print("⚠️  未配置PostgreSQL数据库，跳过设置")
        return
    
    print("🗄️  设置PostgreSQL数据库...")
    
    try:
        from sqlalchemy import create_engine, text
        from app.models.database import Base
        
        # 创建数据库引擎
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # 检查现有表
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            existing_tables = [row[0] for row in result]
            
            if existing_tables:
                print(f"⚠️  发现现有表: {existing_tables}")

                
                # 检查是否需要清理表（只在特定条件下）
                should_clean_tables = os.getenv("CLEAN_DATABASE", "false").lower() == "true"
                
                if should_clean_tables:
                    print("🗑️  清理现有表结构...")
                    
                    # 删除所有现有表
                    for table in reversed(existing_tables):
                        try:
                            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        except Exception as e:
                            print(f"⚠️  删除表 {table} 时出错: {e}")
                    
                    conn.commit()
                    print("✅ 现有表已清理")
                    
                    # 创建新表结构
                    print("🏗️  创建PostgreSQL表结构...")
                    Base.metadata.create_all(bind=engine)
                    print("✅ PostgreSQL表结构创建成功")
                else:
                    print("ℹ️  保留现有表结构，跳过清理")
                    
                    # 只创建缺失的表
                    print("🏗️  检查并创建缺失的表...")
                    Base.metadata.create_all(bind=engine)
                    print("✅ 表结构检查完成")
            else:
                # 没有现有表，创建所有表
                print("🏗️  创建PostgreSQL表结构...")
                Base.metadata.create_all(bind=engine)
                print("✅ PostgreSQL表结构创建成功")
            print("✅ PostgreSQL表结构创建成功")
            
            # 检查SQLite文件是否存在，如果存在则迁移数据
            sqlite_file = os.path.join(data_path, "personalfinance.db")
            if os.path.exists(sqlite_file):

                # 检查PostgreSQL是否已有数据
                result = conn.execute(text("SELECT COUNT(*) FROM user_operations"))
                pg_data_count = result.scalar()
                
                if pg_data_count == 0:
                    print("📦 发现SQLite数据文件，PostgreSQL为空，开始迁移...")
                    migrate_sqlite_to_postgresql(sqlite_file, engine)
                else:
                    print(f"ℹ️  PostgreSQL已有 {pg_data_count} 条数据，跳过SQLite迁移")
            else:
                print("ℹ️  未发现SQLite数据文件，跳过数据迁移")
            
            # 数据库诊断查询将在应用启动完成后执行
            print("ℹ️  数据库诊断查询将在应用启动完成后执行")

        
    except Exception as e:
        print(f"❌ PostgreSQL设置失败: {e}")
        print("⚠️  继续启动，但可能无法使用数据库功能")

def migrate_sqlite_to_postgresql(sqlite_file, pg_engine):
    """将SQLite数据迁移到PostgreSQL，自动修复布尔字段"""
    try:
        import sqlite3
        import pandas as pd
        from sqlalchemy import text
        
        print("🔄 开始数据迁移...")
        
        # 连接SQLite
        sqlite_conn = sqlite3.connect(sqlite_file)
        
        # 获取所有表名
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 发现 {len(tables)} 个表需要迁移")
        
        success_count = 0
        for table_name in tables:
            try:
                # 读取SQLite数据
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
                
                # 针对dca_plans表，自动修复布尔字段
                if table_name == "dca_plans" and not df.empty:
                    for col in ["smart_dca", "skip_holidays", "enable_notification"]:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: True if x in [1, "1", True] else False if x in [0, "0", False] else None)
                
                if not df.empty:
                    # 写入PostgreSQL
                    df.to_sql(table_name, pg_engine, if_exists='append', index=False, method='multi')
                    print(f"✅ {table_name}: {len(df)} 条记录")
                    success_count += 1
                else:
                    print(f"ℹ️  {table_name}: 无数据")
                    success_count += 1
                    
            except Exception as e:
                print(f"❌ {table_name}: {str(e)[:100]}...")  # 只显示前100个字符
        
        sqlite_conn.close()
        
        print(f"🎉 数据迁移完成: {success_count}/{len(tables)} 个表成功")
        
        # 备份SQLite文件
        backup_file = sqlite_file + ".backup"
        import shutil
        try:
            shutil.copy2(sqlite_file, backup_file)
            print(f"💾 SQLite文件已备份到: {backup_file}")
        except Exception as e:
            print(f"⚠️  备份SQLite文件失败: {e}")
        
    except Exception as e:
        print(f"❌ 数据迁移失败: {e}")
        print("⚠️  继续启动，但数据可能不完整")

def auto_alembic_upgrade():
    try:
        print("[ALEMBIC] 自动执行数据库迁移: alembic upgrade head ...")
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("[ALEMBIC] 迁移失败:")
            print(result.stderr)
        else:
            print("[ALEMBIC] 迁移完成")
    except Exception as e:
        print(f"[ALEMBIC] 执行迁移命令出错: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # 检查环境
    check_railway_environment()
    auto_alembic_upgrade()
    
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"🌐 服务端口: {port}")
    print(f"🐛 调试模式: {debug}")
    
    # 生产环境优化配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,  # 生产环境禁用reload
        workers=1,  # 固定使用单进程，避免并发问题
        access_log=debug,  # 生产环境可以禁用访问日志以提高性能
        log_level="info" if not debug else "debug"
    ) 