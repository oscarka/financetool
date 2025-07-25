# 调度器配置指南

## 📋 概述

本指南将帮助你使用新的调度器界面配置各种定时任务，包括每天、每周、每月的任务调度。

## 🎯 配置步骤

### 1. 访问调度器管理页面

1. 打开你的应用
2. 导航到"调度管理"页面
3. 点击"创建任务"按钮

### 2. 选择任务类型

在"选择任务"下拉菜单中选择要执行的任务：

#### 核心任务（推荐优先配置）
- **基金净值更新** (`fund_nav_update`) - 更新基金净值数据
- **Wise余额同步** (`wise_balance_sync`) - 同步Wise账户余额
- **IBKR余额同步** (`ibkr_balance_sync`) - 同步IBKR账户余额
- **定投计划执行** (`dca_execute`) - 执行定投计划

#### 扩展任务（根据需要配置）
- **OKX余额同步** (`okx_balance_sync`) - 同步OKX账户余额
- **Wise交易同步** (`wise_transaction_sync`) - 同步Wise交易记录
- **基金持仓同步** (`fund_position_sync`) - 同步基金持仓数据

#### 维护任务（建议配置）
- **数据清理** (`data_cleanup`) - 清理过期数据
- **数据备份** (`data_backup`) - 备份重要数据
- **报表生成** (`report_generation`) - 生成投资报表

### 3. 配置调度类型

#### 间隔执行（Interval）
适用于需要定期重复执行的任务：

- **分钟间隔**：设置执行间隔的分钟数（1-59）
- **秒间隔**：设置执行间隔的秒数（0-59，可选）

**示例配置：**
- 每30分钟执行一次：分钟间隔 = 30
- 每4小时执行一次：分钟间隔 = 240
- 每1小时执行一次：分钟间隔 = 60

#### Cron表达式（Cron）
适用于需要精确时间控制的任务：

选择**执行频率**：

##### 每天（Daily）
- **小时**：设置执行的小时（0-23）
- **分钟**：设置执行的分钟（0-59）

**推荐配置：**
- 基金净值更新：15:30（基金收盘后）
- Wise余额同步：16:00
- IBKR余额同步：17:00（美股开盘前）
- 定投计划执行：09:00

##### 每周（Weekly）
- **星期几**：选择执行的星期
- **小时**：设置执行的小时（0-23）
- **分钟**：设置执行的分钟（0-59）

**推荐配置：**
- 数据清理：星期日 02:00
- 数据备份：星期六 03:00

##### 每月（Monthly）
- **日期**：设置执行的日期（1-31）
- **小时**：设置执行的小时（0-23）
- **分钟**：设置执行的分钟（0-59）

**推荐配置：**
- 月度报表生成：1日 06:00

##### 自定义（Custom）
可以组合日期、星期、小时、分钟进行精确控制。

### 4. 配置任务参数

在"任务配置 (JSON)"字段中输入任务的具体参数：

#### 基金净值更新
```json
{
  "update_all": true,
  "data_source": "tiantian",
  "retry_times": 3
}
```

#### Wise余额同步
```json
{
  "sync_all_accounts": true,
  "currencies": ["USD", "AUD", "CNY", "HKD", "JPY"]
}
```

#### IBKR余额同步
```json
{
  "sync_positions": true
}
```

#### 定投计划执行
```json
{
  "execute_all_plans": true,
  "check_exclude_dates": true
}
```

#### 数据清理
```json
{
  "cleanup_days": 90,
  "cleanup_types": ["logs", "temp_data", "old_snapshots"]
}
```

## 🚀 推荐配置方案

### 方案一：基础配置（推荐新手）
```
1. 基金净值更新 - 每天 15:30
2. Wise余额同步 - 每天 16:00
3. IBKR余额同步 - 每天 17:00
4. 定投计划执行 - 每天 09:00
5. 数据清理 - 每周日 02:00
```

### 方案二：完整配置（推荐生产环境）
```
1. 基金净值更新 - 每天 15:30
2. Wise余额同步 - 每天 16:00
3. IBKR余额同步 - 每天 17:00
4. 定投计划执行 - 每天 09:00
5. OKX余额同步 - 每4小时
6. Wise交易同步 - 每天 18:00
7. 基金持仓同步 - 每天 16:30
8. 数据清理 - 每周日 02:00
9. 数据备份 - 每周六 03:00
10. 月度报表生成 - 每月1日 06:00
```

## ⚠️ 注意事项

1. **时区设置**：确保系统时区设置正确（推荐Asia/Shanghai）
2. **任务冲突**：避免同时执行多个相同类型的任务
3. **资源监控**：监控系统资源使用情况，避免任务过多导致系统负载过高
4. **日志检查**：定期检查任务执行日志，确保任务正常运行
5. **错误处理**：配置任务失败时的重试机制和通知

## 🔧 故障排除

### 任务未执行
1. 检查调度器状态是否正常运行
2. 检查任务配置是否正确
3. 查看任务执行日志

### 任务执行失败
1. 检查任务参数配置
2. 查看错误日志
3. 验证API连接和权限

### 时间不准确
1. 检查系统时区设置
2. 确认调度器时区配置
3. 验证cron表达式格式

## 📞 技术支持

如果遇到配置问题，请：
1. 查看系统日志
2. 检查任务执行状态
3. 联系技术支持团队 