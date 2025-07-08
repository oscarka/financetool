#!/usr/bin/env python3
"""
分支数据库管理脚本
用于管理多分支开发中的数据库操作
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def get_current_branch():
    """获取当前Git分支名"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "main"

def get_branch_db_path(branch_name):
    """获取分支数据库路径"""
    return f"./data/personalfinance_{branch_name}.db"

def setup_branch_database(branch_name):
    """为指定分支设置数据库"""
    db_path = get_branch_db_path(branch_name)
    main_db_path = "./data/personalfinance.db"
    
    # 确保data目录存在
    os.makedirs("./data", exist_ok=True)
    
    if branch_name == "main":
        print(f"主分支使用数据库: {main_db_path}")
        return
    
    # 如果主数据库存在，复制到分支数据库
    if os.path.exists(main_db_path):
        shutil.copy2(main_db_path, db_path)
        print(f"已复制主数据库到分支数据库: {db_path}")
    else:
        print(f"主数据库不存在，将创建新的分支数据库: {db_path}")
    
    # 设置环境变量
    os.environ["BRANCH_NAME"] = branch_name
    print(f"已设置环境变量 BRANCH_NAME={branch_name}")

def run_migrations(branch_name):
    """运行数据库迁移"""
    print(f"为分支 {branch_name} 运行数据库迁移...")
    
    # 设置环境变量
    os.environ["BRANCH_NAME"] = branch_name
    
    try:
        # 运行alembic迁移
        subprocess.run(['alembic', 'upgrade', 'head'], check=True)
        print("数据库迁移完成")
    except subprocess.CalledProcessError as e:
        print(f"数据库迁移失败: {e}")
        return False
    
    return True

def merge_branch_changes(source_branch, target_branch="main"):
    """合并分支的数据库变更到目标分支"""
    print(f"合并分支 {source_branch} 的变更到 {target_branch}...")
    
    source_db = get_branch_db_path(source_branch)
    target_db = get_branch_db_path(target_branch)
    
    if not os.path.exists(source_db):
        print(f"源分支数据库不存在: {source_db}")
        return False
    
    # 备份目标数据库
    if os.path.exists(target_db):
        backup_path = f"{target_db}.backup"
        shutil.copy2(target_db, backup_path)
        print(f"已备份目标数据库到: {backup_path}")
    
    # 复制源数据库到目标数据库
    shutil.copy2(source_db, target_db)
    print(f"已合并数据库变更")
    
    return True

def cleanup_branch_database(branch_name):
    """清理分支数据库"""
    if branch_name == "main":
        print("不能删除主分支数据库")
        return
    
    db_path = get_branch_db_path(branch_name)
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已删除分支数据库: {db_path}")
    else:
        print(f"分支数据库不存在: {db_path}")

def list_branch_databases():
    """列出所有分支数据库"""
    data_dir = Path("./data")
    if not data_dir.exists():
        print("data目录不存在")
        return
    
    databases = list(data_dir.glob("personalfinance_*.db"))
    if not databases:
        print("没有找到分支数据库")
        return
    
    print("现有的分支数据库:")
    for db in databases:
        size = db.stat().st_size
        print(f"  {db.name} ({size} bytes)")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python branch_db_manager.py setup [branch_name]  # 设置分支数据库")
        print("  python branch_db_manager.py migrate [branch_name]  # 运行迁移")
        print("  python branch_db_manager.py merge <source> [target]  # 合并分支变更")
        print("  python branch_db_manager.py cleanup [branch_name]  # 清理分支数据库")
        print("  python branch_db_manager.py list  # 列出所有分支数据库")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        branch_name = sys.argv[2] if len(sys.argv) > 2 else get_current_branch()
        setup_branch_database(branch_name)
    
    elif command == "migrate":
        branch_name = sys.argv[2] if len(sys.argv) > 2 else get_current_branch()
        run_migrations(branch_name)
    
    elif command == "merge":
        if len(sys.argv) < 3:
            print("请指定源分支名")
            return
        source_branch = sys.argv[2]
        target_branch = sys.argv[3] if len(sys.argv) > 3 else "main"
        merge_branch_changes(source_branch, target_branch)
    
    elif command == "cleanup":
        branch_name = sys.argv[2] if len(sys.argv) > 2 else get_current_branch()
        cleanup_branch_database(branch_name)
    
    elif command == "list":
        list_branch_databases()
    
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()