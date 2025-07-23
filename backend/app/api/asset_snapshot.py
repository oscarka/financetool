from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from app.core.database import get_db
from app.models.asset_snapshot import AssetSnapshot, ExchangeRateSnapshot
from sqlalchemy import desc, func

router = APIRouter(prefix="/api/snapshot", tags=["资产快照"])

@router.get("/assets")
def get_asset_snapshots(
    platform: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    base_currency: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取资产快照，支持多基准货币展示"""
    q = db.query(AssetSnapshot)
    if platform:
        q = q.filter(AssetSnapshot.platform == platform)
    if asset_type:
        q = q.filter(AssetSnapshot.asset_type == asset_type)
    if currency:
        q = q.filter(AssetSnapshot.currency == currency)
    if start:
        q = q.filter(AssetSnapshot.snapshot_time >= start)
    if end:
        q = q.filter(AssetSnapshot.snapshot_time <= end)
    q = q.order_by(desc(AssetSnapshot.snapshot_time))
    data = q.all()
    # 多基准货币展示
    def get_base_value(row):
        if base_currency == 'CNY':
            return row.balance_cny
        elif base_currency == 'USD':
            return row.balance_usd
        elif base_currency == 'EUR':
            return row.balance_eur
        else:
            return row.balance
    return [{
        'id': r.id,
        'user_id': r.user_id,
        'platform': r.platform,
        'asset_type': r.asset_type,
        'asset_code': r.asset_code,
        'asset_name': r.asset_name,
        'currency': r.currency,
        'balance': float(r.balance),
        'balance_cny': float(r.balance_cny) if r.balance_cny else None,
        'balance_usd': float(r.balance_usd) if r.balance_usd else None,
        'balance_eur': float(r.balance_eur) if r.balance_eur else None,
        'base_value': float(get_base_value(r)) if get_base_value(r) else None,
        'snapshot_time': r.snapshot_time.isoformat(),
        'extra': r.extra
    } for r in data]

@router.get("/assets/trend")
def get_asset_trend(
    platform: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    base_currency: Optional[str] = Query('CNY'),
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    """获取资产快照趋势，按天聚合"""
    end = datetime.now()
    start = end - timedelta(days=days)
    q = db.query(
        func.date_trunc('day', AssetSnapshot.snapshot_time).label('day'),
        func.sum(getattr(AssetSnapshot, f'balance_{base_currency.lower()}')).label('total')
    )
    if platform:
        q = q.filter(AssetSnapshot.platform == platform)
    if asset_type:
        q = q.filter(AssetSnapshot.asset_type == asset_type)
    if currency:
        q = q.filter(AssetSnapshot.currency == currency)
    q = q.filter(AssetSnapshot.snapshot_time >= start, AssetSnapshot.snapshot_time <= end)
    q = q.group_by('day').order_by('day')
    return [{
        'date': row.day.date().isoformat(),
        'total': float(row.total) if row.total else 0
    } for row in q.all()]

@router.get("/exchange-rates")
def get_exchange_rate_snapshots(
    from_currency: Optional[str] = Query(None),
    to_currency: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取汇率快照历史"""
    q = db.query(ExchangeRateSnapshot)
    if from_currency:
        q = q.filter(ExchangeRateSnapshot.from_currency == from_currency)
    if to_currency:
        q = q.filter(ExchangeRateSnapshot.to_currency == to_currency)
    if start:
        q = q.filter(ExchangeRateSnapshot.snapshot_time >= start)
    if end:
        q = q.filter(ExchangeRateSnapshot.snapshot_time <= end)
    q = q.order_by(desc(ExchangeRateSnapshot.snapshot_time))
    return [{
        'id': r.id,
        'from_currency': r.from_currency,
        'to_currency': r.to_currency,
        'rate': float(r.rate),
        'snapshot_time': r.snapshot_time.isoformat(),
        'source': r.source,
        'extra': r.extra
    } for r in q.all()]