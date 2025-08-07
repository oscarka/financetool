# 15:00时间点净值匹配功能实现

## 功能概述

本功能实现了根据操作时间自动匹配基金净值的逻辑，确保：
- **15:00之前**的操作匹配**当天**的净值
- **15:00之后**的操作匹配**下一个交易日**的净值

## 核心逻辑

### 1. 时间判断逻辑

```python
def _get_nav_date_by_operation_time(db: Session, fund_code: str, operation_datetime: datetime) -> Optional[date]:
    """根据操作时间确定对应的净值日期"""
    operation_date = operation_datetime.date()
    operation_time = operation_datetime.time()
    
    # 15:00之前使用当天净值，15:00之后使用下一个交易日净值
    if operation_time < time(15, 0):
        nav_date = operation_date
    else:
        # 15:00之后，查找下一个交易日
        next_trading_day = _get_next_trading_day(db, fund_code, operation_date)
        nav_date = next_trading_day if next_trading_day else operation_date
    
    return nav_date
```

### 2. 下一个交易日计算

```python
def _get_next_trading_day(db: Session, fund_code: str, start_date: date) -> Optional[date]:
    """获取下一个交易日（通过查询净值数据判断）"""
    # 查找从start_date开始未来30天内的所有净值记录
    future_navs = db.query(FundNav).filter(
        and_(
            FundNav.fund_code == fund_code,
            FundNav.nav_date > start_date,
            FundNav.nav_date <= start_date + timedelta(days=30)
        )
    ).order_by(FundNav.nav_date).all()
    
    if future_navs:
        return future_navs[0].nav_date
    else:
        # 如果数据库中没有，尝试通过API获取
        return _get_next_trading_day_from_api(fund_code, start_date)
```

## 应用场景

### 1. 手动操作创建

当用户创建买入/卖出操作时：
- 如果用户填写了净值，直接使用用户填写的净值
- 如果用户没有填写净值，根据操作时间自动匹配对应净值

### 2. 定投计划执行

定投计划执行时：
- 根据执行时间（通常是15:45）匹配对应的净值
- 15:00之后执行的定投会匹配下一个交易日的净值

### 3. 待确认操作更新

当净值同步到数据库后：
- 自动检查所有待确认的操作
- 根据操作时间重新匹配对应的净值
- 如果找到对应净值，自动计算份额并确认操作

### 4. 操作修改/删除

当用户修改操作时间时：
- 根据新的操作时间重新匹配净值
- 重新计算份额和状态

## 定时任务安排

### 净值更新流程

1. **15:30** - 更新基金净值
2. **净值更新后** - 自动触发待确认操作更新
3. **16:00** - 更新待确认操作（备用）

### 定投执行流程

1. **15:45** - 执行定投计划
2. **16:15** - 更新定投计划状态

## 测试用例

### 场景1: 15:00之前的操作
- 操作时间: 周一 14:30
- 匹配净值: 周一净值
- 状态: 立即确认

### 场景2: 15:00之后的操作
- 操作时间: 周一 16:30
- 匹配净值: 周二净值
- 状态: 待确认（直到周二净值同步）

### 场景3: 周五15:00之后的操作
- 操作时间: 周五 16:30
- 匹配净值: 下周一净值
- 状态: 待确认（直到下周一净值同步）

## 实现细节

### 1. 净值匹配优先级

1. **用户填写净值** - 最高优先级，直接使用
2. **根据时间匹配** - 根据操作时间匹配对应净值
3. **默认当天** - 如果无法确定下一个交易日，使用当天

### 2. 状态管理

- **confirmed** - 已找到对应净值并计算份额
- **pending** - 等待对应净值同步

### 3. 错误处理

- 如果无法获取下一个交易日，回退到当天
- 如果净值API调用失败，记录错误但不影响其他操作
- 数据库操作失败时自动回滚

## 配置要求

### 环境变量

```bash
# 数据库连接
DATABASE_URL=postgresql://...

# 时区设置
TZ=Asia/Shanghai
```

### 定时任务配置

```json
{
    "fund_nav_update": {
        "cron": "0 23 * * *",
        "enabled": true
    },
    "dca_execute": {
        "cron": "0 10 * * 1-5",
        "enabled": true
    }
}
```

## 监控和日志

### 关键日志点

1. **净值匹配** - 记录操作时间和匹配的净值日期
2. **待确认操作更新** - 记录更新的操作数量和状态变化
3. **错误处理** - 记录API调用失败和数据库操作错误

### 性能考虑

1. **批量查询** - 净值查询使用批量操作
2. **缓存机制** - 净值数据缓存在数据库中
3. **异步处理** - 净值更新和操作确认使用异步处理

## 扩展性

### 未来改进

1. **交易日历** - 集成交易日历API，更准确地判断交易日
2. **多数据源** - 支持多个净值数据源，提高可靠性
3. **智能匹配** - 根据历史数据智能预测下一个交易日

### 兼容性

- 向后兼容现有的操作记录
- 支持手动填写净值的操作
- 不影响现有的定投计划配置 