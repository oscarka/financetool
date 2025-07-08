#!/usr/bin/env python3
"""
检查分支数据库状态脚本
用于快速检查当前分支的数据库配置和状态
"""

import os
import sys
import sqlite3
from pathlib import Path

def get_current_branch():
    """获取当前Git分支名"""
    try:
        import subprocess
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, ImportError):
        return "main"

def get_branch_db_path(branch_name):
    """获取分支数据库路径"""
    return f"./data/personalfinance_{branch_name}.db"

def check_database_status():
    """检查数据库状态"""
    branch_name = get_current_branch()
    print(f"当前分支: {branch_name}")
    
    # 检查环境变量
    branch_env = os.getenv("BRANCH_NAME")
    print(f"环境变量 BRANCH_NAME: {branch_env or '未设置'}")
    
    # 检查数据库文件
    main_db = "./data/personalfinance.db"
    branch_db = get_branch_db_path(branch_name)
    
    print(f"\n数据库文件状态:")
    print(f"  主数据库: {main_db} - {'存在' if os.path.exists(main_db) else '不存在'}")
    print(f"  分支数据库: {branch_db} - {'存在' if os.path.exists(branch_db) else '不存在'}")
    
    # 检查数据库连接
    if branch_name == "main":
        db_path = main_db
    else:
        db_path = branch_db if os.path.exists(branch_db) else main_db
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取表列表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"\n数据库连接成功: {db_path}")
            print(f"表数量: {len(tables)}")
            
            if tables:
                print("现有表:")
                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table[0]})")
                    columns = cursor.fetchall()
                    print(f"  - {table[0]} ({len(columns)} 列)")
            
            conn.close()
            
        except Exception as e:
            print(f"数据库连接失败: {e}")
    else:
        print(f"\n数据库文件不存在: {db_path}")
    
    # 检查迁移状态
    print(f"\n迁移文件状态:")
    migrations_dir = Path("./migrations/versions")
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("*.py"))
        print(f"  迁移文件数量: {len(migration_files)}")
        
        if migration_files:
            print("  最近的迁移文件:")
            for file in sorted(migration_files)[-3:]:
                print(f"    - {file.name}")
    else:
        print("  迁移目录不存在")

def check_configuration():
    """检查配置状态"""
    print(f"\n配置检查:")
    
    # 检查环境文件
    env_files = [".env", ".env.test", ".env.prod"]
    for env_file in env_files:
        exists = os.path.exists(env_file)
        print(f"  {env_file}: {'存在' if exists else '不存在'}")
    
    # 检查当前环境
    app_env = os.getenv("APP_ENV", "test")
    print(f"  当前环境: {app_env}")

def main():
    """主函数"""
    print("=== 分支数据库状态检查 ===\n")
    
    check_database_status()
    check_configuration()
    
    print(f"\n=== 建议 ===")
    branch_name = get_current_branch()
    
    if branch_name != "main":
        print(f"1. 当前在分支 {branch_name}，建议设置分支数据库:")
        print(f"   python scripts/branch_db_manager.py setup {branch_name}")
        print(f"")
        print(f"2. 设置环境变量:")
        print(f"   export BRANCH_NAME={branch_name}")
        print(f"")
        print(f"3. 运行迁移:")
        print(f"   python scripts/branch_db_manager.py migrate {branch_name}")
    else:
        print("1. 当前在主分支，使用主数据库")
        print("2. 确保环境变量 BRANCH_NAME 未设置或设置为 'main'")

if __name__ == "__main__":
    main()