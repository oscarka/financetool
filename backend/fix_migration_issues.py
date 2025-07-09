#!/usr/bin/env python3
"""
数据库迁移问题修复脚本
"""

import os
import shutil
from pathlib import Path

def backup_migrations():
    """备份迁移文件"""
    backup_dir = Path("migrations_backup")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    shutil.copytree("migrations", backup_dir)
    print(f"迁移文件已备份到: {backup_dir}")

def fix_migration_issues():
    """修复迁移问题"""
    migrations_dir = Path("migrations/versions")
    
    # 1. 删除重复的 nav 字段迁移（保留有实际内容的那个）
    nav_migrations = []
    for file in migrations_dir.glob("*nav_field_to_user_operations.py"):
        nav_migrations.append(file)
    
    if len(nav_migrations) == 2:
        # 检查哪个是空的
        empty_migration = None
        valid_migration = None
        
        for file in nav_migrations:
            with open(file, 'r') as f:
                content = f.read()
                if 'pass' in content and len(content.strip()) < 200:
                    empty_migration = file
                else:
                    valid_migration = file
        
        if empty_migration and valid_migration:
            print(f"删除空的迁移文件: {empty_migration.name}")
            empty_migration.unlink()
            
            # 更新依赖关系
            update_dependencies(empty_migration.name, valid_migration.name)
    
    # 2. 删除空的 wise_exchange_rates 迁移
    wise_migration = migrations_dir / "4d412d44dc3e_add_wise_exchange_rates_table.py"
    if wise_migration.exists():
        with open(wise_migration, 'r') as f:
            content = f.read()
            if 'pass' in content and len(content.strip()) < 200:
                print(f"删除空的迁移文件: {wise_migration.name}")
                wise_migration.unlink()
                
                # 更新依赖关系
                update_dependencies(wise_migration.name, "9b2fcf59ac80")

def update_dependencies(deleted_migration, new_parent):
    """更新迁移依赖关系"""
    migrations_dir = Path("migrations/versions")
    
    # 找到所有依赖被删除迁移的文件
    for file in migrations_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
            
        with open(file, 'r') as f:
            content = f.read()
        
        # 检查是否依赖被删除的迁移
        if f"Revises: {deleted_migration.split('_')[0]}" in content:
            print(f"更新依赖关系: {file.name} -> {new_parent}")
            
            # 更新文件内容
            new_content = content.replace(
                f"Revises: {deleted_migration.split('_')[0]}",
                f"Revises: {new_parent}"
            )
            new_content = new_content.replace(
                f"down_revision: Union[str, Sequence[str], None] = '{deleted_migration.split('_')[0]}'",
                f"down_revision: Union[str, Sequence[str], None] = '{new_parent}'"
            )
            
            with open(file, 'w') as f:
                f.write(new_content)

def verify_fixes():
    """验证修复结果"""
    print("\n验证修复结果:")
    
    migrations_dir = Path("migrations/versions")
    
    # 检查是否还有重复的 nav 迁移
    nav_migrations = list(migrations_dir.glob("*nav_field_to_user_operations.py"))
    if len(nav_migrations) == 1:
        print("✓ 重复的 nav 迁移已修复")
    else:
        print(f"✗ 仍有 {len(nav_migrations)} 个 nav 迁移文件")
    
    # 检查是否还有空的迁移
    empty_migrations = []
    for file in migrations_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
        with open(file, 'r') as f:
            content = f.read()
            if 'pass' in content and len(content.strip()) < 200:
                empty_migrations.append(file.name)
    
    if not empty_migrations:
        print("✓ 空的迁移文件已清理")
    else:
        print(f"✗ 仍有空的迁移文件: {empty_migrations}")
    
    # 检查分支
    dependencies = {}
    for file in migrations_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
        with open(file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'down_revision:' in line and "'" in line:
                    revises = line.split("'")[1]
                    if revises != 'None':
                        dependencies[file.name] = revises
                    break
    
    revises_count = {}
    for revises in dependencies.values():
        revises_count[revises] = revises_count.get(revises, 0) + 1
    
    branches = {rev: count for rev, count in revises_count.items() if count > 1}
    if not branches:
        print("✓ 迁移分支已修复")
    else:
        print(f"✗ 仍有迁移分支: {branches}")

def main():
    """主函数"""
    print("=== 开始修复数据库迁移问题 ===\n")
    
    # 备份迁移文件
    print("1. 备份迁移文件...")
    backup_migrations()
    
    # 修复问题
    print("\n2. 修复迁移问题...")
    fix_migration_issues()
    
    # 验证修复
    print("\n3. 验证修复结果...")
    verify_fixes()
    
    print("\n=== 修复完成 ===")
    print("\n下一步操作:")
    print("1. 检查修复后的迁移文件")
    print("2. 运行 alembic upgrade 应用迁移")
    print("3. 如果出现问题，可以从 migrations_backup 恢复")

if __name__ == "__main__":
    main()