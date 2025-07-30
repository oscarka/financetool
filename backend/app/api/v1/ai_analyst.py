"""
AI分析师数据API接口
为外部AI分析师提供原始资产数据和基础计算结果，供其进行独立分析
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
import hashlib
import hmac
import time
from app.utils.database import get_db
from app.models.database import (
    UserOperation, AssetPosition, FundInfo, FundNav, 
    FundDividend, DCAPlan
)
from app.models.asset_snapshot import AssetSnapshot, ExchangeRateSnapshot
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-analyst", tags=["AI分析师数据接口"])

# 数据响应模型
class AssetDataResponse(BaseModel):
    """资产数据响应模型"""
    current_holdings: List[Dict[str, Any]] = Field(..., description="当前持仓数据")
    total_value_by_currency: Dict[str, float] = Field(..., description="按币种统计的总价值")
    platform_summary: List[Dict[str, Any]] = Field(..., description="平台汇总数据")
    asset_type_summary: List[Dict[str, Any]] = Field(..., description="资产类型汇总")
    snapshot_time: str = Field(..., description="数据快照时间")

class TransactionDataResponse(BaseModel):
    """交易数据响应模型"""
    transactions: List[Dict[str, Any]] = Field(..., description="交易记录")
    summary_stats: Dict[str, Any] = Field(..., description="基础统计")
    time_series_data: List[Dict[str, Any]] = Field(..., description="时间序列数据")

class HistoricalDataResponse(BaseModel):
    """历史数据响应模型"""
    asset_values: List[Dict[str, Any]] = Field(..., description="资产价值历史")
    nav_data: List[Dict[str, Any]] = Field(..., description="净值数据") 
    price_data: List[Dict[str, Any]] = Field(..., description="价格数据")

class MarketDataResponse(BaseModel):
    """市场数据响应模型"""
    exchange_rates: List[Dict[str, Any]] = Field(..., description="汇率数据")
    fund_navs: List[Dict[str, Any]] = Field(..., description="基金净值")
    market_indicators: Dict[str, Any] = Field(..., description="市场指标")

class DCADataResponse(BaseModel):
    """定投数据响应模型"""
    dca_plans: List[Dict[str, Any]] = Field(..., description="定投计划")
    execution_history: List[Dict[str, Any]] = Field(..., description="执行历史")
    statistics: Dict[str, Any] = Field(..., description="基础统计")

# API Key验证
def verify_api_key(x_api_key: str = Header(None)):
    """验证API密钥"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="缺少API密钥")
    
    valid_keys = ["ai_analyst_key_2024", "demo_key_12345"]
    
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return x_api_key

@router.get("/asset-data", response_model=AssetDataResponse)
def get_asset_data(
    base_currency: str = Query("CNY", description="基准货币"),
    include_small_amounts: bool = Query(False, description="是否包含小额资产"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取当前资产持仓数据
    
    返回最新的资产快照数据，包括：
    - 所有平台的当前持仓
    - 按币种和平台的汇总
    - 原始数值，不含分析结论
    """
    
    # 获取最新快照时间
    latest_snapshot_time = db.query(func.max(AssetSnapshot.snapshot_time)).scalar()
    if not latest_snapshot_time:
        raise HTTPException(status_code=404, detail="没有找到资产快照数据")
    
    # 获取最新的资产快照
    latest_snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time == latest_snapshot_time
    ).all()
    
    balance_field = f"balance_{base_currency.lower()}"
    min_amount = 0.0 if include_small_amounts else 0.01
    
    # 处理当前持仓数据
    current_holdings = []
    total_by_currency = {}
    platform_totals = {}
    asset_type_totals = {}
    
    for snapshot in latest_snapshots:
        # 获取各币种余额
        balance_cny = float(snapshot.balance_cny) if snapshot.balance_cny else 0
        balance_usd = float(snapshot.balance_usd) if snapshot.balance_usd else 0
        balance_eur = float(snapshot.balance_eur) if snapshot.balance_eur else 0
        balance_original = float(snapshot.balance)
        
        # 基准货币价值
        base_value = getattr(snapshot, balance_field, None)
        base_value = float(base_value) if base_value else balance_original
        
        # 过滤小额资产
        if base_value < min_amount:
            continue
        
        # 持仓明细
        holding = {
            "id": snapshot.id,
            "platform": snapshot.platform,
            "asset_type": snapshot.asset_type,
            "asset_code": snapshot.asset_code,
            "asset_name": snapshot.asset_name,
            "currency": snapshot.currency,
            "balance_original": balance_original,
            "balance_cny": balance_cny,
            "balance_usd": balance_usd,
            "balance_eur": balance_eur,
            "base_currency_value": base_value,
            "snapshot_time": snapshot.snapshot_time.isoformat(),
            "extra_data": snapshot.extra
        }
        current_holdings.append(holding)
        
        # 统计汇总
        currency = snapshot.currency
        if currency not in total_by_currency:
            total_by_currency[currency] = 0
        total_by_currency[currency] += base_value
        
        # 平台汇总
        platform = snapshot.platform
        if platform not in platform_totals:
            platform_totals[platform] = {"count": 0, "value": 0, "currencies": set()}
        platform_totals[platform]["count"] += 1
        platform_totals[platform]["value"] += base_value
        platform_totals[platform]["currencies"].add(currency)
        
        # 资产类型汇总
        asset_type = snapshot.asset_type
        if asset_type not in asset_type_totals:
            asset_type_totals[asset_type] = {"count": 0, "value": 0, "assets": set()}
        asset_type_totals[asset_type]["count"] += 1
        asset_type_totals[asset_type]["value"] += base_value
        asset_type_totals[asset_type]["assets"].add(snapshot.asset_code)
    
    # 格式化平台汇总
    platform_summary = []
    for platform, data in platform_totals.items():
        platform_summary.append({
            "platform": platform,
            "asset_count": data["count"],
            "total_value": data["value"],
            "currencies": list(data["currencies"])
        })
    
    # 格式化资产类型汇总
    asset_type_summary = []
    for asset_type, data in asset_type_totals.items():
        asset_type_summary.append({
            "asset_type": asset_type,
            "asset_count": data["count"],
            "total_value": data["value"],
            "unique_assets": len(data["assets"])
        })
    
    return AssetDataResponse(
        current_holdings=current_holdings,
        total_value_by_currency=total_by_currency,
        platform_summary=platform_summary,
        asset_type_summary=asset_type_summary,
        snapshot_time=latest_snapshot_time.isoformat()
    )

@router.get("/transaction-data", response_model=TransactionDataResponse)
def get_transaction_data(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    asset_type: Optional[str] = Query(None, description="资产类型筛选"),
    operation_type: Optional[str] = Query(None, description="操作类型筛选"),
    limit: int = Query(1000, description="记录数限制"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取交易操作数据
    
    返回用户的交易历史记录，包括：
    - 详细的交易操作记录
    - 基础统计数据
    - 按时间的操作分布
    """
    
    # 构建查询
    query = db.query(UserOperation)
    
    if start_date:
        query = query.filter(UserOperation.operation_date >= start_date)
    if end_date:
        query = query.filter(UserOperation.operation_date <= end_date)
    if platform:
        query = query.filter(UserOperation.platform == platform)
    if asset_type:
        query = query.filter(UserOperation.asset_type == asset_type)
    if operation_type:
        query = query.filter(UserOperation.operation_type == operation_type)
    
    operations = query.order_by(desc(UserOperation.operation_date)).limit(limit).all()
    
    # 格式化交易记录
    transactions = []
    for op in operations:
        transaction = {
            "id": op.id,
            "date": op.operation_date.isoformat(),
            "platform": op.platform,
            "asset_type": op.asset_type,
            "operation_type": op.operation_type,
            "asset_code": op.asset_code,
            "asset_name": op.asset_name,
            "amount": float(op.amount),
            "currency": op.currency,
            "quantity": float(op.quantity) if op.quantity else None,
            "price": float(op.price) if op.price else None,
            "nav": float(op.nav) if op.nav else None,
            "fee": float(op.fee) if op.fee else 0,
            "strategy": op.strategy,
            "emotion_score": op.emotion_score,
            "notes": op.notes,
            "status": op.status,
            "dca_plan_id": op.dca_plan_id,
            "dca_execution_type": op.dca_execution_type
        }
        transactions.append(transaction)
    
    # 基础统计
    total_operations = len(operations)
    operation_types = {}
    currencies = {}
    platforms = {}
    monthly_counts = {}
    
    for op in operations:
        # 操作类型统计
        op_type = op.operation_type
        if op_type not in operation_types:
            operation_types[op_type] = {"count": 0, "total_amount": 0}
        operation_types[op_type]["count"] += 1
        operation_types[op_type]["total_amount"] += float(op.amount)
        
        # 货币统计
        currency = op.currency
        if currency not in currencies:
            currencies[currency] = {"count": 0, "total_amount": 0}
        currencies[currency]["count"] += 1
        currencies[currency]["total_amount"] += float(op.amount)
        
        # 平台统计
        platform = op.platform
        if platform not in platforms:
            platforms[platform] = {"count": 0}
        platforms[platform]["count"] += 1
        
        # 月度统计
        month_key = op.operation_date.strftime('%Y-%m')
        if month_key not in monthly_counts:
            monthly_counts[month_key] = 0
        monthly_counts[month_key] += 1
    
    # 时间序列数据
    time_series_data = []
    for month, count in sorted(monthly_counts.items()):
        time_series_data.append({
            "period": month,
            "operation_count": count
        })
    
    summary_stats = {
        "total_operations": total_operations,
        "operation_types": operation_types,
        "currencies": currencies,
        "platforms": platforms,
        "date_range": {
            "start": operations[-1].operation_date.isoformat() if operations else None,
            "end": operations[0].operation_date.isoformat() if operations else None
        }
    }
    
    return TransactionDataResponse(
        transactions=transactions,
        summary_stats=summary_stats,
        time_series_data=time_series_data
    )

@router.get("/historical-data", response_model=HistoricalDataResponse)
def get_historical_data(
    days: int = Query(90, description="历史天数"),
    asset_codes: Optional[str] = Query(None, description="资产代码，逗号分隔"),
    base_currency: str = Query("CNY", description="基准货币"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取历史数据
    
    返回资产的历史价值变化数据，包括：
    - 资产价值时间序列
    - 基金净值历史
    - 价格变化数据
    """
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 获取资产价值历史
    snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time >= start_date,
        AssetSnapshot.snapshot_time <= end_date
    ).order_by(AssetSnapshot.snapshot_time).all()
    
    # 如果指定了资产代码，进行过滤
    if asset_codes:
        code_list = [code.strip() for code in asset_codes.split(',')]
        snapshots = [s for s in snapshots if s.asset_code in code_list]
    
    # 处理资产价值历史
    asset_values = []
    balance_field = f"balance_{base_currency.lower()}"
    
    for snapshot in snapshots:
        balance = getattr(snapshot, balance_field, None) or snapshot.balance
        if balance:
            asset_values.append({
                "date": snapshot.snapshot_time.isoformat(),
                "platform": snapshot.platform,
                "asset_type": snapshot.asset_type,
                "asset_code": snapshot.asset_code,
                "asset_name": snapshot.asset_name,
                "currency": snapshot.currency,
                "balance_original": float(snapshot.balance),
                "balance_cny": float(snapshot.balance_cny) if snapshot.balance_cny else None,
                "balance_usd": float(snapshot.balance_usd) if snapshot.balance_usd else None,
                "balance_eur": float(snapshot.balance_eur) if snapshot.balance_eur else None,
                "base_value": float(balance),
                "extra_data": snapshot.extra
            })
    
    # 获取基金净值历史
    nav_query = db.query(FundNav).filter(
        FundNav.nav_date >= start_date.date(),
        FundNav.nav_date <= end_date.date()
    )
    
    if asset_codes:
        nav_query = nav_query.filter(FundNav.fund_code.in_(code_list))
    
    nav_data_raw = nav_query.order_by(FundNav.nav_date).all()
    
    nav_data = []
    for nav in nav_data_raw:
        nav_data.append({
            "date": nav.nav_date.isoformat(),
            "fund_code": nav.fund_code,
            "nav": float(nav.nav),
            "accumulated_nav": float(nav.accumulated_nav) if nav.accumulated_nav else None,
            "growth_rate": float(nav.growth_rate) if nav.growth_rate else None,
            "source": nav.source
        })
    
    # 价格数据（基于交易记录中的价格）
    price_query = db.query(UserOperation).filter(
        UserOperation.operation_date >= start_date,
        UserOperation.operation_date <= end_date,
        UserOperation.price.isnot(None)
    )
    
    if asset_codes:
        price_query = price_query.filter(UserOperation.asset_code.in_(code_list))
    
    price_operations = price_query.order_by(UserOperation.operation_date).all()
    
    price_data = []
    for op in price_operations:
        price_data.append({
            "date": op.operation_date.isoformat(),
            "asset_code": op.asset_code,
            "asset_name": op.asset_name,
            "price": float(op.price),
            "nav": float(op.nav) if op.nav else None,
            "operation_type": op.operation_type,
            "platform": op.platform
        })
    
    return HistoricalDataResponse(
        asset_values=asset_values,
        nav_data=nav_data,
        price_data=price_data
    )

@router.get("/market-data", response_model=MarketDataResponse)
def get_market_data(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取市场相关数据
    
    返回市场环境数据，包括：
    - 当前汇率
    - 基金净值
    - 市场基础指标
    """
    
    # 获取最新汇率
    latest_rates_query = db.query(ExchangeRateSnapshot).order_by(desc(ExchangeRateSnapshot.snapshot_time)).limit(50)
    latest_rates = latest_rates_query.all()
    
    exchange_rates = []
    rate_dict = {}
    
    for rate in latest_rates:
        key = f"{rate.from_currency}-{rate.to_currency}"
        if key not in rate_dict or rate.snapshot_time > rate_dict[key]["snapshot_time"]:
            rate_dict[key] = {
                "from_currency": rate.from_currency,
                "to_currency": rate.to_currency,
                "rate": float(rate.rate),
                "snapshot_time": rate.snapshot_time,
                "source": rate.source,
                "extra_data": rate.extra
            }
    
    exchange_rates = list(rate_dict.values())
    
    # 获取最新基金净值（最近7天）
    recent_date = datetime.now().date() - timedelta(days=7)
    recent_navs = db.query(FundNav).filter(
        FundNav.nav_date >= recent_date
    ).order_by(desc(FundNav.nav_date)).limit(100).all()
    
    fund_navs = []
    for nav in recent_navs:
        fund_navs.append({
            "fund_code": nav.fund_code,
            "nav_date": nav.nav_date.isoformat(),
            "nav": float(nav.nav),
            "accumulated_nav": float(nav.accumulated_nav) if nav.accumulated_nav else None,
            "growth_rate": float(nav.growth_rate) if nav.growth_rate else None,
            "source": nav.source
        })
    
    # 市场基础指标
    total_funds = db.query(func.count(FundInfo.id)).scalar()
    active_funds = db.query(func.count(func.distinct(FundNav.fund_code))).filter(
        FundNav.nav_date >= recent_date
    ).scalar()
    
    total_operations = db.query(func.count(UserOperation.id)).scalar()
    recent_operations = db.query(func.count(UserOperation.id)).filter(
        UserOperation.operation_date >= datetime.now() - timedelta(days=30)
    ).scalar()
    
    market_indicators = {
        "total_funds_tracked": total_funds or 0,
        "active_funds_last_week": active_funds or 0,
        "total_user_operations": total_operations or 0,
        "operations_last_30_days": recent_operations or 0,
        "data_freshness": {
            "latest_snapshot": db.query(func.max(AssetSnapshot.snapshot_time)).scalar(),
            "latest_exchange_rate": db.query(func.max(ExchangeRateSnapshot.snapshot_time)).scalar(),
            "latest_fund_nav": db.query(func.max(FundNav.nav_date)).scalar()
        }
    }
    
    return MarketDataResponse(
        exchange_rates=exchange_rates,
        fund_navs=fund_navs,
        market_indicators=market_indicators
    )

@router.get("/dca-data", response_model=DCADataResponse)
def get_dca_data(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取定投计划数据
    
    返回定投相关的原始数据，包括：
    - 定投计划配置
    - 执行历史记录
    - 基础统计信息
    """
    
    # 获取所有定投计划
    dca_plans_raw = db.query(DCAPlan).all()
    
    dca_plans = []
    for plan in dca_plans_raw:
        dca_plans.append({
            "id": plan.id,
            "plan_name": plan.plan_name,
            "platform": plan.platform,
            "asset_type": plan.asset_type,
            "asset_code": plan.asset_code,
            "asset_name": plan.asset_name,
            "amount": float(plan.amount),
            "currency": plan.currency,
            "frequency": plan.frequency,
            "frequency_value": plan.frequency_value,
            "start_date": plan.start_date.isoformat() if plan.start_date else None,
            "end_date": plan.end_date.isoformat() if plan.end_date else None,
            "status": plan.status,
            "strategy": plan.strategy,
            "execution_time": plan.execution_time,
            "next_execution_date": plan.next_execution_date.isoformat() if plan.next_execution_date else None,
            "last_execution_date": plan.last_execution_date.isoformat() if plan.last_execution_date else None,
            "execution_count": plan.execution_count or 0,
            "total_invested": float(plan.total_invested or 0),
            "total_shares": float(plan.total_shares or 0),
            "smart_dca": plan.smart_dca,
            "base_amount": float(plan.base_amount) if plan.base_amount else None,
            "max_amount": float(plan.max_amount) if plan.max_amount else None,
            "increase_rate": float(plan.increase_rate) if plan.increase_rate else None
        })
    
    # 获取定投执行历史
    dca_operations = db.query(UserOperation).filter(
        UserOperation.dca_plan_id.isnot(None)
    ).order_by(desc(UserOperation.operation_date)).all()
    
    execution_history = []
    for op in dca_operations:
        execution_history.append({
            "operation_id": op.id,
            "dca_plan_id": op.dca_plan_id,
            "execution_date": op.operation_date.isoformat(),
            "amount": float(op.amount),
            "quantity": float(op.quantity) if op.quantity else None,
            "nav": float(op.nav) if op.nav else None,
            "fee": float(op.fee) if op.fee else 0,
            "execution_type": op.dca_execution_type,
            "asset_code": op.asset_code,
            "platform": op.platform
        })
    
    # 基础统计
    total_plans = len(dca_plans_raw)
    active_plans = len([p for p in dca_plans_raw if p.status == "active"])
    total_dca_invested = sum([float(op.amount) for op in dca_operations])
    total_dca_operations = len(dca_operations)
    
    # 按计划统计
    plan_stats = {}
    for op in dca_operations:
        plan_id = op.dca_plan_id
        if plan_id not in plan_stats:
            plan_stats[plan_id] = {
                "operation_count": 0,
                "total_invested": 0,
                "avg_nav": []
            }
        plan_stats[plan_id]["operation_count"] += 1
        plan_stats[plan_id]["total_invested"] += float(op.amount)
        if op.nav:
            plan_stats[plan_id]["avg_nav"].append(float(op.nav))
    
    statistics = {
        "total_plans": total_plans,
        "active_plans": active_plans,
        "total_invested": total_dca_invested,
        "total_operations": total_dca_operations,
        "plan_statistics": plan_stats
    }
    
    return DCADataResponse(
        dca_plans=dca_plans,
        execution_history=execution_history,
        statistics=statistics
    )

@router.get("/health")
def health_check(api_key: str = Depends(verify_api_key)):
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
        "message": "AI分析师数据API服务正常运行"
    }