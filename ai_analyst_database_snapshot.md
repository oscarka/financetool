# AI分析师数据库快照

## 数据库概述

这是一个多平台投资管理系统数据库，集成了基金、股票、加密货币、外汇等多个投资渠道的数据。数据库采用PostgreSQL，支持实时数据同步和历史数据分析。

## 数据库表结构

### 1. 用户操作记录表 (user_operations)
记录用户的所有投资操作，包括买入、卖出、定投等。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| operation_date | DateTime | 操作日期时间 |
| platform | String(50) | 平台名称 |
| asset_type | String(50) | 资产类型 |
| operation_type | String(20) | 操作类型(buy/sell/dca) |
| asset_code | String(50) | 资产代码 |
| asset_name | String(100) | 资产名称 |
| amount | DECIMAL(15,4) | 操作金额 |
| currency | String(10) | 货币类型 |
| quantity | DECIMAL(15,8) | 数量 |
| price | DECIMAL(15,4) | 价格 |
| nav | DECIMAL(15,4) | 净值 |
| fee | DECIMAL(10,4) | 手续费 |
| strategy | Text | 策略说明 |
| emotion_score | Integer | 情绪评分 |
| tags | Text | 标签(JSON格式) |
| notes | Text | 备注 |
| status | String(20) | 状态 |
| dca_plan_id | Integer | 定投计划ID |
| dca_execution_type | String(20) | 定投执行类型 |

### 2. 资产持仓表 (asset_positions)
记录当前所有资产的持仓情况。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| platform | String(50) | 平台名称 |
| asset_type | String(50) | 资产类型 |
| asset_code | String(50) | 资产代码 |
| asset_name | String(100) | 资产名称 |
| currency | String(10) | 货币类型 |
| quantity | DECIMAL(15,8) | 持仓数量 |
| avg_cost | DECIMAL(15,4) | 平均成本 |
| current_price | DECIMAL(15,4) | 当前价格 |
| current_value | DECIMAL(15,4) | 当前价值 |
| total_invested | DECIMAL(15,4) | 总投资金额 |
| total_profit | DECIMAL(15,4) | 总收益 |
| profit_rate | DECIMAL(8,4) | 收益率 |

### 3. 基金信息表 (fund_info)
存储基金的基本信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| fund_code | String(20) | 基金代码 |
| fund_name | String(100) | 基金名称 |
| fund_type | String(50) | 基金类型 |
| management_fee | DECIMAL(5,4) | 管理费率 |
| purchase_fee | DECIMAL(5,4) | 申购费率 |
| redemption_fee | DECIMAL(5,4) | 赎回费率 |
| min_purchase | DECIMAL(10,2) | 最小申购金额 |
| risk_level | String(20) | 风险等级 |

### 4. 基金净值表 (fund_nav)
记录基金的历史净值数据。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| fund_code | String(20) | 基金代码 |
| nav_date | Date | 净值日期 |
| nav | DECIMAL(10,4) | 单位净值 |
| accumulated_nav | DECIMAL(10,4) | 累计净值 |
| growth_rate | DECIMAL(8,4) | 增长率 |
| source | String(50) | 数据来源 |

### 5. 定投计划表 (dca_plans)
管理定投计划配置。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| plan_name | String(100) | 计划名称 |
| platform | String(50) | 平台 |
| asset_type | String(50) | 资产类型 |
| asset_code | String(50) | 资产代码 |
| asset_name | String(100) | 资产名称 |
| amount | DECIMAL(10,2) | 定投金额 |
| currency | String(10) | 货币类型 |
| frequency | String(20) | 频率 |
| frequency_value | Integer | 频率值 |
| start_date | Date | 开始日期 |
| end_date | Date | 结束日期 |
| status | String(20) | 状态 |
| smart_dca | Boolean | 是否智能定投 |
| base_amount | DECIMAL(10,2) | 基础金额 |
| max_amount | DECIMAL(10,2) | 最大金额 |

### 6. 汇率表 (exchange_rates)
存储货币汇率数据。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| from_currency | String(10) | 源货币 |
| to_currency | String(10) | 目标货币 |
| rate | DECIMAL(15,6) | 汇率 |
| rate_date | Date | 汇率日期 |
| source | String(50) | 数据来源 |

### 7. IBKR账户相关表
- ibkr_accounts: IBKR账户信息
- ibkr_balances: IBKR余额数据
- ibkr_positions: IBKR持仓数据
- ibkr_sync_logs: IBKR同步日志

### 8. OKX交易所相关表
- okx_balances: OKX余额数据
- okx_transactions: OKX交易记录
- okx_positions: OKX持仓数据
- okx_market_data: OKX市场数据
- okx_account_overview: OKX账户总览

### 9. Wise支付相关表
- wise_transactions: Wise交易记录
- wise_balances: Wise余额数据
- wise_exchange_rates: Wise汇率数据

### 10. Web3相关表
- web3_balances: Web3余额数据
- web3_tokens: Web3代币数据
- web3_transactions: Web3交易记录

## 示例数据

### 用户操作记录示例
```sql
INSERT INTO user_operations VALUES
(1, '2024-01-15 14:30:00', '蚂蚁财富', '基金', 'buy', '000001', '华夏成长混合', 1000.00, 'CNY', 1000.00, 1.0000, 1.0000, 0.00, '价值投资', 7, '["长期投资", "价值投资"]', '看好科技成长股', 'completed', NULL, NULL),
(2, '2024-01-20 10:15:00', '蚂蚁财富', '基金', 'buy', '000002', '易方达消费行业', 2000.00, 'CNY', 2000.00, 1.5000, 1.5000, 0.00, '消费升级', 8, '["消费", "蓝筹"]', '消费行业长期看好', 'completed', NULL, NULL),
(3, '2024-02-01 09:00:00', 'IBKR', '股票', 'buy', 'AAPL', 'Apple Inc.', 5000.00, 'USD', 25.00, 200.00, 200.00, 1.00, '科技股投资', 9, '["科技", "蓝筹"]', '苹果公司长期价值', 'completed', NULL, NULL),
(4, '2024-02-10 15:30:00', 'OKX', '加密货币', 'buy', 'BTC-USDT', 'Bitcoin', 3000.00, 'USDT', 0.075, 40000.00, 40000.00, 0.00, '数字黄金', 6, '["加密货币", "长期持有"]', '比特币减半预期', 'completed', NULL, NULL),
(5, '2024-02-15 14:00:00', '蚂蚁财富', '基金', 'dca', '000001', '华夏成长混合', 500.00, 'CNY', 500.00, 1.0500, 1.0500, 0.00, '定投策略', 5, '["定投", "长期投资"]', '定期定额投资', 'completed', 1, 'scheduled');
```

### 资产持仓示例
```sql
INSERT INTO asset_positions VALUES
(1, '蚂蚁财富', '基金', '000001', '华夏成长混合', 'CNY', 1500.00, 1.0250, 1.0800, 1620.00, 1500.00, 120.00, 0.0800),
(2, '蚂蚁财富', '基金', '000002', '易方达消费行业', 'CNY', 2000.00, 1.5000, 1.6500, 3300.00, 2000.00, 1300.00, 0.6500),
(3, 'IBKR', '股票', 'AAPL', 'Apple Inc.', 'USD', 25.00, 200.00, 220.00, 5500.00, 5000.00, 500.00, 0.1000),
(4, 'OKX', '加密货币', 'BTC-USDT', 'Bitcoin', 'USDT', 0.075, 40000.00, 45000.00, 3375.00, 3000.00, 375.00, 0.1250),
(5, 'Wise', '外汇', 'USD', 'US Dollar', 'USD', 10000.00, 1.0000, 1.0000, 10000.00, 10000.00, 0.00, 0.0000);
```

### 基金信息示例
```sql
INSERT INTO fund_info VALUES
(1, '000001', '华夏成长混合', '混合型', 0.0150, 0.0015, 0.0000, 100.00, '中风险'),
(2, '000002', '易方达消费行业', '股票型', 0.0150, 0.0015, 0.0000, 100.00, '高风险'),
(3, '000003', '招商中证白酒', '指数型', 0.0100, 0.0010, 0.0000, 100.00, '高风险'),
(4, '000004', '工银瑞信货币', '货币型', 0.0033, 0.0000, 0.0000, 1.00, '低风险'),
(5, '000005', '南方中证500ETF', 'ETF', 0.0050, 0.0005, 0.0000, 100.00, '中风险');
```

### 基金净值示例
```sql
INSERT INTO fund_nav VALUES
(1, '000001', '2024-01-15', 1.0000, 1.0000, 0.0000, 'api'),
(2, '000001', '2024-01-16', 1.0050, 1.0050, 0.0050, 'api'),
(3, '000001', '2024-01-17', 1.0100, 1.0100, 0.0050, 'api'),
(4, '000001', '2024-01-18', 1.0080, 1.0080, -0.0020, 'api'),
(5, '000001', '2024-01-19', 1.0150, 1.0150, 0.0070, 'api'),
(6, '000002', '2024-01-20', 1.5000, 1.5000, 0.0000, 'api'),
(7, '000002', '2024-01-21', 1.5200, 1.5200, 0.0133, 'api'),
(8, '000002', '2024-01-22', 1.5500, 1.5500, 0.0197, 'api'),
(9, '000002', '2024-01-23', 1.5800, 1.5800, 0.0194, 'api'),
(10, '000002', '2024-01-24', 1.6500, 1.6500, 0.0443, 'api');
```

### 定投计划示例
```sql
INSERT INTO dca_plans VALUES
(1, '华夏成长定投', '蚂蚁财富', '基金', '000001', '华夏成长混合', 500.00, 'CNY', 'weekly', 7, '2024-01-15', NULL, 'active', '价值投资策略', '15:00', '2024-02-19', '2024-02-12', 5, 2500.00, 2500.00, false, 500.00, 1000.00, 0.1000, 0.8000, 1.2000, true, true, 30, 0.0015, '["2024-02-10", "2024-02-11"]'),
(2, '消费行业定投', '蚂蚁财富', '基金', '000002', '易方达消费行业', 1000.00, 'CNY', 'monthly', 30, '2024-01-20', NULL, 'active', '消费升级策略', '15:00', '2024-02-20', '2024-01-20', 1, 1000.00, 1000.00, true, 1000.00, 2000.00, 0.1500, 1.4000, 1.8000, true, true, 30, 0.0015, '[]'),
(3, '比特币定投', 'OKX', '加密货币', 'BTC-USDT', 'Bitcoin', 100.00, 'USDT', 'weekly', 7, '2024-02-01', NULL, 'active', '数字黄金策略', '10:00', '2024-02-19', '2024-02-12', 2, 200.00, 0.005, false, 100.00, 200.00, 0.2000, 35000.00, 50000.00, true, true, 30, 0.0010, '[]');
```

### 汇率数据示例
```sql
INSERT INTO exchange_rates VALUES
(1, 'USD', 'CNY', 7.2000, '2024-01-15', 'api'),
(2, 'USD', 'CNY', 7.2100, '2024-01-16', 'api'),
(3, 'USD', 'CNY', 7.1900, '2024-01-17', 'api'),
(4, 'USD', 'CNY', 7.2200, '2024-01-18', 'api'),
(5, 'USD', 'CNY', 7.1800, '2024-01-19', 'api'),
(6, 'EUR', 'USD', 1.0850, '2024-01-15', 'api'),
(7, 'EUR', 'USD', 1.0870, '2024-01-16', 'api'),
(8, 'EUR', 'USD', 1.0830, '2024-01-17', 'api'),
(9, 'EUR', 'USD', 1.0890, '2024-01-18', 'api'),
(10, 'EUR', 'USD', 1.0810, '2024-01-19', 'api');
```

### IBKR数据示例
```sql
INSERT INTO ibkr_accounts VALUES
(1, 'U123456789', '个人投资账户', 'INDIVIDUAL', 'USD', 'ACTIVE');

INSERT INTO ibkr_balances VALUES
(1, 'U123456789', 15000.00, 25000.00, 20000.00, 'USD', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler');

INSERT INTO ibkr_positions VALUES
(1, 'U123456789', 'AAPL', 25.00, 5500.00, 200.00, 500.00, 0.00, 'USD', 'STK', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler'),
(2, 'U123456789', 'TSLA', 10.00, 1800.00, 180.00, 0.00, 0.00, 'USD', 'STK', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler'),
(3, 'U123456789', 'SPY', 50.00, 25000.00, 500.00, 0.00, 0.00, 'USD', 'STK', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler');
```

### OKX数据示例
```sql
INSERT INTO okx_balances VALUES
(1, 'OKX001', 'BTC', 0.075, 0.000, 0.075, 'trading', '2024-02-15 16:00:00'),
(2, 'OKX001', 'USDT', 5000.00, 0.000, 5000.00, 'trading', '2024-02-15 16:00:00'),
(3, 'OKX001', 'ETH', 2.50, 0.000, 2.50, 'trading', '2024-02-15 16:00:00');

INSERT INTO okx_positions VALUES
(1, 'OKX001', 'SPOT', 'BTC-USDT', 'long', 'pos_001', 0.075, 40000.00, 375.00, 0.00, 0.00, 45000.00, 'USD', '2024-02-15 16:00:00'),
(2, 'OKX001', 'SPOT', 'ETH-USDT', 'long', 'pos_002', 2.50, 2500.00, 1250.00, 0.00, 0.00, 3000.00, 'USD', '2024-02-15 16:00:00');

INSERT INTO okx_market_data VALUES
(1, 'BTC-USDT', 'SPOT', 45000.00, 44999.00, 45001.00, 46000.00, 44000.00, 1000.00, 5000.00, 0.1250, '2024-02-15 16:00:00'),
(2, 'ETH-USDT', 'SPOT', 3000.00, 2999.00, 3001.00, 3100.00, 2900.00, 500.00, 100.00, 0.0345, '2024-02-15 16:00:00');
```

### Wise数据示例
```sql
INSERT INTO wise_transactions VALUES
(1, 'profile_001', 'account_001', 'txn_001', 'TRANSFER', 1000.00, 'USD', 'Transfer to investment account', 'Investment transfer', '2024-02-15 10:00:00', 'COMPLETED', 'REF001'),
(2, 'profile_001', 'account_001', 'txn_002', 'INTERBALANCE', 500.00, 'EUR', 'Currency conversion', 'EUR to USD conversion', '2024-02-15 11:00:00', 'COMPLETED', 'REF002');

INSERT INTO wise_balances VALUES
(1, 'account_001', 'USD', 5000.00, 0.00, 5000.00, 5000.00, 'STANDARD', 'ACTIVE', '2024-01-01 00:00:00', '2024-02-15 16:00:00', true, true, '2024-02-15 16:00:00'),
(2, 'account_002', 'EUR', 3000.00, 0.00, 3000.00, 3000.00, 'STANDARD', 'ACTIVE', '2024-01-01 00:00:00', '2024-02-15 16:00:00', true, false, '2024-02-15 16:00:00');
```

### Web3数据示例
```sql
INSERT INTO web3_balances VALUES
(1, 'ethereum_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 15000.00, 'USD', '2024-02-15 16:00:00'),
(2, 'polygon_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 5000.00, 'USD', '2024-02-15 16:00:00');

INSERT INTO web3_tokens VALUES
(1, 'ethereum_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'ETH', 'Ethereum', '0x0000000000000000000000000000000000000000', 5.00, 15000.00, 3000.00, '2024-02-15 16:00:00'),
(2, 'ethereum_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'USDC', 'USD Coin', '0xA0b86a33E6441b8C4C9db96C4b4d8b6', 1000.00, 1000.00, 1.00, '2024-02-15 16:00:00'),
(3, 'polygon_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'MATIC', 'Polygon', '0x0000000000000000000000000000000000001010', 10000.00, 5000.00, 0.50, '2024-02-15 16:00:00');
```

## 数据分析维度

### 1. 投资组合分析
- 资产配置比例
- 风险收益分析
- 相关性分析
- 夏普比率计算

### 2. 平台分析
- 各平台资产分布
- 平台收益率对比
- 平台费用分析

### 3. 时间序列分析
- 净值走势
- 收益率变化
- 波动率分析
- 定投效果分析

### 4. 资产类别分析
- 基金表现分析
- 股票投资分析
- 加密货币分析
- 外汇投资分析

### 5. 操作行为分析
- 买卖时机分析
- 情绪评分分析
- 策略效果分析
- 定投执行分析

## 常用查询示例

### 1. 获取当前投资组合总览
```sql
SELECT 
    platform,
    asset_type,
    SUM(current_value) as total_value,
    SUM(total_invested) as total_invested,
    SUM(total_profit) as total_profit,
    AVG(profit_rate) as avg_profit_rate
FROM asset_positions 
GROUP BY platform, asset_type
ORDER BY total_value DESC;
```

### 2. 获取基金净值走势
```sql
SELECT 
    nav_date,
    nav,
    growth_rate,
    LAG(nav) OVER (ORDER BY nav_date) as prev_nav,
    (nav - LAG(nav) OVER (ORDER BY nav_date)) / LAG(nav) OVER (ORDER BY nav_date) as daily_return
FROM fund_nav 
WHERE fund_code = '000001'
ORDER BY nav_date;
```

### 3. 分析定投效果
```sql
SELECT 
    p.plan_name,
    p.asset_name,
    p.total_invested,
    p.total_shares,
    pos.current_value,
    (pos.current_value - p.total_invested) as profit,
    ((pos.current_value - p.total_invested) / p.total_invested) as profit_rate
FROM dca_plans p
JOIN asset_positions pos ON p.asset_code = pos.asset_code
WHERE p.status = 'active';
```

### 4. 获取操作历史分析
```sql
SELECT 
    DATE(operation_date) as op_date,
    operation_type,
    asset_type,
    SUM(amount) as total_amount,
    COUNT(*) as operation_count,
    AVG(emotion_score) as avg_emotion
FROM user_operations 
WHERE operation_date >= '2024-01-01'
GROUP BY DATE(operation_date), operation_type, asset_type
ORDER BY op_date DESC;
```

## 数据更新频率

- **实时数据**: IBKR持仓、OKX市场数据、Web3余额
- **每日数据**: 基金净值、汇率数据
- **定期数据**: 定投执行、系统配置
- **历史数据**: 用户操作记录、交易历史

## 注意事项

1. 所有金额字段都使用DECIMAL类型确保精度
2. 时间字段统一使用UTC时间
3. 汇率数据支持多货币转换
4. 情绪评分范围1-10，用于分析投资行为
5. 标签字段使用JSON格式存储，便于扩展
6. 所有表都有created_at和updated_at时间戳
7. 关键表建立了适当的索引以提高查询性能