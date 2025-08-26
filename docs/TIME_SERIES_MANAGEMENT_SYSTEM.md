# 时间序列管理系统设计文档

## 📋 项目概述

本文档描述了个人财务工具中时间序列管理系统的设计方案，该系统用于处理资产快照数据的时间连续性、数据缺失处理、用户规则配置以及级联更新等复杂场景。

## 🎯 核心设计理念

### 基本思路
- **每次快照都是一条记录** → 记录可以被修改 → 修改会影响后续记录
- **时间序列管理** = 连续的时间点 + 每个时间点的数据状态 + 数据变更的级联影响
- **用户驱动的规则配置**，系统自动执行和级联更新

## 🏗️ 系统架构

### 1. 数据层架构
```
┌─────────────────────────────────────────────────────────────┐
│                    数据层架构                                │
├─────────────────────────────────────────────────────────────┤
│  实时数据层: 当前各平台真实余额                              │
│  ├── WiseBalance, IBKRBalance, OKXBalance, Web3Balance     │
│  └── 汇率数据: WiseExchangeRate, ExchangeRate              │
├─────────────────────────────────────────────────────────────┤
│  快照层: 每小时"拍照"的资产状态                              │
│  ├── AssetSnapshot (资产快照)                               │
│  ├── ExchangeRateSnapshot (汇率快照)                        │
│  └── 数据质量标记和修改历史                                  │
├─────────────────────────────────────────────────────────────┤
│  规则层: 用户配置的时间序列处理规则                          │
│  ├── TimeSeriesRules (时间规则表)                           │
│  ├── 规则优先级和冲突解决                                    │
│  └── 规则应用和级联更新                                      │
├─────────────────────────────────────────────────────────────┤
│  操作记录层: 所有数据变更的审计日志                          │
│  ├── 快照修改历史                                            │
│  ├── 规则变更记录                                            │
│  └── 用户操作追踪                                            │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心组件
- **时间序列引擎**: 生成完整的时间序列，应用所有规则
- **规则管理器**: 处理用户规则配置，解决规则冲突
- **插值引擎**: 智能插值算法，支持多种插值策略
- **级联更新器**: 规则变更时自动更新相关数据
- **数据质量评估器**: 评估数据完整性、新鲜度和一致性

## 🔧 具体场景分析

### 场景1: 快照执行失败（网络/系统问题）

**问题描述**: 1:00快照成功，2:00快照失败，3:00快照成功

**具体数据问题**:
- `AssetSnapshot`表中2:00时间点没有记录
- `ExchangeRateSnapshot`中2:00时间点也没有记录

**解决方案**:
1. **插值选项**: 在1:00和3:00之间插入2:00的记录
   - 资产数据：`(1:00资产 + 3:00资产) / 2`
   - 汇率数据：`(1:00汇率 + 3:00汇率) / 2`
   - 标记：`"is_interpolated": true, "interpolation_source": "1:00_and_3:00"`

2. **归零选项**: 2:00记录显示为0
   - 资产数据：所有平台余额为0
   - 汇率数据：使用1:00的汇率（保持不变）
   - 标记：`"is_zero_filled": true, "reason": "snapshot_failed"`

3. **重建选项**: 从原始数据重建2:00的快照
   - 查询1:00-3:00之间的所有原始数据
   - 重新计算2:00的资产快照
   - 标记：`"is_rebuilt": true, "rebuild_source": "original_data"`

### 场景2: 用户修改历史数据

**问题描述**: 用户修改了1月1日10:00的Wise余额，但10:00的快照还是旧数据

**具体数据问题**:
- `WiseBalance`表中该账户的余额被修改
- `AssetSnapshot`表中10:00的快照数据过时
- 后续所有快照（11:00, 12:00...）都基于过时数据计算

**解决方案**:
1. **快照级联更新**:
   - 检测到10:00的Wise数据被修改
   - 自动重新计算10:00及之后所有快照的Wise部分
   - 更新`AssetSnapshot`表中相关记录
   - 标记：`"last_modified": "2024-01-01T15:30:00", "modification_cascade": true`

2. **选择性更新**:
   - 只更新Wise相关的快照记录
   - 其他平台（IBKR、OKX、Web3）的快照保持不变
   - 标记：`"partial_update": true, "updated_platforms": ["Wise"]`

3. **用户确认更新**:
   - 显示影响范围：`"affected_snapshots": 24, "affected_hours": "10:00-09:00"`
   - 让用户选择是否执行级联更新
   - 提供预览：`"preview_changes": {...}`

### 场景3: 汇率数据缺失

**问题描述**: 快照时某个汇率缺失，导致CNY转换失败

**具体数据问题**:
- `WiseExchangeRate`表中JPY/CNY汇率缺失
- `AssetSnapshot`表中JPY资产无法转换为CNY
- 总资产计算不完整

**解决方案**:
1. **使用最近汇率**:
   - 查找JPY/CNY最近一次成功的汇率记录
   - 在快照中使用该汇率进行转换
   - 标记：`"rate_source": "last_known", "rate_age": "2_hours_old"`

2. **跳过转换**:
   - 保持JPY资产以原币种显示
   - 在总资产中标记：`"unconverted_currencies": ["JPY"], "total_without_jpy": 100000`

3. **用户输入汇率**:
   - 提供手动输入汇率的选项
   - 更新`WiseExchangeRate`表
   - 重新计算相关快照

### 场景4: 平台数据同步延迟

**问题描述**: OKX数据延迟2小时，2:00快照时用的是1:00的数据

**具体数据问题**:
- `OKXBalance`表中2:00时间点没有新数据
- 快照使用了1:00的旧数据
- 数据新鲜度不足

**解决方案**:
1. **等待新鲜数据**:
   - 延迟快照执行，等待OKX数据同步完成
   - 标记：`"waiting_for": "OKX_data", "expected_delay": "2_hours"`

2. **使用可用数据**:
   - 使用1:00的OKX数据，但标记为过期
   - 标记：`"data_freshness": "1_hour_old", "platform": "OKX"`

3. **部分快照**:
   - 先为其他平台生成快照
   - OKX部分标记为待更新
   - 标记：`"partial_snapshot": true, "pending_platforms": ["OKX"]`

### 场景5: 快照数据不完整

**问题描述**: 某个快照只记录了部分平台数据

**具体数据问题**:
- `AssetSnapshot`表中某条记录缺少IBKR数据
- 总资产计算不准确
- 收益分析受影响

**解决方案**:
1. **补充缺失数据**:
   - 从`IBKRBalance`表查询该时间点的数据
   - 更新快照记录
   - 标记：`"completeness": "100%", "supplemented_platforms": ["IBKR"]`

2. **标记不完整**:
   - 在快照中标记缺失的平台
   - 提供重建选项
   - 标记：`"completeness": "75%", "missing_platforms": ["IBKR"]`

## 🗄️ 数据库设计

### 1. 时间规则表
```sql
CREATE TABLE time_series_rules (
    id SERIAL PRIMARY KEY,
    time_range_start TIMESTAMP NOT NULL,
    time_range_end TIMESTAMP NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'zero', 'interpolate', 'actual', 'custom'
    rule_config JSONB NOT NULL,     -- 具体规则参数
    priority INTEGER DEFAULT 1,      -- 规则优先级
    description TEXT,                -- 规则描述
    created_by VARCHAR(100),        -- 创建用户
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_time_range CHECK (time_range_start < time_range_end),
    CONSTRAINT valid_rule_type CHECK (rule_type IN ('zero', 'interpolate', 'actual', 'custom'))
);

-- 索引
CREATE INDEX idx_time_series_rules_time_range ON time_series_rules(time_range_start, time_range_end);
CREATE INDEX idx_time_series_rules_priority ON time_series_rules(priority DESC);
```

### 2. 快照表扩展
```sql
-- 扩展AssetSnapshot表
ALTER TABLE asset_snapshot ADD COLUMN data_quality JSONB;
ALTER TABLE asset_snapshot ADD COLUMN modification_history JSONB[] DEFAULT '{}';
ALTER TABLE asset_snapshot ADD COLUMN interpolation_info JSONB;
ALTER TABLE asset_snapshot ADD COLUMN last_modified TIMESTAMP;
ALTER TABLE asset_snapshot ADD COLUMN applied_rules INTEGER[];

-- 扩展ExchangeRateSnapshot表
ALTER TABLE exchange_rate_snapshot ADD COLUMN data_quality JSONB;
ALTER TABLE exchange_rate_snapshot ADD COLUMN modification_history JSONB[] DEFAULT '{}';
ALTER TABLE exchange_rate_snapshot ADD COLUMN interpolation_info JSONB;
ALTER TABLE exchange_rate_snapshot ADD COLUMN last_modified TIMESTAMP;
ALTER TABLE exchange_rate_snapshot ADD COLUMN applied_rules INTEGER[];
```

### 3. 数据质量标记结构
```json
{
  "data_quality": {
    "completeness": 0.95,                    // 数据完整性 (0-1)
    "freshness": "1_hour_old",               // 数据新鲜度
    "interpolated_platforms": ["Wise"],      // 插值的平台
    "missing_platforms": [],                 // 缺失的平台
    "rate_issues": ["JPY_CNY_delayed"],      // 汇率问题
    "last_modified": "2024-01-01T15:30:00", // 最后修改时间
    "data_source": "actual|interpolated|zero|rebuilt", // 数据来源
    "confidence_score": 0.9                  // 数据可信度 (0-1)
  }
}
```

### 4. 修改历史记录结构
```json
{
  "modification_history": [
    {
      "timestamp": "2024-01-01T15:30:00",
      "type": "balance_correction|rule_update|interpolation|manual_edit",
      "platform": "Wise",
      "affected_snapshots": [10, 11, 12],
      "user_id": "123",
      "description": "用户修正了Wise余额",
      "previous_value": 100000,
      "new_value": 105000
    }
  ]
}
```

## 🔄 核心算法

### 1. 时间序列生成算法
```python
def generate_complete_timeline(start_time, end_time, rules, snapshots):
    """生成完整的时间序列，应用所有规则"""
    
    timeline = []
    current_time = start_time
    
    while current_time <= end_time:
        # 1. 检查是否有实际数据
        actual_data = find_snapshot_at_time(current_time, snapshots)
        
        if actual_data:
            # 有实际数据，直接使用
            timeline.append({
                'time': current_time,
                'data_source': 'actual',
                'data': actual_data,
                'rule_applied': None,
                'confidence_score': 1.0
            })
        else:
            # 没有实际数据，查找适用的规则
            applicable_rule = find_applicable_rule(current_time, rules)
            
            if applicable_rule:
                # 应用规则生成数据
                generated_data = apply_rule(applicable_rule, current_time, snapshots)
                timeline.append({
                    'time': current_time,
                    'data_source': applicable_rule.rule_type,
                    'data': generated_data,
                    'rule_applied': applicable_rule.id,
                    'confidence_score': calculate_confidence(applicable_rule)
                })
            else:
                # 没有规则，显示缺失
                timeline.append({
                    'time': current_time,
                    'data_source': 'missing',
                    'data': None,
                    'rule_applied': None,
                    'confidence_score': 0.0
                })
        
        current_time += timedelta(hours=1)
    
    return timeline
```

### 2. 规则冲突解决算法
```python
def resolve_rule_conflicts(rules):
    """解决规则冲突，按优先级排序"""
    
    # 1. 按优先级排序
    sorted_rules = sorted(rules, key=lambda x: x.priority, reverse=True)
    
    # 2. 检测重叠时间范围
    for i, rule1 in enumerate(sorted_rules):
        for rule2 in sorted_rules[i+1:]:
            if time_ranges_overlap(rule1, rule2):
                # 高优先级规则覆盖低优先级规则
                adjust_rule_boundaries(rule1, rule2)
    
    return sorted_rules

def time_ranges_overlap(rule1, rule2):
    """检查两个规则的时间范围是否重叠"""
    return (rule1.time_range_start <= rule2.time_range_end and 
            rule1.time_range_end >= rule2.time_range_start)
```

### 3. 智能插值算法
```python
def apply_interpolation_rule(rule, target_time, snapshots):
    """应用插值规则"""
    
    if rule.rule_config['method'] == 'linear':
        return linear_interpolation(target_time, rule, snapshots)
    elif rule.rule_config['method'] == 'exponential':
        return exponential_interpolation(target_time, rule, snapshots)
    elif rule.rule_config['method'] == 'custom':
        return custom_interpolation(target_time, rule, snapshots)
    else:
        raise ValueError(f"不支持的插值方法: {rule.rule_config['method']}")

def linear_interpolation(target_time, rule, snapshots):
    """线性插值"""
    before_time = rule.rule_config['source_before']
    after_time = rule.rule_config['source_after']
    
    before_data = find_snapshot_at_time(before_time, snapshots)
    after_data = find_snapshot_at_time(after_time, snapshots)
    
    if not before_data or not after_data:
        return None
    
    # 计算时间权重
    total_diff = (after_time - before_time).total_seconds()
    target_diff = (target_time - before_time).total_seconds()
    
    if total_diff == 0:
        return before_data
    
    weight = target_diff / total_diff
    
    # 线性插值计算
    interpolated_data = {}
    for platform in before_data.keys():
        if platform in after_data:
            before_value = before_data[platform]
            after_value = after_data[platform]
            interpolated_value = before_value + (after_value - before_value) * weight
            interpolated_data[platform] = interpolated_value
    
    return interpolated_data
```

### 4. 级联更新算法
```python
def cascade_update_snapshots(rule, db):
    """当规则变更时，级联更新相关快照"""
    
    # 1. 找到受影响的快照
    affected_snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time >= rule.time_range_start,
        AssetSnapshot.snapshot_time <= rule.time_range_end
    ).all()
    
    # 2. 重新计算每个快照
    for snapshot in affected_snapshots:
        # 应用新规则重新计算
        recalculated_data = recalculate_snapshot_with_rules(snapshot, rule, db)
        
        # 更新快照
        snapshot.data_quality = {
            "last_rule_update": datetime.now().isoformat(),
            "applied_rules": [rule.id],
            "calculation_method": rule.rule_type,
            "confidence_score": calculate_confidence(rule)
        }
        
        # 记录变更历史
        snapshot.modification_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "rule_update",
            "rule_id": rule.id,
            "previous_data": snapshot.balance_cny,
            "new_data": recalculated_data,
            "description": f"应用规则 {rule.rule_type}"
        })
        
        # 更新快照数据
        snapshot.balance_cny = recalculated_data
        snapshot.last_modified = datetime.now()
```

## 🌐 API接口设计

### 1. 时间序列状态查询
```http
GET /api/v1/snapshot/time-series/status?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "time_series": [
      {
        "time": "2024-01-01T00:00:00",
        "data_source": "actual",
        "data": {...},
        "rule_applied": null,
        "confidence_score": 1.0
      },
      {
        "time": "2024-01-01T01:00:00",
        "data_source": "interpolated",
        "data": {...},
        "rule_applied": 123,
        "confidence_score": 0.8
      }
    ],
    "rules_applied": ["interpolate", "zero"],
    "data_coverage": {
      "total_points": 24,
      "actual_data": 20,
      "interpolated": 3,
      "zero_filled": 1,
      "missing": 0
    }
  }
}
```

### 2. 时间规则管理
```http
POST /api/v1/snapshot/time-series/rules
```

**请求示例**:
```json
{
  "time_range_start": "2024-01-01T02:00:00",
  "time_range_end": "2024-01-01T04:00:00",
  "rule_type": "interpolate",
  "rule_config": {
    "method": "linear",
    "source_before": "2024-01-01T01:00:00",
    "source_after": "2024-01-01T05:00:00"
  },
  "priority": 1,
  "description": "2:00-4:00之间线性插值"
}
```

### 3. 收益分析（增强版）
```http
GET /api/v1/snapshot/profit-analysis?period=day&include_interpolated=true&data_quality_threshold=0.7
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "period": "day",
    "profit_data": [...],
    "data_quality_summary": {
      "overall_confidence": 0.85,
      "interpolated_points": 2,
      "zero_filled_points": 0,
      "missing_points": 0,
      "data_freshness": "1_hour_old"
    },
    "recovery_options": {
      "can_rebuild": true,
      "can_interpolate": true,
      "can_use_current": true
    }
  }
}
```

## 🎨 前端用户界面

### 1. 时间规则配置界面
- **时间范围选择器**: 选择开始和结束时间
- **规则类型选择**: 下拉选择归零、插值、实际等
- **插值参数配置**: 选择插值方法和数据源
- **优先级设置**: 设置规则优先级
- **预览效果**: 实时预览规则应用后的效果

### 2. 时间序列状态展示
- **时间轴图表**: 显示每个时间点的数据状态
- **数据质量指示器**: 颜色编码显示数据可信度
- **规则应用标记**: 显示哪些规则被应用到哪些时间点
- **缺失数据高亮**: 突出显示缺失或插值的数据

### 3. 数据修复选项
- **批量操作**: 选择多个时间点进行批量修复
- **插值策略选择**: 选择插值方法（线性、指数、自定义）
- **数据源选择**: 选择使用快照数据还是重建数据
- **影响范围预览**: 显示修复操作会影响哪些相关数据

## 🚀 实施计划

### 阶段1: 基础架构（2周）
- 数据库表结构设计和创建
- 核心时间序列引擎开发
- 基础规则管理功能

### 阶段2: 核心功能（3周）
- 智能插值算法实现
- 规则冲突解决机制
- 级联更新功能

### 阶段3: 高级功能（2周）
- 数据质量评估系统
- 用户界面开发
- 性能优化

### 阶段4: 测试和部署（1周）
- 单元测试和集成测试
- 性能测试
- 生产环境部署

## 🔍 技术考虑

### 1. 性能优化
- **数据库索引**: 为时间范围查询创建复合索引
- **缓存策略**: 缓存常用的时间序列数据
- **批量操作**: 支持批量规则应用和数据更新

### 2. 数据一致性
- **事务管理**: 确保规则应用和快照更新的原子性
- **并发控制**: 处理多用户同时修改规则的情况
- **数据验证**: 验证规则配置的合理性

### 3. 扩展性
- **插件化架构**: 支持自定义插值算法
- **规则模板**: 提供常用的规则模板
- **API版本控制**: 支持API的向后兼容

## 📝 总结

这个时间序列管理系统解决了个人财务工具中复杂的数据连续性问题，通过用户驱动的规则配置和智能的插值算法，确保了时间序列的完整性和数据的可信度。系统设计充分考虑了各种实际场景，提供了灵活的数据处理选项和完整的审计追踪功能。

后续实现时，建议优先实现核心的时间序列引擎和基础规则管理功能，然后逐步添加高级特性如智能插值、数据质量评估等。
