# 数据库设计文档

## 📋 核心表结构

### 1. 用户操作记录表 (user_operations)
记录用户的所有投资决策和操作

```sql
CREATE TABLE user_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_date DATETIME NOT NULL,           -- 操作日期时间
    platform VARCHAR(50) NOT NULL,              -- 平台：支付宝、OKX、Wise等
    asset_type VARCHAR(50) NOT NULL,            -- 资产类型：基金、数字货币、外汇等
    operation_type VARCHAR(20) NOT NULL,        -- 操作类型：买入、卖出、转入、转出等
    asset_code VARCHAR(50) NOT NULL,            -- 资产代码：基金代码、币种等
    asset_name VARCHAR(100) NOT NULL,           -- 资产名称
    amount DECIMAL(15,4) NOT NULL,              -- 操作金额
    currency VARCHAR(10) NOT NULL,              -- 币种：CNY、USD、USDT等
    quantity DECIMAL(15,8),                     -- 数量/份额（系统自动计算）
    price DECIMAL(15,4),                        -- 价格/净值（系统自动获取）
    fee DECIMAL(10,4) DEFAULT 0,                -- 手续费
    strategy TEXT,                              -- 策略逻辑
    emotion_score INTEGER,                      -- 情绪评分 1-10
    tags TEXT,                                  -- 标签，JSON格式
    notes TEXT,                                 -- 备注
    status VARCHAR(20) DEFAULT 'pending',       -- 状态：pending、confirmed、cancelled
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 资产持仓表 (asset_positions)
记录当前所有资产的持仓状态

```sql
CREATE TABLE asset_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR(50) NOT NULL,              -- 平台
    asset_type VARCHAR(50) NOT NULL,            -- 资产类型
    asset_code VARCHAR(50) NOT NULL,            -- 资产代码
    asset_name VARCHAR(100) NOT NULL,           -- 资产名称
    currency VARCHAR(10) NOT NULL,              -- 币种
    quantity DECIMAL(15,8) NOT NULL,            -- 当前数量
    avg_cost DECIMAL(15,4) NOT NULL,            -- 平均成本
    current_price DECIMAL(15,4) NOT NULL,       -- 当前价格
    current_value DECIMAL(15,4) NOT NULL,       -- 当前市值
    total_invested DECIMAL(15,4) NOT NULL,      -- 累计投入
    total_profit DECIMAL(15,4) NOT NULL,        -- 累计收益
    profit_rate DECIMAL(8,4) NOT NULL,          -- 收益率
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, asset_code, currency)
);
```

### 3. 基金信息表 (fund_info)
存储基金的基本信息

```sql
CREATE TABLE fund_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(20) UNIQUE NOT NULL,      -- 基金代码
    fund_name VARCHAR(100) NOT NULL,            -- 基金名称
    fund_type VARCHAR(50),                      -- 基金类型：股票型、债券型等
    management_fee DECIMAL(5,4),                -- 管理费率
    purchase_fee DECIMAL(5,4),                  -- 申购费率
    redemption_fee DECIMAL(5,4),                -- 赎回费率
    min_purchase DECIMAL(10,2),                 -- 最小申购金额
    risk_level VARCHAR(20),                     -- 风险等级
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 基金净值表 (fund_nav)
记录基金每日净值

```sql
CREATE TABLE fund_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(20) NOT NULL,             -- 基金代码
    nav_date DATE NOT NULL,                     -- 净值日期
    nav DECIMAL(10,4) NOT NULL,                 -- 单位净值
    accumulated_nav DECIMAL(10,4),              -- 累计净值
    growth_rate DECIMAL(8,4),                   -- 日增长率
    source VARCHAR(50) DEFAULT 'api',           -- 数据来源
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, nav_date),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code)
);
```

### 5. 定投计划表 (dca_plans)
记录定投计划

```sql
CREATE TABLE dca_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name VARCHAR(100) NOT NULL,            -- 计划名称
    platform VARCHAR(50) NOT NULL,              -- 平台
    asset_code VARCHAR(50) NOT NULL,            -- 资产代码
    asset_name VARCHAR(100) NOT NULL,           -- 资产名称
    amount DECIMAL(10,2) NOT NULL,              -- 定投金额
    currency VARCHAR(10) NOT NULL,              -- 币种
    frequency VARCHAR(20) NOT NULL,             -- 频率：daily、weekly、monthly
    frequency_value INTEGER NOT NULL,           -- 频率值：1、7、30等
    start_date DATE NOT NULL,                   -- 开始日期
    end_date DATE,                              -- 结束日期（可选）
    status VARCHAR(20) DEFAULT 'active',        -- 状态：active、paused、stopped
    strategy TEXT,                              -- 定投策略
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6. 汇率表 (exchange_rates)
记录汇率信息

```sql
CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_currency VARCHAR(10) NOT NULL,         -- 源币种
    to_currency VARCHAR(10) NOT NULL,           -- 目标币种
    rate DECIMAL(15,6) NOT NULL,                -- 汇率
    rate_date DATE NOT NULL,                    -- 汇率日期
    source VARCHAR(50) DEFAULT 'api',           -- 数据来源
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_currency, to_currency, rate_date)
);
```

### 7. 系统配置表 (system_config)
存储系统配置

```sql
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,    -- 配置键
    config_value TEXT,                          -- 配置值
    description TEXT,                           -- 描述
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔗 表关系图

```
user_operations (1) -----> (N) asset_positions
fund_info (1) -----> (N) fund_nav
dca_plans (1) -----> (N) user_operations
```

## 📝 索引设计

```sql
-- 用户操作记录索引
CREATE INDEX idx_operations_date ON user_operations(operation_date);
CREATE INDEX idx_operations_platform ON user_operations(platform);
CREATE INDEX idx_operations_asset ON user_operations(asset_code);

-- 资产持仓索引
CREATE INDEX idx_positions_platform ON asset_positions(platform);
CREATE INDEX idx_positions_asset ON asset_positions(asset_code);

-- 基金净值索引
CREATE INDEX idx_fund_nav_date ON fund_nav(nav_date);
CREATE INDEX idx_fund_nav_code ON fund_nav(fund_code);

-- 汇率索引
CREATE INDEX idx_exchange_rates_date ON exchange_rates(rate_date);
CREATE INDEX idx_exchange_rates_currency ON exchange_rates(from_currency, to_currency);
```

## 🎯 数据流程

1. **操作录入**：用户录入投资决策 → `user_operations`
2. **数据获取**：系统从API获取价格/净值 → `fund_nav`, `exchange_rates`
3. **持仓计算**：根据操作记录计算当前持仓 → `asset_positions`
4. **收益分析**：基于持仓和价格计算收益

## 🔄 数据同步策略

- **基金净值**：每日15:00后自动获取
- **汇率数据**：每日更新一次
- **持仓计算**：每次操作后重新计算
- **收益统计**：实时计算 