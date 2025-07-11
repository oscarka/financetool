from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import json

from app.models.database import (
    AssetPosition, UserOperation, FundNav, ExchangeRate,
    WiseBalance, IBKRBalance, IBKRPosition, WiseTransaction
)
from app.models.schemas import OverviewResponse, PortfolioSummary, AssetAllocation
from app.database import get_db

router = APIRouter(prefix="/overview", tags=["总览"])


@router.get("/summary", response_model=OverviewResponse)
async def get_overview_summary(db: Session = Depends(get_db)):
    """获取投资组合总览"""
    try:
        # 获取当前日期
        today = date.today()
        month_ago = today - timedelta(days=30)
        
        # 1. 基金持仓统计
        fund_positions = db.query(AssetPosition).filter(
            AssetPosition.asset_type == "基金"
        ).all()
        
        fund_total_value = sum(float(pos.current_value) for pos in fund_positions)
        fund_total_invested = sum(float(pos.total_invested) for pos in fund_positions)
        fund_total_profit = sum(float(pos.total_profit) for pos in fund_positions)
        
        # 2. IBKR持仓统计
        latest_ibkr_balance = db.query(IBKRBalance).order_by(
            IBKRBalance.snapshot_date.desc()
        ).first()
        
        ibkr_positions = db.query(IBKRPosition).filter(
            IBKRPosition.snapshot_date == latest_ibkr_balance.snapshot_date if latest_ibkr_balance else None
        ).all() if latest_ibkr_balance else []
        
        ibkr_total_value = float(latest_ibkr_balance.net_liquidation) if latest_ibkr_balance else 0
        ibkr_total_invested = sum(float(pos.average_cost * pos.quantity) for pos in ibkr_positions)
        ibkr_total_profit = ibkr_total_value - ibkr_total_invested
        
        # 3. Wise余额统计
        wise_balances = db.query(WiseBalance).filter(
            WiseBalance.visible == True
        ).all()
        
        wise_total_value = sum(float(balance.total_worth) for balance in wise_balances)
        
        # 4. 计算总资产
        total_assets = fund_total_value + ibkr_total_value + wise_total_value
        total_invested = fund_total_invested + ibkr_total_invested
        total_profit = fund_total_profit + ibkr_total_profit
        
        # 5. 计算收益率
        total_profit_rate = (total_profit / total_invested * 100) if total_invested > 0 else 0
        
        # 6. 本月收益计算
        month_operations = db.query(UserOperation).filter(
            and_(
                UserOperation.operation_date >= month_ago,
                UserOperation.operation_date <= today
            )
        ).all()
        
        month_profit = sum(
            float(op.amount) if op.operation_type in ["卖出", "赎回"] else -float(op.amount)
            for op in month_operations
        )
        
        # 7. 持仓数量统计
        total_positions = len(fund_positions) + len(ibkr_positions)
        
        # 8. 资产配置
        asset_allocation = [
            {
                "platform": "基金",
                "value": fund_total_value,
                "percentage": (fund_total_value / total_assets * 100) if total_assets > 0 else 0
            },
            {
                "platform": "IBKR",
                "value": ibkr_total_value,
                "percentage": (ibkr_total_value / total_assets * 100) if total_assets > 0 else 0
            },
            {
                "platform": "Wise",
                "value": wise_total_value,
                "percentage": (wise_total_value / total_assets * 100) if total_assets > 0 else 0
            }
        ]
        
        return OverviewResponse(
            total_assets=total_assets,
            total_invested=total_invested,
            total_profit=total_profit,
            total_profit_rate=total_profit_rate,
            month_profit=month_profit,
            total_positions=total_positions,
            asset_allocation=asset_allocation,
            last_updated=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取总览数据失败: {str(e)}")


@router.get("/portfolio", response_model=List[PortfolioSummary])
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """获取各平台投资组合详情"""
    try:
        portfolios = []
        
        # 1. 基金组合
        fund_positions = db.query(AssetPosition).filter(
            AssetPosition.asset_type == "基金"
        ).all()
        
        if fund_positions:
            fund_total_value = sum(float(pos.current_value) for pos in fund_positions)
            fund_total_profit = sum(float(pos.total_profit) for pos in fund_positions)
            fund_total_invested = sum(float(pos.total_invested) for pos in fund_positions)
            
            portfolios.append(PortfolioSummary(
                platform="基金",
                total_value=fund_total_value,
                total_profit=fund_total_profit,
                total_invested=fund_total_invested,
                profit_rate=(fund_total_profit / fund_total_invested * 100) if fund_total_invested > 0 else 0,
                position_count=len(fund_positions),
                top_positions=[
                    {
                        "asset_code": pos.asset_code,
                        "asset_name": pos.asset_name,
                        "value": float(pos.current_value),
                        "profit_rate": float(pos.profit_rate)
                    }
                    for pos in sorted(fund_positions, key=lambda x: float(x.current_value), reverse=True)[:5]
                ]
            ))
        
        # 2. IBKR组合
        latest_ibkr_balance = db.query(IBKRBalance).order_by(
            IBKRBalance.snapshot_date.desc()
        ).first()
        
        if latest_ibkr_balance:
            ibkr_positions = db.query(IBKRPosition).filter(
                IBKRPosition.snapshot_date == latest_ibkr_balance.snapshot_date
            ).all()
            
            ibkr_total_value = float(latest_ibkr_balance.net_liquidation)
            ibkr_total_invested = sum(float(pos.average_cost * pos.quantity) for pos in ibkr_positions)
            ibkr_total_profit = ibkr_total_value - ibkr_total_invested
            
            portfolios.append(PortfolioSummary(
                platform="IBKR",
                total_value=ibkr_total_value,
                total_profit=ibkr_total_profit,
                total_invested=ibkr_total_invested,
                profit_rate=(ibkr_total_profit / ibkr_total_invested * 100) if ibkr_total_invested > 0 else 0,
                position_count=len(ibkr_positions),
                top_positions=[
                    {
                        "asset_code": pos.symbol,
                        "asset_name": pos.symbol,
                        "value": float(pos.market_value),
                        "profit_rate": (float(pos.unrealized_pnl) / (float(pos.average_cost * pos.quantity)) * 100) if pos.average_cost * pos.quantity > 0 else 0
                    }
                    for pos in sorted(ibkr_positions, key=lambda x: float(x.market_value), reverse=True)[:5]
                ]
            ))
        
        # 3. Wise组合
        wise_balances = db.query(WiseBalance).filter(
            WiseBalance.visible == True
        ).all()
        
        if wise_balances:
            wise_total_value = sum(float(balance.total_worth) for balance in wise_balances)
            
            portfolios.append(PortfolioSummary(
                platform="Wise",
                total_value=wise_total_value,
                total_profit=0,  # Wise主要是现金，不计算投资收益
                total_invested=wise_total_value,
                profit_rate=0,
                position_count=len(wise_balances),
                top_positions=[
                    {
                        "asset_code": balance.currency,
                        "asset_name": f"{balance.currency} 余额",
                        "value": float(balance.total_worth),
                        "profit_rate": 0
                    }
                    for balance in sorted(wise_balances, key=lambda x: float(x.total_worth), reverse=True)[:5]
                ]
            ))
        
        return portfolios
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取投资组合详情失败: {str(e)}")


@router.get("/asset-allocation", response_model=List[AssetAllocation])
async def get_asset_allocation(db: Session = Depends(get_db)):
    """获取资产配置详情"""
    try:
        allocations = []
        
        # 1. 按平台分类
        platform_allocation = {}
        
        # 基金
        fund_positions = db.query(AssetPosition).filter(
            AssetPosition.asset_type == "基金"
        ).all()
        fund_total = sum(float(pos.current_value) for pos in fund_positions)
        if fund_total > 0:
            platform_allocation["基金"] = fund_total
        
        # IBKR
        latest_ibkr_balance = db.query(IBKRBalance).order_by(
            IBKRBalance.snapshot_date.desc()
        ).first()
        if latest_ibkr_balance:
            platform_allocation["IBKR"] = float(latest_ibkr_balance.net_liquidation)
        
        # Wise
        wise_balances = db.query(WiseBalance).filter(
            WiseBalance.visible == True
        ).all()
        wise_total = sum(float(balance.total_worth) for balance in wise_balances)
        if wise_total > 0:
            platform_allocation["Wise"] = wise_total
        
        total_assets = sum(platform_allocation.values())
        
        for platform, value in platform_allocation.items():
            allocations.append(AssetAllocation(
                category=platform,
                value=value,
                percentage=(value / total_assets * 100) if total_assets > 0 else 0,
                count=len(fund_positions) if platform == "基金" else 
                      (len(db.query(IBKRPosition).filter(IBKRPosition.snapshot_date == latest_ibkr_balance.snapshot_date).all()) if platform == "IBKR" and latest_ibkr_balance else 0) if platform == "IBKR" else
                      len(wise_balances) if platform == "Wise" else 0
            ))
        
        return allocations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资产配置失败: {str(e)}")


@router.get("/recent-activities")
async def get_recent_activities(db: Session = Depends(get_db), limit: int = 10):
    """获取最近活动"""
    try:
        # 获取最近的用户操作
        recent_operations = db.query(UserOperation).order_by(
            UserOperation.operation_date.desc()
        ).limit(limit).all()
        
        activities = []
        for op in recent_operations:
            activities.append({
                "id": op.id,
                "date": op.operation_date,
                "platform": op.platform,
                "type": op.operation_type,
                "asset_code": op.asset_code,
                "asset_name": op.asset_name,
                "amount": float(op.amount),
                "currency": op.currency,
                "quantity": float(op.quantity) if op.quantity else None,
                "price": float(op.price) if op.price else None
            })
        
        return activities
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近活动失败: {str(e)}")


@router.get("/performance-trend")
async def get_performance_trend(db: Session = Depends(get_db), days: int = 30):
    """获取收益趋势"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 这里可以添加更复杂的收益趋势计算逻辑
        # 暂时返回简单的日期范围
        return {
            "start_date": start_date,
            "end_date": end_date,
            "days": days,
            "message": "收益趋势计算功能待完善"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收益趋势失败: {str(e)}")