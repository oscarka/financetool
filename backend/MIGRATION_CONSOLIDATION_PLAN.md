# 数据库迁移整合详细计划

## 当前状态分析

### 迁移文件统计
- **总迁移文件数**: 18个
- **最早迁移**: `c56f9f034ac1_add_okx_tables.py` (OKX表)
- **最新迁移**: `ffcccccc0004_add_base_value_to_asset_snapshot.py` (资产快照基础值)
- **主要功能模块**: IBKR、Wise、OKX、Web3、DCA计划、基金、用户操作

### 迁移文件分类

#### 1. 核心业务表 (6个)
- `a1b2c3d4e5f6_add_ibkr_tables.py` - IBKR相关表
- `9b2fcf59ac80_add_wise_transactions_and_balances_.py` - Wise交易和余额表
- `c56f9f034ac1_add_okx_tables.py` - OKX基础表
- `8a343c129269_add_web3_tables.py` - Web3相关表
- `c6ea9ed77ea8_add_dca_plan_fields_and_user_operation_.py` - DCA计划和用户操作
- `94e7ccaad3b2_add_fund_dividend_table.py` - 基金分红表

#### 2. 功能增强迁移 (8个)
- `033880ebf93b_add_okx_account_overview_table.py` - OKX账户总览
- `04f8249fc418_add_fee_rate_to_dca_plans.py` - DCA计划手续费
- `843fdae84b37_add_nav_field_to_user_operations.py` - 用户操作净值字段
- `9ab46480ba00_fix_okx_market_data_precision.py` - OKX市场数据精度修复
- `a75b8ab8d7ec_add_asset_type_to_dca_plans_table.py` - DCA计划资产类型
- `f9adc45cf4ec_add_exclude_dates_to_dca_plans.py` - DCA计划排除日期
- `ff5423642f10_add_wise_primary_secondary_amount_fields.py` - Wise主次金额字段
- `ffaaaaaa0000_add_incremental_okx_and_wise_balance.py` - 增量OKX和Wise余额

#### 3. 数据修复迁移 (2个)
- `1c00ade64ab5_fix_wise_tables_structure.py` - Wise表结构修复
- `ffcccccc0002_remove_wise_balance_account_id_unique_index.py` - 移除Wise余额唯一索引

#### 4. 新增功能迁移 (2个)
- `ffcccccc0003_add_asset_and_exchange_rate_snapshot.py` - 资产和汇率快照
- `ffcccccc0004_add_base_value_to_asset_snapshot.py` - 资产快照基础值

## 整合方案详细步骤

### 方案A：完全整合（推荐）

#### 第一步：环境准备
```bash
# 1. 进入backend目录
cd backend

# 2. 检查当前数据库状态
alembic current

# 3. 检查所有迁移历史
alembic history
```

#### 第二步：数据备份
```bash
# 1. 创建备份目录
mkdir -p backups/migrations_$(date +%Y%m%d_%H%M%S)

# 2. 备份所有迁移文件
cp migrations/versions/*.py backups/migrations_$(date +%Y%m%d_%H%M%S)/

# 3. 备份数据库数据（通过API）
python pre_deploy_backup.py
```

#### 第三步：创建整合脚本
创建文件：`backend/consolidate_migrations.py`

```python
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
```

#### 第四步：Railway部署配置

修改 `railway.toml`:
```toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile"

[deploy]
startCommand = "cd backend && python consolidate_migrations.py consolidate && python run.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[deploy.environment]
PORT = "8000"
DEBUG = "false"
WORKERS = "1"
APP_ENV = "prod"

# 添加数据卷配置
[[deploy.volumes]]
source = "database"
target = "/app/data"
```

#### 第五步：数据备份脚本

创建文件：`backend/backup_critical_data.py`

```python
#!/usr/bin/env python3
"""
关键数据备份脚本
在整合迁移前备份重要数据
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

class CriticalDataBackup:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.service_url = os.getenv('RAILWAY_SERVICE_URL')
        
    def backup_table_data(self, table_name, endpoint):
        """备份单个表的数据"""
        try:
            if not self.service_url:
                print(f"⚠️  未设置RAILWAY_SERVICE_URL，跳过 {table_name}")
                return []
            
            response = requests.get(f"{self.service_url}{endpoint}?limit=10000", timeout=30)
            if response.status_code == 200:
                data = response.json()
                records = data.get('data', [])
                print(f"✅ 备份 {table_name}: {len(records)} 条记录")
                return records
            else:
                print(f"⚠️  备份 {table_name} 失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️  备份 {table_name} 异常: {e}")
            return []
    
    def backup_all_critical_data(self):
        """备份所有关键数据"""
        print("🔄 开始备份关键数据...")
        
        critical_tables = [
            ("user_operations", "/api/v1/operations"),
            ("asset_positions", "/api/v1/positions"),
            ("fund_info", "/api/v1/funds"),
            ("dca_plans", "/api/v1/dca-plans"),
            ("wise_transactions", "/api/v1/wise/transactions"),
            ("wise_balances", "/api/v1/wise/balances"),
            ("ibkr_accounts", "/api/v1/ibkr/accounts"),
            ("ibkr_balances", "/api/v1/ibkr/balances"),
            ("ibkr_positions", "/api/v1/ibkr/positions"),
            ("okx_balances", "/api/v1/okx/balances"),
            ("okx_transactions", "/api/v1/okx/transactions"),
            ("okx_positions", "/api/v1/okx/positions"),
            ("web3_balances", "/api/v1/web3/balances"),
            ("web3_tokens", "/api/v1/web3/tokens"),
            ("asset_snapshots", "/api/v1/snapshots"),
            ("exchange_rates", "/api/v1/exchange-rates"),
            ("system_config", "/api/v1/system/config")
        ]
        
        backup_data = {
            "backup_time": datetime.now().isoformat(),
            "consolidation_type": "migration_consolidation",
            "total_tables": len(critical_tables)
        }
        
        total_records = 0
        for table_name, endpoint in critical_tables:
            records = self.backup_table_data(table_name, endpoint)
            backup_data[table_name] = records
            total_records += len(records)
        
        backup_data["total_records"] = total_records
        
        # 保存备份文件
        backup_file = self.backup_dir / f"critical_data_backup_{self.timestamp}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 关键数据备份完成: {backup_file}")
        print(f"📊 总计备份: {len(critical_tables)} 个表, {total_records} 条记录")
        return str(backup_file)

def main():
    backup = CriticalDataBackup()
    backup.backup_all_critical_data()

if __name__ == "__main__":
    main()
```

#### 第六步：数据恢复脚本

创建文件：`backend/restore_critical_data.py`

```python
#!/usr/bin/env python3
"""
关键数据恢复脚本
在整合迁移后恢复重要数据
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

class CriticalDataRestore:
    def __init__(self):
        self.service_url = os.getenv('RAILWAY_SERVICE_URL')
        
    def restore_table_data(self, table_name, endpoint, data):
        """恢复单个表的数据"""
        try:
            if not self.service_url:
                print(f"⚠️  未设置RAILWAY_SERVICE_URL，跳过 {table_name}")
                return True
            
            restored_count = 0
            for record in data:
                # 移除自动生成字段
                for field in ['id', 'created_at', 'updated_at']:
                    if field in record:
                        del record[field]
                
                response = requests.post(f"{self.service_url}{endpoint}", json=record, timeout=30)
                if response.status_code in [200, 201]:
                    restored_count += 1
                else:
                    print(f"⚠️  恢复记录失败: {response.status_code} - {response.text}")
            
            print(f"✅ 恢复 {table_name}: {restored_count}/{len(data)} 条记录")
            return True
        except Exception as e:
            print(f"⚠️  恢复 {table_name} 异常: {e}")
            return False
    
    def restore_from_backup(self, backup_file):
        """从备份文件恢复数据"""
        print(f"🔄 从备份文件恢复数据: {backup_file}")
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            endpoint_map = {
                "user_operations": "/api/v1/operations",
                "asset_positions": "/api/v1/positions",
                "fund_info": "/api/v1/funds",
                "dca_plans": "/api/v1/dca-plans",
                "wise_transactions": "/api/v1/wise/transactions",
                "wise_balances": "/api/v1/wise/balances",
                "ibkr_accounts": "/api/v1/ibkr/accounts",
                "ibkr_balances": "/api/v1/ibkr/balances",
                "ibkr_positions": "/api/v1/ibkr/positions",
                "okx_balances": "/api/v1/okx/balances",
                "okx_transactions": "/api/v1/okx/transactions",
                "okx_positions": "/api/v1/okx/positions",
                "web3_balances": "/api/v1/web3/balances",
                "web3_tokens": "/api/v1/web3/tokens",
                "asset_snapshots": "/api/v1/snapshots",
                "exchange_rates": "/api/v1/exchange-rates",
                "system_config": "/api/v1/system/config"
            }
            
            total_restored = 0
            for table_name, data in backup_data.items():
                if table_name in ['backup_time', 'consolidation_type', 'total_tables', 'total_records']:
                    continue
                
                if table_name in endpoint_map and data:
                    endpoint = endpoint_map[table_name]
                    if self.restore_table_data(table_name, endpoint, data):
                        total_restored += len(data)
            
            print(f"✅ 数据恢复完成，总计恢复: {total_restored} 条记录")
            return True
            
        except Exception as e:
            print(f"❌ 数据恢复失败: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("❌ 请指定备份文件路径")
        print("用法: python restore_critical_data.py <backup_file>")
        return
    
    backup_file = sys.argv[1]
    restore = CriticalDataRestore()
    restore.restore_from_backup(backup_file)

if __name__ == "__main__":
    main()
```

### 方案B：选择性整合

如果方案A风险太大，可以选择性保留一些重要迁移：

#### 保留的迁移文件（6个核心迁移）
1. `a1b2c3d4e5f6_add_ibkr_tables.py` - IBKR核心表
2. `9b2fcf59ac80_add_wise_transactions_and_balances_.py` - Wise核心表
3. `c56f9f034ac1_add_okx_tables.py` - OKX核心表
4. `8a343c129269_add_web3_tables.py` - Web3核心表
5. `c6ea9ed77ea8_add_dca_plan_fields_and_user_operation_.py` - DCA和用户操作
6. `ffcccccc0003_add_asset_and_exchange_rate_snapshot.py` - 资产快照

#### 删除的迁移文件（12个小改动）
- 所有功能增强迁移
- 数据修复迁移
- 新增功能迁移

### 执行时间表

#### 准备阶段（1-2天）
1. 在测试环境验证整合流程
2. 准备备份和恢复脚本
3. 通知团队成员

#### 执行阶段（1天）
1. 生产环境数据备份
2. 执行迁移整合
3. 验证数据完整性

#### 验证阶段（1-2天）
1. 功能测试
2. 数据验证
3. 性能测试

### 风险评估和应对措施

#### 高风险操作
1. **删除迁移文件**
   - 风险：无法回滚到特定版本
   - 应对：完整备份所有迁移文件

2. **数据丢失**
   - 风险：整合过程中数据丢失
   - 应对：多重备份策略

#### 中风险操作
1. **数据库状态不一致**
   - 风险：迁移标记与实际状态不符
   - 应对：使用 `alembic stamp head` 重新标记

#### 低风险操作
1. **创建新迁移文件**
   - 风险：新迁移可能有问题
   - 应对：在测试环境验证

### 回滚方案

如果整合过程中出现问题：

#### 立即回滚
```bash
# 1. 恢复原始迁移文件
cp backups/migrations_YYYYMMDD_HHMMSS/*.py migrations/versions/

# 2. 重新标记迁移
alembic stamp <last_working_revision>

# 3. 恢复数据
python restore_critical_data.py backups/critical_data_backup_YYYYMMDD_HHMMSS.json
```

#### 完全回滚
```bash
# 1. 回滚到上一个Railway部署
# 2. 恢复数据库备份
# 3. 重新部署应用
```

### 验证清单

#### 整合前验证
- [ ] 数据库连接正常
- [ ] 所有API端点正常
- [ ] 数据备份完成
- [ ] 迁移文件备份完成

#### 整合后验证
- [ ] 数据库结构正确
- [ ] 所有表都存在
- [ ] 数据完整性检查
- [ ] API功能正常
- [ ] 应用启动正常

#### 功能测试
- [ ] IBKR数据同步
- [ ] Wise数据同步
- [ ] OKX数据同步
- [ ] Web3数据同步
- [ ] DCA计划功能
- [ ] 用户操作记录
- [ ] 资产快照功能

这个详细方案是否满足您的需求？我可以根据您的具体情况进行调整。