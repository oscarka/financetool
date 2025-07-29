import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.database import AssetPosition, WiseBalance, IBKRBalance, OKXBalance, ExchangeRate, WiseExchangeRate
from app.models.asset_snapshot import AssetSnapshot, ExchangeRateSnapshot
import redis
import json
import os

# Redis缓存配置
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = int(os.getenv('REDIS_DB', 0))
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
    # 测试连接
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    logging.warning(f"Redis连接失败，将使用内存缓存: {e}")
    REDIS_AVAILABLE = False
    redis_client = None

CACHE_EXPIRY = 300  # 5分钟缓存

# 内存缓存（当Redis不可用时使用）
_memory_cache = {}
_memory_cache_timestamps = {}

def get_cached_rate(from_currency: str, to_currency: str, time_point: datetime = None):
    """从缓存获取汇率"""
    try:
        cache_key = f"rate:{from_currency}:{to_currency}"
        
        if REDIS_AVAILABLE and redis_client:
            # 使用Redis缓存
            cached_data = redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # 检查缓存时间是否在5分钟内
                cache_time = datetime.fromisoformat(data['timestamp'])
                if (datetime.now() - cache_time).seconds < CACHE_EXPIRY:
                    return Decimal(data['rate'])
        else:
            # 使用内存缓存
            if cache_key in _memory_cache:
                cache_time = _memory_cache_timestamps.get(cache_key)
                if cache_time and (datetime.now() - cache_time).seconds < CACHE_EXPIRY:
                    return Decimal(_memory_cache[cache_key])
        
        return None
    except Exception as e:
        logging.warning(f"缓存读取失败: {e}")
        return None

def update_cache_rate(from_currency: str, to_currency: str, rate: Decimal):
    """更新缓存汇率"""
    try:
        cache_key = f"rate:{from_currency}:{to_currency}"
        cache_data = {
            'rate': str(rate),
            'timestamp': datetime.now().isoformat()
        }
        
        if REDIS_AVAILABLE and redis_client:
            # 使用Redis缓存
            redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(cache_data))
        else:
            # 使用内存缓存
            _memory_cache[cache_key] = str(rate)
            _memory_cache_timestamps[cache_key] = datetime.now()
            
    except Exception as e:
        logging.warning(f"缓存更新失败: {e}")

def get_latest_rate(db: Session, from_currency: str, to_currency: str, time_point: datetime = None):
    """获取最新汇率"""
    if from_currency == to_currency:
        return Decimal('1.0')
    
    # 首先尝试从缓存获取
    cached_rate = get_cached_rate(from_currency, to_currency, time_point)
    if cached_rate:
        return cached_rate
    
    # 从数据库获取最新汇率
    try:
        # 尝试从WiseExchangeRate表获取
        rate_record = db.query(WiseExchangeRate).filter(
            WiseExchangeRate.source_currency == from_currency,
            WiseExchangeRate.target_currency == to_currency
        ).order_by(desc(WiseExchangeRate.time)).first()
        
        if rate_record:
            rate = Decimal(str(rate_record.rate))
            update_cache_rate(from_currency, to_currency, rate)
            return rate
        
        # 尝试从ExchangeRate表获取
        rate_record = db.query(ExchangeRate).filter(
            ExchangeRate.from_currency == from_currency,
            ExchangeRate.to_currency == to_currency
        ).order_by(desc(ExchangeRate.rate_date)).first()
        
        if rate_record:
            rate = Decimal(str(rate_record.rate))
            update_cache_rate(from_currency, to_currency, rate)
            return rate
        
        # 如果都没有找到，使用默认汇率（仅用于常见货币对）
        default_rates = {
            ('USD', 'CNY'): Decimal('7.2'),
            ('EUR', 'CNY'): Decimal('7.8'),
            ('JPY', 'CNY'): Decimal('0.048'),
            ('AUD', 'CNY'): Decimal('4.8'),
            ('HKD', 'CNY'): Decimal('0.92'),
            ('USDT', 'CNY'): Decimal('7.2'),
            ('USDC', 'CNY'): Decimal('7.2'),
            ('ETH', 'CNY'): Decimal('15000'),  # 估算汇率
            ('BTC', 'CNY'): Decimal('450000'),  # 估算汇率
            ('POL', 'CNY'): Decimal('0.1'),     # 估算汇率
            ('SOL', 'CNY'): Decimal('800'),     # 估算汇率
            ('RIO', 'CNY'): Decimal('0.01'),    # 估算汇率
            ('MXC', 'CNY'): Decimal('0.001'),   # 估算汇率
            ('TRUMP', 'CNY'): Decimal('0.1'),   # 估算汇率
        }
        
        default_rate = default_rates.get((from_currency, to_currency))
        if default_rate:
            logging.warning(f"使用默认汇率: {from_currency} -> {to_currency} = {default_rate}")
            return default_rate
        
        # 如果都没有找到，返回None
        logging.warning(f"无法获取汇率: {from_currency} -> {to_currency}")
        return None
        
    except Exception as e:
        logging.error(f"获取汇率失败: {e}")
        return None

def aggregate_asset_data(db: Session, base_currency: str = 'CNY'):
    """聚合所有平台的资产数据 - 只获取最新记录，避免重复计算"""
    all_assets = []
    
    logging.info(f"[aggregate_asset_data] 开始聚合资产数据，基准货币: {base_currency}")
    
    # 1. 聚合基金资产 (AssetPosition) - 基金资产通常是最新的
    asset_positions = db.query(AssetPosition).all()
    logging.info(f"[aggregate_asset_data] 找到 {len(asset_positions)} 条基金资产")
    for p in asset_positions:
        asset_info = {
            'user_id': None,
            'platform': p.platform,
            'asset_type': p.asset_type,
            'asset_code': p.asset_code,
            'asset_name': p.asset_name,
            'currency': p.currency,
            'balance': p.current_value
        }
        all_assets.append(asset_info)
        logging.info(f"[aggregate_asset_data] 基金资产: {p.platform} - {p.asset_type} - {p.asset_name} - {p.current_value} {p.currency}")
    
    # 2. 聚合Wise外汇资产 - 只获取每个账户的最新记录
    from sqlalchemy import desc, func
    from datetime import datetime, timedelta
    
    # 获取最近24小时内的最新记录
    yesterday = datetime.now() - timedelta(days=1)
    
    # 使用窗口函数获取每个账户的最新记录
    wise_latest_query = db.query(
        WiseBalance.account_id,
        WiseBalance.currency,
        WiseBalance.available_balance,
        WiseBalance.update_time,
        func.row_number().over(
            partition_by=[WiseBalance.account_id, WiseBalance.currency],
            order_by=desc(WiseBalance.update_time)
        ).label('rn')
    ).filter(
        WiseBalance.update_time >= yesterday
    ).subquery()
    
    # 只获取每个账户+货币组合的最新记录
    wise_latest = db.query(
        wise_latest_query.c.account_id,
        wise_latest_query.c.currency,
        wise_latest_query.c.available_balance,
        wise_latest_query.c.update_time
    ).filter(
        wise_latest_query.c.rn == 1
    ).all()
    
    logging.info(f"[aggregate_asset_data] 找到 {len(wise_latest)} 条Wise外汇最新资产")
    for w in wise_latest:
        asset_info = {
            'user_id': None,
            'platform': 'Wise',
            'asset_type': '外汇',
            'asset_code': w.account_id,
            'asset_name': '',
            'currency': w.currency,
            'balance': w.available_balance
        }
        all_assets.append(asset_info)
        logging.info(f"[aggregate_asset_data] Wise资产: {w.account_id} - {w.available_balance} {w.currency} (更新时间: {w.update_time})")
    
    # 3. 聚合IBKR证券资产 - 只获取每个账户的最新记录
    ibkr_latest_query = db.query(
        IBKRBalance.account_id,
        IBKRBalance.currency,
        IBKRBalance.net_liquidation,
        IBKRBalance.snapshot_time,
        func.row_number().over(
            partition_by=[IBKRBalance.account_id, IBKRBalance.currency],
            order_by=desc(IBKRBalance.snapshot_time)
        ).label('rn')
    ).filter(
        IBKRBalance.snapshot_time >= yesterday
    ).subquery()
    
    ibkr_latest = db.query(
        ibkr_latest_query.c.account_id,
        ibkr_latest_query.c.currency,
        ibkr_latest_query.c.net_liquidation,
        ibkr_latest_query.c.snapshot_time
    ).filter(
        ibkr_latest_query.c.rn == 1
    ).all()
    
    logging.info(f"[aggregate_asset_data] 找到 {len(ibkr_latest)} 条IBKR证券最新资产")
    for i in ibkr_latest:
        asset_info = {
            'user_id': None,
            'platform': 'IBKR',
            'asset_type': '证券',
            'asset_code': i.account_id,
            'asset_name': '',
            'currency': i.currency,
            'balance': i.net_liquidation
        }
        all_assets.append(asset_info)
        logging.info(f"[aggregate_asset_data] IBKR资产: {i.account_id} - {i.net_liquidation} {i.currency} (更新时间: {i.snapshot_time})")
    
    # 4. 聚合OKX数字货币资产 - 只获取每个账户的最新记录
    okx_latest_query = db.query(
        OKXBalance.account_id,
        OKXBalance.currency,
        OKXBalance.total_balance,
        OKXBalance.update_time,
        func.row_number().over(
            partition_by=[OKXBalance.account_id, OKXBalance.currency],
            order_by=desc(OKXBalance.update_time)
        ).label('rn')
    ).filter(
        OKXBalance.update_time >= yesterday
    ).subquery()
    
    okx_latest = db.query(
        okx_latest_query.c.account_id,
        okx_latest_query.c.currency,
        okx_latest_query.c.total_balance,
        okx_latest_query.c.update_time
    ).filter(
        okx_latest_query.c.rn == 1
    ).all()
    
    logging.info(f"[aggregate_asset_data] 找到 {len(okx_latest)} 条OKX数字货币最新资产")
    for o in okx_latest:
        asset_info = {
            'user_id': None,
            'platform': 'OKX',
            'asset_type': '数字货币',
            'asset_code': o.account_id,
            'asset_name': '',
            'currency': o.currency,
            'balance': o.total_balance
        }
        all_assets.append(asset_info)
        logging.info(f"[aggregate_asset_data] OKX资产: {o.account_id} - {o.total_balance} {o.currency} (更新时间: {o.update_time})")
    
    logging.info(f"[aggregate_asset_data] 聚合完成，总共 {len(all_assets)} 条最新资产数据")
    return all_assets

def calculate_aggregated_stats(db: Session, base_currency: str = 'CNY'):
    """计算聚合统计数据"""
    all_assets = aggregate_asset_data(db, base_currency)
    
    # 汇率缓存
    rate_cache = {}
    used_default_rates = False
    
    def get_rate(from_cur, to_cur):
        key = (from_cur, to_cur)
        if key not in rate_cache:
            rate_cache[key] = get_latest_rate(db, from_cur, to_cur)
            # 检查是否使用了默认汇率
            if rate_cache[key] and from_cur != to_cur:
                # 检查是否是默认汇率
                default_rates = {
                    ('USD', 'CNY'): Decimal('7.2'),
                    ('EUR', 'CNY'): Decimal('7.8'),
                    ('JPY', 'CNY'): Decimal('0.048'),
                    ('AUD', 'CNY'): Decimal('4.8'),
                    ('HKD', 'CNY'): Decimal('0.92'),
                    ('USDT', 'CNY'): Decimal('7.2'),
                    ('USDC', 'CNY'): Decimal('7.2'),
                    ('ETH', 'CNY'): Decimal('15000'),
                    ('BTC', 'CNY'): Decimal('450000'),
                    ('POL', 'CNY'): Decimal('0.1'),
                    ('SOL', 'CNY'): Decimal('800'),
                    ('RIO', 'CNY'): Decimal('0.01'),
                    ('MXC', 'CNY'): Decimal('0.001'),
                    ('TRUMP', 'CNY'): Decimal('0.1'),
                }
                if (from_cur, to_cur) in default_rates and rate_cache[key] == default_rates[(from_cur, to_cur)]:
                    nonlocal used_default_rates
                    used_default_rates = True
        return rate_cache[key]
    
    # 计算统计数据
    total_value = Decimal('0')
    platform_stats = {}
    asset_type_stats = {}
    currency_stats = {}
    
    # 添加详细调试日志
    logging.info(f"[calculate_aggregated_stats] 开始计算聚合统计，基准货币: {base_currency}")
    logging.info(f"[calculate_aggregated_stats] 总资产数量: {len(all_assets)}")
    
    # 检查是否有重复的资产记录
    asset_keys = set()
    duplicate_count = 0
    
    for i, asset in enumerate(all_assets):
        # 创建唯一标识符
        asset_key = f"{asset['platform']}_{asset['asset_code']}_{asset['currency']}"
        
        if asset_key in asset_keys:
            duplicate_count += 1
            logging.warning(f"[calculate_aggregated_stats] 发现重复资产: {asset_key}")
        else:
            asset_keys.add(asset_key)
        
        # 获取汇率
        base_rate = get_rate(asset['currency'], base_currency)
        original_value = Decimal(str(asset['balance']))
        
        if base_rate:
            base_value = original_value * base_rate
            total_value += base_value
            
            # 按平台统计
            platform = asset['platform']
            if platform not in platform_stats:
                platform_stats[platform] = Decimal('0')
            platform_stats[platform] += base_value
            
            # 按资产类型统计
            asset_type = asset['asset_type']
            if asset_type not in asset_type_stats:
                asset_type_stats[asset_type] = Decimal('0')
            asset_type_stats[asset_type] += base_value
            
            # 按币种统计
            currency = asset['currency']
            if currency not in currency_stats:
                currency_stats[currency] = Decimal('0')
            currency_stats[currency] += base_value
            
            # 详细日志
            logging.info(f"[calculate_aggregated_stats] 资产 {i+1}: {asset['platform']} - {asset['asset_type']} - {asset['asset_name']} - {original_value} {asset['currency']} (汇率: {base_rate}) = {base_value} {base_currency}")
        else:
            logging.warning(f"[calculate_aggregated_stats] 资产 {i+1}: {asset['platform']} - {asset['asset_type']} - {asset['asset_name']} - {original_value} {asset['currency']} (无法获取汇率)")
    
    logging.info(f"[calculate_aggregated_stats] 重复资产数量: {duplicate_count}")
    logging.info(f"[calculate_aggregated_stats] 最终统计结果:")
    logging.info(f"[calculate_aggregated_stats] 总价值: {total_value} {base_currency}")
    logging.info(f"[calculate_aggregated_stats] 平台分布: {dict(platform_stats)}")
    logging.info(f"[calculate_aggregated_stats] 资产类型分布: {dict(asset_type_stats)}")
    logging.info(f"[calculate_aggregated_stats] 币种分布: {dict(currency_stats)}")
    
    # 转换为前端需要的格式
    result = {
        'total_value': float(total_value),
        'platform_stats': {k: float(v) for k, v in platform_stats.items()},
        'asset_type_stats': {k: float(v) for k, v in asset_type_stats.items()},
        'currency_stats': {k: float(v) for k, v in currency_stats.items()},
        'asset_count': len(all_assets),
        'platform_count': len(platform_stats),
        'asset_type_count': len(asset_type_stats),
        'currency_count': len(currency_stats),
        'has_default_rates': used_default_rates
    }
    
    return result

def get_asset_trend_data(db: Session, days: int = 30, base_currency: str = 'CNY'):
    """获取资产趋势数据"""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    # 从快照表获取趋势数据 - 使用PostgreSQL的date_trunc函数
    q = db.query(
        func.date_trunc('day', AssetSnapshot.snapshot_time).label('day'),
        func.sum(getattr(AssetSnapshot, f'balance_{base_currency.lower()}')).label('total')
    )
    
    q = q.filter(AssetSnapshot.snapshot_time >= start, AssetSnapshot.snapshot_time <= end)
    q = q.group_by('day').order_by('day')
    
    result = [{
        'date': row.day.date().isoformat(),
        'total': float(row.total) if row.total else 0
    } for row in q.all()]
    
    return result

def get_asset_distribution_data(db: Session, base_currency: str = 'CNY'):
    """获取资产分布数据"""
    all_assets = aggregate_asset_data(db, base_currency)
    
    # 汇率缓存
    rate_cache = {}
    def get_rate(from_cur, to_cur):
        key = (from_cur, to_cur)
        if key not in rate_cache:
            rate_cache[key] = get_latest_rate(db, from_cur, to_cur)
        return rate_cache[key]
    
    # 按资产类型聚合
    asset_type_data = {}
    for asset in all_assets:
        asset_type = asset['asset_type']
        base_rate = get_rate(asset['currency'], base_currency)
        
        if base_rate:
            base_value = Decimal(str(asset['balance'])) * base_rate
            
            if asset_type not in asset_type_data:
                asset_type_data[asset_type] = Decimal('0')
            asset_type_data[asset_type] += base_value
    
    # 转换为图表数据格式
    chart_data = []
    for asset_type, value in asset_type_data.items():
        chart_data.append({
            'type': asset_type,
            'value': float(value)
        })
    
    # 按价值排序
    chart_data.sort(key=lambda x: x['value'], reverse=True)
    
    return chart_data

def get_platform_distribution_data(db: Session, base_currency: str = 'CNY'):
    """获取平台分布数据"""
    all_assets = aggregate_asset_data(db, base_currency)
    
    # 汇率缓存
    rate_cache = {}
    def get_rate(from_cur, to_cur):
        key = (from_cur, to_cur)
        if key not in rate_cache:
            rate_cache[key] = get_latest_rate(db, from_cur, to_cur)
        return rate_cache[key]
    
    # 按平台聚合
    platform_data = {}
    for asset in all_assets:
        platform = asset['platform']
        base_rate = get_rate(asset['currency'], base_currency)
        
        if base_rate:
            base_value = Decimal(str(asset['balance'])) * base_rate
            
            if platform not in platform_data:
                platform_data[platform] = Decimal('0')
            platform_data[platform] += base_value
    
    # 转换为图表数据格式
    chart_data = []
    for platform, value in platform_data.items():
        chart_data.append({
            'platform': platform,
            'value': float(value)
        })
    
    # 按价值排序
    chart_data.sort(key=lambda x: x['value'], reverse=True)
    
    return chart_data