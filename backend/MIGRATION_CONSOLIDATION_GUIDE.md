# 数据库迁移整合执行指南

## 概述

本指南将帮助您安全地整合18个数据库迁移文件，将它们合并成一个初始迁移文件，以简化数据库版本管理。

## 当前状态

- **迁移文件数量**: 18个
- **主要功能模块**: IBKR、Wise、OKX、Web3、DCA计划、基金、用户操作
- **整合目标**: 创建1个初始迁移文件

## 执行前准备

### 1. 环境检查

```bash
# 进入backend目录
cd backend

# 检查数据库连接
alembic current

# 检查迁移历史
alembic history

# 检查当前迁移文件
ls -la migrations/versions/
```

### 2. 数据备份

```bash
# 备份关键数据
python backup_critical_data.py

# 检查备份文件
ls -la backups/
```

### 3. 迁移文件备份

```bash
# 备份现有迁移文件
python consolidate_migrations.py backup

# 检查备份
ls -la backups/migrations_*/
```

## 执行步骤

### 方案A：完全整合（推荐）

#### 第一步：测试环境验证

```bash
# 1. 在测试环境执行整合
python consolidate_migrations.py consolidate

# 2. 验证整合结果
python consolidate_migrations.py verify

# 3. 检查新迁移文件
ls -la migrations/versions/
```

#### 第二步：生产环境执行

```bash
# 1. 确保在backend目录
cd backend

# 2. 执行完整整合流程
python consolidate_migrations.py consolidate

# 3. 验证结果
python consolidate_migrations.py verify
```

#### 第三步：Railway部署

修改 `railway.toml` 中的启动命令：

```toml
[deploy]
startCommand = "python backup_critical_data.py && python consolidate_migrations.py consolidate && python run.py"
```

### 方案B：选择性整合

如果完全整合风险太大，可以选择性保留核心迁移：

#### 保留的迁移文件（6个）
1. `a1b2c3d4e5f6_add_ibkr_tables.py` - IBKR核心表
2. `9b2fcf59ac80_add_wise_transactions_and_balances_.py` - Wise核心表
3. `c56f9f034ac1_add_okx_tables.py` - OKX核心表
4. `8a343c129269_add_web3_tables.py` - Web3核心表
5. `c6ea9ed77ea8_add_dca_plan_fields_and_user_operation_.py` - DCA和用户操作
6. `ffcccccc0003_add_asset_and_exchange_rate_snapshot.py` - 资产快照

#### 删除的迁移文件（12个）
- 所有功能增强迁移
- 数据修复迁移
- 新增功能迁移

## 验证清单

### 整合前验证
- [ ] 数据库连接正常
- [ ] 所有API端点正常
- [ ] 数据备份完成
- [ ] 迁移文件备份完成
- [ ] 测试环境验证通过

### 整合后验证
- [ ] 数据库结构正确
- [ ] 所有表都存在
- [ ] 数据完整性检查
- [ ] API功能正常
- [ ] 应用启动正常

### 功能测试
- [ ] IBKR数据同步
- [ ] Wise数据同步
- [ ] OKX数据同步
- [ ] Web3数据同步
- [ ] DCA计划功能
- [ ] 用户操作记录
- [ ] 资产快照功能

## 回滚方案

### 立即回滚

如果整合过程中出现问题：

```bash
# 1. 恢复原始迁移文件
cp backups/migrations_YYYYMMDD_HHMMSS/*.py migrations/versions/

# 2. 重新标记迁移
alembic stamp <last_working_revision>

# 3. 恢复数据（如果需要）
python restore_critical_data.py backups/critical_data_backup_YYYYMMDD_HHMMSS.json
```

### 完全回滚

```bash
# 1. 回滚到上一个Railway部署
# 2. 恢复数据库备份
# 3. 重新部署应用
```

## 脚本说明

### consolidate_migrations.py

主要功能：
- `check`: 检查数据库状态
- `backup`: 备份现有迁移文件
- `consolidate`: 执行完整整合流程
- `verify`: 验证整合结果

### backup_critical_data.py

功能：
- 备份所有关键表的数据
- 通过API接口获取数据
- 保存为JSON格式

### restore_critical_data.py

功能：
- 从备份文件恢复数据
- 通过API接口恢复数据
- 自动处理字段映射

## 注意事项

### 高风险操作
1. **删除迁移文件**: 无法回滚到特定版本
2. **数据丢失**: 整合过程中可能丢失数据
3. **数据库状态不一致**: 迁移标记与实际状态不符

### 安全措施
1. **多重备份**: 迁移文件备份 + 数据备份
2. **测试环境验证**: 先在测试环境执行
3. **分步执行**: 不要一次性执行所有操作
4. **监控验证**: 整合后验证数据完整性

## 执行时间表

### 准备阶段（1-2天）
1. 在测试环境验证整合流程
2. 准备备份和恢复脚本
3. 通知团队成员

### 执行阶段（1天）
1. 生产环境数据备份
2. 执行迁移整合
3. 验证数据完整性

### 验证阶段（1-2天）
1. 功能测试
2. 数据验证
3. 性能测试

## 联系信息

如果在执行过程中遇到问题，请：

1. 检查日志文件
2. 查看备份文件
3. 参考回滚方案
4. 联系技术支持

## 成功标准

整合成功的标志：

1. ✅ 只有一个初始迁移文件
2. ✅ 所有表结构正确
3. ✅ 数据完整性保持
4. ✅ 所有功能正常工作
5. ✅ 应用启动正常
6. ✅ 性能无显著下降

---

**重要提醒**: 在执行整合前，请确保已经充分测试并备份了所有重要数据。整合过程是不可逆的，请谨慎操作。