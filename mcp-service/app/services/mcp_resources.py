"""MCP Resources管理器 - 提供数据库schema和示例查询资源"""

import json
import logging
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPResourcesManager:
    """MCP Resources管理器 - 生成和管理数据库相关资源"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.resources = {}
        self._generate_resources()
    
    def _generate_resources(self):
        """生成所有可用的Resources"""
        try:
            self.resources = {
                "db://schema/overview.md": self._generate_schema_overview(),
                "db://schema/tables/asset_snapshot.json": self._generate_table_schema("asset_snapshot"),
                "db://examples/queries.sql": self._generate_example_queries(),
                "db://examples/analysis_patterns.md": self._generate_analysis_patterns()
            }
            logger.info(f"✅ 成功生成 {len(self.resources)} 个MCP Resources")
        except Exception as e:
            logger.error(f"❌ 生成Resources失败: {e}")
            # 使用默认资源
            self.resources = self._get_default_resources()
    
    def get_resource(self, uri: str) -> Optional[str]:
        """获取指定URI的资源"""
        return self.resources.get(uri)
    
    def get_all_resources(self) -> Dict[str, str]:
        """获取所有可用的Resources"""
        return self.resources
    
    def list_resources(self) -> List[str]:
        """列出所有可用的Resource URI"""
        return list(self.resources.keys())
    
    def _generate_schema_overview(self) -> str:
        """生成业务域到schema的映射文档"""
        return """# 财务数据库Schema总览

## 核心业务域

### 1. 资产快照 (asset_snapshot)
- **业务含义**：各平台资产的实时快照，用于资产分布分析和趋势监控
- **主要字段**：
  - `platform`: 平台名称 (支付宝, Wise, IBKR, OKX, Web3)
  - `asset_type`: 资产类型 (基金, 外汇, 股票, 数字货币, 现金, 储蓄)
  - `asset_code`: 资产代码 (如: 005827, USD, AAPL, BTC)
  - `asset_name`: 资产名称
  - `balance_cny`: 人民币余额 - 主要分析字段（可能为NULL）
  - `snapshot_time`: 快照时间 - 用于时间序列分析
- **分析场景**：资产分布、平台对比、类型分析、时间趋势

### 2. 交易历史 (transaction_history)  
- **业务含义**：所有交易操作的记录，用于交易分析和收益计算
- **主要字段**：
  - `operation_date`: 操作时间
  - `platform`: 操作平台
  - `operation_type`: 操作类型 (买入, 卖出, 转账, 分红)
  - `amount`: 操作金额
  - `quantity`: 操作数量
  - `price`: 价格
- **分析场景**：交易趋势、收益分析、操作频率、成本分析

### 3. 资产持仓 (asset_positions)
- **业务含义**：当前持仓的详细信息，用于持仓分析和风险评估
- **主要字段**：
  - `quantity`: 持仓数量
  - `current_value`: 当前价值
  - `total_invested`: 总投入
  - `total_profit`: 总收益
  - `profit_rate`: 收益率
- **分析场景**：持仓分析、收益计算、风险评估、投资组合优化

## 数据关系
- `asset_snapshot` 是核心事实表，包含所有资产的最新状态
- `transaction_history` 记录所有操作，用于追踪资产变化
- `asset_positions` 提供持仓的汇总视图，便于快速分析

## 常用分析维度
1. **平台维度**：按平台分析资产分布和表现
2. **资产类型维度**：按资产类型分析风险和收益
3. **时间维度**：按日、周、月、季度分析趋势
4. **价值维度**：按余额、收益、收益率等数值分析

## 数据质量说明
- `balance_cny` 字段可能为NULL，需要使用 `COALESCE(balance_cny, 0)` 处理
- `snapshot_time` 使用UTC时间，分析时注意时区处理
- 历史数据可能不完整，分析时建议指定明确的时间范围
"""
    
    def _generate_table_schema(self, table_name: str) -> str:
        """生成表的详细JSON schema"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 获取字段信息
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default, 
                               character_maximum_length, numeric_precision, numeric_scale,
                               ordinal_position
                        FROM information_schema.columns 
                        WHERE table_name = %s AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """, (table_name,))
                    
                    columns = cursor.fetchall()
                    
                    # 获取主键信息
                    cursor.execute("""
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY' 
                            AND tc.table_name = %s
                    """, (table_name,))
                    
                    primary_keys = [row["column_name"] for row in cursor.fetchall()]
                    
                    # 获取索引信息
                    cursor.execute("""
                        SELECT indexname, indexdef
                        FROM pg_indexes 
                        WHERE tablename = %s
                    """, (table_name,))
                    
                    indexes = [{"name": row["indexname"], "definition": row["indexdef"]} 
                              for row in cursor.fetchall()]
                    
                    # 获取表统计信息
                    cursor.execute("""
                        SELECT n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
                        FROM pg_stat_user_tables 
                        WHERE relname = %s
                    """, (table_name,))
                    
                    stats = cursor.fetchone()
                    
                    schema = {
                        "table_name": table_name,
                        "generated_at": datetime.now().isoformat(),
                        "columns": [
                            {
                                "name": col["column_name"],
                                "type": col["data_type"],
                                "nullable": col["is_nullable"] == "YES",
                                "default": col["column_default"],
                                "max_length": col["character_maximum_length"],
                                "precision": col["numeric_precision"],
                                "scale": col["numeric_scale"],
                                "position": col["ordinal_position"]
                            }
                            for col in columns
                        ],
                        "primary_keys": primary_keys,
                        "indexes": indexes,
                        "statistics": {
                            "total_rows": stats["n_live_tup"] if stats else 0,
                            "inserted_rows": stats["n_tup_ins"] if stats else 0,
                            "updated_rows": stats["n_tup_upd"] if stats else 0,
                            "deleted_rows": stats["n_tup_del"] if stats else 0
                        },
                        "total_columns": len(columns)
                    }
                    
                    return json.dumps(schema, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            logger.error(f"获取表 {table_name} 的schema失败: {e}")
            return json.dumps({
                "error": f"获取表schema失败: {str(e)}",
                "table_name": table_name
            }, ensure_ascii=False, indent=2)
    
    def _generate_example_queries(self) -> str:
        """生成高质量示例查询"""
        return """-- ========================================
-- 财务数据分析示例查询
-- ========================================

-- 1. 平台资产分布分析
-- 用途：分析各平台资产占比，了解资产配置情况
SELECT 
    platform,
    SUM(COALESCE(balance_cny, 0)) as total_value,
    COUNT(*) as asset_count,
    ROUND(SUM(COALESCE(balance_cny, 0)) / SUM(SUM(COALESCE(balance_cny, 0))) OVER() * 100, 2) as percentage
FROM asset_snapshot 
WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
    AND COALESCE(balance_cny, 0) > 0
GROUP BY platform 
ORDER BY total_value DESC;

-- 2. 资产类型趋势分析
-- 用途：分析各资产类型的历史变化趋势
SELECT 
    DATE_TRUNC('month', snapshot_time) as month,
    asset_type,
    SUM(COALESCE(balance_cny, 0)) as monthly_total,
    COUNT(*) as asset_count
FROM asset_snapshot 
WHERE snapshot_time >= CURRENT_DATE - INTERVAL '12 months'
    AND COALESCE(balance_cny, 0) > 0
GROUP BY month, asset_type 
ORDER BY month DESC, monthly_total DESC;

-- 3. 平台资产变化对比
-- 用途：对比不同时间点的平台资产变化
WITH current_snapshot AS (
    SELECT platform, SUM(COALESCE(balance_cny, 0)) as current_value
    FROM asset_snapshot 
    WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
    GROUP BY platform
),
previous_snapshot AS (
    SELECT platform, SUM(COALESCE(balance_cny, 0)) as previous_value
    FROM asset_snapshot 
    WHERE snapshot_time = (
        SELECT MAX(snapshot_time) 
        FROM asset_snapshot 
        WHERE snapshot_time < (SELECT MAX(snapshot_time) FROM asset_snapshot)
    )
    GROUP BY platform
)
SELECT 
    c.platform,
    c.current_value,
    COALESCE(p.previous_value, 0) as previous_value,
    c.current_value - COALESCE(p.previous_value, 0) as change_amount,
    CASE 
        WHEN COALESCE(p.previous_value, 0) = 0 THEN NULL
        ELSE ROUND((c.current_value - p.previous_value) / p.previous_value * 100, 2)
    END as change_percentage
FROM current_snapshot c
LEFT JOIN previous_snapshot p ON c.platform = p.platform
ORDER BY change_percentage DESC NULLS LAST;

-- 4. 资产类型分布详情
-- 用途：深入了解各资产类型的详细分布
SELECT 
    asset_type,
    platform,
    COUNT(*) as asset_count,
    SUM(COALESCE(balance_cny, 0)) as total_value,
    AVG(COALESCE(balance_cny, 0)) as avg_value,
    MIN(COALESCE(balance_cny, 0)) as min_value,
    MAX(COALESCE(balance_cny, 0)) as max_value
FROM asset_snapshot 
WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
    AND COALESCE(balance_cny, 0) > 0
GROUP BY asset_type, platform
ORDER BY asset_type, total_value DESC;

-- 5. 时间序列资产变化
-- 用途：分析资产总量的时间变化趋势
SELECT 
    DATE_TRUNC('day', snapshot_time) as day,
    SUM(COALESCE(balance_cny, 0)) as daily_total,
    COUNT(*) as asset_count,
    LAG(SUM(COALESCE(balance_cny, 0))) OVER (ORDER BY DATE_TRUNC('day', snapshot_time)) as previous_day_total
FROM asset_snapshot 
WHERE snapshot_time >= CURRENT_DATE - INTERVAL '30 days'
    AND COALESCE(balance_cny, 0) > 0
GROUP BY day
ORDER BY day;

-- 6. 平台资产集中度分析
-- 用途：分析各平台资产的集中程度
WITH platform_stats AS (
    SELECT 
        platform,
        SUM(COALESCE(balance_cny, 0)) as total_value,
        COUNT(*) as asset_count,
        AVG(COALESCE(balance_cny, 0)) as avg_value,
        STDDEV(COALESCE(balance_cny, 0)) as std_value
    FROM asset_snapshot 
    WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM asset_snapshot)
        AND COALESCE(balance_cny, 0) > 0
    GROUP BY platform
)
SELECT 
    platform,
    total_value,
    asset_count,
    avg_value,
    std_value,
    CASE 
        WHEN avg_value = 0 THEN NULL
        ELSE ROUND(std_value / avg_value * 100, 2)
    END as coefficient_of_variation
FROM platform_stats
ORDER BY total_value DESC;

-- 注意事项：
-- 1. 所有查询都使用了COALESCE处理NULL值
-- 2. 时间范围明确指定，避免全表扫描
-- 3. 使用LIMIT限制结果行数（示例中省略，实际使用时需要添加）
-- 4. 优先使用索引字段进行过滤和排序
"""
    
    def _generate_analysis_patterns(self) -> str:
        """生成分析模式指南"""
        return """# 财务数据分析模式指南

## 常用分析模式

### 1. 分布分析模式
**适用场景**：了解资产在不同维度的分布情况
**SQL模式**：
```sql
SELECT 
    dimension_field,
    SUM(value_field) as total_value,
    COUNT(*) as count,
    ROUND(SUM(value_field) / SUM(SUM(value_field)) OVER() * 100, 2) as percentage
FROM table_name
WHERE conditions
GROUP BY dimension_field
ORDER BY total_value DESC;
```

**示例**：平台资产分布、资产类型分布、时间分布

### 2. 趋势分析模式
**适用场景**：分析数据随时间的变化趋势
**SQL模式**：
```sql
SELECT 
    DATE_TRUNC('time_unit', time_field) as time_period,
    dimension_field,
    SUM(value_field) as period_total
FROM table_name
WHERE time_field >= start_date
GROUP BY time_period, dimension_field
ORDER BY time_period DESC, period_total DESC;
```

**示例**：月度资产变化、季度收益趋势、年度增长率

### 3. 对比分析模式
**适用场景**：对比不同时间点或不同维度的数据
**SQL模式**：
```sql
WITH current_data AS (
    SELECT dimension_field, SUM(value_field) as current_value
    FROM table_name WHERE current_condition GROUP BY dimension_field
),
previous_data AS (
    SELECT dimension_field, SUM(value_field) as previous_value
    FROM table_name WHERE previous_condition GROUP BY dimension_field
)
SELECT 
    c.dimension_field,
    c.current_value,
    p.previous_value,
    c.current_value - p.previous_value as change_amount,
    ROUND((c.current_value - p.previous_value) / p.previous_value * 100, 2) as change_percentage
FROM current_data c
LEFT JOIN previous_data p ON c.dimension_field = p.dimension_field;
```

**示例**：平台资产变化对比、资产类型增长对比

### 4. 排名分析模式
**适用场景**：找出表现最好或最差的资产
**SQL模式**：
```sql
SELECT 
    asset_name,
    platform,
    value_field,
    ROW_NUMBER() OVER (ORDER BY value_field DESC) as rank
FROM table_name
WHERE conditions
ORDER BY value_field DESC
LIMIT top_n;
```

**示例**：前10大资产、收益率排名、风险排名

### 5. 聚合统计模式
**适用场景**：获取数据的统计摘要信息
**SQL模式**：
```sql
SELECT 
    dimension_field,
    COUNT(*) as count,
    SUM(value_field) as total,
    AVG(value_field) as average,
    MIN(value_field) as minimum,
    MAX(value_field) as maximum,
    STDDEV(value_field) as standard_deviation
FROM table_name
WHERE conditions
GROUP BY dimension_field;
```

**示例**：平台资产统计、资产类型统计

## 性能优化建议

### 1. 索引使用
- 在 `platform`, `asset_type`, `snapshot_time` 字段上创建索引
- 复合索引：`(platform, asset_type)`, `(snapshot_time, platform)`

### 2. 查询优化
- 使用 `EXPLAIN ANALYZE` 分析查询计划
- 避免在WHERE子句中使用函数
- 合理使用LIMIT限制结果行数

### 3. 数据预处理
- 定期清理历史数据
- 使用物化视图优化复杂查询
- 考虑数据分区提高查询性能

## 数据质量处理

### 1. NULL值处理
- 使用 `COALESCE(field, 0)` 处理数值字段的NULL值
- 使用 `COALESCE(field, 'Unknown')` 处理文本字段的NULL值

### 2. 异常值过滤
- 过滤掉余额为0或负数的记录
- 过滤掉明显异常的时间范围
- 使用统计方法识别异常值

### 3. 数据一致性
- 检查时间字段的格式一致性
- 验证平台和资产类型的枚举值
- 确保数值字段的数据类型正确
"""
    
    def _get_default_resources(self) -> Dict[str, str]:
        """获取默认资源（当数据库连接失败时使用）"""
        return {
            "db://schema/overview.md": self._generate_schema_overview(),
            "db://examples/queries.sql": self._generate_example_queries(),
            "db://examples/analysis_patterns.md": self._generate_analysis_patterns()
        }
