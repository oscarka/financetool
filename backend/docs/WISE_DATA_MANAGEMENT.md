# Wise数据管理架构

## 📋 概述

Wise数据管理模块统一管理所有与Wise汇率相关的数据库维护、检查和诊断功能。

## 🏗️ 架构设计

### 核心模块
- **`app/utils/wise_data_manager.py`** - 统一的数据管理类
- **`check_wise_data.py`** - 命令行检查工具
- **`run.py`** - 启动时可选维护功能

### 功能整合
- ✅ 序列修复
- ✅ 重复记录清理
- ✅ 数据状态检查
- ✅ 问题诊断
- ✅ 维护任务

## 🚀 使用方法

### 1. 命令行检查
```bash
# 检查数据状态
python check_wise_data.py

# 使用管理模块
python -m app.utils.wise_data_manager --action check
python -m app.utils.wise_data_manager --action maintenance
python -m app.utils.wise_data_manager --action fix-sequence
python -m app.utils.wise_data_manager --action clean-duplicates
```

### 2. 启动时维护
```bash
# 启用启动时维护
RUN_WISE_MAINTENANCE=true python run.py
```

### 3. 编程接口
```python
from app.utils.wise_data_manager import WiseDataManager

# 创建管理器
manager = WiseDataManager()

# 运行维护
result = manager.run_maintenance()

# 检查状态
status = manager.check_data_status()

# 获取摘要
summary = manager.get_data_summary()
```

## 🔧 功能说明

### 序列修复
- 修复PostgreSQL自增序列与表中最大ID不匹配的问题
- 适用于数据迁移、手动插入等场景

### 重复记录清理
- 检查并清理相同币种对和时间的重复记录
- 保留ID最小的记录，删除其他重复

### 数据状态检查
- 检查表是否存在
- 统计记录数和币种对分布
- 分析时间范围和数据新鲜度
- 自动诊断问题并提供建议

### 维护任务
- 统一执行所有维护操作
- 提供详细的执行结果报告

## 📊 检查内容

### 基础检查
- ✅ 表结构存在性
- 📊 总记录数统计
- 🏦 币种对分布分析

### 时间分析
- ⏰ 数据时间范围
- 📅 最近7天数据量
- 🔍 各币种对最新记录

### 问题诊断
- ❌ 数据缺失问题
- ⚠️ 数据不完整问题
- 🔧 自动问题识别
- 💡 修复建议

## 🛠️ 环境配置

### 必需环境变量
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
```

### 可选环境变量
```bash
# 启用启动时维护
RUN_WISE_MAINTENANCE=true

# 自定义数据库URL
DATABASE_URL=postgresql://custom_url
```

## 📈 监控集成

### 健康检查
```bash
# 返回状态码
python check_wise_data.py
echo $?  # 0=正常, 1=异常
```

### 日志输出
- 使用loguru进行结构化日志
- 支持不同日志级别
- 便于监控系统集成

## 🔄 迁移历史

### 从分散代码到统一模块
- **之前**: 代码分散在 `run.py` 和独立脚本中
- **现在**: 统一在 `WiseDataManager` 类中
- **优势**: 更好的维护性、可测试性和可扩展性

### 启动时维护优化
- **之前**: 每次启动都执行维护
- **现在**: 可选执行，通过环境变量控制
- **优势**: 避免不必要的启动延迟

## 🚨 故障排除

### 常见问题

1. **序列不同步**
   ```bash
   python -m app.utils.wise_data_manager --action fix-sequence
   ```

2. **重复记录**
   ```bash
   python -m app.utils.wise_data_manager --action clean-duplicates
   ```

3. **数据状态异常**
   ```bash
   python check_wise_data.py
   ```

### 调试模式
```bash
# 启用详细日志
LOGURU_LEVEL=DEBUG python check_wise_data.py
```

## 📝 开发指南

### 添加新功能
1. 在 `WiseDataManager` 类中添加新方法
2. 更新命令行参数解析
3. 添加相应的测试
4. 更新文档

### 测试
```bash
# 运行单元测试
python -m pytest tests/test_wise_data_manager.py

# 运行集成测试
python check_wise_data.py
```

## 🔮 未来计划

- [ ] 添加数据备份功能
- [ ] 支持更多数据源
- [ ] 添加性能监控
- [ ] 集成告警系统
- [ ] 支持批量操作 