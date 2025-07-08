# 多分支数据库开发最佳实践指南

## 概述

当多个分支同时进行数据库开发时，需要特别注意数据库迁移和版本控制，以避免冲突和数据不一致的问题。

## 当前项目配置

- **数据库类型**: SQLite
- **迁移工具**: Alembic
- **分支隔离**: 每个分支使用独立的数据库文件

## 最佳实践

### 1. 分支数据库隔离

每个分支使用独立的数据库文件，避免冲突：

```bash
# 设置当前分支的数据库
python scripts/branch_db_manager.py setup

# 或者指定分支名
python scripts/branch_db_manager.py setup feature-branch
```

### 2. 数据库操作类型分析

#### ✅ 安全的操作（添加）
- 创建新表
- 添加新字段
- 添加新索引
- 添加新约束（不影响现有数据）

#### ⚠️ 需要谨慎的操作（修改）
- 修改字段类型
- 修改字段约束
- 重命名字段
- 修改表结构

#### ❌ 高风险操作（删除）
- 删除表
- 删除字段
- 删除索引
- 修改主键

### 3. 迁移文件管理

#### 创建迁移文件
```bash
# 在分支上创建迁移
alembic revision --autogenerate -m "描述变更内容"

# 运行迁移
python scripts/branch_db_manager.py migrate
```

#### 合并迁移文件
当分支合并时，可能需要合并迁移文件：

```bash
# 合并迁移文件
alembic merge -m "merge branch changes" <revision1> <revision2>
```

### 4. 分支开发流程

#### 开始新分支
```bash
# 1. 创建新分支
git checkout -b feature-branch

# 2. 设置分支数据库
python scripts/branch_db_manager.py setup

# 3. 运行现有迁移
python scripts/branch_db_manager.py migrate
```

#### 开发过程中
```bash
# 1. 修改模型
# 2. 创建迁移文件
alembic revision --autogenerate -m "add new feature"

# 3. 运行迁移
python scripts/branch_db_manager.py migrate

# 4. 测试功能
```

#### 合并分支
```bash
# 1. 合并代码
git checkout main
git merge feature-branch

# 2. 合并数据库变更
python scripts/branch_db_manager.py merge feature-branch main

# 3. 运行迁移确保一致性
python scripts/branch_db_manager.py migrate main

# 4. 清理分支数据库
python scripts/branch_db_manager.py cleanup feature-branch
```

### 5. 常见问题和解决方案

#### 问题1: 迁移文件冲突
**症状**: 多个分支创建了相同名称的迁移文件

**解决方案**:
```bash
# 重命名迁移文件
mv migrations/versions/conflict_file.py migrations/versions/new_name.py

# 更新迁移文件中的revision ID
# 编辑迁移文件，确保revision ID唯一
```

#### 问题2: 数据库状态不一致
**症状**: 不同分支的数据库结构不同

**解决方案**:
```bash
# 重新同步数据库
python scripts/branch_db_manager.py setup
python scripts/branch_db_manager.py migrate
```

#### 问题3: 迁移顺序问题
**症状**: 迁移文件执行顺序错误

**解决方案**:
```bash
# 检查迁移历史
alembic history

# 手动调整迁移顺序
# 编辑迁移文件中的dependencies
```

### 6. 环境变量配置

在开发环境中设置分支名：

```bash
# 在 .env.test 文件中
BRANCH_NAME=feature-branch

# 或者在启动时设置
export BRANCH_NAME=feature-branch
python run.py
```

### 7. 测试策略

#### 单元测试
- 每个分支的测试使用对应的分支数据库
- 测试完成后清理测试数据

#### 集成测试
- 使用独立的测试数据库
- 测试数据库迁移的正确性

### 8. 部署注意事项

#### 开发环境
- 使用分支数据库进行测试
- 定期同步主分支的数据库结构

#### 生产环境
- 始终使用主数据库
- 部署前验证所有迁移文件
- 备份生产数据库

### 9. 监控和日志

#### 数据库变更日志
```python
# 在迁移文件中添加日志
import logging
logger = logging.getLogger(__name__)

def upgrade():
    logger.info("开始执行迁移: add new table")
    # 迁移代码
    logger.info("迁移完成")
```

#### 分支数据库状态监控
```bash
# 查看所有分支数据库
python scripts/branch_db_manager.py list
```

### 10. 紧急情况处理

#### 数据库损坏
```bash
# 从主分支恢复
python scripts/branch_db_manager.py setup
python scripts/branch_db_manager.py migrate
```

#### 迁移失败
```bash
# 回滚到上一个版本
alembic downgrade -1

# 修复迁移文件后重新执行
alembic upgrade +1
```

## 总结

通过遵循这些最佳实践，可以安全地在多个分支中进行数据库开发：

1. **隔离**: 每个分支使用独立数据库
2. **版本控制**: 使用Alembic管理迁移
3. **测试**: 充分测试数据库变更
4. **备份**: 定期备份重要数据
5. **监控**: 监控数据库状态和变更

这样可以最大程度地减少多分支开发中的数据库冲突问题。