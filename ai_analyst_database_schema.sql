-- AI分析师数据库快照 - 完整SQL脚本
-- 包含表结构和示例数据

-- 创建数据库表结构

-- 1. 用户操作记录表
CREATE TABLE IF NOT EXISTS user_operations (
    id SERIAL PRIMARY KEY,
    operation_date TIMESTAMP NOT NULL,
    platform VARCHAR(50) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    asset_code VARCHAR(50) NOT NULL,
    asset_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15,4) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,8),
    price DECIMAL(15,4),
    nav DECIMAL(15,4),
    fee DECIMAL(10,4) DEFAULT 0,
    strategy TEXT,
    emotion_score INTEGER,
    tags TEXT,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    dca_plan_id INTEGER,
    dca_execution_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 资产持仓表
CREATE TABLE IF NOT EXISTS asset_positions (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    asset_code VARCHAR(50) NOT NULL,
    asset_name VARCHAR(100) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,8) NOT NULL,
    avg_cost DECIMAL(15,4) NOT NULL,
    current_price DECIMAL(15,4) NOT NULL,
    current_value DECIMAL(15,4) NOT NULL,
    total_invested DECIMAL(15,4) NOT NULL,
    total_profit DECIMAL(15,4) NOT NULL,
    profit_rate DECIMAL(8,4) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, asset_code, currency)
);

-- 3. 基金信息表
CREATE TABLE IF NOT EXISTS fund_info (
    id SERIAL PRIMARY KEY,
    fund_code VARCHAR(20) UNIQUE NOT NULL,
    fund_name VARCHAR(100) NOT NULL,
    fund_type VARCHAR(50),
    management_fee DECIMAL(5,4),
    purchase_fee DECIMAL(5,4),
    redemption_fee DECIMAL(5,4),
    min_purchase DECIMAL(10,2),
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 基金净值表
CREATE TABLE IF NOT EXISTS fund_nav (
    id SERIAL PRIMARY KEY,
    fund_code VARCHAR(20) NOT NULL,
    nav_date DATE NOT NULL,
    nav DECIMAL(10,4) NOT NULL,
    accumulated_nav DECIMAL(10,4),
    growth_rate DECIMAL(8,4),
    source VARCHAR(50) DEFAULT 'api',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, nav_date)
);

-- 5. 定投计划表
CREATE TABLE IF NOT EXISTS dca_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    asset_type VARCHAR(50) NOT NULL DEFAULT '基金',
    asset_code VARCHAR(50) NOT NULL,
    asset_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    frequency_value INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    strategy TEXT,
    execution_time VARCHAR(10) DEFAULT '15:00',
    next_execution_date DATE,
    last_execution_date DATE,
    execution_count INTEGER DEFAULT 0,
    total_invested DECIMAL(15,4) DEFAULT 0,
    total_shares DECIMAL(15,8) DEFAULT 0,
    smart_dca BOOLEAN DEFAULT FALSE,
    base_amount DECIMAL(10,2),
    max_amount DECIMAL(10,2),
    increase_rate DECIMAL(5,4),
    min_nav DECIMAL(10,4),
    max_nav DECIMAL(10,4),
    skip_holidays BOOLEAN DEFAULT TRUE,
    enable_notification BOOLEAN DEFAULT TRUE,
    notification_before INTEGER DEFAULT 30,
    fee_rate DECIMAL(5,4) DEFAULT 0,
    exclude_dates TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 汇率表
CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    from_currency VARCHAR(10) NOT NULL,
    to_currency VARCHAR(10) NOT NULL,
    rate DECIMAL(15,6) NOT NULL,
    rate_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'api',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_currency, to_currency, rate_date)
);

-- 7. IBKR账户表
CREATE TABLE IF NOT EXISTS ibkr_accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) UNIQUE NOT NULL,
    account_name VARCHAR(100),
    account_type VARCHAR(50) DEFAULT 'INDIVIDUAL',
    base_currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. IBKR余额表
CREATE TABLE IF NOT EXISTS ibkr_balances (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    total_cash DECIMAL(15,2) NOT NULL DEFAULT 0,
    net_liquidation DECIMAL(15,2) NOT NULL DEFAULT 0,
    buying_power DECIMAL(15,2) NOT NULL DEFAULT 0,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    snapshot_date DATE NOT NULL,
    snapshot_time TIMESTAMP NOT NULL,
    sync_source VARCHAR(50) DEFAULT 'gcp_scheduler',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, snapshot_date)
);

-- 9. IBKR持仓表
CREATE TABLE IF NOT EXISTS ibkr_positions (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15,6) NOT NULL DEFAULT 0,
    market_value DECIMAL(15,2) NOT NULL DEFAULT 0,
    average_cost DECIMAL(15,2) NOT NULL DEFAULT 0,
    unrealized_pnl DECIMAL(15,2) DEFAULT 0,
    realized_pnl DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    asset_class VARCHAR(50) DEFAULT 'STK',
    snapshot_date DATE NOT NULL,
    snapshot_time TIMESTAMP NOT NULL,
    sync_source VARCHAR(50) DEFAULT 'gcp_scheduler',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, symbol, snapshot_date)
);

-- 10. OKX余额表
CREATE TABLE IF NOT EXISTS okx_balances (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    available_balance DECIMAL(15,8) NOT NULL DEFAULT 0,
    frozen_balance DECIMAL(15,8) NOT NULL DEFAULT 0,
    total_balance DECIMAL(15,8) NOT NULL DEFAULT 0,
    account_type VARCHAR(20) NOT NULL DEFAULT 'trading',
    update_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, currency, account_type)
);

-- 11. OKX持仓表
CREATE TABLE IF NOT EXISTS okx_positions (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    inst_type VARCHAR(20) NOT NULL,
    inst_id VARCHAR(50) NOT NULL,
    position_side VARCHAR(10) NOT NULL,
    position_id VARCHAR(100) NOT NULL,
    quantity DECIMAL(15,8) NOT NULL DEFAULT 0,
    avg_price DECIMAL(15,8) NOT NULL DEFAULT 0,
    unrealized_pnl DECIMAL(15,8) NOT NULL DEFAULT 0,
    realized_pnl DECIMAL(15,8) NOT NULL DEFAULT 0,
    margin_ratio DECIMAL(15,8),
    leverage DECIMAL(15,8),
    mark_price DECIMAL(15,8),
    liquidation_price DECIMAL(15,8),
    currency VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, inst_id, position_side, position_id)
);

-- 12. OKX市场数据表
CREATE TABLE IF NOT EXISTS okx_market_data (
    id SERIAL PRIMARY KEY,
    inst_id VARCHAR(50) NOT NULL,
    inst_type VARCHAR(20) NOT NULL,
    last_price DECIMAL(20,8) NOT NULL,
    bid_price DECIMAL(20,8),
    ask_price DECIMAL(20,8),
    high_24h DECIMAL(20,8),
    low_24h DECIMAL(20,8),
    volume_24h DECIMAL(20,8),
    change_24h DECIMAL(20,8),
    change_rate_24h DECIMAL(20,8),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(inst_id, timestamp)
);

-- 13. Wise交易记录表
CREATE TABLE IF NOT EXISTS wise_transactions (
    id SERIAL PRIMARY KEY,
    profile_id VARCHAR(50) NOT NULL,
    account_id VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(200) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    amount DECIMAL(15,4) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    description TEXT,
    title TEXT,
    date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    reference_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Wise余额表
CREATE TABLE IF NOT EXISTS wise_balances (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) UNIQUE NOT NULL,
    currency VARCHAR(10) NOT NULL,
    available_balance DECIMAL(15,4) NOT NULL,
    reserved_balance DECIMAL(15,4) NOT NULL,
    cash_amount DECIMAL(15,4) NOT NULL,
    total_worth DECIMAL(15,4) NOT NULL,
    type VARCHAR(50) NOT NULL,
    investment_state VARCHAR(50) NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    modification_time TIMESTAMP NOT NULL,
    visible BOOLEAN DEFAULT TRUE,
    primary BOOLEAN DEFAULT FALSE,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Web3余额表
CREATE TABLE IF NOT EXISTS web3_balances (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100) NOT NULL,
    total_value DECIMAL(20,8) NOT NULL DEFAULT 0,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    update_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, account_id)
);

-- 16. Web3代币表
CREATE TABLE IF NOT EXISTS web3_tokens (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100) NOT NULL,
    token_symbol VARCHAR(20) NOT NULL,
    token_name VARCHAR(100) NOT NULL,
    token_address VARCHAR(100),
    balance DECIMAL(20,8) NOT NULL DEFAULT 0,
    value_usd DECIMAL(20,8) NOT NULL DEFAULT 0,
    price_usd DECIMAL(20,8),
    update_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, account_id, token_symbol)
);

-- 创建索引
CREATE INDEX idx_user_operations_date ON user_operations(operation_date);
CREATE INDEX idx_user_operations_platform ON user_operations(platform);
CREATE INDEX idx_user_operations_asset_code ON user_operations(asset_code);
CREATE INDEX idx_asset_positions_platform ON asset_positions(platform);
CREATE INDEX idx_asset_positions_asset_code ON asset_positions(asset_code);
CREATE INDEX idx_fund_nav_fund_code ON fund_nav(fund_code);
CREATE INDEX idx_fund_nav_date ON fund_nav(nav_date);
CREATE INDEX idx_exchange_rates_date ON exchange_rates(rate_date);
CREATE INDEX idx_ibkr_balances_date ON ibkr_balances(snapshot_date);
CREATE INDEX idx_ibkr_positions_date ON ibkr_positions(snapshot_date);
CREATE INDEX idx_okx_balances_time ON okx_balances(update_time);
CREATE INDEX idx_okx_positions_time ON okx_positions(timestamp);
CREATE INDEX idx_okx_market_data_time ON okx_market_data(timestamp);
CREATE INDEX idx_wise_transactions_date ON wise_transactions(date);
CREATE INDEX idx_web3_balances_time ON web3_balances(update_time);
CREATE INDEX idx_web3_tokens_time ON web3_tokens(update_time);

-- 插入示例数据

-- 用户操作记录示例
INSERT INTO user_operations (operation_date, platform, asset_type, operation_type, asset_code, asset_name, amount, currency, quantity, price, nav, fee, strategy, emotion_score, tags, notes, status) VALUES
('2024-01-15 14:30:00', '蚂蚁财富', '基金', 'buy', '000001', '华夏成长混合', 1000.00, 'CNY', 1000.00, 1.0000, 1.0000, 0.00, '价值投资', 7, '["长期投资", "价值投资"]', '看好科技成长股', 'completed'),
('2024-01-20 10:15:00', '蚂蚁财富', '基金', 'buy', '000002', '易方达消费行业', 2000.00, 'CNY', 2000.00, 1.5000, 1.5000, 0.00, '消费升级', 8, '["消费", "蓝筹"]', '消费行业长期看好', 'completed'),
('2024-02-01 09:00:00', 'IBKR', '股票', 'buy', 'AAPL', 'Apple Inc.', 5000.00, 'USD', 25.00, 200.00, 200.00, 1.00, '科技股投资', 9, '["科技", "蓝筹"]', '苹果公司长期价值', 'completed'),
('2024-02-10 15:30:00', 'OKX', '加密货币', 'buy', 'BTC-USDT', 'Bitcoin', 3000.00, 'USDT', 0.075, 40000.00, 40000.00, 0.00, '数字黄金', 6, '["加密货币", "长期持有"]', '比特币减半预期', 'completed'),
('2024-02-15 14:00:00', '蚂蚁财富', '基金', 'dca', '000001', '华夏成长混合', 500.00, 'CNY', 500.00, 1.0500, 1.0500, 0.00, '定投策略', 5, '["定投", "长期投资"]', '定期定额投资', 'completed');

-- 资产持仓示例
INSERT INTO asset_positions (platform, asset_type, asset_code, asset_name, currency, quantity, avg_cost, current_price, current_value, total_invested, total_profit, profit_rate) VALUES
('蚂蚁财富', '基金', '000001', '华夏成长混合', 'CNY', 1500.00, 1.0250, 1.0800, 1620.00, 1500.00, 120.00, 0.0800),
('蚂蚁财富', '基金', '000002', '易方达消费行业', 'CNY', 2000.00, 1.5000, 1.6500, 3300.00, 2000.00, 1300.00, 0.6500),
('IBKR', '股票', 'AAPL', 'Apple Inc.', 'USD', 25.00, 200.00, 220.00, 5500.00, 5000.00, 500.00, 0.1000),
('OKX', '加密货币', 'BTC-USDT', 'Bitcoin', 'USDT', 0.075, 40000.00, 45000.00, 3375.00, 3000.00, 375.00, 0.1250),
('Wise', '外汇', 'USD', 'US Dollar', 'USD', 10000.00, 1.0000, 1.0000, 10000.00, 10000.00, 0.00, 0.0000);

-- 基金信息示例
INSERT INTO fund_info (fund_code, fund_name, fund_type, management_fee, purchase_fee, redemption_fee, min_purchase, risk_level) VALUES
('000001', '华夏成长混合', '混合型', 0.0150, 0.0015, 0.0000, 100.00, '中风险'),
('000002', '易方达消费行业', '股票型', 0.0150, 0.0015, 0.0000, 100.00, '高风险'),
('000003', '招商中证白酒', '指数型', 0.0100, 0.0010, 0.0000, 100.00, '高风险'),
('000004', '工银瑞信货币', '货币型', 0.0033, 0.0000, 0.0000, 1.00, '低风险'),
('000005', '南方中证500ETF', 'ETF', 0.0050, 0.0005, 0.0000, 100.00, '中风险');

-- 基金净值示例
INSERT INTO fund_nav (fund_code, nav_date, nav, accumulated_nav, growth_rate, source) VALUES
('000001', '2024-01-15', 1.0000, 1.0000, 0.0000, 'api'),
('000001', '2024-01-16', 1.0050, 1.0050, 0.0050, 'api'),
('000001', '2024-01-17', 1.0100, 1.0100, 0.0050, 'api'),
('000001', '2024-01-18', 1.0080, 1.0080, -0.0020, 'api'),
('000001', '2024-01-19', 1.0150, 1.0150, 0.0070, 'api'),
('000002', '2024-01-20', 1.5000, 1.5000, 0.0000, 'api'),
('000002', '2024-01-21', 1.5200, 1.5200, 0.0133, 'api'),
('000002', '2024-01-22', 1.5500, 1.5500, 0.0197, 'api'),
('000002', '2024-01-23', 1.5800, 1.5800, 0.0194, 'api'),
('000002', '2024-01-24', 1.6500, 1.6500, 0.0443, 'api');

-- 定投计划示例
INSERT INTO dca_plans (plan_name, platform, asset_type, asset_code, asset_name, amount, currency, frequency, frequency_value, start_date, status, strategy, smart_dca, base_amount, max_amount, increase_rate) VALUES
('华夏成长定投', '蚂蚁财富', '基金', '000001', '华夏成长混合', 500.00, 'CNY', 'weekly', 7, '2024-01-15', 'active', '价值投资策略', false, 500.00, 1000.00, 0.1000),
('消费行业定投', '蚂蚁财富', '基金', '000002', '易方达消费行业', 1000.00, 'CNY', 'monthly', 30, '2024-01-20', 'active', '消费升级策略', true, 1000.00, 2000.00, 0.1500),
('比特币定投', 'OKX', '加密货币', 'BTC-USDT', 'Bitcoin', 100.00, 'USDT', 'weekly', 7, '2024-02-01', 'active', '数字黄金策略', false, 100.00, 200.00, 0.2000);

-- 汇率数据示例
INSERT INTO exchange_rates (from_currency, to_currency, rate, rate_date, source) VALUES
('USD', 'CNY', 7.2000, '2024-01-15', 'api'),
('USD', 'CNY', 7.2100, '2024-01-16', 'api'),
('USD', 'CNY', 7.1900, '2024-01-17', 'api'),
('USD', 'CNY', 7.2200, '2024-01-18', 'api'),
('USD', 'CNY', 7.1800, '2024-01-19', 'api'),
('EUR', 'USD', 1.0850, '2024-01-15', 'api'),
('EUR', 'USD', 1.0870, '2024-01-16', 'api'),
('EUR', 'USD', 1.0830, '2024-01-17', 'api'),
('EUR', 'USD', 1.0890, '2024-01-18', 'api'),
('EUR', 'USD', 1.0810, '2024-01-19', 'api');

-- IBKR数据示例
INSERT INTO ibkr_accounts (account_id, account_name, account_type, base_currency, status) VALUES
('U123456789', '个人投资账户', 'INDIVIDUAL', 'USD', 'ACTIVE');

INSERT INTO ibkr_balances (account_id, total_cash, net_liquidation, buying_power, currency, snapshot_date, snapshot_time, sync_source) VALUES
('U123456789', 15000.00, 25000.00, 20000.00, 'USD', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler');

INSERT INTO ibkr_positions (account_id, symbol, quantity, market_value, average_cost, unrealized_pnl, realized_pnl, currency, asset_class, snapshot_date, snapshot_time, sync_source) VALUES
('U123456789', 'AAPL', 25.00, 5500.00, 200.00, 500.00, 0.00, 'USD', 'STK', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler'),
('U123456789', 'TSLA', 10.00, 1800.00, 180.00, 0.00, 0.00, 'USD', 'STK', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler'),
('U123456789', 'SPY', 50.00, 25000.00, 500.00, 0.00, 0.00, 'USD', 'STK', '2024-02-15', '2024-02-15 16:00:00', 'gcp_scheduler');

-- OKX数据示例
INSERT INTO okx_balances (account_id, currency, available_balance, frozen_balance, total_balance, account_type, update_time) VALUES
('OKX001', 'BTC', 0.075, 0.000, 0.075, 'trading', '2024-02-15 16:00:00'),
('OKX001', 'USDT', 5000.00, 0.000, 5000.00, 'trading', '2024-02-15 16:00:00'),
('OKX001', 'ETH', 2.50, 0.000, 2.50, 'trading', '2024-02-15 16:00:00');

INSERT INTO okx_positions (account_id, inst_type, inst_id, position_side, position_id, quantity, avg_price, unrealized_pnl, realized_pnl, currency, timestamp) VALUES
('OKX001', 'SPOT', 'BTC-USDT', 'long', 'pos_001', 0.075, 40000.00, 375.00, 0.00, 'USD', '2024-02-15 16:00:00'),
('OKX001', 'SPOT', 'ETH-USDT', 'long', 'pos_002', 2.50, 2500.00, 1250.00, 0.00, 'USD', '2024-02-15 16:00:00');

INSERT INTO okx_market_data (inst_id, inst_type, last_price, bid_price, ask_price, high_24h, low_24h, volume_24h, change_24h, change_rate_24h, timestamp) VALUES
('BTC-USDT', 'SPOT', 45000.00, 44999.00, 45001.00, 46000.00, 44000.00, 1000.00, 5000.00, 0.1250, '2024-02-15 16:00:00'),
('ETH-USDT', 'SPOT', 3000.00, 2999.00, 3001.00, 3100.00, 2900.00, 500.00, 100.00, 0.0345, '2024-02-15 16:00:00');

-- Wise数据示例
INSERT INTO wise_transactions (profile_id, account_id, transaction_id, type, amount, currency, description, title, date, status, reference_number) VALUES
('profile_001', 'account_001', 'txn_001', 'TRANSFER', 1000.00, 'USD', 'Transfer to investment account', 'Investment transfer', '2024-02-15 10:00:00', 'COMPLETED', 'REF001'),
('profile_001', 'account_001', 'txn_002', 'INTERBALANCE', 500.00, 'EUR', 'Currency conversion', 'EUR to USD conversion', '2024-02-15 11:00:00', 'COMPLETED', 'REF002');

INSERT INTO wise_balances (account_id, currency, available_balance, reserved_balance, cash_amount, total_worth, type, investment_state, creation_time, modification_time, visible, primary) VALUES
('account_001', 'USD', 5000.00, 0.00, 5000.00, 5000.00, 'STANDARD', 'ACTIVE', '2024-01-01 00:00:00', '2024-02-15 16:00:00', true, true),
('account_002', 'EUR', 3000.00, 0.00, 3000.00, 3000.00, 'STANDARD', 'ACTIVE', '2024-01-01 00:00:00', '2024-02-15 16:00:00', true, false);

-- Web3数据示例
INSERT INTO web3_balances (project_id, account_id, total_value, currency, update_time) VALUES
('ethereum_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 15000.00, 'USD', '2024-02-15 16:00:00'),
('polygon_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 5000.00, 'USD', '2024-02-15 16:00:00');

INSERT INTO web3_tokens (project_id, account_id, token_symbol, token_name, token_address, balance, value_usd, price_usd, update_time) VALUES
('ethereum_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'ETH', 'Ethereum', '0x0000000000000000000000000000000000000000', 5.00, 15000.00, 3000.00, '2024-02-15 16:00:00'),
('ethereum_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'USDC', 'USD Coin', '0xA0b86a33E6441b8C4C9db96C4b4d8b6', 1000.00, 1000.00, 1.00, '2024-02-15 16:00:00'),
('polygon_mainnet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'MATIC', 'Polygon', '0x0000000000000000000000000000000000001010', 10000.00, 5000.00, 0.50, '2024-02-15 16:00:00');

-- 创建视图：投资组合总览
CREATE OR REPLACE VIEW portfolio_overview AS
SELECT 
    platform,
    asset_type,
    COUNT(*) as asset_count,
    SUM(current_value) as total_value,
    SUM(total_invested) as total_invested,
    SUM(total_profit) as total_profit,
    AVG(profit_rate) as avg_profit_rate,
    MAX(profit_rate) as max_profit_rate,
    MIN(profit_rate) as min_profit_rate
FROM asset_positions 
GROUP BY platform, asset_type
ORDER BY total_value DESC;

-- 创建视图：基金表现分析
CREATE OR REPLACE VIEW fund_performance AS
SELECT 
    f.fund_code,
    f.fund_name,
    f.fund_type,
    f.risk_level,
    nav.nav as current_nav,
    nav.nav_date as latest_date,
    nav.growth_rate as latest_growth,
    (SELECT AVG(growth_rate) FROM fund_nav WHERE fund_code = f.fund_code AND nav_date >= CURRENT_DATE - INTERVAL '30 days') as avg_30d_growth,
    (SELECT AVG(growth_rate) FROM fund_nav WHERE fund_code = f.fund_code AND nav_date >= CURRENT_DATE - INTERVAL '90 days') as avg_90d_growth
FROM fund_info f
LEFT JOIN (
    SELECT DISTINCT ON (fund_code) fund_code, nav, nav_date, growth_rate
    FROM fund_nav 
    ORDER BY fund_code, nav_date DESC
) nav ON f.fund_code = nav.fund_code;

-- 创建视图：定投效果分析
CREATE OR REPLACE VIEW dca_performance AS
SELECT 
    p.plan_name,
    p.asset_name,
    p.total_invested,
    p.total_shares,
    p.execution_count,
    pos.current_value,
    (pos.current_value - p.total_invested) as profit,
    CASE 
        WHEN p.total_invested > 0 THEN ((pos.current_value - p.total_invested) / p.total_invested)
        ELSE 0 
    END as profit_rate,
    p.smart_dca,
    p.status
FROM dca_plans p
LEFT JOIN asset_positions pos ON p.asset_code = pos.asset_code
WHERE p.status = 'active';

-- 创建视图：操作行为分析
CREATE OR REPLACE VIEW operation_analysis AS
SELECT 
    DATE(operation_date) as op_date,
    platform,
    asset_type,
    operation_type,
    SUM(amount) as total_amount,
    COUNT(*) as operation_count,
    AVG(emotion_score) as avg_emotion,
    STRING_AGG(DISTINCT strategy, ', ') as strategies_used
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(operation_date), platform, asset_type, operation_type
ORDER BY op_date DESC;

COMMIT;