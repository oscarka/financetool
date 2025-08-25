"""MCP Prompts管理器 - 提供SQL编写规范和财务分析指南"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MCPPromptsManager:
    """MCP Prompts管理器 - 提供各种分析指南和规范"""
    
    def __init__(self):
        self.prompts = {
            "sql_style_guide": self._get_sql_style_guide(),
            "red_team_sql": self._get_red_team_sql(),
            "financial_analysis_guide": self._get_financial_analysis_guide(),
            "query_optimization_guide": self._get_query_optimization_guide(),
            "postgresql_syntax_rules": self._postgresql_syntax_rules()
        }
        logger.info(f"✅ 成功加载 {len(self.prompts)} 个MCP Prompts")
    
    def get_prompt(self, name: str) -> Optional[str]:
        """获取指定的Prompt"""
        return self.prompts.get(name)
    
    def get_all_prompts(self) -> Dict[str, str]:
        """获取所有可用的Prompts"""
        return self.prompts
    
    def list_prompts(self) -> list:
        """列出所有可用的Prompt名称"""
        return list(self.prompts.keys())
    
    def _get_sql_style_guide(self) -> str:
        """SQL编写规范指南"""
        return """# SQL编写规范指南

## 核心原则
1. **先思考后生成**：分析用户需求，确定查询目标，设计查询逻辑
2. **先describe_schema再写SQL**：了解数据结构，避免字段错误，确保表名正确
3. **一律显式列名**：不使用SELECT *，明确指定需要的字段，提高查询性能
4. **必带LIMIT**：所有查询都要有行数限制，默认200行，防止返回过多数据
5. **时间范围必须写清楚**：使用明确的日期范围，避免全表扫描，提高查询效率

## 具体规范

### 字段处理
- 使用 `COALESCE(balance_cny, 0)` 处理NULL值，确保计算结果准确
- 使用 `LOWER(field_name)` 进行不区分大小写的比较
- 使用 `TRIM(field_name)` 去除字符串前后的空格

### 时间函数
- 使用 `DATE_TRUNC('month', snapshot_time)` 进行时间分组
- 使用 `CURRENT_DATE - INTERVAL '30 days'` 指定时间范围
- 使用 `NOW()` 获取当前时间

### 聚合函数
- 使用 `SUM`, `COUNT`, `AVG`, `MAX`, `MIN` 进行数据聚合
- 使用 `GROUP BY` 进行分组，确保聚合字段的一致性
- 使用 `HAVING` 对聚合结果进行过滤

### 排序和限制
- 使用 `ORDER BY` 对结果进行排序，指定排序方向（ASC/DESC）
- 使用 `LIMIT` 限制返回行数，避免性能问题
- 使用 `OFFSET` 进行分页查询

## 禁止操作
- **不能SELECT ***：必须明确指定需要的字段
- **禁写DDL/DML**：不能执行CREATE, INSERT, UPDATE, DELETE等写操作
- **不能无WHERE条件**：避免全表扫描，必须指定过滤条件
- **不能无LIMIT**：必须限制返回行数，防止内存溢出
- **不能使用危险函数**：避免使用可能影响系统的函数

## 最佳实践
- 优先使用索引字段进行过滤和排序
- 合理使用子查询和CTE（WITH语句）
- 避免在WHERE子句中使用函数，影响索引使用
- 使用EXPLAIN分析查询计划，优化查询性能
"""
    
    def _get_red_team_sql(self) -> str:
        """危险SQL模式识别指南"""
        return """# 危险SQL模式识别指南

## 高风险模式

### 1. 无WHERE的大JOIN
**风险**：可能导致笛卡尔积，性能灾难
**示例**：
```sql
-- 危险：无WHERE条件的JOIN
SELECT * FROM table1 JOIN table2;  -- 可能产生大量行

-- 安全：有明确条件的JOIN
SELECT * FROM table1 t1 
JOIN table2 t2 ON t1.id = t2.id 
WHERE t1.status = 'active';
```

### 2. 隐式类型转换
**风险**：可能导致索引失效，全表扫描
**示例**：
```sql
-- 危险：隐式类型转换
WHERE string_field = 123;  -- 可能导致索引失效

-- 安全：显式类型转换
WHERE string_field = '123';
```

### 3. 无上限聚合
**风险**：COUNT(*) FROM huge_table，可能超时
**示例**：
```sql
-- 危险：无限制的聚合查询
SELECT COUNT(*) FROM huge_table;  -- 可能超时

-- 安全：有条件的聚合查询
SELECT COUNT(*) FROM huge_table WHERE status = 'active';
```

### 4. 复杂子查询
**风险**：嵌套过深，性能问题
**示例**：
```sql
-- 危险：嵌套过深的子查询
SELECT * FROM table1 
WHERE id IN (
    SELECT id FROM table2 
    WHERE field IN (
        SELECT field FROM table3 
        WHERE condition IN (...)
    )
);

-- 安全：使用JOIN或CTE
WITH filtered_data AS (
    SELECT field FROM table3 WHERE condition = 'value'
)
SELECT t1.* FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id
JOIN filtered_data fd ON t2.field = fd.field;
```

### 5. 时间范围过大
**风险**：查询历史全量数据，性能问题
**示例**：
```sql
-- 危险：时间范围过大
WHERE snapshot_time > '2020-01-01';  -- 可能扫描大量数据

-- 安全：合理的时间范围
WHERE snapshot_time >= CURRENT_DATE - INTERVAL '30 days';
```

## 安全检查清单
- [ ] 是否有WHERE条件？
- [ ] WHERE条件是否使用了索引字段？
- [ ] 是否有LIMIT限制？
- [ ] 聚合查询是否有合理的分组？
- [ ] 时间范围是否合理？
- [ ] 是否避免了SELECT *？
- [ ] JOIN条件是否明确？
- [ ] 子查询是否过于复杂？

## 性能优化建议
- 使用 `EXPLAIN ANALYZE` 分析查询计划
- 优先使用索引字段进行过滤
- 合理使用LIMIT和OFFSET
- 避免在WHERE中使用函数
- 使用CTE（WITH语句）简化复杂查询
- 考虑使用物化视图优化重复查询
"""
    
    def _get_financial_analysis_guide(self) -> str:
        """财务分析专用指南"""
        return """# 财务分析专用指南

## 常用分析维度

### 1. 平台维度
**分析目标**：了解各平台的资产分布和表现
**关键字段**：`platform`
**常用值**：支付宝、Wise、IBKR、OKX、Web3
**分析场景**：平台对比、风险分散、资产配置优化

### 2. 资产类型维度
**分析目标**：了解不同资产类型的风险和收益特征
**关键字段**：`asset_type`
**常用值**：基金、外汇、股票、数字货币、现金、储蓄
**分析场景**：资产配置、风险分析、收益优化

### 3. 时间维度
**分析目标**：了解资产变化的时间趋势
**关键字段**：`snapshot_time`
**常用粒度**：日、周、月、季度、年度
**分析场景**：趋势分析、周期性分析、预测分析

### 4. 价值维度
**分析目标**：了解资产的价值分布和变化
**关键字段**：`balance_cny`、`current_value`、`profit_rate`
**分析场景**：价值分析、收益分析、风险评估

## 标准分析模板

### 1. 分布分析模板
**用途**：分析资产在不同维度的分布情况
**SQL模式**：
```sql
SELECT 
    dimension_field,
    SUM(COALESCE(balance_cny, 0)) as total_value,
    COUNT(*) as asset_count,
    ROUND(SUM(COALESCE(balance_cny, 0)) / SUM(SUM(COALESCE(balance_cny, 0))) OVER() * 100, 2) as percentage
FROM asset_snapshot 
WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
    AND COALESCE(balance_cny, 0) > 0
GROUP BY dimension_field
ORDER BY total_value DESC;
```

**应用场景**：平台资产分布、资产类型分布、时间分布

### 2. 趋势分析模板
**用途**：分析数据随时间的变化趋势
**SQL模式**：
```sql
SELECT 
    DATE_TRUNC('time_unit', snapshot_time) as time_period,
    dimension_field,
    SUM(COALESCE(balance_cny, 0)) as period_total,
    LAG(SUM(COALESCE(balance_cny, 0))) OVER (ORDER BY DATE_TRUNC('time_unit', snapshot_time)) as previous_period
FROM asset_snapshot 
WHERE snapshot_time >= start_date
    AND COALESCE(balance_cny, 0) > 0
GROUP BY time_period, dimension_field
ORDER BY time_period DESC;
```

**应用场景**：月度资产变化、季度收益趋势、年度增长率

### 3. 对比分析模板
**用途**：对比不同时间点或不同维度的数据
**SQL模式**：
```sql
WITH current_data AS (
    SELECT dimension_field, SUM(COALESCE(balance_cny, 0)) as current_value
    FROM asset_snapshot WHERE current_condition GROUP BY dimension_field
),
previous_data AS (
    SELECT dimension_field, SUM(COALESCE(balance_cny, 0)) as previous_value
    FROM asset_snapshot WHERE previous_condition GROUP BY dimension_field
)
SELECT 
    c.dimension_field,
    c.current_value,
    p.previous_value,
    c.current_value - p.previous_value as change_amount,
    CASE 
        WHEN p.previous_value = 0 THEN NULL
        ELSE ROUND((c.current_value - p.previous_value) / p.previous_value * 100, 2)
    END as change_percentage
FROM current_data c
LEFT JOIN previous_data p ON c.dimension_field = p.dimension_field;
```

**应用场景**：平台资产变化对比、资产类型增长对比

### 4. 排名分析模板
**用途**：找出表现最好或最差的资产
**SQL模式**：
```sql
SELECT 
    asset_name,
    platform,
    COALESCE(balance_cny, 0) as value,
    ROW_NUMBER() OVER (ORDER BY COALESCE(balance_cny, 0) DESC) as rank
FROM asset_snapshot
WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
    AND COALESCE(balance_cny, 0) > 0
ORDER BY value DESC
LIMIT top_n;
```

**应用场景**：前10大资产、收益率排名、风险排名

## 数据质量处理

### 1. NULL值处理
- 使用 `COALESCE(balance_cny, 0)` 处理数值字段的NULL值
- 使用 `COALESCE(asset_name, 'Unknown')` 处理文本字段的NULL值
- 在WHERE条件中明确处理NULL值：`WHERE balance_cny IS NOT NULL`

### 2. 异常值过滤
- 过滤掉余额为0或负数的记录：`WHERE COALESCE(balance_cny, 0) > 0`
- 过滤掉明显异常的时间范围：`WHERE snapshot_time >= '2020-01-01'`
- 使用统计方法识别异常值：`WHERE balance_cny BETWEEN avg_value - 3*std_value AND avg_value + 3*std_value`

### 3. 数据一致性
- 检查时间字段的格式一致性：使用标准的时间函数
- 验证平台和资产类型的枚举值：使用IN子句限制有效值
- 确保数值字段的数据类型正确：使用类型转换函数

## 性能优化要点

### 1. 索引使用
- 在 `platform`, `asset_type`, `snapshot_time` 字段上创建索引
- 创建复合索引：`(platform, asset_type)`, `(snapshot_time, platform)`
- 使用 `EXPLAIN ANALYZE` 验证索引使用情况

### 2. 查询优化
- 使用 `LIMIT` 限制结果行数，默认200行
- 使用 `OFFSET` 进行分页查询
- 避免在WHERE子句中使用函数，影响索引使用

### 3. 数据预处理
- 定期清理历史数据，保持表大小合理
- 使用物化视图优化复杂查询
- 考虑数据分区提高查询性能
"""
    
    def _get_query_optimization_guide(self) -> str:
        """查询优化指南"""
        return """# 查询优化指南

## 查询性能分析

### 1. 使用EXPLAIN分析查询计划
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT platform, SUM(balance_cny) 
FROM asset_snapshot 
WHERE snapshot_time >= '2024-01-01' 
GROUP BY platform;
```

### 2. 关键性能指标
- **执行时间**：查询的总执行时间
- **扫描行数**：实际扫描的数据行数
- **缓冲区使用**：内存缓冲区的使用情况
- **索引使用**：是否有效使用了索引

## 常见性能问题及解决方案

### 1. 全表扫描问题
**问题**：查询扫描了整个表，性能差
**解决方案**：
- 添加合适的WHERE条件
- 在过滤字段上创建索引
- 使用LIMIT限制结果行数

### 2. 索引失效问题
**问题**：索引存在但未被使用
**解决方案**：
- 避免在WHERE子句中使用函数
- 确保数据类型匹配
- 使用正确的比较操作符

### 3. 内存使用问题
**问题**：查询消耗过多内存
**解决方案**：
- 使用LIMIT限制返回行数
- 避免SELECT *
- 使用分页查询处理大量数据

## 优化最佳实践

### 1. 查询结构优化
- 使用CTE（WITH语句）简化复杂查询
- 避免嵌套子查询，使用JOIN替代
- 合理使用UNION和UNION ALL

### 2. 数据访问优化
- 只查询需要的字段，避免SELECT *
- 使用适当的JOIN类型（INNER, LEFT, RIGHT）
- 在JOIN条件中使用索引字段

### 3. 聚合查询优化
- 在GROUP BY之前使用WHERE过滤
- 使用HAVING对聚合结果进行过滤
- 考虑使用窗口函数替代子查询
"""

    def _postgresql_syntax_rules(self):
        """PostgreSQL特定的语法规则和约束"""
        return """
## PostgreSQL语法规则

### GROUP BY约束
- 使用GROUP BY时，SELECT中的非聚合字段必须出现在GROUP BY中
- 或者必须被包装在聚合函数中
- 避免在GROUP BY查询中使用窗口函数OVER()

### 窗口函数使用
- 窗口函数只能在非GROUP BY查询中使用
- 或者使用子查询来分离聚合和窗口计算
- 正确的模式：先计算聚合，再计算窗口函数

### 数据类型处理
- 使用CAST()进行明确的类型转换
- 注意PostgreSQL的严格类型检查
- 使用COALESCE处理NULL值

### 常见语法错误
1. **GROUP BY + 窗口函数冲突**：
   ```sql
   -- 错误示例
   SELECT platform, SUM(balance) OVER() FROM table GROUP BY platform
   
   -- 正确示例
   SELECT platform, SUM(balance) FROM table GROUP BY platform
   ```

2. **聚合函数使用**：
   ```sql
   -- 错误示例
   SELECT platform, balance FROM table GROUP BY platform
   
   -- 正确示例
   SELECT platform, SUM(balance) FROM table GROUP BY platform
   ```

### 最佳实践
1. **使用CTE分离复杂计算**：
   ```sql
   WITH aggregated AS (
       SELECT platform, SUM(balance) as total_balance
       FROM table GROUP BY platform
   )
   SELECT platform, total_balance, 
          total_balance * 100.0 / SUM(total_balance) OVER() as percentage
   FROM aggregated
   ```

2. **子查询结构**：
   ```sql
   SELECT platform, total_balance, percentage
   FROM (
       SELECT platform, SUM(balance) as total_balance
       FROM table GROUP BY platform
   ) t1
   CROSS JOIN (
       SELECT SUM(balance) as grand_total FROM table
   ) t2
   ```

3. **避免混合聚合和窗口函数**：
   - 先完成所有聚合计算
   - 再在结果集上应用窗口函数
"""
