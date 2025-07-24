from datetime import datetime
from sqlalchemy.orm import Session
from app.models.asset_snapshot import AssetSnapshot, ExchangeRateSnapshot
from app.models.database import AssetPosition, WiseBalance, IBKRBalance, OKXBalance, ExchangeRate, WiseExchangeRate
from decimal import Decimal
import logging

# 假设有汇率获取函数

def get_latest_rate(db: Session, from_currency: str, to_currency: str, time_point: datetime = None):
    # 优先用ExchangeRate表，回退WiseExchangeRate
    q = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == from_currency,
        ExchangeRate.to_currency == to_currency
    )
    if time_point:
        q = q.filter(ExchangeRate.rate_date <= time_point.date())
    rate = q.order_by(ExchangeRate.rate_date.desc()).first()
    if rate:
        return Decimal(rate.rate)
    # WiseExchangeRate回退
    q2 = db.query(WiseExchangeRate).filter(
        WiseExchangeRate.source_currency == from_currency,
        WiseExchangeRate.target_currency == to_currency
    )
    if time_point:
        q2 = q2.filter(WiseExchangeRate.time <= time_point)
    wise_rate = q2.order_by(WiseExchangeRate.time.desc()).first()
    if wise_rate:
        return Decimal(wise_rate.rate)
    return None


def extract_asset_snapshot(db: Session, snapshot_time: datetime = None):
    if snapshot_time is None:
        snapshot_time = datetime.now()
    # 汇率缓存，减少重复查表
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
        cny_rate = get_rate(asset['currency'], 'CNY')
        usd_rate = get_rate(asset['currency'], 'USD')
        eur_rate = get_rate(asset['currency'], 'EUR')
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
            snapshot_time=snapshot_time,
            extra={}
        )
        logging.warning(f"[extract_asset_snapshot] writing snapshot: {{'platform': {snapshot.platform}, 'asset_type': {snapshot.asset_type}, 'asset_code': {snapshot.asset_code}, 'currency': {snapshot.currency}, 'balance': {snapshot.balance}, 'balance_cny': {snapshot.balance_cny}, 'balance_usd': {snapshot.balance_usd}, 'balance_eur': {snapshot.balance_eur}}}")
        db.add(snapshot)
        snapshot_count += 1
    db.commit()
    return snapshot_count


def extract_exchange_rate_snapshot(db: Session, snapshot_time: datetime = None):
    if snapshot_time is None:
        snapshot_time = datetime.now()
    for r in db.query(ExchangeRate).all():
        snapshot = ExchangeRateSnapshot(
            from_currency=r.from_currency,
            to_currency=r.to_currency,
            rate=r.rate,
            snapshot_time=snapshot_time,
            source=r.source,
            extra={}
        )
        db.add(snapshot)
    for w in db.query(WiseExchangeRate).all():
        snapshot = ExchangeRateSnapshot(
            from_currency=w.source_currency,
            to_currency=w.target_currency,
            rate=w.rate,
            snapshot_time=w.time,
            source='wise',
            extra={}
        )
        db.add(snapshot)
    db.commit()