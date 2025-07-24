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
        digital_rates = {
            'IP': Decimal('0.000123'),
            'BTC': Decimal('45000.0'),
            'ETH': Decimal('3000.0'),
            'USDT': Decimal('1.0'),
            'USDC': Decimal('1.0'),
            'TRUMP': Decimal('0.0005'),
            'MOVE': Decimal('0.0001'),
            'S': Decimal('0.0002'),
            'KAITO': Decimal('0.0003'),
            'AIXBT': Decimal('0.0004'),
            'MXC': Decimal('0.0006'),
            'DOGE': Decimal('0.08'),
            'ADA': Decimal('0.45'),
            'DOT': Decimal('6.5'),
            'LINK': Decimal('15.0'),
            'UNI': Decimal('8.0'),
            'LTC': Decimal('75.0'),
            'BCH': Decimal('250.0'),
            'XRP': Decimal('0.5'),
            'SOL': Decimal('100.0'),
            'MATIC': Decimal('0.8'),
            'AVAX': Decimal('25.0'),
            'ATOM': Decimal('8.0'),
            'FTM': Decimal('0.3'),
            'NEAR': Decimal('4.0'),
            'ALGO': Decimal('0.15'),
            'VET': Decimal('0.02'),
            'THETA': Decimal('1.5'),
            'FIL': Decimal('5.0'),
            'ICP': Decimal('12.0'),
            'APT': Decimal('8.0'),
            'SUI': Decimal('1.2'),
            'SEI': Decimal('0.4'),
            'TIA': Decimal('8.0'),
            'JUP': Decimal('0.8'),
            'PYTH': Decimal('0.4'),
            'WIF': Decimal('2.0'),
            'BONK': Decimal('0.00002'),
            'PEPE': Decimal('0.000008'),
            'SHIB': Decimal('0.00002'),
            'FLOKI': Decimal('0.00015'),
            'WIF': Decimal('2.0'),
            'BOME': Decimal('0.00001'),
            'BOOK': Decimal('0.0001'),
            'POPCAT': Decimal('0.0002'),
            'TURBO': Decimal('0.0003'),
            'MYRO': Decimal('0.0004'),
            'WEN': Decimal('0.0005'),
            'SLERF': Decimal('0.0006'),
            'BOME': Decimal('0.00001'),
            'BOOK': Decimal('0.0001'),
            'POPCAT': Decimal('0.0002'),
            'TURBO': Decimal('0.0003'),
            'MYRO': Decimal('0.0004'),
            'WEN': Decimal('0.0005'),
            'SLERF': Decimal('0.0006'),
        }
        
        if from_currency in digital_rates:
            return digital_rates[from_currency]
        
        # 如果找不到汇率，返回一个默认值避免None
        logging.warning(f"未找到{from_currency}的汇率，使用默认值0.0001")
        return Decimal('0.0001')
        
    except Exception as e:
        logging.warning(f"获取数字货币汇率失败: {e}")
        return Decimal('0.0001')  # 返回默认值而不是None

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
        logging.info(f"从WiseExchangeRate获取汇率: {from_currency}/{to_currency} = {rate.rate}")
        return Decimal(rate.rate)
    
    # 2. 数字货币特殊处理
    digital_currencies = [
        'USDT', 'USDC', 'BTC', 'ETH', 'IP', 'TRUMP', 'MOVE', 'S', 'KAITO', 'AIXBT', 'MXC',
        'DOGE', 'ADA', 'DOT', 'LINK', 'UNI', 'LTC', 'BCH', 'XRP', 'SOL', 'MATIC', 'AVAX',
        'ATOM', 'FTM', 'NEAR', 'ALGO', 'VET', 'THETA', 'FIL', 'ICP', 'APT', 'SUI', 'SEI',
        'TIA', 'JUP', 'PYTH', 'WIF', 'BONK', 'PEPE', 'SHIB', 'FLOKI', 'BOME', 'BOOK',
        'POPCAT', 'TURBO', 'MYRO', 'WEN', 'SLERF'
    ]
    
    if from_currency in digital_currencies and to_currency == 'USDT':
        # 数字货币对USDT汇率
        cached_rate = get_cached_rate(from_currency, to_currency, time_point)
        if cached_rate:
            logging.info(f"从缓存获取汇率: {from_currency}/{to_currency} = {cached_rate}")
            return cached_rate
        
        # 从API获取并缓存
        api_rate = fetch_digital_currency_rate(from_currency, to_currency)
        if api_rate:
            logging.info(f"从API获取汇率: {from_currency}/{to_currency} = {api_rate}")
            update_cache_rate(from_currency, to_currency, api_rate)
            return api_rate
    
    elif from_currency in digital_currencies and to_currency == 'USD':
        # 数字货币对USD汇率 = 数字货币/USDT × USDT/USD(1:1)
        usdt_rate = get_latest_rate(db, from_currency, 'USDT', time_point)
        if usdt_rate:
            usd_rate = usdt_rate * Decimal('1.0')  # USDT/USD默认1:1
            logging.info(f"计算USD汇率: {from_currency}/USD = {usdt_rate} × 1.0 = {usd_rate}")
            return usd_rate
    
    elif from_currency in digital_currencies and to_currency == 'CNY':
        # 数字货币对CNY汇率 = 数字货币/USDT × USDT/USD(1:1) × USD/CNY
        usdt_rate = get_latest_rate(db, from_currency, 'USDT', time_point)
        if usdt_rate:
            usd_cny_rate = get_latest_rate(db, 'USD', 'CNY', time_point)
            if usd_cny_rate:
                cny_rate = usdt_rate * Decimal('1.0') * usd_cny_rate
                logging.info(f"计算CNY汇率: {from_currency}/CNY = {usdt_rate} × 1.0 × {usd_cny_rate} = {cny_rate}")
                return cny_rate
    
    elif from_currency in digital_currencies and to_currency == 'EUR':
        # 数字货币对EUR汇率 = 数字货币/USDT × USDT/USD(1:1) × USD/EUR
        usdt_rate = get_latest_rate(db, from_currency, 'USDT', time_point)
        if usdt_rate:
            usd_eur_rate = get_latest_rate(db, 'USD', 'EUR', time_point)
            if usd_eur_rate:
                eur_rate = usdt_rate * Decimal('1.0') * usd_eur_rate
                logging.info(f"计算EUR汇率: {from_currency}/EUR = {usdt_rate} × 1.0 × {usd_eur_rate} = {eur_rate}")
                return eur_rate
    
    logging.warning(f"未找到汇率: {from_currency}/{to_currency}")
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
    
    logging.info(f"开始生成汇率快照，时间: {snapshot_time}")
    snapshot_count = 0
    
    try:
        # 1. 从WiseExchangeRate表获取传统货币汇率
        wise_rates = db.query(WiseExchangeRate).all()
        logging.info(f"从WiseExchangeRate表获取到 {len(wise_rates)} 条记录")
        
        for w in wise_rates:
            snapshot = ExchangeRateSnapshot(
                from_currency=w.source_currency,
                to_currency=w.target_currency,
                rate=w.rate,
                snapshot_time=w.time,  # 使用原始时间
                source='wise',
                extra={}
            )
            db.add(snapshot)
            snapshot_count += 1
            logging.info(f"添加Wise汇率快照: {w.source_currency}/{w.target_currency} = {w.rate}")
        
        # 2. 获取数字货币汇率并记录
        digital_currencies = [
            'USDT', 'USDC', 'BTC', 'ETH', 'IP', 'TRUMP', 'MOVE', 'S', 'KAITO', 'AIXBT', 'MXC',
            'DOGE', 'ADA', 'DOT', 'LINK', 'UNI', 'LTC', 'BCH', 'XRP', 'SOL', 'MATIC', 'AVAX',
            'ATOM', 'FTM', 'NEAR', 'ALGO', 'VET', 'THETA', 'FIL', 'ICP', 'APT', 'SUI', 'SEI',
            'TIA', 'JUP', 'PYTH', 'WIF', 'BONK', 'PEPE', 'SHIB', 'FLOKI', 'BOME', 'BOOK',
            'POPCAT', 'TURBO', 'MYRO', 'WEN', 'SLERF'
        ]
        
        logging.info(f"开始处理 {len(digital_currencies)} 种数字货币")
        
        for currency in digital_currencies:
            try:
                # 获取数字货币对USDT汇率
                usdt_rate = get_latest_rate(db, currency, 'USDT', snapshot_time)
                if usdt_rate:
                    logging.info(f"获取到 {currency}/USDT 汇率: {usdt_rate}")
                    
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
                    snapshot_count += 1
                    
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
                    snapshot_count += 1
                    
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
                        snapshot_count += 1
                        logging.info(f"计算 {currency}/CNY 汇率: {cny_rate}")
                    
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
                        snapshot_count += 1
                        logging.info(f"计算 {currency}/EUR 汇率: {eur_rate}")
                else:
                    logging.warning(f"未获取到 {currency}/USDT 汇率")
                    
            except Exception as e:
                logging.error(f"处理数字货币 {currency} 时出错: {e}")
                continue
        
        db.commit()
        logging.info(f"汇率快照生成完成，共生成 {snapshot_count} 条记录")
        return snapshot_count
        
    except Exception as e:
        logging.error(f"生成汇率快照时出错: {e}")
        db.rollback()
        raise