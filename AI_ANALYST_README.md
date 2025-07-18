# AI分析师数据库快照使用指南

## 概述

本数据库快照为AI分析师提供了一个完整的多平台投资管理系统数据样本，包含基金、股票、加密货币、外汇等多个投资渠道的数据。通过分析这些数据，AI分析师可以提供投资建议、风险评估、策略优化等服务。

## 文件说明

### 1. `ai_analyst_database_snapshot.md`
- **内容**: 完整的数据库结构说明和示例数据
- **用途**: 了解数据库表结构、字段含义和数据关系
- **适合**: 初次接触数据库的分析师

### 2. `ai_analyst_database_schema.sql`
- **内容**: 完整的SQL脚本，包含表结构和示例数据
- **用途**: 直接在数据库中创建表结构和插入示例数据
- **适合**: 需要搭建本地测试环境的分析师

### 3. `ai_analyst_queries.sql`
- **内容**: 常用分析查询示例
- **用途**: 快速获取关键数据进行分析
- **适合**: 需要快速开始数据分析的分析师

## 数据库特点

### 多平台集成
- **蚂蚁财富**: 基金投资
- **IBKR**: 美股投资
- **OKX**: 加密货币交易
- **Wise**: 外汇管理
- **Web3**: 区块链资产

### 数据类型丰富
- **基金数据**: 净值、分红、费率等
- **股票数据**: 持仓、盈亏、交易记录
- **加密货币**: 余额、持仓、市场数据
- **外汇数据**: 汇率、交易记录
- **用户行为**: 操作记录、情绪评分、策略标签

### 时间序列完整
- 历史净值数据
- 操作记录时间线
- 汇率变化趋势
- 市场数据更新

## 快速开始

### 1. 环境准备
```bash
# 安装PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# 创建数据库
createdb investment_analysis

# 导入数据
psql -d investment_analysis -f ai_analyst_database_schema.sql
```

### 2. 基础查询示例
```sql
-- 查看投资组合总览
SELECT * FROM portfolio_overview;

-- 查看基金表现
SELECT * FROM fund_performance;

-- 查看定投效果
SELECT * FROM dca_performance;

-- 查看操作分析
SELECT * FROM operation_analysis;
```

### 3. 常用分析维度

#### 投资组合分析
- 资产配置比例
- 风险收益分析
- 相关性分析
- 夏普比率计算

#### 平台分析
- 各平台资产分布
- 平台收益率对比
- 平台费用分析

#### 时间序列分析
- 净值走势
- 收益率变化
- 波动率分析
- 定投效果分析

#### 行为分析
- 买卖时机分析
- 情绪评分分析
- 策略效果分析
- 定投执行分析

## 分析场景示例

### 场景1: 投资组合风险评估
```sql
-- 分析资产集中度
SELECT 
    asset_name,
    current_value,
    ROUND(current_value * 100.0 / SUM(current_value) OVER (), 2) as concentration_percent
FROM asset_positions 
ORDER BY current_value DESC;
```

### 场景2: 基金表现对比
```sql
-- 对比不同基金的表现
SELECT 
    f.fund_code,
    f.fund_name,
    f.fund_type,
    nav.growth_rate as latest_growth,
    ROUND((SELECT AVG(growth_rate) FROM fund_nav WHERE fund_code = f.fund_code AND nav_date >= CURRENT_DATE - INTERVAL '30 days'), 4) as avg_30d_growth
FROM fund_info f
LEFT JOIN (
    SELECT DISTINCT ON (fund_code) fund_code, growth_rate
    FROM fund_nav 
    ORDER BY fund_code, nav_date DESC
) nav ON f.fund_code = nav.fund_code
ORDER BY nav.growth_rate DESC;
```

### 场景3: 定投策略效果分析
```sql
-- 分析定投计划效果
SELECT 
    p.plan_name,
    p.asset_name,
    p.total_invested,
    pos.current_value,
    ROUND(((pos.current_value - p.total_invested) / p.total_invested) * 100, 2) as profit_rate_percent,
    p.smart_dca
FROM dca_plans p
LEFT JOIN asset_positions pos ON p.asset_code = pos.asset_code
WHERE p.status = 'active'
ORDER BY profit_rate_percent DESC;
```

### 场景4: 用户行为模式分析
```sql
-- 分析投资行为模式
SELECT 
    CASE 
        WHEN emotion_score >= 8 THEN '非常乐观'
        WHEN emotion_score >= 6 THEN '乐观'
        WHEN emotion_score >= 4 THEN '中性'
        WHEN emotion_score >= 2 THEN '悲观'
        ELSE '非常悲观'
    END as emotion_level,
    COUNT(*) as operation_count,
    AVG(amount) as avg_amount
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY emotion_level
ORDER BY operation_count DESC;
```

## 数据更新说明

### 实时数据
- IBKR持仓数据
- OKX市场数据
- Web3余额数据

### 每日数据
- 基金净值数据
- 汇率数据

### 定期数据
- 定投执行记录
- 系统配置更新

### 历史数据
- 用户操作记录
- 交易历史数据

## 注意事项

### 数据精度
- 所有金额字段使用DECIMAL类型确保精度
- 汇率数据支持6位小数
- 基金净值支持4位小数

### 时间处理
- 所有时间字段使用UTC时间
- 支持时区转换查询
- 历史数据按日期分区存储

### 数据完整性
- 关键表建立了唯一约束
- 外键关系确保数据一致性
- 索引优化查询性能

### 扩展性
- 标签字段使用JSON格式存储
- 支持自定义策略和标签
- 预留扩展字段

## 常见问题

### Q1: 如何添加新的资产类型？
A: 在`asset_positions`表中添加新记录，`asset_type`字段可以自定义。

### Q2: 如何分析多币种投资组合？
A: 使用`exchange_rates`表进行货币转换，参考查询8.2。

### Q3: 如何计算投资组合的夏普比率？
A: 使用基金净值数据计算收益率和波动率，参考查询2.3。

### Q4: 如何分析定投策略的效果？
A: 使用`dca_plans`和`asset_positions`表关联分析，参考查询3.1。

### Q5: 如何预测基金走势？
A: 使用移动平均线和趋势分析，参考查询10.1。

## 联系支持

如果在使用过程中遇到问题，可以：
1. 查看SQL查询示例文件
2. 参考数据库结构说明
3. 检查数据完整性约束
4. 验证查询语法正确性

## 版本信息

- **数据库版本**: PostgreSQL 12+
- **数据更新时间**: 2024年2月
- **数据范围**: 2024年1月-2月
- **平台支持**: 蚂蚁财富、IBKR、OKX、Wise、Web3

---

*本数据库快照仅供AI分析师学习和研究使用，数据为模拟数据，不构成投资建议。*