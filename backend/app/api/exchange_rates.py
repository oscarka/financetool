from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.services.wise_api_service import WiseRateUpdater, WiseRateMonitor, update_wise_rates_sync
from app.services.asset_display_service import AssetDisplayService, get_asset_overview, get_asset_trend
from app.models.exchange_rate_models import (
    ExchangeRateTimeline, RateUpdateLog, AssetDisplayConfig, UserAssetPreference
)

router = APIRouter(prefix="/api/exchange-rates", tags=["汇率管理"])
logger = logging.getLogger(__name__)


@router.get("/status")
def get_rate_update_status(db: Session = Depends(get_db)):
    """获取汇率更新状态"""
    try:
        updater = WiseRateUpdater(db)
        status = updater.get_rate_update_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"获取汇率更新状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
def update_exchange_rates(db: Session = Depends(get_db)):
    """手动更新汇率"""
    try:
        result = update_wise_rates_sync()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"更新汇率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rates")
def get_exchange_rates(
    from_currency: Optional[str] = Query(None, description="源币种"),
    to_currency: Optional[str] = Query(None, description="目标币种"),
    limit: int = Query(100, description="返回记录数限制"),
    db: Session = Depends(get_db)
):
    """获取汇率历史"""
    try:
        query = db.query(ExchangeRateTimeline)
        
        if from_currency:
            query = query.filter(ExchangeRateTimeline.from_currency == from_currency)
        if to_currency:
            query = query.filter(ExchangeRateTimeline.to_currency == to_currency)
        
        rates = query.order_by(ExchangeRateTimeline.effective_time.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": rate.id,
                    "from_currency": rate.from_currency,
                    "to_currency": rate.to_currency,
                    "rate": float(rate.rate),
                    "effective_time": rate.effective_time.isoformat(),
                    "source": rate.source,
                    "created_at": rate.created_at.isoformat()
                }
                for rate in rates
            ]
        }
    except Exception as e:
        logger.error(f"获取汇率历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rates/latest")
def get_latest_rates(
    from_currency: Optional[str] = Query(None, description="源币种"),
    to_currency: Optional[str] = Query(None, description="目标币种"),
    db: Session = Depends(get_db)
):
    """获取最新汇率"""
    try:
        query = db.query(ExchangeRateTimeline)
        
        if from_currency:
            query = query.filter(ExchangeRateTimeline.from_currency == from_currency)
        if to_currency:
            query = query.filter(ExchangeRateTimeline.to_currency == to_currency)
        
        # 获取每个汇率对的最新记录
        latest_rates = []
        if from_currency and to_currency:
            # 指定了具体的汇率对
            rate = query.order_by(ExchangeRateTimeline.effective_time.desc()).first()
            if rate:
                latest_rates.append(rate)
        else:
            # 获取所有汇率对的最新记录
            from sqlalchemy import func
            subquery = db.query(
                ExchangeRateTimeline.from_currency,
                ExchangeRateTimeline.to_currency,
                func.max(ExchangeRateTimeline.effective_time).label('max_time')
            ).group_by(
                ExchangeRateTimeline.from_currency,
                ExchangeRateTimeline.to_currency
            ).subquery()
            
            rates = db.query(ExchangeRateTimeline).join(
                subquery,
                (ExchangeRateTimeline.from_currency == subquery.c.from_currency) &
                (ExchangeRateTimeline.to_currency == subquery.c.to_currency) &
                (ExchangeRateTimeline.effective_time == subquery.c.max_time)
            ).all()
            
            latest_rates = rates
        
        return {
            "success": True,
            "data": [
                {
                    "from_currency": rate.from_currency,
                    "to_currency": rate.to_currency,
                    "rate": float(rate.rate),
                    "effective_time": rate.effective_time.isoformat(),
                    "source": rate.source
                }
                for rate in latest_rates
            ]
        }
    except Exception as e:
        logger.error(f"获取最新汇率失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
def get_rate_update_logs(
    source_type: Optional[str] = Query(None, description="数据源类型"),
    status: Optional[str] = Query(None, description="状态"),
    limit: int = Query(100, description="返回记录数限制"),
    db: Session = Depends(get_db)
):
    """获取汇率更新日志"""
    try:
        query = db.query(RateUpdateLog)
        
        if source_type:
            query = query.filter(RateUpdateLog.source_type == source_type)
        if status:
            query = query.filter(RateUpdateLog.status == status)
        
        logs = query.order_by(RateUpdateLog.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": log.id,
                    "source_type": log.source_type,
                    "from_currency": log.from_currency,
                    "to_currency": log.to_currency,
                    "status": log.status,
                    "rate_value": float(log.rate_value) if log.rate_value else None,
                    "error_message": log.error_message,
                    "request_duration_ms": log.request_duration_ms,
                    "records_updated": log.records_updated,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    except Exception as e:
        logger.error(f"获取汇率更新日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def check_rate_health(db: Session = Depends(get_db)):
    """检查汇率系统健康状态"""
    try:
        monitor = WiseRateMonitor(db)
        is_healthy = monitor.check_rate_health()
        
        return {
            "success": True,
            "data": {
                "is_healthy": is_healthy,
                "check_time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"检查汇率健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 资产展示相关API
@router.get("/assets/overview")
def get_assets_overview(
    user_id: int = Query(1, description="用户ID"),
    currencies: str = Query("CNY,USD,JPY", description="币种列表，逗号分隔"),
    base_currency: Optional[str] = Query(None, description="基准货币"),
    time_point: Optional[str] = Query(None, description="时间点，ISO格式"),
    db: Session = Depends(get_db)
):
    """获取多币种资产概览"""
    try:
        # 解析参数
        currency_list = [c.strip() for c in currencies.split(",")]
        time_obj = None
        if time_point:
            time_obj = datetime.fromisoformat(time_point.replace('Z', '+00:00'))
        
        service = AssetDisplayService(db)
        result = service.get_multi_currency_overview(
            user_id, currency_list, base_currency, time_obj
        )
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"获取资产概览失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/trend")
def get_assets_trend(
    user_id: int = Query(1, description="用户ID"),
    currency: str = Query("CNY", description="币种"),
    days: int = Query(30, description="天数"),
    db: Session = Depends(get_db)
):
    """获取资产趋势"""
    try:
        service = AssetDisplayService(db)
        trend_data = service.get_asset_trend(user_id, currency, days)
        
        return {"success": True, "data": trend_data}
    except Exception as e:
        logger.error(f"获取资产趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/preferences")
def get_user_preferences(
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户资产偏好"""
    try:
        service = AssetDisplayService(db)
        preferences = service.get_user_preferences(user_id)
        
        return {"success": True, "data": preferences}
    except Exception as e:
        logger.error(f"获取用户偏好失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assets/preferences")
def save_user_preference(
    user_id: int,
    asset_type: str,
    preferred_currency: str,
    db: Session = Depends(get_db)
):
    """保存用户资产偏好"""
    try:
        service = AssetDisplayService(db)
        service.save_user_preference(user_id, asset_type, preferred_currency)
        
        return {"success": True, "message": "偏好设置已保存"}
    except Exception as e:
        logger.error(f"保存用户偏好失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/display-configs")
def get_display_configs(
    user_id: Optional[int] = Query(None, description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取展示配置"""
    try:
        service = AssetDisplayService(db)
        configs = service.get_display_configs(user_id)
        
        return {"success": True, "data": configs}
    except Exception as e:
        logger.error(f"获取展示配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assets/display-configs")
def save_display_config(
    config_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """保存展示配置"""
    try:
        service = AssetDisplayService(db)
        result = service.save_display_config(config_data)
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"保存展示配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 便捷API
@router.get("/assets/summary")
def get_assets_summary(
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取资产汇总（简化版）"""
    try:
        # 获取CNY和USD基准的资产概览
        service = AssetDisplayService(db)
        
        # CNY基准
        cny_overview = service.get_multi_currency_overview(
            user_id, ['CNY'], 'CNY'
        )
        
        # USD基准
        usd_overview = service.get_multi_currency_overview(
            user_id, ['USD'], 'USD'
        )
        
        return {
            "success": True,
            "data": {
                "cny_total": float(cny_overview['currency_totals'].get('CNY', 0)),
                "usd_total": float(usd_overview['currency_totals'].get('USD', 0)),
                "update_time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"获取资产汇总失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))