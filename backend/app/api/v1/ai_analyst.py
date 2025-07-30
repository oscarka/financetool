"""
AI分析师专用API接口
为外部AI分析师提供资产数据查询和分析功能
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

router = APIRouter(prefix="/ai-analyst", tags=["AI分析师接口"])

# Pydantic响应模型
class AssetSummaryResponse(BaseModel):
    """资产总览响应模型"""
    total_assets: Dict[str, float] = Field(..., description="总资产，按币种分组")
    platform_breakdown: List[Dict[str, Any]] = Field(..., description="平台资产分布")
    asset_type_breakdown: List[Dict[str, Any]] = Field(..., description="资产类型分布") 
    top_holdings: List[Dict[str, Any]] = Field(..., description="主要持仓")
    last_update_time: str = Field(..., description="最后更新时间")

class InvestmentHistoryResponse(BaseModel):
    """投资历史响应模型"""
    operations: List[Dict[str, Any]] = Field(..., description="操作记录")
    total_invested: Dict[str, float] = Field(..., description="总投入，按币种分组")
    profit_summary: Dict[str, Any] = Field(..., description="收益汇总")
    monthly_flow: List[Dict[str, Any]] = Field(..., description="月度资金流")

class PerformanceAnalysisResponse(BaseModel):
    """绩效分析响应模型"""
    overall_return: Dict[str, float] = Field(..., description="整体收益率")
    asset_performance: List[Dict[str, Any]] = Field(..., description="资产表现")
    trend_analysis: Dict[str, Any] = Field(..., description="趋势分析")
    risk_metrics: Dict[str, Any] = Field(..., description="风险指标")

class ExchangeRateResponse(BaseModel):
    """汇率响应模型"""
    rates: List[Dict[str, Any]] = Field(..., description="汇率数据")
    last_update: str = Field(..., description="最后更新时间")
    supported_currencies: List[str] = Field(..., description="支持的货币")

class MarketDataResponse(BaseModel):
    """市场数据响应模型"""
    fund_navs: List[Dict[str, Any]] = Field(..., description="基金净值")
    market_summary: Dict[str, Any] = Field(..., description="市场概况")

# API Key验证（简单示例，生产环境需要更完善的认证）
def verify_api_key(x_api_key: str = Header(None)):
    """验证API密钥"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="缺少API密钥")
    
    # 这里可以实现更复杂的验证逻辑
    # 比如从数据库或配置中验证密钥
    valid_keys = ["ai_analyst_key_2024", "demo_key_12345"]  # 示例密钥
    
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return x_api_key

@router.get("/asset-summary", response_model=AssetSummaryResponse)
def get_asset_summary(
    base_currency: str = Query("CNY", description="基准货币"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取资产总览
    
    提供最新的资产分布情况，包括：
    - 总资产按币种分组
    - 平台资产分布
    - 资产类型分布
    - 主要持仓信息
    """
    
    # 获取最新快照时间
    latest_snapshot_time = db.query(func.max(AssetSnapshot.snapshot_time)).scalar()
    if not latest_snapshot_time:
        raise HTTPException(status_code=404, detail="没有找到资产快照数据")
    
    # 获取最新的资产快照
    latest_snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time == latest_snapshot_time
    ).all()
    
    # 计算总资产
    total_assets = {}
    platform_breakdown = {}
    asset_type_breakdown = {}
    
    for snapshot in latest_snapshots:
        # 总资产计算
        balance_field = f"balance_{base_currency.lower()}"
        balance = getattr(snapshot, balance_field, None) or snapshot.balance
        
        if balance and float(balance) >= 0.01:  # 过滤小额资产
            currency = snapshot.currency
            if currency not in total_assets:
                total_assets[currency] = 0
            total_assets[currency] += float(balance)
            
            # 平台分布
            platform = snapshot.platform
            if platform not in platform_breakdown:
                platform_breakdown[platform] = 0
            platform_breakdown[platform] += float(balance)
            
            # 资产类型分布
            asset_type = snapshot.asset_type
            if asset_type not in asset_type_breakdown:
                asset_type_breakdown[asset_type] = 0
            asset_type_breakdown[asset_type] += float(balance)
    
    # 转换为列表格式
    platform_list = [{"platform": k, "value": v, "percentage": v / sum(platform_breakdown.values()) * 100} 
                     for k, v in sorted(platform_breakdown.items(), key=lambda x: x[1], reverse=True)]
    
    asset_type_list = [{"asset_type": k, "value": v, "percentage": v / sum(asset_type_breakdown.values()) * 100} 
                       for k, v in sorted(asset_type_breakdown.items(), key=lambda x: x[1], reverse=True)]
    
    # 获取主要持仓（按价值排序前10）
    top_holdings = []
    for snapshot in sorted(latest_snapshots, key=lambda x: float(getattr(x, f"balance_{base_currency.lower()}", 0) or 0), reverse=True)[:10]:
        balance = getattr(snapshot, f"balance_{base_currency.lower()}", None) or snapshot.balance
        if balance and float(balance) >= 0.01:
            top_holdings.append({
                "platform": snapshot.platform,
                "asset_type": snapshot.asset_type,
                "asset_code": snapshot.asset_code,
                "asset_name": snapshot.asset_name,
                "value": float(balance),
                "currency": snapshot.currency,
                "percentage": float(balance) / sum(total_assets.values()) * 100 if total_assets else 0
            })
    
    return AssetSummaryResponse(
        total_assets=total_assets,
        platform_breakdown=platform_list,
        asset_type_breakdown=asset_type_list,
        top_holdings=top_holdings,
        last_update_time=latest_snapshot_time.isoformat()
    )

@router.get("/investment-history", response_model=InvestmentHistoryResponse)
def get_investment_history(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    asset_type: Optional[str] = Query(None, description="资产类型筛选"),
    limit: int = Query(100, description="记录数限制"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取投资历史记录
    
    提供详细的投资操作历史，包括：
    - 买入/卖出操作记录
    - 总投入统计
    - 收益汇总
    - 月度资金流
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
    
    operations = query.order_by(desc(UserOperation.operation_date)).limit(limit).all()
    
    # 格式化操作记录
    operation_list = []
    total_invested = {}
    
    for op in operations:
        operation_data = {
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
            "notes": op.notes
        }
        operation_list.append(operation_data)
        
        # 统计总投入
        currency = op.currency
        if currency not in total_invested:
            total_invested[currency] = 0
        if op.operation_type == "buy":
            total_invested[currency] += float(op.amount)
        elif op.operation_type == "sell":
            total_invested[currency] -= float(op.amount)
    
    # 计算月度资金流
    monthly_flow = db.query(
        func.date_trunc('month', UserOperation.operation_date).label('month'),
        UserOperation.currency,
        func.sum(
            func.case(
                (UserOperation.operation_type == 'buy', UserOperation.amount),
                else_=0
            )
        ).label('buy_amount'),
        func.sum(
            func.case(
                (UserOperation.operation_type == 'sell', UserOperation.amount),
                else_=0
            )
        ).label('sell_amount')
    ).group_by('month', UserOperation.currency).order_by('month').all()
    
    monthly_flow_list = []
    for flow in monthly_flow:
        monthly_flow_list.append({
            "month": flow.month.strftime('%Y-%m'),
            "currency": flow.currency,
            "buy_amount": float(flow.buy_amount or 0),
            "sell_amount": float(flow.sell_amount or 0),
            "net_flow": float((flow.buy_amount or 0) - (flow.sell_amount or 0))
        })
    
    # 简单的收益汇总计算
    profit_summary = {
        "note": "详细收益计算需要结合当前持仓和历史价格数据",
        "total_operations": len(operations),
        "buy_operations": len([op for op in operations if op.operation_type == "buy"]),
        "sell_operations": len([op for op in operations if op.operation_type == "sell"])
    }
    
    return InvestmentHistoryResponse(
        operations=operation_list,
        total_invested=total_invested,
        profit_summary=profit_summary,
        monthly_flow=monthly_flow_list
    )

@router.get("/performance-analysis", response_model=PerformanceAnalysisResponse)
def get_performance_analysis(
    base_currency: str = Query("CNY", description="基准货币"),
    days: int = Query(30, description="分析天数"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取绩效分析
    
    提供投资绩效分析，包括：
    - 整体收益率
    - 各资产表现
    - 趋势分析
    - 风险指标
    """
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 获取时间段内的快照数据进行趋势分析
    snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time >= start_date,
        AssetSnapshot.snapshot_time <= end_date
    ).order_by(AssetSnapshot.snapshot_time).all()
    
    if not snapshots:
        raise HTTPException(status_code=404, detail="指定时间段内没有快照数据")
    
    # 计算整体收益率（简化版本）
    balance_field = f"balance_{base_currency.lower()}"
    
    # 按天分组计算总资产
    daily_totals = {}
    for snapshot in snapshots:
        date_key = snapshot.snapshot_time.date()
        balance = getattr(snapshot, balance_field, None) or snapshot.balance
        if balance:
            if date_key not in daily_totals:
                daily_totals[date_key] = 0
            daily_totals[date_key] += float(balance)
    
    # 计算收益率
    dates = sorted(daily_totals.keys())
    if len(dates) >= 2:
        start_value = daily_totals[dates[0]]
        end_value = daily_totals[dates[-1]]
        total_return = (end_value - start_value) / start_value * 100 if start_value > 0 else 0
    else:
        total_return = 0
    
    overall_return = {
        base_currency.lower(): total_return,
        "period_days": days,
        "start_value": daily_totals.get(dates[0], 0) if dates else 0,
        "end_value": daily_totals.get(dates[-1], 0) if dates else 0
    }
    
    # 按资产分析表现
    asset_performance = []
    latest_snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time == max(s.snapshot_time for s in snapshots)
    ).all()
    
    for snapshot in latest_snapshots:
        balance = getattr(snapshot, balance_field, None) or snapshot.balance
        if balance and float(balance) >= 0.01:
            asset_performance.append({
                "platform": snapshot.platform,
                "asset_type": snapshot.asset_type,
                "asset_code": snapshot.asset_code,
                "asset_name": snapshot.asset_name,
                "current_value": float(balance),
                "currency": snapshot.currency
            })
    
    # 趋势分析
    trend_data = []
    for date_key in sorted(daily_totals.keys()):
        trend_data.append({
            "date": date_key.isoformat(),
            "total_value": daily_totals[date_key]
        })
    
    trend_analysis = {
        "daily_values": trend_data,
        "trend_direction": "up" if len(trend_data) >= 2 and trend_data[-1]["total_value"] > trend_data[0]["total_value"] else "down",
        "volatility": "low"  # 简化版本
    }
    
    # 风险指标（简化版本）
    values = [d["total_value"] for d in trend_data]
    if len(values) >= 2:
        daily_returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values)) if values[i-1] > 0]
        volatility = (sum([(r - sum(daily_returns) / len(daily_returns)) ** 2 for r in daily_returns]) / len(daily_returns)) ** 0.5 if daily_returns else 0
    else:
        volatility = 0
    
    risk_metrics = {
        "volatility": volatility,
        "max_drawdown": "需要更多历史数据计算",
        "var_95": "需要更多历史数据计算"
    }
    
    return PerformanceAnalysisResponse(
        overall_return=overall_return,
        asset_performance=asset_performance,
        trend_analysis=trend_analysis,
        risk_metrics=risk_metrics
    )

@router.get("/exchange-rates", response_model=ExchangeRateResponse)
def get_exchange_rates(
    base_currency: str = Query("CNY", description="基准货币"),
    target_currencies: Optional[str] = Query(None, description="目标货币，逗号分隔"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取汇率数据
    
    提供最新的汇率信息，支持：
    - 实时汇率查询
    - 多货币对转换
    - 汇率历史趋势
    """
    
    # 获取最新汇率快照
    query = db.query(ExchangeRateSnapshot)
    
    if target_currencies:
        target_list = [currency.strip() for currency in target_currencies.split(',')]
        query = query.filter(
            or_(
                and_(ExchangeRateSnapshot.from_currency == base_currency, 
                     ExchangeRateSnapshot.to_currency.in_(target_list)),
                and_(ExchangeRateSnapshot.from_currency.in_(target_list), 
                     ExchangeRateSnapshot.to_currency == base_currency)
            )
        )
    
    # 获取每个货币对的最新汇率
    latest_rates = query.order_by(desc(ExchangeRateSnapshot.snapshot_time)).all()
    
    # 按货币对分组，只保留最新的
    rate_dict = {}
    for rate in latest_rates:
        key = f"{rate.from_currency}-{rate.to_currency}"
        if key not in rate_dict or rate.snapshot_time > rate_dict[key]["snapshot_time"]:
            rate_dict[key] = {
                "from_currency": rate.from_currency,
                "to_currency": rate.to_currency,
                "rate": float(rate.rate),
                "snapshot_time": rate.snapshot_time,
                "source": rate.source
            }
    
    rates_list = list(rate_dict.values())
    
    # 获取支持的货币列表
    supported_currencies = list(set(
        [rate.from_currency for rate in latest_rates] + 
        [rate.to_currency for rate in latest_rates]
    ))
    
    last_update = max([rate["snapshot_time"] for rate in rates_list]).isoformat() if rates_list else datetime.now().isoformat()
    
    return ExchangeRateResponse(
        rates=[{
            "from_currency": rate["from_currency"],
            "to_currency": rate["to_currency"],
            "rate": rate["rate"],
            "last_update": rate["snapshot_time"].isoformat(),
            "source": rate["source"]
        } for rate in rates_list],
        last_update=last_update,
        supported_currencies=sorted(supported_currencies)
    )

@router.get("/market-data", response_model=MarketDataResponse)
def get_market_data(
    fund_codes: Optional[str] = Query(None, description="基金代码，逗号分隔"),
    days: int = Query(7, description="获取天数"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取市场数据
    
    提供市场相关数据，包括：
    - 基金净值数据
    - 市场概况
    - 行业信息
    """
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # 获取基金净值数据
    nav_query = db.query(FundNav).filter(
        FundNav.nav_date >= start_date,
        FundNav.nav_date <= end_date
    )
    
    if fund_codes:
        code_list = [code.strip() for code in fund_codes.split(',')]
        nav_query = nav_query.filter(FundNav.fund_code.in_(code_list))
    
    nav_data = nav_query.order_by(desc(FundNav.nav_date)).all()
    
    # 格式化净值数据
    fund_navs = []
    for nav in nav_data:
        fund_navs.append({
            "fund_code": nav.fund_code,
            "nav_date": nav.nav_date.isoformat(),
            "nav": float(nav.nav),
            "accumulated_nav": float(nav.accumulated_nav) if nav.accumulated_nav else None,
            "growth_rate": float(nav.growth_rate) if nav.growth_rate else None,
            "source": nav.source
        })
    
    # 市场概况（简化版本）
    total_funds = db.query(func.count(FundInfo.id)).scalar()
    active_funds = db.query(func.count(func.distinct(FundNav.fund_code))).filter(
        FundNav.nav_date >= start_date
    ).scalar()
    
    market_summary = {
        "total_funds_tracked": total_funds or 0,
        "active_funds_in_period": active_funds or 0,
        "data_period_days": days,
        "last_update": end_date.isoformat()
    }
    
    return MarketDataResponse(
        fund_navs=fund_navs,
        market_summary=market_summary
    )

@router.get("/health")
def health_check(api_key: str = Depends(verify_api_key)):
    """
    健康检查接口
    
    用于验证API服务状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
        "message": "AI分析师API服务正常运行"
    }

# 添加高级聚合分析接口

class PortfolioAnalysisResponse(BaseModel):
    """投资组合分析响应模型"""
    portfolio_summary: Dict[str, Any] = Field(..., description="组合概况")
    allocation_analysis: Dict[str, Any] = Field(..., description="配置分析")
    concentration_risk: Dict[str, Any] = Field(..., description="集中度风险")
    diversification_score: float = Field(..., description="分散化评分")
    rebalancing_suggestions: List[Dict[str, Any]] = Field(..., description="再平衡建议")

class DCAAnalysisResponse(BaseModel):
    """定投分析响应模型"""
    active_plans: List[Dict[str, Any]] = Field(..., description="活跃定投计划")
    execution_stats: Dict[str, Any] = Field(..., description="执行统计")
    performance_metrics: Dict[str, Any] = Field(..., description="定投绩效")
    cost_averaging_effect: Dict[str, Any] = Field(..., description="成本平均效应")

@router.get("/portfolio-analysis", response_model=PortfolioAnalysisResponse)
def get_portfolio_analysis(
    base_currency: str = Query("CNY", description="基准货币"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取投资组合分析
    
    提供全面的投资组合分析，包括：
    - 组合概况和配置分析
    - 集中度风险评估
    - 分散化评分
    - 再平衡建议
    """
    
    # 获取最新资产快照
    latest_snapshot_time = db.query(func.max(AssetSnapshot.snapshot_time)).scalar()
    if not latest_snapshot_time:
        raise HTTPException(status_code=404, detail="没有找到资产快照数据")
    
    latest_snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time == latest_snapshot_time
    ).all()
    
    balance_field = f"balance_{base_currency.lower()}"
    
    # 计算总资产价值
    total_portfolio_value = 0
    platform_values = {}
    asset_type_values = {}
    individual_assets = []
    
    for snapshot in latest_snapshots:
        balance = getattr(snapshot, balance_field, None) or snapshot.balance
        if balance and float(balance) >= 0.01:
            value = float(balance)
            total_portfolio_value += value
            
            # 平台分布
            if snapshot.platform not in platform_values:
                platform_values[snapshot.platform] = 0
            platform_values[snapshot.platform] += value
            
            # 资产类型分布
            if snapshot.asset_type not in asset_type_values:
                asset_type_values[snapshot.asset_type] = 0
            asset_type_values[snapshot.asset_type] += value
            
            # 个别资产记录
            individual_assets.append({
                "platform": snapshot.platform,
                "asset_type": snapshot.asset_type,
                "asset_code": snapshot.asset_code,
                "asset_name": snapshot.asset_name,
                "value": value,
                "weight": value / total_portfolio_value if total_portfolio_value > 0 else 0
            })
    
    # 组合概况
    portfolio_summary = {
        "total_value": total_portfolio_value,
        "currency": base_currency,
        "number_of_assets": len(individual_assets),
        "number_of_platforms": len(platform_values),
        "last_update": latest_snapshot_time.isoformat()
    }
    
    # 配置分析
    allocation_analysis = {
        "by_platform": [
            {"name": platform, "value": value, "weight": value / total_portfolio_value * 100}
            for platform, value in sorted(platform_values.items(), key=lambda x: x[1], reverse=True)
        ],
        "by_asset_type": [
            {"name": asset_type, "value": value, "weight": value / total_portfolio_value * 100}
            for asset_type, value in sorted(asset_type_values.items(), key=lambda x: x[1], reverse=True)
        ]
    }
    
    # 集中度风险分析
    # 计算赫芬达尔指数（HHI）
    individual_weights = [asset["weight"] for asset in individual_assets]
    hhi = sum([w**2 for w in individual_weights]) * 10000  # 标准化到0-10000
    
    # 最大持仓权重
    max_holding_weight = max(individual_weights) * 100 if individual_weights else 0
    
    # 前5大持仓权重
    top5_weight = sum(sorted(individual_weights, reverse=True)[:5]) * 100
    
    concentration_risk = {
        "hhi_index": hhi,
        "hhi_interpretation": "低" if hhi < 1500 else "中" if hhi < 2500 else "高",
        "max_holding_weight": max_holding_weight,
        "top5_weight": top5_weight,
        "risk_level": "低" if max_holding_weight < 20 else "中" if max_holding_weight < 40 else "高"
    }
    
    # 分散化评分（简化版本）
    platform_diversity = len(platform_values)
    asset_type_diversity = len(asset_type_values)
    concentration_penalty = max(0, (max_holding_weight - 10) / 10)  # 超过10%开始扣分
    
    diversification_score = min(100, 
        (platform_diversity * 10) + 
        (asset_type_diversity * 15) + 
        30 - (concentration_penalty * 5)
    )
    
    # 再平衡建议
    rebalancing_suggestions = []
    
    # 如果某个资产权重过高
    for asset in individual_assets:
        if asset["weight"] > 0.3:  # 超过30%
            rebalancing_suggestions.append({
                "type": "reduce_position",
                "asset": asset["asset_name"],
                "current_weight": asset["weight"] * 100,
                "suggested_weight": 25,
                "reason": "单一资产权重过高，建议降低至25%以下"
            })
    
    # 如果某个平台权重过高
    for platform_data in allocation_analysis["by_platform"]:
        if platform_data["weight"] > 60:
            rebalancing_suggestions.append({
                "type": "diversify_platform",
                "platform": platform_data["name"],
                "current_weight": platform_data["weight"],
                "reason": "单一平台权重过高，建议分散到其他平台"
            })
    
    return PortfolioAnalysisResponse(
        portfolio_summary=portfolio_summary,
        allocation_analysis=allocation_analysis,
        concentration_risk=concentration_risk,
        diversification_score=diversification_score,
        rebalancing_suggestions=rebalancing_suggestions
    )

@router.get("/dca-analysis", response_model=DCAAnalysisResponse)
def get_dca_analysis(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取定投计划分析
    
    提供定投计划的全面分析，包括：
    - 活跃定投计划概况
    - 执行统计和绩效
    - 成本平均效应分析
    """
    
    # 获取所有定投计划
    dca_plans = db.query(DCAPlan).all()
    
    # 活跃计划
    active_plans = []
    total_monthly_investment = 0
    
    for plan in dca_plans:
        if plan.status == "active":
            # 计算月投入金额
            if plan.frequency == "monthly":
                monthly_amount = float(plan.amount)
            elif plan.frequency == "weekly":
                monthly_amount = float(plan.amount) * 4.33  # 平均每月4.33周
            elif plan.frequency == "daily":
                monthly_amount = float(plan.amount) * 30
            else:
                monthly_amount = float(plan.amount)  # 默认按月计算
            
            total_monthly_investment += monthly_amount
            
            active_plans.append({
                "id": plan.id,
                "plan_name": plan.plan_name,
                "platform": plan.platform,
                "asset_code": plan.asset_code,
                "asset_name": plan.asset_name,
                "amount": float(plan.amount),
                "currency": plan.currency,
                "frequency": plan.frequency,
                "monthly_equivalent": monthly_amount,
                "start_date": plan.start_date.isoformat() if plan.start_date else None,
                "total_invested": float(plan.total_invested or 0),
                "execution_count": plan.execution_count or 0,
                "smart_dca": plan.smart_dca,
                "next_execution": plan.next_execution_date.isoformat() if plan.next_execution_date else None
            })
    
    # 执行统计
    total_plans = len(dca_plans)
    active_count = len([p for p in dca_plans if p.status == "active"])
    paused_count = len([p for p in dca_plans if p.status == "paused"])
    completed_count = len([p for p in dca_plans if p.status == "completed"])
    
    execution_stats = {
        "total_plans": total_plans,
        "active_plans": active_count,
        "paused_plans": paused_count,
        "completed_plans": completed_count,
        "total_monthly_investment": total_monthly_investment,
        "average_plan_value": total_monthly_investment / active_count if active_count > 0 else 0
    }
    
    # 获取定投相关的操作记录
    dca_operations = db.query(UserOperation).filter(
        UserOperation.dca_plan_id.isnot(None)
    ).all()
    
    # 绩效指标
    total_dca_invested = sum([float(op.amount) for op in dca_operations if op.operation_type == "buy"])
    total_dca_operations = len(dca_operations)
    
    # 按月统计定投金额
    monthly_investment_data = db.query(
        func.date_trunc('month', UserOperation.operation_date).label('month'),
        func.sum(UserOperation.amount).label('amount')
    ).filter(
        UserOperation.dca_plan_id.isnot(None),
        UserOperation.operation_type == 'buy'
    ).group_by('month').order_by('month').all()
    
    monthly_data = []
    for data in monthly_investment_data:
        monthly_data.append({
            "month": data.month.strftime('%Y-%m'),
            "amount": float(data.amount)
        })
    
    performance_metrics = {
        "total_invested": total_dca_invested,
        "total_operations": total_dca_operations,
        "average_operation_size": total_dca_invested / total_dca_operations if total_dca_operations > 0 else 0,
        "monthly_investment_trend": monthly_data[-12:] if len(monthly_data) >= 12 else monthly_data,  # 最近12个月
        "consistency_score": len(monthly_data) / 12 * 100 if len(monthly_data) <= 12 else 100  # 一致性评分
    }
    
    # 成本平均效应分析（简化版本）
    # 这里需要结合净值数据来计算真实的成本平均效应
    cost_averaging_effect = {
        "note": "成本平均效应分析需要结合净值历史数据",
        "total_shares_acquired": sum([float(plan.total_shares or 0) for plan in dca_plans]),
        "average_cost_basis": "需要净值数据计算",
        "dollar_cost_averaging_benefit": "需要市场波动数据分析"
    }
    
    return DCAAnalysisResponse(
        active_plans=active_plans,
        execution_stats=execution_stats,
        performance_metrics=performance_metrics,
        cost_averaging_effect=cost_averaging_effect
    )

@router.get("/risk-assessment")
def get_risk_assessment(
    base_currency: str = Query("CNY", description="基准货币"),
    days: int = Query(90, description="分析天数"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取风险评估
    
    提供投资组合的风险评估，包括：
    - 波动率分析
    - 最大回撤
    - 风险指标
    - 压力测试结果
    """
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 获取历史快照数据
    snapshots = db.query(AssetSnapshot).filter(
        AssetSnapshot.snapshot_time >= start_date,
        AssetSnapshot.snapshot_time <= end_date
    ).order_by(AssetSnapshot.snapshot_time).all()
    
    if len(snapshots) < 10:
        raise HTTPException(status_code=404, detail="历史数据不足，无法进行风险评估")
    
    balance_field = f"balance_{base_currency.lower()}"
    
    # 按日汇总资产价值
    daily_values = {}
    for snapshot in snapshots:
        date_key = snapshot.snapshot_time.date()
        balance = getattr(snapshot, balance_field, None) or snapshot.balance
        if balance:
            if date_key not in daily_values:
                daily_values[date_key] = 0
            daily_values[date_key] += float(balance)
    
    # 计算日收益率
    sorted_dates = sorted(daily_values.keys())
    daily_returns = []
    values = []
    
    for i in range(1, len(sorted_dates)):
        prev_value = daily_values[sorted_dates[i-1]]
        curr_value = daily_values[sorted_dates[i]]
        if prev_value > 0:
            daily_return = (curr_value - prev_value) / prev_value
            daily_returns.append(daily_return)
            values.append(curr_value)
    
    if not daily_returns:
        raise HTTPException(status_code=404, detail="无法计算收益率，数据不足")
    
    # 风险指标计算
    mean_return = sum(daily_returns) / len(daily_returns)
    variance = sum([(r - mean_return) ** 2 for r in daily_returns]) / len(daily_returns)
    volatility = variance ** 0.5
    annual_volatility = volatility * (252 ** 0.5)  # 年化波动率
    
    # 最大回撤计算
    peak = values[0]
    max_drawdown = 0
    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # VaR计算（简化版本）
    sorted_returns = sorted(daily_returns)
    var_95 = sorted_returns[int(len(sorted_returns) * 0.05)] if len(sorted_returns) > 20 else min(sorted_returns)
    var_99 = sorted_returns[int(len(sorted_returns) * 0.01)] if len(sorted_returns) > 100 else min(sorted_returns)
    
    # 夏普比率（假设无风险利率为2%）
    risk_free_rate = 0.02 / 252  # 日无风险利率
    excess_return = mean_return - risk_free_rate
    sharpe_ratio = excess_return / volatility if volatility > 0 else 0
    
    # 风险等级评估
    def get_risk_level(annual_vol):
        if annual_vol < 0.1:
            return "低风险"
        elif annual_vol < 0.2:
            return "中低风险"
        elif annual_vol < 0.3:
            return "中风险"
        elif annual_vol < 0.4:
            return "中高风险"
        else:
            return "高风险"
    
    return {
        "risk_metrics": {
            "daily_volatility": volatility,
            "annual_volatility": annual_volatility,
            "max_drawdown": max_drawdown,
            "var_95_daily": var_95,
            "var_99_daily": var_99,
            "sharpe_ratio": sharpe_ratio,
            "risk_level": get_risk_level(annual_volatility)
        },
        "analysis_period": {
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "days_analyzed": len(sorted_dates),
            "data_points": len(daily_returns)
        },
        "interpretation": {
            "volatility_interpretation": "低" if annual_volatility < 0.15 else "中" if annual_volatility < 0.25 else "高",
            "drawdown_interpretation": "轻微" if max_drawdown < 0.1 else "适中" if max_drawdown < 0.2 else "严重",
            "overall_risk_assessment": get_risk_level(annual_volatility)
        },
        "recommendations": [
            "定期检查投资组合配置" if annual_volatility > 0.2 else "当前风险水平适中",
            "考虑增加防御性资产" if max_drawdown > 0.15 else "风险控制良好",
            "建议分散投资" if len(daily_values) < 30 else "数据样本充足"
        ]
    }