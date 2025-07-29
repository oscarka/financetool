from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.database import get_db
from app.services.asset_aggregation_service import (
    calculate_aggregated_stats,
    get_asset_trend_data,
    get_asset_distribution_data,
    get_platform_distribution_data
)
import logging

router = APIRouter(prefix="/aggregation", tags=["数据聚合"])

@router.get("/stats")
def get_aggregated_stats(
    base_currency: str = Query('CNY', description="基准货币"),
    db: Session = Depends(get_db)
):
    """获取聚合统计数据"""
    try:
        stats = calculate_aggregated_stats(db, base_currency)
        return {
            "success": True,
            "message": "获取聚合统计数据成功",
            "data": stats
        }
    except Exception as e:
        logging.error(f"获取聚合统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@router.get("/trend")
def get_asset_trend(
    days: int = Query(30, description="天数"),
    base_currency: str = Query('CNY', description="基准货币"),
    db: Session = Depends(get_db)
):
    """获取资产趋势数据"""
    try:
        trend_data = get_asset_trend_data(db, days, base_currency)
        return {
            "success": True,
            "message": f"获取到 {len(trend_data)} 条趋势数据",
            "data": trend_data
        }
    except Exception as e:
        logging.error(f"获取资产趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@router.get("/distribution/asset-type")
def get_asset_type_distribution(
    base_currency: str = Query('CNY', description="基准货币"),
    db: Session = Depends(get_db)
):
    """获取资产类型分布数据"""
    try:
        distribution_data = get_asset_distribution_data(db, base_currency)
        return {
            "success": True,
            "message": f"获取到 {len(distribution_data)} 种资产类型分布",
            "data": distribution_data
        }
    except Exception as e:
        logging.error(f"获取资产类型分布数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分布数据失败: {str(e)}")

@router.get("/distribution/platform")
def get_platform_distribution(
    base_currency: str = Query('CNY', description="基准货币"),
    db: Session = Depends(get_db)
):
    """获取平台分布数据"""
    try:
        distribution_data = get_platform_distribution_data(db, base_currency)
        return {
            "success": True,
            "message": f"获取到 {len(distribution_data)} 个平台分布",
            "data": distribution_data
        }
    except Exception as e:
        logging.error(f"获取平台分布数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分布数据失败: {str(e)}")

@router.get("/dashboard")
def get_dashboard_data(
    base_currency: str = Query('CNY', description="基准货币"),
    days: int = Query(30, description="趋势天数"),
    db: Session = Depends(get_db)
):
    """获取仪表板完整数据"""
    try:
        # 获取所有聚合数据
        stats = calculate_aggregated_stats(db, base_currency)
        trend_data = get_asset_trend_data(db, days, base_currency)
        asset_type_distribution = get_asset_distribution_data(db, base_currency)
        platform_distribution = get_platform_distribution_data(db, base_currency)
        
        dashboard_data = {
            "stats": stats,
            "trend": trend_data,
            "asset_type_distribution": asset_type_distribution,
            "platform_distribution": platform_distribution,
            "base_currency": base_currency,
            "trend_days": days
        }
        
        return {
            "success": True,
            "message": "获取仪表板数据成功",
            "data": dashboard_data
        }
    except Exception as e:
        logging.error(f"获取仪表板数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")