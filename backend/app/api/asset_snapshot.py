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
    time_granularity: str = Query('day', description="时间粒度: day(天), half_day(半天), hour(小时)"),
    db: Session = Depends(get_db)
):
    """获取资产快照趋势，支持不同时间粒度，取每个时间段的最新数据"""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    # 根据时间粒度确定时间截断函数
    if time_granularity == 'hour':
        time_trunc_func = func.date_trunc('hour', AssetSnapshot.snapshot_time)
        time_label = 'hour'
    elif time_granularity == 'half_day':
        # 自定义半天截断：上午(00:00-11:59)和下午(12:00-23:59)
        time_trunc_func = func.case(
            (func.extract('hour', AssetSnapshot.snapshot_time) < 12,
             func.date_trunc('day', AssetSnapshot.snapshot_time)),
            else_=func.date_trunc('day', AssetSnapshot.snapshot_time) + func.interval('12 hours')
        )
        time_label = 'half_day'
    else:  # default: day
        time_trunc_func = func.date_trunc('day', AssetSnapshot.snapshot_time)
        time_label = 'day'
    
    # 使用窗口函数获取每个时间段的最新快照
    from sqlalchemy import text
    
    # 构建子查询：为每个时间段找到最新的快照ID
    latest_snapshot_subquery = db.query(
        time_trunc_func.label('time_period'),
        func.max(AssetSnapshot.snapshot_time).label('latest_time')
    ).filter(
        AssetSnapshot.snapshot_time >= start,
        AssetSnapshot.snapshot_time <= end
    )
    
    if platform:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(AssetSnapshot.platform == platform)
    if asset_type:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(AssetSnapshot.asset_type == asset_type)
    if currency:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(AssetSnapshot.currency == currency)
    
    latest_snapshot_subquery = latest_snapshot_subquery.group_by('time_period')
    
    # 主查询：基于最新快照时间聚合资产
    q = db.query(
        time_trunc_func.label('time_period'),
        func.sum(getattr(AssetSnapshot, f'balance_{base_currency.lower()}')).label('total')
    ).join(
        latest_snapshot_subquery.subquery(),
        AssetSnapshot.snapshot_time == latest_snapshot_subquery.subquery().c.latest_time
    ).filter(
        AssetSnapshot.snapshot_time >= start,
        AssetSnapshot.snapshot_time <= end
    )
    
    if platform:
        q = q.filter(AssetSnapshot.platform == platform)
    if asset_type:
        q = q.filter(AssetSnapshot.asset_type == asset_type)
    if currency:
        q = q.filter(AssetSnapshot.currency == currency)
    
    q = q.group_by('time_period').order_by('time_period')
    
    result = []
    for row in q.all():
        # 格式化时间显示
        if time_granularity == 'hour':
            date_str = row.time_period.strftime('%Y-%m-%d %H:00')
        elif time_granularity == 'half_day':
            if row.time_period.hour == 0:
                date_str = row.time_period.strftime('%Y-%m-%d 上午')
            else:
                date_str = row.time_period.strftime('%Y-%m-%d 下午')
        else:  # day
            date_str = row.time_period.date().isoformat()
        
        result.append({
            'date': date_str,
            'datetime': row.time_period.isoformat(),
            'total': float(row.total) if row.total else 0,
            'time_granularity': time_granularity
        })
    
    return {
        "success": True,
        "message": f"获取到 {len(result)} 条趋势数据 (粒度: {time_granularity})",
        "data": result,
        "time_granularity": time_granularity
    }

@router.get("/exchange-rates")
def get_exchange_rate_snapshots(
    from_currency: Optional[str] = Query(None),
    to_currency: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    time_granularity: str = Query('day', description="时间粒度: day(天), half_day(半天), hour(小时), raw(原始数据)"),
    db: Session = Depends(get_db)
):
    """获取汇率快照历史，支持时间粒度聚合"""
    
    # 如果请求原始数据，直接返回所有快照
    if time_granularity == 'raw':
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
            "message": f"获取到 {len(result)} 条原始汇率快照数据",
            "data": result,
            "time_granularity": "raw"
        }
    
    # 时间粒度聚合逻辑
    if time_granularity == 'hour':
        time_trunc_func = func.date_trunc('hour', ExchangeRateSnapshot.snapshot_time)
    elif time_granularity == 'half_day':
        time_trunc_func = func.case(
            (func.extract('hour', ExchangeRateSnapshot.snapshot_time) < 12,
             func.date_trunc('day', ExchangeRateSnapshot.snapshot_time)),
            else_=func.date_trunc('day', ExchangeRateSnapshot.snapshot_time) + func.interval('12 hours')
        )
    else:  # default: day
        time_trunc_func = func.date_trunc('day', ExchangeRateSnapshot.snapshot_time)
    
    # 构建子查询：为每个时间段找到最新的快照
    latest_snapshot_subquery = db.query(
        time_trunc_func.label('time_period'),
        ExchangeRateSnapshot.from_currency,
        ExchangeRateSnapshot.to_currency,
        func.max(ExchangeRateSnapshot.snapshot_time).label('latest_time')
    )
    
    if from_currency:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(ExchangeRateSnapshot.from_currency == from_currency)
    if to_currency:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(ExchangeRateSnapshot.to_currency == to_currency)
    if start:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(ExchangeRateSnapshot.snapshot_time >= start)
    if end:
        latest_snapshot_subquery = latest_snapshot_subquery.filter(ExchangeRateSnapshot.snapshot_time <= end)
    
    latest_snapshot_subquery = latest_snapshot_subquery.group_by(
        'time_period', 
        ExchangeRateSnapshot.from_currency, 
        ExchangeRateSnapshot.to_currency
    )
    
    # 主查询：基于最新快照时间获取汇率数据
    q = db.query(
        time_trunc_func.label('time_period'),
        ExchangeRateSnapshot.from_currency,
        ExchangeRateSnapshot.to_currency,
        ExchangeRateSnapshot.rate,
        ExchangeRateSnapshot.snapshot_time,
        ExchangeRateSnapshot.source,
        ExchangeRateSnapshot.extra
    ).join(
        latest_snapshot_subquery.subquery(),
        (ExchangeRateSnapshot.snapshot_time == latest_snapshot_subquery.subquery().c.latest_time) &
        (ExchangeRateSnapshot.from_currency == latest_snapshot_subquery.subquery().c.from_currency) &
        (ExchangeRateSnapshot.to_currency == latest_snapshot_subquery.subquery().c.to_currency)
    )
    
    if from_currency:
        q = q.filter(ExchangeRateSnapshot.from_currency == from_currency)
    if to_currency:
        q = q.filter(ExchangeRateSnapshot.to_currency == to_currency)
    if start:
        q = q.filter(ExchangeRateSnapshot.snapshot_time >= start)
    if end:
        q = q.filter(ExchangeRateSnapshot.snapshot_time <= end)
    
    q = q.order_by('time_period', ExchangeRateSnapshot.from_currency, ExchangeRateSnapshot.to_currency)
    
    result = []
    for row in q.all():
        # 格式化时间显示
        if time_granularity == 'hour':
            date_str = row.time_period.strftime('%Y-%m-%d %H:00')
        elif time_granularity == 'half_day':
            if row.time_period.hour == 0:
                date_str = row.time_period.strftime('%Y-%m-%d 上午')
            else:
                date_str = row.time_period.strftime('%Y-%m-%d 下午')
        else:  # day
            date_str = row.time_period.date().isoformat()
        
        result.append({
            'time_period': date_str,
            'datetime': row.time_period.isoformat(),
            'from_currency': row.from_currency,
            'to_currency': row.to_currency,
            'rate': float(row.rate),
            'snapshot_time': row.snapshot_time.isoformat(),
            'source': row.source,
            'extra': row.extra
        })
    
    return {
        "success": True,
        "message": f"获取到 {len(result)} 条聚合汇率数据 (粒度: {time_granularity})",
        "data": result,
        "time_granularity": time_granularity
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