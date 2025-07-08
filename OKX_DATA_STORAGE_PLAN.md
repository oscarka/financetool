# OKX数据入库存储与更新计划

## 📋 项目概述

为多资产投资记录与收益分析系统添加OKX数据的入库存储功能，包括定时任务自动同步和手动按钮触发更新机制。

## 🎯 核心目标

1. **数据入库存储**：将OKX API获取的数据持久化存储到数据库
2. **定时任务同步**：设置自动化的数据同步调度任务
3. **手动触发更新**：提供按钮/接口支持手动触发数据更新
4. **数据管理**：完整的数据查询、分析和日志管理功能

## 🏗️ 系统架构

### 数据库设计

#### 1. OKX账户余额表 (`okx_account_balances`)
```sql
- currency: 币种
- equity: 币种权益
- available_balance: 可用余额
- frozen_balance: 冻结余额
- position_value: 持仓价值
- unrealized_pnl: 未实现盈亏
- interest: 计息
- margin_required: 保证金要求
- borrowed: 借币量
- data_timestamp: 数据时间戳
```

#### 2. OKX持仓表 (`okx_positions`)
```sql
- inst_id: 产品ID
- inst_type: 产品类型
- position_side: 持仓方向
- currency: 币种
- quantity: 持仓数量
- available_quantity: 可用数量
- avg_price: 开仓均价
- mark_price: 标记价格
- notional_value: 名义价值
- unrealized_pnl: 未实现盈亏
- unrealized_pnl_ratio: 未实现盈亏比例
```

#### 3. OKX交易记录表 (`okx_transactions`)
```sql
- bill_id: 账单ID (唯一)
- inst_id: 产品ID
- currency: 币种
- bill_type: 账单类型
- amount: 变动数量
- balance: 余额
- fee: 手续费
- fill_price: 成交价格
- fill_quantity: 成交数量
- bill_time: 账单时间
```

#### 4. OKX行情数据表 (`okx_market_data`)
```sql
- inst_id: 产品ID
- last_price: 最新价格
- best_bid/ask: 最优买卖价
- open_24h/high_24h/low_24h: 24小时开盘/最高/最低价
- volume_24h: 24小时成交量
- change_24h: 24小时涨跌幅
```

#### 5. OKX同步日志表 (`okx_sync_logs`)
```sql
- sync_type: 同步类型 (balance/position/transaction/market)
- sync_status: 同步状态 (success/failed/running)
- start_time/end_time: 开始/结束时间
- duration: 执行时长
- records_processed/success/failed: 处理记录统计
- error_message: 错误信息
```

### 服务层设计

#### 1. OKXDataService (数据管理服务)
```python
class OKXDataService:
    # 余额数据管理
    - save_account_balance()
    - get_latest_balance()
    
    # 持仓数据管理
    - save_positions()
    - get_latest_positions()
    
    # 交易记录管理
    - save_transactions()
    - get_recent_transactions()
    
    # 行情数据管理
    - save_market_data()
    - get_latest_market_data()
    
    # 同步日志管理
    - create_sync_log()
    - update_sync_log()
    - get_sync_logs()
    
    # 主要同步方法
    - sync_all_data()
```

#### 2. SchedulerService (调度服务扩展)
```python
# 新增OKX数据同步任务
- _sync_okx_data(): 每天16:45执行
```

## 🔄 数据同步机制

### 定时任务调度

#### 现有任务时间安排
- 15:30 - 更新基金净值
- 15:45 - 执行定投计划
- 16:00 - 更新待确认操作
- 16:15 - 更新定投计划状态
- 16:30 - 同步Wise数据
- **16:45 - 同步OKX数据** (新增)

#### OKX数据同步流程
1. **账户余额同步** - 获取并存储最新余额信息
2. **持仓数据同步** - 获取并存储当前持仓状态
3. **交易记录同步** - 增量同步最近100条交易记录
4. **行情数据同步** - 获取并存储现货市场行情数据
5. **同步日志记录** - 记录每个步骤的执行状态和结果

### 手动触发机制

#### API接口列表

**数据同步接口**
- `POST /api/v1/funds/okx/sync/all` - 同步所有OKX数据
- `POST /api/v1/funds/okx/sync/balance` - 同步账户余额
- `POST /api/v1/funds/okx/sync/positions` - 同步持仓数据
- `POST /api/v1/funds/okx/sync/transactions` - 同步交易记录
- `POST /api/v1/funds/okx/sync/market` - 同步行情数据

**数据查询接口**
- `GET /api/v1/funds/okx/data/balance` - 获取存储的余额数据
- `GET /api/v1/funds/okx/data/positions` - 获取存储的持仓数据
- `GET /api/v1/funds/okx/data/transactions` - 获取存储的交易记录
- `GET /api/v1/funds/okx/data/market` - 获取存储的行情数据

**管理接口**
- `GET /api/v1/funds/okx/sync-logs` - 获取同步日志
- `POST /api/v1/funds/scheduler/okx-sync` - 手动执行OKX同步任务

## 🚀 部署步骤

### 1. 数据库迁移
```bash
# 执行数据库迁移（创建OKX数据表）
cd backend
alembic upgrade head
```

### 2. 环境配置
确保OKX API配置完整：
```env
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
OKX_SANDBOX=false  # 正式环境设为false
```

### 3. 服务重启
```bash
# 重启后端服务以加载新的调度任务
systemctl restart your-backend-service
```

## 📊 数据流转

```
OKX API → OKXAPIService → OKXDataService → Database
                                     ↓
                              SchedulerService
                                     ↓
                              定时任务调度
                                     ↓
                              日志记录 & 错误处理
```

## 🔍 监控与维护

### 同步状态监控
- **同步日志查看**：通过 `/okx/sync-logs` 接口查看历史同步记录
- **状态检查**：每次同步会记录成功/失败状态和详细信息
- **错误追踪**：失败时记录具体错误信息，便于排查

### 数据质量保证
- **唯一性约束**：防止重复数据插入
- **时间戳管理**：精确记录数据获取时间
- **增量同步**：交易记录采用增量同步，避免重复处理
- **数据校验**：在保存前验证数据格式的正确性

### 性能优化
- **批量处理**：支持批量插入和更新操作
- **索引优化**：为常用查询字段建立合适索引
- **分页查询**：大量数据查询支持分页功能
- **缓存策略**：最新数据查询使用优化的SQL查询

## 🎛️ 使用指南

### 前端集成建议

#### 1. OKX数据看板
```javascript
// 获取OKX账户概览
const balance = await api.get('/api/v1/funds/okx/data/balance');
const positions = await api.get('/api/v1/funds/okx/data/positions');

// 显示总资产、持仓分布、盈亏状况
```

#### 2. 手动同步按钮
```javascript
// 全量同步按钮
const syncAll = async () => {
  const result = await api.post('/api/v1/funds/okx/sync/all');
  showNotification(result.message);
};

// 分类同步按钮
const syncBalance = async () => {
  await api.post('/api/v1/funds/okx/sync/balance');
};
```

#### 3. 同步状态显示
```javascript
// 获取最近同步日志
const logs = await api.get('/api/v1/funds/okx/sync-logs?limit=10');

// 显示同步状态和时间
logs.data.logs.forEach(log => {
  console.log(`${log.sync_type}: ${log.sync_status} at ${log.start_time}`);
});
```

### 调度任务管理
```javascript
// 获取所有定时任务状态
const jobs = await api.get('/api/v1/funds/scheduler/jobs');

// 手动触发OKX同步
const manualSync = await api.post('/api/v1/funds/scheduler/okx-sync');
```

## 🔧 故障排除

### 常见问题

1. **API认证失败**
   - 检查OKX API密钥配置
   - 确认API权限设置正确
   - 验证沙盒/正式环境配置

2. **数据同步失败**
   - 查看同步日志获取详细错误信息
   - 检查网络连接和API限制
   - 验证数据库连接状态

3. **定时任务未执行**
   - 检查调度器服务状态
   - 确认任务时间配置正确
   - 查看服务日志

### 日志分析
```python
# 查看OKX同步日志
GET /api/v1/funds/okx/sync-logs?sync_type=balance&limit=50

# 日志字段说明
{
  "sync_type": "同步类型",
  "sync_status": "执行状态",
  "duration": "执行时长(秒)",
  "records_processed": "处理记录数",
  "error_message": "错误信息"
}
```

## 📈 扩展计划

### 后续优化方向

1. **实时数据推送**
   - WebSocket连接实现实时行情推送
   - 重要持仓变动的实时通知

2. **数据分析功能**
   - 收益分析和趋势统计
   - 风险评估和预警机制

3. **智能提醒**
   - 异常波动提醒
   - 定期报告生成

4. **多账户支持**
   - 支持多个OKX账户管理
   - 账户间数据对比分析

## ✅ 验收标准

### 功能验收
- [ ] 数据库表结构创建成功
- [ ] API接口正常响应
- [ ] 定时任务按时执行
- [ ] 手动同步功能正常
- [ ] 数据存储和查询正确
- [ ] 错误处理和日志记录完整

### 性能验收
- [ ] 单次同步操作在30秒内完成
- [ ] 数据查询响应时间小于2秒
- [ ] 支持并发操作无冲突
- [ ] 内存使用稳定无泄露

### 可靠性验收
- [ ] 网络异常时能正确处理
- [ ] API限制时有重试机制
- [ ] 数据完整性保证
- [ ] 同步失败时有明确的错误提示

---

## 📝 总结

本计划实现了完整的OKX数据入库存储和更新机制，包括：

🔄 **自动化同步**：定时任务每日自动同步OKX数据
🎛️ **手动触发**：提供API接口支持按需手动更新
📊 **数据管理**：完整的数据存储、查询和分析功能
📈 **监控日志**：详细的同步日志和状态监控
🛡️ **错误处理**：完善的异常处理和重试机制

系统设计遵循模块化原则，便于维护和扩展，为后续的数据分析和投资决策提供了可靠的数据基础。