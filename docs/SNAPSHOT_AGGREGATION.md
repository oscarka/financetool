# 快照聚合逻辑说明

## 概述

本系统支持资产快照和汇率快照的时间粒度聚合，解决了"一天多次快照导致数据累加错误"的问题。

## 核心问题

### 问题描述
- 数据库中存在大量快照数据，一天可能有多次快照
- 如果直接累加所有快照数据，会导致资产/汇率数据严重失真
- 例如：上午买入1000元，下午卖出，累加会显示2000元（错误）

### 解决方案
- **按时间段聚合**：将时间分为天/半天/小时等粒度
- **取最新数据**：每个时间段只取最新的一条快照数据
- **避免累加**：确保每个时间段的数据是准确的

## 时间粒度支持

### 1. 按天聚合 (day)
- 时间段：00:00:00 - 23:59:59
- 显示格式：`2024-07-01`
- 适用场景：长期趋势分析

### 2. 按半天聚合 (half_day)
- 上午：00:00:00 - 11:59:59
- 下午：12:00:00 - 23:59:59
- 显示格式：`2024-07-01 上午` / `2024-07-01 下午`
- 适用场景：日内变化分析

### 3. 按小时聚合 (hour)
- 时间段：每小时的00分-59分
- 显示格式：`2024-07-01 14:00`
- 适用场景：短期波动分析

### 4. 原始数据 (raw)
- 返回所有快照数据，不做聚合
- 适用场景：详细数据查看

## API接口

### 资产趋势接口
```
GET /api/v1/snapshot/assets/trend
```

参数：
- `time_granularity`: 时间粒度 (day/half_day/hour)
- `base_currency`: 基准货币 (CNY/USD)
- `days`: 查询天数
- `platform`: 平台过滤
- `asset_type`: 资产类型过滤
- `currency`: 币种过滤

### 汇率快照接口
```
GET /api/v1/snapshot/exchange-rates
```

参数：
- `time_granularity`: 时间粒度 (day/half_day/hour/raw)
- `from_currency`: 源货币
- `to_currency`: 目标货币
- `start`: 开始时间
- `end`: 结束时间

## 聚合逻辑实现

### SQL聚合逻辑
```sql
-- 1. 子查询：找到每个时间段的最新快照时间
WITH latest_snapshots AS (
    SELECT 
        date_trunc('day', snapshot_time) as time_period,
        MAX(snapshot_time) as latest_time
    FROM asset_snapshot
    WHERE snapshot_time BETWEEN start AND end
    GROUP BY time_period
)

-- 2. 主查询：基于最新时间聚合数据
SELECT 
    date_trunc('day', s.snapshot_time) as time_period,
    SUM(s.balance_cny) as total
FROM asset_snapshot s
JOIN latest_snapshots ls ON s.snapshot_time = ls.latest_time
WHERE s.snapshot_time BETWEEN start AND end
GROUP BY time_period
ORDER BY time_period
```

### 半天聚合的特殊处理
```sql
-- 自定义半天截断逻辑
CASE 
    WHEN EXTRACT(hour FROM snapshot_time) < 12 
    THEN date_trunc('day', snapshot_time)
    ELSE date_trunc('day', snapshot_time) + INTERVAL '12 hours'
END
```

## 前端使用

### 资产趋势图表
```typescript
// 支持时间粒度切换
const [timeGranularity, setTimeGranularity] = useState<'day' | 'half_day' | 'hour'>('day');

// 获取趋势数据
const response = await snapshotAPI.getAssetTrend({
    days: 30,
    time_granularity: timeGranularity,
    base_currency: 'CNY'
});
```

### 汇率历史数据
```typescript
// 支持多种时间粒度
const response = await snapshotAPI.getExchangeRateSnapshots({
    from_currency: 'USD',
    to_currency: 'CNY',
    time_granularity: 'half_day'
});
```

## 数据示例

### 输入数据（一天多次快照）
```
2024-07-01 09:00:00 - 资产: 1000 CNY
2024-07-01 14:00:00 - 资产: 1500 CNY (买入)
2024-07-01 18:00:00 - 资产: 1200 CNY (卖出)
```

### 按天聚合结果
```
2024-07-01 - 资产: 1200 CNY (取当天最新)
```

### 按半天聚合结果
```
2024-07-01 上午 - 资产: 1000 CNY (取上午最新)
2024-07-01 下午 - 资产: 1200 CNY (取下午最新)
```

## 手动触发快照

### 资产快照
```typescript
await snapshotAPI.extractAssetSnapshot();
```

### 汇率快照
```typescript
await snapshotAPI.extractExchangeRateSnapshot();
```

## 定时任务配置

快照生成已配置为定时任务：
- 资产快照：每6小时自动生成
- 汇率快照：每6小时自动生成

## 测试验证

运行测试脚本验证聚合逻辑：
```bash
cd backend
python test_snapshot_aggregation.py
```

该脚本会：
1. 显示最近的快照数据
2. 测试按天聚合逻辑
3. 测试按半天聚合逻辑
4. 对比累加 vs 取最新的差异

## 注意事项

1. **数据一致性**：确保聚合后的数据反映真实状态
2. **性能考虑**：大量历史数据时，建议使用适当的时间范围
3. **缓存策略**：频繁查询的数据建议使用Redis缓存
4. **数据清理**：定期清理过期的快照数据以节省存储空间