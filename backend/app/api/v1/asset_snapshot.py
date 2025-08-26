from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from app.utils.database import get_db
from app.models.asset_snapshot import AssetSnapshot, ExchangeRateSnapshot
from sqlalchemy import desc, func
import logging
from app.services.asset_snapshot_service import extract_asset_snapshot, extract_exchange_rate_snapshot

router = APIRouter(prefix="/snapshot", tags=["资产快照"])

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
    logging.warning(f"[asset_snapshot] called with platform={platform}, asset_type={asset_type}, currency={currency}, base_currency={base_currency}, start={start}, end={end}")
    """获取资产快照，支持多基准货币展示"""
    
    # 设置默认基准货币
    if base_currency is None:
        base_currency = 'CNY'
    
    # 特殊处理Wise和OKX平台：使用5分钟时间窗口获取最新快照数据
    if platform == 'Wise' or (asset_type == '外汇' and not platform):
        # 获取最新快照时间
        latest_snapshot_time = db.query(func.max(AssetSnapshot.snapshot_time)).scalar()
        if latest_snapshot_time:
            # 使用前后5分钟时间窗口获取快照数据，避免精确时间匹配导致的数据缺失
            time_window_start = latest_snapshot_time - timedelta(minutes=5)
            time_window_end = latest_snapshot_time + timedelta(minutes=5)
            
            q = db.query(AssetSnapshot).filter(
                AssetSnapshot.platform == 'Wise',
                AssetSnapshot.snapshot_time >= time_window_start,
                AssetSnapshot.snapshot_time <= time_window_end
            )
            logging.warning(f"[asset_snapshot] Wise平台使用5分钟时间窗口: {time_window_start} 到 {time_window_end}")
        else:
            # 如果没有快照数据，使用默认查询
            q = db.query(AssetSnapshot).filter(AssetSnapshot.platform == 'Wise')
    elif platform == 'OKX' or (asset_type == '数字货币' and not platform):
        # 获取最新快照时间
        latest_snapshot_time = db.query(func.max(AssetSnapshot.snapshot_time)).scalar()
        if latest_snapshot_time:
            # 使用前后5分钟时间窗口获取快照数据，避免精确时间匹配导致的数据缺失
            time_window_start = latest_snapshot_time - timedelta(minutes=5)
            time_window_end = latest_snapshot_time + timedelta(minutes=5)
            
            q = db.query(AssetSnapshot).filter(
                AssetSnapshot.platform == 'OKX',
                AssetSnapshot.snapshot_time >= time_window_start,
                AssetSnapshot.snapshot_time <= time_window_end
            )
            logging.warning(f"[asset_snapshot] OKX平台使用5分钟时间窗口: {time_window_start} 到 {time_window_end}")
        else:
            # 如果没有快照数据，使用默认查询
            q = db.query(AssetSnapshot).filter(AssetSnapshot.platform == 'OKX')
    else:
        # 其他平台使用原有逻辑
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
    logging.warning(f"[asset_snapshot] returning {len(data)} rows")
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
    
    # 过滤掉base_value为null或小于0.01的记录
    filtered_data = []
    for r in data:
        base_value = get_base_value(r)
        if base_value is None:
            # 如果base_value为null，跳过这条记录
            continue
        
        # 四舍五入到2位小数
        rounded_value = round(float(base_value), 2)
        # 如果四舍五入后小于0.01，跳过这条记录
        if rounded_value < 0.01:
            continue
        
        filtered_data.append(r)
    
    result = [{
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
    } for r in filtered_data]
    
    return {
        "success": True,
        "message": f"获取到 {len(result)} 条快照数据",
        "data": result
    }

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
    result = [{
        'date': row.day.date().isoformat(),
        'total': float(row.total) if row.total else 0
    } for row in q.all()]
    
    return {
        "success": True,
        "message": f"获取到 {len(result)} 条趋势数据",
        "data": result
    }

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
    result = [{
        'id': r.id,
        'from_currency': r.from_currency,
        'to_currency': r.to_currency,
        'rate': float(r.rate),
        'snapshot_time': r.snapshot_time.isoformat(),
        'source': r.source,
        'extra': r.extra
    } for r in q.all()]
    
    return {
        "success": True,
        "message": f"获取到 {len(result)} 条汇率快照数据",
        "data": result
    }

@router.post("/extract")
def extract_asset_snapshot_api(
    base_currency: str = Query('CNY', description="基准货币"),
    db: Session = Depends(get_db)
):
    """主动触发资产快照"""
    try:
        count = extract_asset_snapshot(db, base_currency=base_currency)
        return {"success": True, "message": f"已写入{count}条资产快照"}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}

@router.post("/extract-exchange-rates")
def extract_exchange_rate_snapshot_api(
    db: Session = Depends(get_db)
):
    """主动触发汇率快照"""
    try:
        count = extract_exchange_rate_snapshot(db)
        return {"success": True, "message": f"已写入{count}条汇率快照"}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}