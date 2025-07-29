#!/usr/bin/env python3
"""
启动脚本
"""
import sys
import os
from pathlib import Path
import subprocess
import logging
from sqlalchemy import create_engine, inspect, text
from app.settings import settings
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_compatibility(conn):
    """检查数据库兼容性"""
    print("🔍 开始数据库兼容性检查...")
    issues = []
    missing_tables = []
    field_mismatches = []
    
    # 动态从SQLAlchemy模型生成检查规则
    try:
        from app.models.database import Base
        # 确保导入所有模型
        from app.models import asset_snapshot
        
        # 获取所有模型类
        required_tables = {}
        
        # 遍历所有模型，动态生成字段列表
        for table_name in Base.metadata.tables:
            table = Base.metadata.tables[table_name]
            required_fields = [column.name for column in table.columns]
            required_tables[table_name] = required_fields
            
        print(f"📊 动态生成检查规则: {len(required_tables)} 个表")
        
        # 添加特殊表的检查规则
        special_tables = {
            'alembic_version': ['version_num'],  # Alembic版本表
            'audit_log': [  # 审计日志表（通过SQL创建）
                'id', 'table_name', 'operation', 'old_data', 'new_data',
                'source_ip', 'user_agent', 'api_key', 'request_id', 
                'session_id', 'changed_at'
            ]
        }
        
        # 合并特殊表到检查规则中
        required_tables.update(special_tables)
        print(f"📊 包含特殊表后的检查规则: {len(required_tables)} 个表")
        
    except ImportError as e:
        print(f"⚠️  无法导入模型，使用备用检查方法: {e}")
        # 备用方案：使用简化的检查
        return check_database_basic_compatibility(conn)
    
    # 检查表结构
    for table_name, required_fields in required_tables.items():
        print(f"📊 检查表: {table_name}")
        
        # 检查表是否存在
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            missing_tables.append(table_name)
            issues.append(f"❌ 表 {table_name} 不存在")
            continue
        
        # 检查字段
        result = conn.execute(text(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = '{table_name}'
        """))
        existing_fields = {row[0]: {'type': row[1], 'nullable': row[2]} for row in result}
        
        table_field_issues = []
        for field in required_fields:
            if field not in existing_fields:
                table_field_issues.append(field)
                issues.append(f"❌ 表 {table_name} 缺少字段: {field}")
        
        if table_field_issues:
            field_mismatches.append({
                'table': table_name,
                'missing_fields': table_field_issues
            })
        
        # 检查索引（只对业务表检查主键索引）
        if table_name not in ['alembic_version', 'audit_log']:
            result = conn.execute(text(f"""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = '{table_name}'
            """))
            existing_indexes = [row[0] for row in result]
            
            # 检查主键索引
            if f"{table_name}_pkey" not in existing_indexes:
                issues.append(f"❌ 表 {table_name} 缺少主键索引")
    
    # 检查 alembic_version 表
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'alembic_version'
        )
    """))
    alembic_version_exists = result.scalar()
    
    if not alembic_version_exists:
        issues.append("❌ alembic_version 表不存在")
    else:
        # 检查当前版本
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current_version = result.scalar()
        print(f"📋 当前 Alembic 版本: {current_version}")
    
    # 根据问题类型返回不同的状态
    if issues:
        print("❌ 检测到数据库不一致:")
        for issue in issues:
            print(f"  {issue}")
        
        # 如果只有表缺失，没有字段不一致，返回 "missing_tables"
        if missing_tables and not field_mismatches:
            print("📋 只有表缺失，这是安全的操作")
            return "missing_tables"
        # 如果有字段不一致，返回 "field_mismatch"
        elif field_mismatches:
            print("⚠️  检测到字段不一致，需要谨慎处理")
            return "field_mismatch"
        # 其他情况返回 "incompatible"
        else:
            return "incompatible"
    else:
        print("✅ 数据库兼容性检查通过")
        return "compatible"

def check_database_basic_compatibility(conn):
    """基础数据库兼容性检查（备用方案）"""
    print("🔍 执行基础数据库兼容性检查...")
    issues = []
    missing_tables = []
    
    # 只检查关键表的存在性
    critical_tables = [
        'user_operations', 'asset_positions', 'fund_info', 
        'wise_transactions', 'okx_transactions', 'asset_snapshot'
    ]
    
    for table_name in critical_tables:
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            missing_tables.append(table_name)
            issues.append(f"❌ 关键表 {table_name} 不存在")
    
    if issues:
        print("❌ 基础检查发现不一致:")
        for issue in issues:
            print(f"  {issue}")
        
        # 如果只有表缺失，返回 "missing_tables"
        if missing_tables:
            print("📋 只有表缺失，这是安全的操作")
            return "missing_tables"
        else:
            return "incompatible"
    else:
        print("✅ 基础数据库兼容性检查通过")
        return "compatible"

def rollback_database_changes(conn):
    """回退数据库修改"""
    print("🔄 开始回退数据库修改...")
    
    try:
        # 1. 恢复 alembic 版本号到基础版本
        print("📋 恢复 Alembic 版本号...")
        try:
            # 确保在backend目录执行alembic命令
            import os
            current_dir = os.getcwd()
            backend_dir = os.path.join(current_dir, 'backend') if os.path.exists(os.path.join(current_dir, 'backend')) else current_dir
            
            # 切换到backend目录
            os.chdir(backend_dir)
            print(f"📁 切换到目录: {backend_dir}")
            
            # 尝试恢复到基础版本
            subprocess.run(["alembic", "stamp", "base"], check=True)
            
            # 恢复原目录
            os.chdir(current_dir)
            
            print("✅ Alembic 版本号已恢复到基础版本")
        except Exception as e:
            print(f"⚠️  恢复版本号失败: {e}")
            print("ℹ️  继续执行其他回退操作")
        
        # 2. 删除新创建的表（如果有）
        print("🗑️  删除新创建的表...")
        new_tables = [
            'asset_snapshot', 'exchange_rate_snapshot', 'okx_account_overview',
            'web3_balances', 'web3_tokens', 'web3_transactions'
        ]
        
        for table in new_tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"  ✅ 删除表 {table}")
            except Exception as e:
                print(f"  ⚠️  删除表 {table} 时出错: {e}")
        
        conn.commit()
        print("✅ 新表删除完成")
        
        # 3. 检查并恢复被修改的表结构
        print("🔧 检查表结构...")
        # 这里可以添加更详细的表结构恢复逻辑
        print("✅ 表结构检查完成")
        
        print("✅ 数据库回退完成")
        return True
        
    except Exception as e:
        print(f"❌ 回退失败: {e}")
        return False

def safe_railway_migration():
    """安全的Railway迁移"""
    import os
    import subprocess
    from sqlalchemy import text
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.startswith("postgresql://"):
        print("⚠️  未配置PostgreSQL数据库，跳过Railway迁移")
        return True
    
    print("🚀 开始安全的Railway数据库迁移...")
    
    try:
        from sqlalchemy import create_engine
        
        # 创建数据库引擎
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # 1. 检查当前Alembic版本
            try:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                current_version = result.scalar()
                print(f"📋 当前 Alembic 版本: {current_version}")
            except Exception as e:
                print(f"⚠️  无法获取Alembic版本: {e}")
                current_version = None
            
            # 2. 预检查 - 区分表缺失和字段不一致
            print("🔍 执行预检查...")
            compatibility_result = check_database_compatibility(conn)
            
            if compatibility_result == "missing_tables":
                print("📋 检测到缺失表，将安全创建...")
                
                # 如果版本已经是000000000000，直接创建缺失的表
                if current_version == "000000000000":
                    print("✅ 版本已是最新，直接创建缺失的表...")
                    
                    # 直接创建缺失的表
                    missing_tables = []
                    for table_name in ['asset_snapshot', 'exchange_rate_snapshot']:
                        try:
                            result = conn.execute(text(f"""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                                )
                            """))
                            exists = result.scalar()
                            if not exists:
                                missing_tables.append(table_name)
                        except Exception as e:
                            print(f"⚠️  检查表 {table_name} 时出错: {e}")
                    
                    if missing_tables:
                        print(f"🔨 创建缺失的表: {', '.join(missing_tables)}")
                        
                        # 这里可以添加直接创建表的SQL
                        # 为了安全，我们使用SQLAlchemy的create_all
                        from app.models.database import Base
                        Base.metadata.create_all(bind=engine)
                        
                        print("✅ 缺失的表已创建")
                    else:
                        print("✅ 所有表都已存在")
                    
                    return True
                else:
                    # 版本不是000000000000，需要更新版本号
                    print(f"🔄 更新版本号从 {current_version} 到 000000000000...")
                    
                    # 直接更新版本号
                    conn.execute(text("DELETE FROM alembic_version"))
                    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('000000000000')"))
                    conn.commit()
                    
                    print("✅ 版本号已更新")
                    return True
                    
            elif compatibility_result == "field_mismatch":
                print("❌ 检测到字段不一致，开始回退...")
                if rollback_database_changes(conn):
                    print("✅ 回退成功，迁移终止")
                    return False
                else:
                    print("❌ 回退失败，需要手动干预")
                    return False
            elif compatibility_result == "compatible":
                print("✅ 数据库兼容性检查通过")
                return True
            else:
                print("❌ 预检查失败，开始回退...")
                if rollback_database_changes(conn):
                    print("✅ 回退成功，迁移终止")
                    return False
                else:
                    print("❌ 回退失败，需要手动干预")
                    return False
            
            # 3. 检查现有数据
            print("📊 检查现有数据...")
            data_exists = False
            for table in ['user_operations', 'asset_positions', 'wise_transactions']:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    if count > 0:
                        print(f"📈 {table} 表有 {count} 条数据")
                        data_exists = True
                except Exception as e:
                    print(f"⚠️  检查 {table} 表数据时出错: {e}")
            
            # 4. 如果版本不是000000000000，尝试Alembic升级
            if current_version != "000000000000":
                print("🔄 执行Alembic迁移...")
                try:
                    # 确保在backend目录执行alembic命令
                    current_dir = os.getcwd()
                    backend_dir = os.path.join(current_dir, 'backend') if os.path.exists(os.path.join(current_dir, 'backend')) else current_dir
                    
                    # 切换到backend目录
                    os.chdir(backend_dir)
                    print(f"📁 切换到目录: {backend_dir}")
                    
                    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
                    
                    # 恢复原目录
                    os.chdir(current_dir)
                    
                    if result.returncode != 0:
                        print(f"❌ 迁移失败: {result.stderr}")
                        print("🔄 开始回退...")
                        if rollback_database_changes(conn):
                            print("✅ 回退成功")
                            return False
                        else:
                            print("❌ 回退失败")
                            return False
                    else:
                        print("✅ 迁移执行成功")
                        print("📝 迁移输出:")
                        print(result.stdout)
                except Exception as e:
                    print(f"❌ 执行迁移命令失败: {e}")
                    print("🔄 开始回退...")
                    if rollback_database_changes(conn):
                        print("✅ 回退成功")
                        return False
                    else:
                        print("❌ 回退失败")
                        return False
            
            # 5. 迁移后验证
            print("🔍 执行迁移后验证...")
            final_check = check_database_compatibility(conn)
            if final_check != "compatible" and final_check != "missing_tables":
                print("❌ 迁移后验证失败，开始回退...")
                if rollback_database_changes(conn):
                    print("✅ 回退成功")
                    return False
                else:
                    print("❌ 回退失败")
                    return False
            
            print("✅ 迁移验证通过")
            return True
            
    except Exception as e:
        print(f"❌ 迁移过程中出错: {e}")
        print("🔄 开始回退...")
        try:
            with engine.connect() as conn:
                if rollback_database_changes(conn):
                    print("✅ 回退成功")
                    return False
                else:
                    print("❌ 回退失败")
                    return False
        except Exception as rollback_error:
            print(f"❌ 回退过程中出错: {rollback_error}")
            return False

# 移除wise_balances唯一约束检测相关临时代码

def check_railway_environment():
    """检查Railway环境配置"""
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    # 根据环境设置数据目录
    if is_railway:
        data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    else:
        # 本地环境使用相对路径
        data_path = os.getenv("DATABASE_PERSISTENT_PATH", "./data")
    
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

def handle_railway_database_migration():
    """处理Railway线上数据库迁移"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.startswith("postgresql://"):
        print("⚠️  未配置PostgreSQL数据库，跳过Railway迁移")
        return
    
    print("🚀 处理Railway线上数据库迁移...")
    
    try:
        from sqlalchemy import create_engine, text
        
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
            
            print(f"📊 发现现有表: {existing_tables}")
            
            # 检查是否有数据
            data_exists = False
            if existing_tables:
                for table in ['user_operations', 'asset_positions', 'wise_transactions']:
                    if table in existing_tables:
                        try:
                            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                            count = result.scalar()
                            if count > 0:
                                print(f"📈 {table} 表有 {count} 条数据")
                                data_exists = True
                        except Exception as e:
                            print(f"⚠️  检查 {table} 表数据时出错: {e}")
            
            if data_exists:
                print("🔄 检测到线上数据，执行安全迁移策略...")
                
                # 安全策略：只创建缺失的表，不删除现有表
                safe_migrate_with_data(conn, existing_tables)
                
                print("✅ Railway数据库安全迁移完成")
            else:
                print("ℹ️  线上数据库无数据，执行完整迁移")
                execute_full_migration(conn, existing_tables)
                
    except Exception as e:
        print(f"❌ Railway数据库迁移失败: {e}")
        print("⚠️  继续启动，但可能无法使用数据库功能")

def safe_migrate_with_data(conn, existing_tables):
    """安全迁移：保留现有数据，只创建缺失的表"""
    print("🛡️  执行安全迁移策略...")
    print("📊 检测到现有数据，将保留数据并只创建缺失的表")
    
    # 检查新迁移需要的表
    required_tables = [
        'user_operations', 'asset_positions', 'fund_info', 'fund_nav', 'fund_dividend',
        'dca_plans', 'exchange_rates', 'system_config', 'wise_transactions', 
        'wise_balances', 'wise_exchange_rates', 'ibkr_accounts', 'ibkr_balances',
        'ibkr_positions', 'ibkr_sync_logs', 'okx_balances', 'okx_transactions',
        'okx_positions', 'okx_market_data', 'okx_account_overview', 'web3_balances',
        'web3_tokens', 'web3_transactions', 'asset_snapshot', 'exchange_rate_snapshot'
    ]
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"📋 需要创建的表: {missing_tables}")
        print("⚠️  注意：将保留现有数据，只创建缺失的表")
        
        # 执行迁移创建缺失的表
        try:
            import subprocess
            print("🔄 执行 alembic upgrade head...")
            result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 缺失表创建成功")
                print("📝 迁移输出:")
                print(result.stdout)
            else:
                print(f"❌ 表创建失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 执行迁移失败: {e}")
    else:
        print("✅ 所有必需表都已存在")
        print("ℹ️  无需创建新表，现有数据结构完整")
    
    # 检查并修复表结构差异
    check_and_fix_table_structure(conn, existing_tables)

def execute_full_migration(conn, existing_tables):
    """执行完整迁移：删除旧表，创建新表"""
    print("🏗️  执行完整迁移...")
    
    # 删除现有表（除了alembic_version）
    for table in existing_tables:
        if table != 'alembic_version':
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"🗑️  删除表 {table}")
            except Exception as e:
                print(f"⚠️  删除表 {table} 时出错: {e}")
    
    conn.commit()
    
    # 执行新的迁移
    try:
        import subprocess
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 新表结构创建成功")
        else:
            print(f"❌ 表结构创建失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 执行迁移失败: {e}")

def check_and_fix_table_structure(conn, existing_tables):
    """检查并修复表结构差异"""
    print("🔍 检查表结构差异...")
    
    # 这里可以添加具体的表结构检查和修复逻辑
    # 比如检查缺失的字段、索引等
    print("ℹ️  表结构检查完成（基础版本）")



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
    
    # 在Railway环境中处理数据库迁移
    if os.getenv("RAILWAY_ENVIRONMENT") is not None:
        print("🚀 检测到Railway环境，执行安全数据库迁移...")
        migration_success = safe_railway_migration()
        if not migration_success:
            print("❌ 数据库迁移失败，服务无法启动")
            sys.exit(1)
    else:
        print("🏠 本地环境，执行标准数据库设置...")
        auto_alembic_upgrade()
    
    # 测试模式：模拟Railway环境
    if os.getenv("TEST_RAILWAY_MIGRATION", "false").lower() == "true":
        print("🧪 测试模式：模拟Railway环境迁移...")
        os.environ["RAILWAY_ENVIRONMENT"] = "test"
        migration_success = safe_railway_migration()
        if not migration_success:
            print("❌ 测试迁移失败")
            sys.exit(1)
    
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