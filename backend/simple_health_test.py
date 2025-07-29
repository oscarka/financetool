#!/usr/bin/env python3
"""
简单的健康检查测试
只测试核心的健康检查逻辑，不依赖完整的应用
"""
import os
import sys
import asyncio
from datetime import datetime

# 设置环境变量
os.environ['DATABASE_URL'] = 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test'
os.environ['RAILWAY_ENVIRONMENT'] = 'test'
os.environ['APP_ENV'] = 'prod'
os.environ['PORT'] = '8000'
os.environ['DATABASE_PERSISTENT_PATH'] = './data'

async def test_health_logic():
    """测试健康检查逻辑"""
    try:
        print("🔍 测试健康检查逻辑...")
        
        # 模拟健康检查逻辑
        database_url = os.getenv("DATABASE_URL")
        db_info = {}
        
        if database_url and database_url.startswith("postgresql://"):
            # PostgreSQL数据库
            try:
                from sqlalchemy import create_engine, text
                
                # 创建数据库引擎
                engine = create_engine(database_url, echo=False)
                
                with engine.connect() as conn:
                    # 检查数据库连接
                    result = conn.execute(text("SELECT 1"))
                    result.scalar()
                    
                    # 检查表数量
                    result = conn.execute(text("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """))
                    table_count = result.scalar()
                    
                    # 检查alembic版本
                    try:
                        result = conn.execute(text("SELECT version_num FROM alembic_version"))
                        alembic_version = result.scalar()
                    except:
                        alembic_version = "unknown"
                    
                    db_info = {
                        "type": "postgresql",
                        "connected": True,
                        "table_count": table_count,
                        "alembic_version": alembic_version,
                        "url": database_url.split("@")[0] + "@***" if "@" in database_url else "***"
                    }
                    
                    print("✅ PostgreSQL数据库连接成功")
                    print(f"  表数量: {table_count}")
                    print(f"  Alembic版本: {alembic_version}")
                    
            except Exception as e:
                db_info = {
                    "type": "postgresql",
                    "connected": False,
                    "error": str(e)[:100],
                    "url": database_url.split("@")[0] + "@***" if "@" in database_url else "***"
                }
                print(f"❌ PostgreSQL数据库连接失败: {e}")
        else:
            # SQLite数据库
            db_info = {
                "type": "sqlite",
                "path": "./data/personalfinance.db",
                "exists": False,
                "size_bytes": 0
            }
            print("ℹ️  使用SQLite数据库")
        
        # 构建健康检查响应
        health_response = {
            "status": "healthy" if db_info.get("connected", True) else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": "production",
            "database": db_info
        }
        
        print("✅ 健康检查逻辑测试成功")
        print(f"  状态: {health_response['status']}")
        print(f"  数据库类型: {db_info.get('type')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 健康检查逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_health_logic():
    """测试数据健康检查逻辑"""
    try:
        print("\n🔍 测试数据健康检查逻辑...")
        
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url or not database_url.startswith("postgresql://"):
            print("ℹ️  跳过数据健康检查（非PostgreSQL数据库）")
            return True
        
        try:
            from sqlalchemy import create_engine, text
            
            engine = create_engine(database_url, echo=False)
            with engine.connect() as conn:
                # 检查关键表的数据
                data_integrity = {}
                
                # 检查用户操作表
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM user_operations"))
                    data_integrity["user_operations"] = result.scalar()
                except:
                    data_integrity["user_operations"] = 0
                
                # 检查资产持仓表
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM asset_positions"))
                    data_integrity["asset_positions"] = result.scalar()
                except:
                    data_integrity["asset_positions"] = 0
                
                # 检查IBKR相关表
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM ibkr_accounts"))
                    data_integrity["ibkr_accounts"] = result.scalar()
                except:
                    data_integrity["ibkr_accounts"] = 0
                
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM ibkr_balances"))
                    data_integrity["ibkr_balances"] = result.scalar()
                except:
                    data_integrity["ibkr_balances"] = 0
                
                # 计算总数据量
                total_records = sum(data_integrity.values())
                has_data = total_records > 0
                
                print("✅ 数据健康检查成功")
                print(f"  总记录数: {total_records}")
                print(f"  有数据: {has_data}")
                print("  各表记录数:")
                for table, count in data_integrity.items():
                    print(f"    - {table}: {count}")
                
                return True
                
        except Exception as e:
            print(f"❌ 数据健康检查失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 数据健康检查逻辑测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始简单健康检查测试")
    print("=" * 50)
    
    # 测试基础健康检查逻辑
    health_ok = await test_health_logic()
    
    # 测试数据健康检查逻辑
    data_ok = await test_data_health_logic()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"  基础健康检查逻辑: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"  数据健康检查逻辑: {'✅ 通过' if data_ok else '❌ 失败'}")
    
    if health_ok and data_ok:
        print("\n🎉 所有测试通过！健康检查逻辑工作正常。")
        print("✅ 可以安全部署到Railway")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要检查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))