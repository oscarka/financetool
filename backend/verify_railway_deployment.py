#!/usr/bin/env python3
"""
Railway部署验证脚本
检查volume配置和数据持久化是否正确工作
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import json

def check_environment():
    """检查环境变量"""
    print("🔍 检查环境变量...")
    
    env_vars = {
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
        "DATABASE_PERSISTENT_PATH": os.getenv("DATABASE_PERSISTENT_PATH"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "PORT": os.getenv("PORT"),
        "APP_ENV": os.getenv("APP_ENV")
    }
    
    for key, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value or '未设置'}")
    
    return env_vars

def check_data_directory():
    """检查数据目录"""
    print("\n📁 检查数据目录...")
    
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    data_dir = Path(data_path)
    
    print(f"  数据目录路径: {data_path}")
    print(f"  目录存在: {'✅' if data_dir.exists() else '❌'}")
    
    if data_dir.exists():
        print(f"  目录权限: {oct(data_dir.stat().st_mode)[-3:]}")
        
        # 列出目录内容
        files = list(data_dir.glob("*"))
        print(f"  目录内容: {len(files)} 个文件/目录")
        for file in files:
            if file.is_file():
                size = file.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"    📄 {file.name} ({size_mb:.2f}MB)")
            else:
                print(f"    📁 {file.name}/")
    
    return data_dir

def check_database():
    """检查数据库文件"""
    print("\n📊 检查数据库文件...")
    
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    db_path = os.path.join(data_path, "personalfinance.db")
    
    print(f"  数据库路径: {db_path}")
    print(f"  文件存在: {'✅' if os.path.exists(db_path) else '❌'}")
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        size_mb = size / (1024 * 1024)
        print(f"  文件大小: {size_mb:.2f}MB")
        
        # 检查数据库连接
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取表列表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"  数据库表数量: {len(tables)}")
            
            # 检查关键表
            key_tables = ['fund_nav', 'user_operations', 'fund_info', 'asset_positions']
            for table in key_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"    📋 {table}: {count} 条记录")
            
            conn.close()
            print("  ✅ 数据库连接正常")
            
        except Exception as e:
            print(f"  ❌ 数据库连接失败: {e}")
    else:
        print("  ⚠️  数据库文件不存在，将在首次运行时创建")
    
    return db_path

def check_volume_mount():
    """检查volume挂载"""
    print("\n🔗 检查volume挂载...")
    
    # 检查是否在Railway环境中
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    if not is_railway:
        print("  ⚠️  不在Railway环境中，跳过volume检查")
        return False
    
    # 检查数据目录是否可写
    data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    test_file = os.path.join(data_path, "volume_test.txt")
    
    try:
        # 写入测试文件
        with open(test_file, 'w') as f:
            f.write(f"Volume test at {datetime.now()}")
        
        # 读取测试文件
        with open(test_file, 'r') as f:
            content = f.read()
        
        # 删除测试文件
        os.remove(test_file)
        
        print("  ✅ Volume挂载正常，可读写")
        return True
        
    except Exception as e:
        print(f"  ❌ Volume挂载失败: {e}")
        return False

def check_railway_config():
    """检查Railway配置"""
    print("\n⚙️  检查Railway配置...")
    
    # 检查railway.toml
    railway_toml = Path("railway.toml")
    if railway_toml.exists():
        print("  ✅ railway.toml 文件存在")
        
        # 读取并检查volume配置
        content = railway_toml.read_text()
        if "[[deploy.volumes]]" in content:
            print("  ✅ volume配置已设置")
        else:
            print("  ❌ volume配置缺失")
    else:
        print("  ❌ railway.toml 文件不存在")
    
    # 检查Dockerfile
    dockerfile = Path("Dockerfile")
    if dockerfile.exists():
        print("  ✅ Dockerfile 文件存在")
        
        content = dockerfile.read_text()
        if "DATABASE_PERSISTENT_PATH" in content:
            print("  ✅ 数据持久化环境变量已设置")
        else:
            print("  ❌ 数据持久化环境变量缺失")
    else:
        print("  ❌ Dockerfile 文件不存在")

def generate_report():
    """生成验证报告"""
    print("\n📋 生成验证报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "is_railway": bool(os.getenv("RAILWAY_ENVIRONMENT")),
            "data_path": os.getenv("DATABASE_PERSISTENT_PATH", "/app/data"),
            "port": os.getenv("PORT", "8000")
        },
        "checks": {}
    }
    
    # 执行检查
    env_vars = check_environment()
    data_dir = check_data_directory()
    db_path = check_database()
    volume_ok = check_volume_mount()
    check_railway_config()
    
    # 总结
    print("\n🎯 验证总结:")
    print(f"  📍 运行环境: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else '本地/其他'}")
    print(f"  📁 数据目录: {os.getenv('DATABASE_PERSISTENT_PATH', '/app/data')}")
    print(f"  📊 数据库文件: {'存在' if os.path.exists(db_path) else '不存在'}")
    print(f"  🔗 Volume挂载: {'正常' if volume_ok else '异常'}")
    
    # 保存报告
    report_file = "railway_deployment_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 验证报告已保存: {report_file}")

if __name__ == "__main__":
    print("🚀 Railway部署验证工具")
    print("=" * 50)
    
    generate_report()
    
    print("\n✅ 验证完成！")