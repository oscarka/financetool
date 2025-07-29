#!/usr/bin/env python3
"""
数据库迁移整合脚本
将18个迁移文件整合成一个初始迁移
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class MigrationConsolidator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backups/migrations_{self.timestamp}")
        self.migrations_dir = Path("migrations/versions")
        
    def backup_existing_migrations(self):
        """备份现有迁移文件"""
        print("🔄 备份现有迁移文件...")
        
        # 创建备份目录
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制所有迁移文件
        for file in self.migrations_dir.glob("*.py"):
            if file.name != "__init__.py":
                shutil.copy2(file, self.backup_dir / file.name)
        
        print(f"✅ 迁移文件已备份到: {self.backup_dir}")
        return True
    
    def check_database_status(self):
        """检查数据库状态"""
        print("🔄 检查数据库状态...")
        
        try:
            result = subprocess.run(["alembic", "current"], 
                                  capture_output=True, text=True, check=True)
            current_revision = result.stdout.strip()
            print(f"✅ 当前数据库版本: {current_revision}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 数据库状态检查失败: {e.stderr}")
            return False
    
    def delete_existing_migrations(self):
        """删除现有迁移文件"""
        print("🔄 删除现有迁移文件...")
        
        deleted_count = 0
        for file in self.migrations_dir.glob("*.py"):
            if file.name != "__init__.py":
                file.unlink()
                deleted_count += 1
        
        print(f"✅ 删除了 {deleted_count} 个迁移文件")
        return True
    
    def create_consolidated_migration(self):
        """创建整合的初始迁移"""
        print("🔄 创建整合迁移文件...")
        
        try:
            result = subprocess.run([
                "alembic", "revision", "--autogenerate", 
                "-m", "initial_schema_consolidated"
            ], capture_output=True, text=True, check=True)
            
            print("✅ 创建整合迁移文件成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 创建整合迁移失败: {e.stderr}")
            return False
    
    def stamp_migration(self):
        """标记迁移为已应用"""
        print("🔄 标记迁移为已应用...")
        
        try:
            result = subprocess.run(["alembic", "stamp", "head"], 
                                  capture_output=True, text=True, check=True)
            print("✅ 标记迁移成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 标记迁移失败: {e.stderr}")
            return False
    
    def verify_consolidation(self):
        """验证整合结果"""
        print("🔄 验证整合结果...")
        
        try:
            # 检查迁移状态
            result = subprocess.run(["alembic", "current"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ 当前迁移版本: {result.stdout.strip()}")
            
            # 检查迁移历史
            result = subprocess.run(["alembic", "history"], 
                                  capture_output=True, text=True, check=True)
            print("✅ 迁移历史验证成功")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 验证失败: {e.stderr}")
            return False
    
    def run_consolidation(self):
        """执行完整的整合流程"""
        print("🚀 开始数据库迁移整合流程...")
        print(f"📅 整合时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        steps = [
            ("检查数据库状态", self.check_database_status),
            ("备份现有迁移", self.backup_existing_migrations),
            ("删除现有迁移", self.delete_existing_migrations),
            ("创建整合迁移", self.create_consolidated_migration),
            ("标记迁移", self.stamp_migration),
            ("验证整合结果", self.verify_consolidation)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 步骤: {step_name}")
            if not step_func():
                print(f"❌ {step_name} 失败，停止整合流程")
                return False
        
        print("\n✅ 数据库迁移整合完成！")
        print(f"📁 原迁移文件备份在: {self.backup_dir}")
        return True

def main():
    consolidator = MigrationConsolidator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            consolidator.check_database_status()
        elif command == "backup":
            consolidator.backup_existing_migrations()
        elif command == "consolidate":
            consolidator.run_consolidation()
        elif command == "verify":
            consolidator.verify_consolidation()
        else:
            print("❌ 未知命令。可用命令: check, backup, consolidate, verify")
    else:
        print("""
数据库迁移整合工具

用法:
  python consolidate_migrations.py check      # 检查数据库状态
  python consolidate_migrations.py backup     # 备份现有迁移
  python consolidate_migrations.py consolidate # 执行完整整合流程
  python consolidate_migrations.py verify     # 验证整合结果

注意: 整合流程会删除所有现有迁移文件并创建新的初始迁移
        """)

if __name__ == "__main__":
    main()