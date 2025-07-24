import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
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

def fetch_digital_currency_rate(from_currency: str, to_currency: str):
    """从OKX API获取数字货币汇率"""
    try:
        # 这里应该调用OKX API获取实时汇率
        # 暂时使用模拟数据
        if from_currency == 'IP' and to_currency == 'USDT':
            return Decimal('0.000123')
        elif from_currency == 'BTC' and to_currency == 'USDT':
            return Decimal('45000.0')
        elif from_currency == 'ETH' and to_currency == 'USDT':
            return Decimal('3000.0')
        # 添加更多数字货币汇率
        return None
    except Exception as e:
        logging.warning(f"获取数字货币汇率失败: {e}")
        return None

def get_latest_rate(db: Session, from_currency: str, to_currency: str, time_point: datetime = None):
    """获取最新汇率，支持多层转换"""
    # 1. 优先查询WiseExchangeRate表
    q = db.query(WiseExchangeRate).filter(
        WiseExchangeRate.source_currency == from_currency,
        WiseExchangeRate.target_currency == to_currency
    )
    if time_point:
        q = q.filter(WiseExchangeRate.time <= time_point)
    rate = q.order_by(WiseExchangeRate.time.desc()).first()
    if rate:
        return Decimal(rate.rate)
    
    # 2. 数字货币特殊处理
    digital_currencies = ['USDT', 'USDC', 'BTC', 'ETH', 'IP', 'TRUMP', 'MXC']
    
    if from_currency in digital_currencies and to_currency == 'USDT':
        # 数字货币对USDT汇率
        cached_rate = get_cached_rate(from_currency, to_currency, time_point)
        if cached_rate:
            return cached_rate
        
        # 从API获取并缓存
        api_rate = fetch_digital_currency_rate(from_currency, to_currency)
        if api_rate:
            update_cache_rate(from_currency, to_currency, api_rate)
            return api_rate
    
    elif from_currency in digital_currencies and to_currency == 'USD':
        # 数字货币对USD汇率 = 数字货币/USDT × USDT/USD(1:1)
        usdt_rate = get_latest_rate(db, from_currency, 'USDT', time_point)
        if usdt_rate:
            return usdt_rate * Decimal('1.0')  # USDT/USD默认1:1
    
    elif from_currency in digital_currencies and to_currency == 'CNY':
        # 数字货币对CNY汇率 = 数字货币/USDT × USDT/USD(1:1) × USD/CNY
        usdt_rate = get_latest_rate(db, from_currency, 'USDT', time_point)
        if usdt_rate:
            usd_cny_rate = get_latest_rate(db, 'USD', 'CNY', time_point)
            if usd_cny_rate:
                return usdt_rate * Decimal('1.0') * usd_cny_rate
    
    elif from_currency in digital_currencies and to_currency == 'EUR':
        # 数字货币对EUR汇率 = 数字货币/USDT × USDT/USD(1:1) × USD/EUR
        usdt_rate = get_latest_rate(db, from_currency, 'USDT', time_point)
        if usdt_rate:
            usd_eur_rate = get_latest_rate(db, 'USD', 'EUR', time_point)
            if usd_eur_rate:
                return usdt_rate * Decimal('1.0') * usd_eur_rate
    
    return None


def extract_asset_snapshot(db: Session, snapshot_time: datetime = None, base_currency: str = 'CNY'):
    if snapshot_time is None:
        snapshot_time = datetime.now()
    
    # 汇率缓存
    rate_cache = {}
    def get_rate(from_cur, to_cur):
        key = (from_cur, to_cur)
        if key not in rate_cache:
            rate_cache[key] = get_latest_rate(db, from_cur, to_cur, snapshot_time)
        return rate_cache[key]
    
    # 聚合资产
    all_assets = []
    for p in db.query(AssetPosition).all():
        all_assets.append({
            'user_id': None,
            'platform': p.platform,
            'asset_type': p.asset_type,
            'asset_code': p.asset_code,
            'asset_name': p.asset_name,
            'currency': p.currency,
            'balance': p.current_value
        })
    for w in db.query(WiseBalance).all():
        all_assets.append({
            'user_id': None,
            'platform': 'Wise',
            'asset_type': 'Wise',
            'asset_code': w.account_id,
            'asset_name': '',
            'currency': w.currency,
            'balance': w.available_balance
        })
    for i in db.query(IBKRBalance).all():
        all_assets.append({
            'user_id': None,
            'platform': 'IBKR',
            'asset_type': 'IBKR',
            'asset_code': i.account_id,
            'asset_name': '',
            'currency': i.currency,
            'balance': i.net_liquidation
        })
    for o in db.query(OKXBalance).all():
        all_assets.append({
            'user_id': None,
            'platform': 'OKX',
            'asset_type': 'OKX',
            'asset_code': o.account_id,
            'asset_name': '',
            'currency': o.currency,
            'balance': o.total_balance
        })
    
    logging.warning(f"[extract_asset_snapshot] all_assets count: {len(all_assets)}")
    snapshot_count = 0
    for asset in all_assets:
        logging.warning(f"[extract_asset_snapshot] asset: {asset}")
        
        # 使用时间匹配的汇率查询
        cny_rate = get_rate(asset['currency'], 'CNY')
        usd_rate = get_rate(asset['currency'], 'USD')
        eur_rate = get_rate(asset['currency'], 'EUR')
        
        # 计算base_value
        base_rate = get_rate(asset['currency'], base_currency)
        base_value = Decimal(asset['balance']) * base_rate if base_rate else None
        
        snapshot = AssetSnapshot(
            user_id=asset['user_id'],
            platform=asset['platform'],
            asset_type=asset['asset_type'],
            asset_code=asset['asset_code'],
            asset_name=asset['asset_name'],
            currency=asset['currency'],
            balance=asset['balance'],
            balance_cny=Decimal(asset['balance']) * cny_rate if cny_rate else None,
            balance_usd=Decimal(asset['balance']) * usd_rate if usd_rate else None,
            balance_eur=Decimal(asset['balance']) * eur_rate if eur_rate else None,
            base_value=base_value,
            snapshot_time=snapshot_time,
            extra={}
        )
        logging.warning(f"[extract_asset_snapshot] writing snapshot: {{'platform': {snapshot.platform}, 'asset_type': {snapshot.asset_type}, 'asset_code': {snapshot.asset_code}, 'currency': {snapshot.currency}, 'balance': {snapshot.balance}, 'base_value': {snapshot.base_value}}}")
        db.add(snapshot)
        snapshot_count += 1
    db.commit()
    return snapshot_count


def extract_exchange_rate_snapshot(db: Session, snapshot_time: datetime = None):
    if snapshot_time is None:
        snapshot_time = datetime.now()
    
    # 1. 从WiseExchangeRate表获取传统货币汇率
    for w in db.query(WiseExchangeRate).all():
        snapshot = ExchangeRateSnapshot(
            from_currency=w.source_currency,
            to_currency=w.target_currency,
            rate=w.rate,
            snapshot_time=w.time,  # 使用原始时间
            source='wise',
            extra={}
        )
        db.add(snapshot)
    
    # 2. 获取数字货币汇率并记录
    digital_currencies = ['USDT', 'USDC', 'BTC', 'ETH', 'IP', 'TRUMP', 'MXC']
    
    for currency in digital_currencies:
        # 获取数字货币对USDT汇率
        usdt_rate = get_latest_rate(db, currency, 'USDT', snapshot_time)
        if usdt_rate:
            # 记录数字货币/USDT汇率
            snapshot = ExchangeRateSnapshot(
                from_currency=currency,
                to_currency='USDT',
                rate=usdt_rate,
                snapshot_time=snapshot_time,
                source='cache',
                extra={
                    'cache_source': 'okx_cache',
                    'cache_timestamp': datetime.now().isoformat(),
                    'market_pair': f'{currency}-USDT'
                }
            )
            db.add(snapshot)
            
            # 计算并记录数字货币/USD汇率
            usd_rate = usdt_rate * Decimal('1.0')  # USDT/USD默认1:1
            snapshot_usd = ExchangeRateSnapshot(
                from_currency=currency,
                to_currency='USD',
                rate=usd_rate,
                snapshot_time=snapshot_time,
                source='calculated',
                extra={
                    f'{currency.lower()}_usdt_rate': str(usdt_rate),
                    'usdt_usd_rate': '1.0',
                    'calculation_method': 'multilayer'
                }
            )
            db.add(snapshot_usd)
            
            # 计算并记录数字货币/CNY汇率
            usd_cny_rate = get_latest_rate(db, 'USD', 'CNY', snapshot_time)
            if usd_cny_rate:
                cny_rate = usdt_rate * Decimal('1.0') * usd_cny_rate
                snapshot_cny = ExchangeRateSnapshot(
                    from_currency=currency,
                    to_currency='CNY',
                    rate=cny_rate,
                    snapshot_time=snapshot_time,
                    source='calculated',
                    extra={
                        f'{currency.lower()}_usdt_rate': str(usdt_rate),
                        'usdt_usd_rate': '1.0',
                        'usd_cny_rate': str(usd_cny_rate),
                        'calculation_method': 'multilayer'
                    }
                )
                db.add(snapshot_cny)
            
            # 计算并记录数字货币/EUR汇率
            usd_eur_rate = get_latest_rate(db, 'USD', 'EUR', snapshot_time)
            if usd_eur_rate:
                eur_rate = usdt_rate * Decimal('1.0') * usd_eur_rate
                snapshot_eur = ExchangeRateSnapshot(
                    from_currency=currency,
                    to_currency='EUR',
                    rate=eur_rate,
                    snapshot_time=snapshot_time,
                    source='calculated',
                    extra={
                        f'{currency.lower()}_usdt_rate': str(usdt_rate),
                        'usdt_usd_rate': '1.0',
                        'usd_eur_rate': str(usd_eur_rate),
                        'calculation_method': 'multilayer'
                    }
                )
                db.add(snapshot_eur)
    
    db.commit()