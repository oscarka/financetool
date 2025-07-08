# Wise数据入库与更新计划 📊

## 🎯 项目目标

将现有的Wise API数据查询功能升级为完整的数据管理系统，实现：
- 数据持久化存储
- 定时自动更新
- 主动手动更新
- 数据状态监控

## 📋 现状分析

### ✅ 已有功能
- 完整的Wise API集成服务(`WiseAPIService`)
- 数据库模型定义(`WiseTransaction`, `WiseBalance`, `WiseExchangeRate`)
- 完整的API路由和前端界面
- 定时任务框架(每日16:30执行)

### ❌ 缺失功能
- 定时任务中的实际数据库存储逻辑
- 余额数据的入库功能
- 主动更新按钮和API接口
- 数据库状态监控

## 🚀 实施方案

### 1. 后端数据库存储功能

#### 1.1 WiseAPIService新增方法
```python
# 文件: backend/app/services/wise_api_service.py

async def sync_all_balances_to_db(self) -> Dict[str, Any]
"""同步所有账户余额到数据库"""

async def sync_exchange_rates_to_db(self, currency_pairs: List[tuple] = None) -> Dict[str, Any]
"""同步汇率数据到数据库"""

async def sync_all_data_to_db(self, days: int = 7) -> Dict[str, Any]
"""综合同步所有Wise数据到数据库"""
```

#### 1.2 定时任务优化
```python
# 文件: backend/app/services/scheduler_service.py

async def _sync_wise_data(self):
    """使用新的综合同步方法，真正存储数据到数据库"""
    wise_service = WiseAPIService()
    result = await wise_service.sync_all_data_to_db(days=7)
```

### 2. API接口扩展

#### 2.1 新增同步接口
```python
# 文件: backend/app/api/v1/wise.py

@router.post("/sync-balances")
"""主动同步Wise所有账户余额到数据库"""

@router.post("/sync-exchange-rates") 
"""主动同步Wise汇率数据到数据库"""

@router.post("/sync-all")
"""主动同步所有Wise数据到数据库（交易、余额、汇率）"""

@router.get("/db-status")
"""获取数据库中Wise数据的状态统计"""
```

### 3. 前端用户界面

#### 3.1 数据库状态展示
- 数据库交易记录数量和最后更新时间
- 数据库余额记录数量和最后更新时间  
- 数据库汇率记录数量和最后更新时间
- 总体数据状态指示器

#### 3.2 主动同步功能
- "同步到数据库"主按钮
- 同步操作模态框
- 综合同步选项（7天/30天/365天）
- 分别同步选项（交易/余额/汇率）
- 同步结果反馈

## 💾 数据库设计

### 表结构确认
```sql
-- 交易记录表
wise_transactions (
    id, profile_id, account_id, transaction_id,
    type, amount, currency, description, title,
    date, status, reference_number, created_at, updated_at
)

-- 账户余额表  
wise_balances (
    id, account_id, currency, available_balance,
    reserved_balance, cash_amount, total_worth,
    type, name, icon, investment_state,
    creation_time, modification_time, visible, primary,
    created_at, updated_at
)

-- 汇率数据表
wise_exchange_rates (
    id, source_currency, target_currency, rate,
    time, created_at, updated_at
)
```

## ⏰ 定时任务配置

### 自动同步策略
- **执行时间**: 每日16:30
- **同步范围**: 最近7天的交易记录
- **数据类型**: 交易记录 + 账户余额 + 汇率数据
- **错误处理**: 分类记录，失败重试机制

## 🔧 主要功能特性

### 4.1 数据去重与更新
- 交易记录：基于`transaction_id`去重
- 账户余额：基于`account_id`更新
- 汇率数据：基于`source_currency + target_currency + date`去重

### 4.2 错误处理与监控
- 详细的日志记录
- 同步状态实时反馈
- 失败原因分析和提示
- 数据库状态监控

### 4.3 用户体验优化
- 加载状态指示
- 同步进度展示
- 操作结果通知
- 数据状态可视化

## 📊 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Wise API      │    │   后端服务       │    │   数据库        │
│                 │    │                 │    │                 │
│ • 账户余额      │────│ • API Service   │────│ • wise_balances │
│ • 交易记录      │    │ • 定时任务      │    │ • wise_transactions│
│ • 汇率数据      │    │ • 路由接口      │    │ • wise_exchange_rates│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   前端界面       │
                       │                 │
                       │ • 数据展示      │
                       │ • 状态监控      │
                       │ • 主动同步      │
                       └─────────────────┘
```

## 🎯 成功标准

### 功能完成度
- [x] 数据库存储方法实现
- [x] 定时任务数据库集成
- [x] 主动同步API接口
- [x] 前端同步界面
- [x] 数据状态监控

### 性能要求
- 定时同步完成时间 < 5分钟
- 主动同步响应时间 < 30秒
- 数据库查询响应时间 < 3秒
- 界面加载时间 < 2秒

### 可靠性要求
- 数据同步成功率 > 95%
- 重复数据处理准确率 100%
- 错误处理覆盖率 100%
- 系统稳定运行时间 > 99%

## 📈 后续扩展计划

### 短期优化
- 增量同步策略
- 并发同步处理
- 数据压缩存储
- 性能监控告警

### 长期规划
- 多账户管理
- 数据分析报表
- 智能预警系统
- 移动端支持

## 🔒 安全考虑

- API Token安全存储
- 数据库访问权限控制
- 敏感信息脱敏处理
- 操作日志审计

## 📝 部署说明

1. **数据库迁移**: 确保数据库表结构最新
2. **环境变量**: 配置Wise API Token
3. **定时任务**: 启动scheduler服务
4. **前端部署**: 更新前端代码
5. **功能测试**: 验证同步功能正常

---

**📅 完成时间**: 2025年1月

**👨‍💻 负责人**: 开发团队

**📞 联系方式**: 技术支持团队

---

## 🎉 总结

通过本次升级，Wise数据管理将从单纯的API查询升级为完整的数据管理系统，提供：

1. **自动化**: 定时任务自动同步数据
2. **可控性**: 主动同步按钮随时更新
3. **可视化**: 数据库状态实时监控
4. **可靠性**: 完善的错误处理机制

这将大大提升用户体验，为后续的数据分析和业务扩展奠定坚实基础。