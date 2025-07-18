-- AI分析师常用查询示例
-- 这些查询可以帮助AI分析师快速获取关键数据进行分析

-- ========================================
-- 1. 投资组合总览分析
-- ========================================

-- 1.1 获取当前投资组合总览
SELECT 
    platform,
    asset_type,
    COUNT(*) as asset_count,
    SUM(current_value) as total_value,
    SUM(total_invested) as total_invested,
    SUM(total_profit) as total_profit,
    ROUND(AVG(profit_rate) * 100, 2) as avg_profit_rate_percent,
    ROUND(MAX(profit_rate) * 100, 2) as max_profit_rate_percent,
    ROUND(MIN(profit_rate) * 100, 2) as min_profit_rate_percent
FROM asset_positions 
GROUP BY platform, asset_type
ORDER BY total_value DESC;

-- 1.2 获取各平台资产分布
SELECT 
    platform,
    SUM(current_value) as total_value,
    ROUND(SUM(current_value) * 100.0 / SUM(SUM(current_value)) OVER (), 2) as percentage
FROM asset_positions 
GROUP BY platform
ORDER BY total_value DESC;

-- 1.3 获取各资产类型分布
SELECT 
    asset_type,
    SUM(current_value) as total_value,
    ROUND(SUM(current_value) * 100.0 / SUM(SUM(current_value)) OVER (), 2) as percentage
FROM asset_positions 
GROUP BY asset_type
ORDER BY total_value DESC;

-- 1.4 获取收益率排名前10的资产
SELECT 
    asset_name,
    platform,
    asset_type,
    current_value,
    total_invested,
    total_profit,
    ROUND(profit_rate * 100, 2) as profit_rate_percent
FROM asset_positions 
ORDER BY profit_rate DESC
LIMIT 10;

-- ========================================
-- 2. 基金投资分析
-- ========================================

-- 2.1 获取基金净值走势（最近30天）
SELECT 
    nav_date,
    nav,
    growth_rate,
    LAG(nav) OVER (ORDER BY nav_date) as prev_nav,
    ROUND((nav - LAG(nav) OVER (ORDER BY nav_date)) / LAG(nav) OVER (ORDER BY nav_date) * 100, 4) as daily_return_percent
FROM fund_nav 
WHERE fund_code = '000001' 
    AND nav_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY nav_date;

-- 2.2 获取基金表现对比
SELECT 
    f.fund_code,
    f.fund_name,
    f.fund_type,
    f.risk_level,
    nav.nav as current_nav,
    nav.nav_date as latest_date,
    nav.growth_rate as latest_growth,
    ROUND((SELECT AVG(growth_rate) FROM fund_nav WHERE fund_code = f.fund_code AND nav_date >= CURRENT_DATE - INTERVAL '30 days'), 4) as avg_30d_growth,
    ROUND((SELECT AVG(growth_rate) FROM fund_nav WHERE fund_code = f.fund_code AND nav_date >= CURRENT_DATE - INTERVAL '90 days'), 4) as avg_90d_growth
FROM fund_info f
LEFT JOIN (
    SELECT DISTINCT ON (fund_code) fund_code, nav, nav_date, growth_rate
    FROM fund_nav 
    ORDER BY fund_code, nav_date DESC
) nav ON f.fund_code = nav.fund_code
ORDER BY nav.growth_rate DESC;

-- 2.3 计算基金波动率（30天）
SELECT 
    fund_code,
    STDDEV(growth_rate) as volatility_30d,
    AVG(growth_rate) as avg_return_30d,
    ROUND(STDDEV(growth_rate) / ABS(AVG(growth_rate)), 2) as sharpe_ratio
FROM fund_nav 
WHERE nav_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY fund_code
ORDER BY volatility_30d DESC;

-- ========================================
-- 3. 定投效果分析
-- ========================================

-- 3.1 定投计划效果分析
SELECT 
    p.plan_name,
    p.asset_name,
    p.total_invested,
    p.total_shares,
    p.execution_count,
    pos.current_value,
    (pos.current_value - p.total_invested) as profit,
    ROUND(((pos.current_value - p.total_invested) / p.total_invested) * 100, 2) as profit_rate_percent,
    p.smart_dca,
    p.status
FROM dca_plans p
LEFT JOIN asset_positions pos ON p.asset_code = pos.asset_code
WHERE p.status = 'active'
ORDER BY profit_rate_percent DESC;

-- 3.2 定投执行频率分析
SELECT 
    frequency,
    COUNT(*) as plan_count,
    AVG(amount) as avg_amount,
    SUM(total_invested) as total_invested,
    AVG(execution_count) as avg_executions
FROM dca_plans 
WHERE status = 'active'
GROUP BY frequency
ORDER BY plan_count DESC;

-- 3.3 智能定投vs普通定投效果对比
SELECT 
    CASE WHEN smart_dca THEN '智能定投' ELSE '普通定投' END as dca_type,
    COUNT(*) as plan_count,
    AVG(amount) as avg_amount,
    SUM(total_invested) as total_invested,
    AVG(execution_count) as avg_executions
FROM dca_plans 
WHERE status = 'active'
GROUP BY smart_dca
ORDER BY dca_type;

-- ========================================
-- 4. 操作行为分析
-- ========================================

-- 4.1 操作历史分析（最近90天）
SELECT 
    DATE(operation_date) as op_date,
    platform,
    asset_type,
    operation_type,
    SUM(amount) as total_amount,
    COUNT(*) as operation_count,
    ROUND(AVG(emotion_score), 2) as avg_emotion,
    STRING_AGG(DISTINCT strategy, ', ') as strategies_used
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(operation_date), platform, asset_type, operation_type
ORDER BY op_date DESC;

-- 4.2 情绪评分分析
SELECT 
    CASE 
        WHEN emotion_score >= 8 THEN '非常乐观'
        WHEN emotion_score >= 6 THEN '乐观'
        WHEN emotion_score >= 4 THEN '中性'
        WHEN emotion_score >= 2 THEN '悲观'
        ELSE '非常悲观'
    END as emotion_level,
    COUNT(*) as operation_count,
    AVG(amount) as avg_amount,
    STRING_AGG(DISTINCT strategy, ', ') as strategies_used
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY emotion_level
ORDER BY operation_count DESC;

-- 4.3 策略使用分析
SELECT 
    strategy,
    COUNT(*) as usage_count,
    AVG(amount) as avg_amount,
    ROUND(AVG(emotion_score), 2) as avg_emotion,
    COUNT(DISTINCT asset_type) as asset_types_covered
FROM user_operations 
WHERE strategy IS NOT NULL 
    AND operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY strategy
ORDER BY usage_count DESC;

-- 4.4 买卖时机分析
SELECT 
    operation_type,
    asset_type,
    COUNT(*) as operation_count,
    AVG(amount) as avg_amount,
    ROUND(AVG(emotion_score), 2) as avg_emotion,
    STRING_AGG(DISTINCT strategy, ', ') as strategies_used
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY operation_type, asset_type
ORDER BY operation_type, operation_count DESC;

-- ========================================
-- 5. 平台对比分析
-- ========================================

-- 5.1 各平台收益率对比
SELECT 
    platform,
    COUNT(*) as asset_count,
    SUM(current_value) as total_value,
    SUM(total_invested) as total_invested,
    SUM(total_profit) as total_profit,
    ROUND(AVG(profit_rate) * 100, 2) as avg_profit_rate_percent,
    ROUND(MAX(profit_rate) * 100, 2) as max_profit_rate_percent,
    ROUND(MIN(profit_rate) * 100, 2) as min_profit_rate_percent
FROM asset_positions 
GROUP BY platform
ORDER BY avg_profit_rate_percent DESC;

-- 5.2 各平台资产类型分布
SELECT 
    platform,
    asset_type,
    COUNT(*) as asset_count,
    SUM(current_value) as total_value,
    ROUND(SUM(current_value) * 100.0 / SUM(SUM(current_value)) OVER (PARTITION BY platform), 2) as platform_percentage
FROM asset_positions 
GROUP BY platform, asset_type
ORDER BY platform, total_value DESC;

-- ========================================
-- 6. 时间序列分析
-- ========================================

-- 6.1 基金净值时间序列（最近60天）
SELECT 
    nav_date,
    fund_code,
    nav,
    growth_rate,
    ROUND((nav - LAG(nav) OVER (PARTITION BY fund_code ORDER BY nav_date)) / LAG(nav) OVER (PARTITION BY fund_code ORDER BY nav_date) * 100, 4) as daily_return_percent
FROM fund_nav 
WHERE nav_date >= CURRENT_DATE - INTERVAL '60 days'
ORDER BY fund_code, nav_date;

-- 6.2 操作金额时间序列（最近30天）
SELECT 
    DATE(operation_date) as op_date,
    SUM(amount) as daily_total_amount,
    COUNT(*) as daily_operation_count,
    AVG(emotion_score) as daily_avg_emotion
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(operation_date)
ORDER BY op_date;

-- ========================================
-- 7. 风险分析
-- ========================================

-- 7.1 资产集中度分析
SELECT 
    asset_name,
    current_value,
    ROUND(current_value * 100.0 / SUM(current_value) OVER (), 2) as concentration_percent
FROM asset_positions 
ORDER BY current_value DESC;

-- 7.2 平台风险分散度
SELECT 
    platform,
    COUNT(*) as asset_count,
    SUM(current_value) as total_value,
    ROUND(SUM(current_value) * 100.0 / SUM(SUM(current_value)) OVER (), 2) as platform_percentage
FROM asset_positions 
GROUP BY platform
ORDER BY total_value DESC;

-- 7.3 资产类型风险分散度
SELECT 
    asset_type,
    COUNT(*) as asset_count,
    SUM(current_value) as total_value,
    ROUND(SUM(current_value) * 100.0 / SUM(SUM(current_value)) OVER (), 2) as type_percentage
FROM asset_positions 
GROUP BY asset_type
ORDER BY total_value DESC;

-- ========================================
-- 8. 汇率影响分析
-- ========================================

-- 8.1 汇率变化趋势（最近30天）
SELECT 
    rate_date,
    from_currency,
    to_currency,
    rate,
    ROUND((rate - LAG(rate) OVER (ORDER BY rate_date)) / LAG(rate) OVER (ORDER BY rate_date) * 100, 4) as daily_change_percent
FROM exchange_rates 
WHERE rate_date >= CURRENT_DATE - INTERVAL '30 days'
    AND from_currency = 'USD' AND to_currency = 'CNY'
ORDER BY rate_date;

-- 8.2 多币种资产价值（转换为USD）
SELECT 
    ap.asset_name,
    ap.platform,
    ap.currency,
    ap.current_value,
    CASE 
        WHEN ap.currency = 'USD' THEN ap.current_value
        WHEN ap.currency = 'CNY' THEN ap.current_value / er.rate
        WHEN ap.currency = 'EUR' THEN ap.current_value * er_eur.rate
        ELSE ap.current_value
    END as value_usd
FROM asset_positions ap
LEFT JOIN exchange_rates er ON er.from_currency = 'USD' AND er.to_currency = 'CNY' AND er.rate_date = CURRENT_DATE
LEFT JOIN exchange_rates er_eur ON er_eur.from_currency = 'EUR' AND er_eur.to_currency = 'USD' AND er_eur.rate_date = CURRENT_DATE
ORDER BY value_usd DESC;

-- ========================================
-- 9. 综合报表查询
-- ========================================

-- 9.1 投资组合综合报表
WITH portfolio_summary AS (
    SELECT 
        SUM(current_value) as total_portfolio_value,
        SUM(total_invested) as total_invested,
        SUM(total_profit) as total_profit,
        AVG(profit_rate) as avg_profit_rate
    FROM asset_positions
),
platform_summary AS (
    SELECT 
        platform,
        SUM(current_value) as platform_value,
        COUNT(*) as asset_count
    FROM asset_positions
    GROUP BY platform
),
asset_type_summary AS (
    SELECT 
        asset_type,
        SUM(current_value) as type_value,
        COUNT(*) as asset_count
    FROM asset_positions
    GROUP BY asset_type
)
SELECT 
    '投资组合总览' as report_type,
    ps.total_portfolio_value,
    ps.total_invested,
    ps.total_profit,
    ROUND(ps.avg_profit_rate * 100, 2) as avg_profit_rate_percent
FROM portfolio_summary ps
UNION ALL
SELECT 
    '平台分布' as report_type,
    pls.platform_value,
    pls.asset_count,
    NULL,
    NULL
FROM platform_summary pls
UNION ALL
SELECT 
    '资产类型分布' as report_type,
    ats.type_value,
    ats.asset_count,
    NULL,
    NULL
FROM asset_type_summary ats;

-- 9.2 月度投资表现报表
SELECT 
    DATE_TRUNC('month', operation_date) as month,
    COUNT(*) as total_operations,
    SUM(CASE WHEN operation_type = 'buy' THEN amount ELSE 0 END) as total_buy_amount,
    SUM(CASE WHEN operation_type = 'sell' THEN amount ELSE 0 END) as total_sell_amount,
    SUM(CASE WHEN operation_type = 'dca' THEN amount ELSE 0 END) as total_dca_amount,
    AVG(emotion_score) as avg_emotion,
    COUNT(DISTINCT asset_type) as asset_types_traded
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', operation_date)
ORDER BY month DESC;

-- ========================================
-- 10. 预测分析查询
-- ========================================

-- 10.1 基金趋势预测（基于历史数据）
SELECT 
    fund_code,
    nav_date,
    nav,
    growth_rate,
    ROUND(AVG(growth_rate) OVER (PARTITION BY fund_code ORDER BY nav_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 4) as moving_avg_7d,
    ROUND(AVG(growth_rate) OVER (PARTITION BY fund_code ORDER BY nav_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 4) as moving_avg_30d
FROM fund_nav 
WHERE nav_date >= CURRENT_DATE - INTERVAL '60 days'
ORDER BY fund_code, nav_date;

-- 10.2 投资行为模式分析
SELECT 
    EXTRACT(DOW FROM operation_date) as day_of_week,
    EXTRACT(HOUR FROM operation_date) as hour_of_day,
    COUNT(*) as operation_count,
    AVG(amount) as avg_amount,
    AVG(emotion_score) as avg_emotion
FROM user_operations 
WHERE operation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY EXTRACT(DOW FROM operation_date), EXTRACT(HOUR FROM operation_date)
ORDER BY day_of_week, hour_of_day;

-- 10.3 资产相关性分析（基于收益率）
WITH daily_returns AS (
    SELECT 
        nav_date,
        fund_code,
        (nav - LAG(nav) OVER (PARTITION BY fund_code ORDER BY nav_date)) / LAG(nav) OVER (PARTITION BY fund_code ORDER BY nav_date) as daily_return
    FROM fund_nav 
    WHERE nav_date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT 
    f1.fund_code as fund1,
    f2.fund_code as fund2,
    ROUND(CORR(f1.daily_return, f2.daily_return), 4) as correlation
FROM daily_returns f1
JOIN daily_returns f2 ON f1.nav_date = f2.nav_date AND f1.fund_code < f2.fund_code
WHERE f1.daily_return IS NOT NULL AND f2.daily_return IS NOT NULL
GROUP BY f1.fund_code, f2.fund_code
ORDER BY ABS(CORR(f1.daily_return, f2.daily_return)) DESC;