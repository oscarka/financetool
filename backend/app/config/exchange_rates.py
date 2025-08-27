"""
汇率配置文件
包含硬编码的常用汇率数据，用于备用汇率计算
"""

# 常用货币对的备用汇率（基于市场大致水平，定期更新）
FALLBACK_EXCHANGE_RATES = {
    # 主要货币对
    ('USD', 'CNY'): 7.2,
    ('CNY', 'USD'): 0.139,
    ('EUR', 'CNY'): 7.8,
    ('CNY', 'EUR'): 0.128,
    ('JPY', 'CNY'): 0.048,
    ('CNY', 'JPY'): 20.83,
    ('HKD', 'CNY'): 0.92,
    ('CNY', 'HKD'): 1.087,
    ('GBP', 'CNY'): 9.1,
    ('CNY', 'GBP'): 0.110,
    ('AUD', 'CNY'): 4.8,
    ('CNY', 'AUD'): 0.208,
    ('CAD', 'CNY'): 5.3,
    ('CNY', 'CAD'): 0.189,
    
    # 数字货币（基于大致市场价）
    ('BTC', 'CNY'): 450000,
    ('CNY', 'BTC'): 0.00000222,
    ('ETH', 'CNY'): 15000,
    ('CNY', 'ETH'): 0.0000667,
    ('USDT', 'CNY'): 7.2,
    ('CNY', 'USDT'): 0.139,
    ('USDC', 'CNY'): 7.2,
    ('CNY', 'USDC'): 0.139,
    
    # 交叉汇率
    ('USD', 'EUR'): 0.92,
    ('EUR', 'USD'): 1.087,
    ('USD', 'JPY'): 150,
    ('JPY', 'USD'): 0.00667,
    ('USD', 'GBP'): 0.79,
    ('GBP', 'USD'): 1.266,
}

def get_fallback_exchange_rate(amount: float, from_currency: str, to_currency: str) -> tuple[float, bool]:
    """
    获取备用汇率
    
    Args:
        amount: 金额
        from_currency: 源货币
        to_currency: 目标货币
    
    Returns:
        (转换后的金额, 是否使用了默认汇率)，如果无法转换则返回(None, False)
    """
    # 直接查找
    direct_rate = FALLBACK_EXCHANGE_RATES.get((from_currency, to_currency))
    if direct_rate is not None:
        return amount * direct_rate, True
    
    # 通过CNY进行交叉转换
    if from_currency != 'CNY' and to_currency != 'CNY':
        cny_from = FALLBACK_EXCHANGE_RATES.get((from_currency, 'CNY'))
        cny_to = FALLBACK_EXCHANGE_RATES.get(('CNY', to_currency))
        if cny_from is not None and cny_to is not None:
            return amount * cny_from * cny_to, True
    
    return None, False
