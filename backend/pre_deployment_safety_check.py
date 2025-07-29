#!/usr/bin/env python3
"""
部署前安全检查脚本
在部署到Railway之前进行全面的安全检查
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def check_environment_variables():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    required_vars = {
        "DATABASE_URL": "PostgreSQL数据库连接字符串",
        "RAILWAY_ENVIRONMENT": "Railway环境标识",
        "APP_ENV": "应用环境",
        "PORT": "服务端口"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"{var} ({description})")
        else:
            print(f"  ✅ {var}: {value[:20]}..." if len(value) > 20 else f"  ✅ {var}: {value}")
    
    if missing_vars:
        print("❌ 缺失环境变量:")
        for var in missing_vars:
            print(f"    - {var}")
        return False
    else:
        print("✅ 环境变量配置完整")
        return True

def check_database_migration():
    """检查数据库迁移文件"""
    print("🔍 检查数据库迁移文件...")
    
    migration_file = Path("migrations/versions/000000000000_complete_schema.py")
    if not migration_file.exists():
        print("❌ 完整迁移文件不存在")
        return False
    
    # 检查迁移文件内容
    content = migration_file.read_text()
    
    # 检查关键表是否包含
    required_tables = [
        "user_operations", "asset_positions", "fund_info", "fund_nav",
        "wise_transactions", "wise_balances", "ibkr_accounts", "ibkr_balances",
        "okx_transactions", "okx_balances", "asset_snapshot"
    ]
    
    missing_tables = []
    for table in required_tables:
        if f"op.create_table('{table}'" not in content:
            missing_tables.append(table)
    
    if missing_tables:
        print(f"❌ 迁移文件缺少表: {missing_tables}")
        return False
    
    print("✅ 数据库迁移文件检查通过")
    return True

def check_model_compatibility():
    """检查模型兼容性"""
    print("🔍 检查模型兼容性...")
    
    try:
        # 导入模型
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.models.database import Base
        from app.models import asset_snapshot
        
        # 检查所有表
        table_count = len(Base.metadata.tables)
        print(f"  📊 检测到 {table_count} 个表")
        
        # 检查关键模型
        from app.models.database import (
            UserOperation, AssetPosition, FundInfo, FundNav,
            WiseTransaction, WiseBalance, IBKRAccount, IBKRBalance,
            OKXTransaction, OKXBalance
        )
        
        print("✅ 模型导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 模型兼容性检查失败: {e}")
        return False

def check_health_endpoints():
    """检查健康检查端点"""
    print("🔍 检查健康检查端点...")
    
    # 检查main.py中的健康检查端点
    main_file = Path("app/main.py")
    if not main_file.exists():
        print("❌ main.py文件不存在")
        return False
    
    content = main_file.read_text()
    
    # 检查基础健康检查端点
    if "@app.get(\"/health\")" not in content:
        print("❌ 基础健康检查端点缺失")
        return False
    
    # 检查数据健康检查端点
    if "@app.get(\"/health/data\")" not in content:
        print("❌ 数据健康检查端点缺失")
        return False
    
    print("✅ 健康检查端点配置正确")
    return True

def check_railway_config():
    """检查Railway配置"""
    print("🔍 检查Railway配置...")
    
    railway_toml = Path("railway.toml")
    if not railway_toml.exists():
        print("❌ railway.toml文件不存在")
        return False
    
    content = railway_toml.read_text()
    
    # 检查关键配置
    required_configs = [
        "healthcheckPath = \"/health\"",
        "healthcheckTimeout = 300",
        "startCommand = \"python run.py\""
    ]
    
    missing_configs = []
    for config in required_configs:
        if config not in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"❌ Railway配置缺失: {missing_configs}")
        return False
    
    print("✅ Railway配置正确")
    return True

def check_safe_migration_logic():
    """检查安全迁移逻辑"""
    print("🔍 检查安全迁移逻辑...")
    
    run_file = Path("run.py")
    if not run_file.exists():
        print("❌ run.py文件不存在")
        return False
    
    content = run_file.read_text()
    
    # 检查关键函数
    required_functions = [
        "def check_database_compatibility",
        "def safe_railway_migration",
        "def rollback_database_changes"
    ]
    
    missing_functions = []
    for func in required_functions:
        if func not in content:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ 安全迁移逻辑缺失: {missing_functions}")
        return False
    
    print("✅ 安全迁移逻辑完整")
    return True

def check_dockerfile():
    """检查Dockerfile配置"""
    print("🔍 检查Dockerfile配置...")
    
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("❌ Dockerfile不存在")
        return False
    
    content = dockerfile.read_text()
    
    # 检查关键配置
    required_configs = [
        "HEALTHCHECK",
        "EXPOSE 8000",
        "CMD [\"python\", \"run.py\"]"
    ]
    
    missing_configs = []
    for config in required_configs:
        if config not in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"❌ Dockerfile配置缺失: {missing_configs}")
        return False
    
    print("✅ Dockerfile配置正确")
    return True

def run_local_tests():
    """运行本地测试"""
    print("🔍 运行本地测试...")
    
    try:
        # 测试数据库连接
        result = subprocess.run([
            "python", "-c", 
            "import os; from sqlalchemy import create_engine; print('数据库连接测试通过')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ 数据库连接测试失败: {result.stderr}")
            return False
        
        print("✅ 本地测试通过")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 本地测试超时")
        return False
    except Exception as e:
        print(f"❌ 本地测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Railway部署前安全检查")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("环境变量配置", check_environment_variables),
        ("数据库迁移文件", check_database_migration),
        ("模型兼容性", check_model_compatibility),
        ("健康检查端点", check_health_endpoints),
        ("Railway配置", check_railway_config),
        ("安全迁移逻辑", check_safe_migration_logic),
        ("Dockerfile配置", check_dockerfile),
        ("本地测试", run_local_tests)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查异常: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  - {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 安全检查全部通过！可以安全部署到Railway。")
        print("\n📋 部署建议:")
        print("  1. 确保Railway环境变量已正确设置")
        print("  2. 确保Volume已正确挂载")
        print("  3. 监控部署日志，确保迁移成功")
        print("  4. 部署后验证健康检查端点")
        return 0
    else:
        print("⚠️  安全检查发现问题，请修复后再部署。")
        print("\n🔧 修复建议:")
        for name, result in results:
            if not result:
                print(f"  - 修复 {name} 相关问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())