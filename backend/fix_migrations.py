#!/usr/bin/env python3
"""
数据库迁移修复脚本
解决重复迁移文件和空迁移文件的问题
"""

import os
import sqlite3
from pathlib import Path

def check_database_schema():
    """检查数据库当前状态"""
    db_path = "data/personalfinance.db"
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 alembic_version 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        if cursor.fetchone():
            cursor.execute("SELECT version_num FROM alembic_version")
            current_version = cursor.fetchone()
            print(f"当前迁移版本: {current_version[0] if current_version else 'None'}")
        else:
            print("alembic_version 表不存在")
        
        # 检查 user_operations 表结构
        cursor.execute("PRAGMA table_info(user_operations)")
        columns = cursor.fetchall()
        nav_column_exists = any(col[1] == 'nav' for col in columns)
        print(f"user_operations 表 nav 字段存在: {nav_column_exists}")
        
        # 检查 wise_exchange_rates 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wise_exchange_rates'")
        wise_table_exists = cursor.fetchone() is not None
        print(f"wise_exchange_rates 表存在: {wise_table_exists}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

def list_migration_files():
    """列出所有迁移文件"""
    migrations_dir = Path("migrations/versions")
    if not migrations_dir.exists():
        print("migrations/versions 目录不存在")
        return []
    
    migration_files = []
    for file in migrations_dir.glob("*.py"):
        if file.name != "__init__.py":
            migration_files.append(file.name)
    
    migration_files.sort()
    print("迁移文件列表:")
    for file in migration_files:
        print(f"  - {file}")
    
    return migration_files

def analyze_migration_dependencies():
    """分析迁移依赖关系"""
    migrations_dir = Path("migrations/versions")
    dependencies = {}
    
    for file in migrations_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
            
        with open(file, 'r') as f:
            content = f.read()
            
        # 提取 revision ID
        revision_line = None
        revises_line = None
        
        for line in content.split('\n'):
            if 'revision: str =' in line:
                revision_line = line.strip()
            elif 'down_revision:' in line:
                revises_line = line.strip()
        
        if revision_line and revises_line:
            revision = revision_line.split("'")[1]
            revises_part = revises_line.split("'")
            revises = revises_part[1] if len(revises_part) > 1 else None
            dependencies[file.name] = {
                'revision': revision,
                'revises': revises,
                'is_empty': 'pass' in content and len(content.strip()) < 200
            }
    
    print("\n迁移依赖分析:")
    for file, info in dependencies.items():
        status = "空" if info['is_empty'] else "正常"
        print(f"  {file}: {info['revision']} -> {info['revises']} ({status})")
    
    return dependencies

def identify_problems(dependencies):
    """识别迁移问题"""
    print("\n发现的问题:")
    
    # 检查重复的 nav 字段迁移
    nav_migrations = []
    for file, info in dependencies.items():
        if 'nav_field_to_user_operations' in file:
            nav_migrations.append((file, info))
    
    if len(nav_migrations) > 1:
        print("1. 重复的 nav 字段迁移:")
        for file, info in nav_migrations:
            status = "空" if info['is_empty'] else "正常"
            print(f"   - {file} ({status})")
    
    # 检查空迁移
    empty_migrations = []
    for file, info in dependencies.items():
        if info['is_empty']:
            empty_migrations.append(file)
    
    if empty_migrations:
        print("2. 空的迁移文件:")
        for file in empty_migrations:
            print(f"   - {file}")
    
    # 检查分支
    revises_count = {}
    for file, info in dependencies.items():
        if info['revises']:
            revises_count[info['revises']] = revises_count.get(info['revises'], 0) + 1
    
    branches = {rev: count for rev, count in revises_count.items() if count > 1}
    if branches:
        print("3. 迁移分支:")
        for rev, count in branches.items():
            print(f"   - {rev} 被 {count} 个迁移依赖")

def main():
    """主函数"""
    print("=== 数据库迁移问题诊断 ===\n")
    
    # 检查数据库状态
    print("1. 检查数据库状态:")
    check_database_schema()
    
    # 列出迁移文件
    print("\n2. 迁移文件列表:")
    migration_files = list_migration_files()
    
    # 分析依赖关系
    print("\n3. 迁移依赖分析:")
    dependencies = analyze_migration_dependencies()
    
    # 识别问题
    print("\n4. 问题识别:")
    identify_problems(dependencies)
    
    print("\n=== 诊断完成 ===")
    print("\n建议的修复步骤:")
    print("1. 删除空的迁移文件")
    print("2. 删除重复的迁移文件")
    print("3. 重新整理迁移链")
    print("4. 运行 alembic upgrade 应用修复后的迁移")

if __name__ == "__main__":
    main()