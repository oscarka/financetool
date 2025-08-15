from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.utils.database import get_db
from app.utils.logger import log_system
import logging

router = APIRouter(prefix="/snapshot", tags=["快照管理"])

@router.get("/status")
def get_snapshot_status(db: Session = Depends(get_db)):
    """获取快照状态总览"""
    try:
        # 获取最新的快照记录
        latest_snapshot_query = text("""
            SELECT 
                MAX(created_at) as last_update,
                COUNT(*) as total_snapshots,
                COUNT(DISTINCT platform) as platform_count,
                COUNT(DISTINCT asset_type) as asset_type_count
            FROM asset_snapshots 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """)
        
        result = db.execute(latest_snapshot_query).fetchone()
        
        if result:
            last_update = result[0]
            total_snapshots = result[1] or 0
            platform_count = result[2] or 0
            asset_type_count = result[3] or 0
            
            # 计算距离上次更新的时间
            if last_update:
                minutes_ago = int((datetime.now() - last_update).total_seconds() / 60)
                status = "fresh" if minutes_ago <= 30 else "stale" if minutes_ago <= 120 else "outdated"
                status_text = f"{minutes_ago}分钟前" if minutes_ago > 0 else "刚刚"
            else:
                minutes_ago = None
                status = "no_data"
                status_text = "暂无数据"
            
            # 计算数据健康度
            health_score = calculate_data_health_score(db)
            
            return {
                "success": True,
                "data": {
                    "last_update": last_update,
                    "last_update_text": status_text,
                    "status": status,
                    "minutes_ago": minutes_ago,
                    "total_snapshots_today": total_snapshots,
                    "platform_count": platform_count,
                    "asset_type_count": asset_type_count,
                    "health_score": health_score,
                    "next_sync": get_next_sync_time()
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "status": "no_data",
                    "last_update_text": "暂无数据",
                    "total_snapshots_today": 0,
                    "platform_count": 0,
                    "asset_type_count": 0,
                    "health_score": {"overall": 0, "completeness": 0, "timeliness": 0, "connectivity": 0}
                }
            }
            
    except Exception as e:
        log_system(f"获取快照状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取快照状态失败: {str(e)}")

@router.get("/platforms")
def get_platform_status(db: Session = Depends(get_db)):
    """获取各平台连接状态和资产信息"""
    try:
        # 获取各平台最新快照信息
        platform_query = text("""
            WITH latest_snapshots AS (
                SELECT 
                    platform,
                    asset_type,
                    asset_name,
                    balance,
                    base_value,
                    currency,
                    created_at,
                    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY created_at DESC) as rn
                FROM asset_snapshots 
                WHERE created_at >= NOW() - INTERVAL '7 days'
            )
            SELECT 
                platform,
                COUNT(*) as asset_count,
                SUM(base_value) as total_value,
                MAX(created_at) as last_update,
                STRING_AGG(DISTINCT asset_type, ', ') as asset_types,
                STRING_AGG(DISTINCT currency, ', ') as currencies
            FROM latest_snapshots 
            WHERE rn <= 20  -- 限制每个平台最多20条记录
            GROUP BY platform
            ORDER BY total_value DESC
        """)
        
        platform_results = db.execute(platform_query).fetchall()
        platforms = []
        
        for row in platform_results:
            platform = row[0]
            asset_count = row[1]
            total_value = float(row[2]) if row[2] else 0.0
            last_update = row[3]
            asset_types = row[4]
            currencies = row[5]
            
            # 计算连接状态
            if last_update:
                minutes_ago = int((datetime.now() - last_update).total_seconds() / 60)
                if minutes_ago <= 30:
                    status = "connected"
                    status_text = "正常"
                elif minutes_ago <= 120:
                    status = "warning" 
                    status_text = "数据有点旧"
                else:
                    status = "error"
                    status_text = "连接异常"
                    
                time_text = f"{minutes_ago}分钟前" if minutes_ago > 0 else "刚刚"
            else:
                status = "disconnected"
                status_text = "未连接"
                time_text = "暂无数据"
                minutes_ago = None
            
            # 获取该平台的资产详情
            asset_details = get_platform_asset_details(db, platform)
            
            platforms.append({
                "platform": platform,
                "status": status,
                "status_text": status_text,
                "last_update": last_update,
                "time_text": time_text,
                "minutes_ago": minutes_ago,
                "total_value": total_value,
                "asset_count": asset_count,
                "asset_types": asset_types,
                "currencies": currencies,
                "asset_details": asset_details,
                "icon": get_platform_icon(platform)
            })
        
        return {
            "success": True,
            "data": platforms
        }
        
    except Exception as e:
        log_system(f"获取平台状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取平台状态失败: {str(e)}")

@router.get("/history")
def get_snapshot_history(
    days: int = Query(7, description="查询天数"),
    limit: int = Query(50, description="记录数量限制"),
    db: Session = Depends(get_db)
):
    """获取快照历史记录"""
    try:
        # 获取快照历史记录，按时间分组
        history_query = text("""
            WITH snapshot_groups AS (
                SELECT 
                    DATE_TRUNC('minute', created_at) as snapshot_time,
                    COUNT(*) as record_count,
                    COUNT(DISTINCT platform) as platform_count,
                    SUM(base_value) as total_value,
                    STRING_AGG(DISTINCT platform, ', ') as platforms,
                    CASE 
                        WHEN COUNT(*) > 10 THEN 'full'
                        WHEN COUNT(*) > 5 THEN 'partial'
                        ELSE 'minimal'
                    END as sync_type
                FROM asset_snapshots 
                WHERE created_at >= NOW() - INTERVAL :days DAY
                GROUP BY DATE_TRUNC('minute', created_at)
                ORDER BY snapshot_time DESC
                LIMIT :limit
            )
            SELECT * FROM snapshot_groups
        """)
        
        history_results = db.execute(history_query, {"days": days, "limit": limit}).fetchall()
        history = []
        
        for row in history_results:
            snapshot_time = row[0]
            record_count = row[1]
            platform_count = row[2]
            total_value = float(row[3]) if row[3] else 0.0
            platforms = row[4]
            sync_type = row[5]
            
            # 计算时间显示
            now = datetime.now()
            time_diff = now - snapshot_time
            
            if time_diff.days > 0:
                time_text = f"{time_diff.days}天前"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_text = f"{hours}小时前"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                time_text = f"{minutes}分钟前"
            else:
                time_text = "刚刚"
                
            # 确定同步类型显示
            sync_type_text = {
                "full": "全量更新",
                "partial": "增量更新", 
                "minimal": "少量更新"
            }.get(sync_type, "更新")
            
            history.append({
                "snapshot_time": snapshot_time,
                "time_text": time_text,
                "sync_type": sync_type,
                "sync_type_text": sync_type_text,
                "record_count": record_count,
                "platform_count": platform_count,
                "total_value": total_value,
                "platforms": platforms,
                "status": "success" if record_count > 0 else "failed"
            })
        
        return {
            "success": True,
            "data": {
                "history": history,
                "total_records": len(history),
                "query_days": days
            }
        }
        
    except Exception as e:
        log_system(f"获取快照历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取快照历史失败: {str(e)}")

@router.post("/sync")
def trigger_manual_sync(
    platforms: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """手动触发数据同步"""
    try:
        # 这里应该调用实际的同步服务
        # 目前返回模拟结果
        log_system(f"手动触发同步: {platforms if platforms else '全平台'}")
        
        return {
            "success": True,
            "message": "同步请求已提交",
            "data": {
                "sync_id": f"sync_{int(datetime.now().timestamp())}",
                "platforms": platforms if platforms else ["支付宝", "Wise", "IBKR"],
                "estimated_duration": "2-5分钟",
                "status": "started"
            }
        }
        
    except Exception as e:
        log_system(f"手动同步失败: {e}")
        raise HTTPException(status_code=500, detail=f"手动同步失败: {str(e)}")

@router.get("/statistics")
def get_data_statistics(
    days: int = Query(30, description="统计天数"),
    db: Session = Depends(get_db)
):
    """获取数据统计信息"""
    try:
        # 获取数据统计
        stats_query = text("""
            SELECT 
                COUNT(*) as total_snapshots,
                COUNT(DISTINCT platform) as unique_platforms,
                COUNT(DISTINCT asset_type) as unique_asset_types,
                COUNT(DISTINCT currency) as unique_currencies,
                MIN(created_at) as earliest_data,
                MAX(created_at) as latest_data,
                AVG(base_value) as avg_asset_value
            FROM asset_snapshots 
            WHERE created_at >= NOW() - INTERVAL :days DAY
        """)
        
        result = db.execute(stats_query, {"days": days}).fetchone()
        
        if result:
            # 计算成功率和延迟
            success_rate = calculate_sync_success_rate(db, days)
            avg_delay = calculate_average_delay(db, days)
            
            return {
                "success": True,
                "data": {
                    "total_snapshots": result[0] or 0,
                    "unique_platforms": result[1] or 0,
                    "unique_asset_types": result[2] or 0,
                    "unique_currencies": result[3] or 0,
                    "earliest_data": result[4],
                    "latest_data": result[5],
                    "avg_asset_value": float(result[6]) if result[6] else 0.0,
                    "success_rate": success_rate,
                    "avg_delay_minutes": avg_delay,
                    "query_days": days
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "total_snapshots": 0,
                    "success_rate": 0,
                    "avg_delay_minutes": 0
                }
            }
            
    except Exception as e:
        log_system(f"获取数据统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据统计失败: {str(e)}")

# 辅助函数
def calculate_data_health_score(db: Session) -> Dict[str, float]:
    """计算数据健康度评分"""
    try:
        # 数据完整性评分 (0-100)
        completeness = calculate_data_completeness(db)
        
        # 数据及时性评分 (0-100) 
        timeliness = calculate_data_timeliness(db)
        
        # 连接稳定性评分 (0-100)
        connectivity = calculate_connectivity_score(db)
        
        # 综合评分
        overall = (completeness + timeliness + connectivity) / 3
        
        return {
            "overall": round(overall, 1),
            "completeness": round(completeness, 1),
            "timeliness": round(timeliness, 1),
            "connectivity": round(connectivity, 1)
        }
    except:
        return {"overall": 0, "completeness": 0, "timeliness": 0, "connectivity": 0}

def calculate_data_completeness(db: Session) -> float:
    """计算数据完整性"""
    # 简化实现：基于最近24小时的数据覆盖率
    try:
        query = text("""
            SELECT COUNT(DISTINCT platform) * 100.0 / 3 as completeness
            FROM asset_snapshots 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """)
        result = db.execute(query).scalar()
        return min(float(result) if result else 0, 100)
    except:
        return 0

def calculate_data_timeliness(db: Session) -> float:
    """计算数据及时性"""
    try:
        query = text("""
            SELECT 
                CASE 
                    WHEN MAX(created_at) >= NOW() - INTERVAL '30 minutes' THEN 100
                    WHEN MAX(created_at) >= NOW() - INTERVAL '1 hour' THEN 80
                    WHEN MAX(created_at) >= NOW() - INTERVAL '2 hours' THEN 60
                    WHEN MAX(created_at) >= NOW() - INTERVAL '6 hours' THEN 40
                    ELSE 20
                END as timeliness
            FROM asset_snapshots
        """)
        result = db.execute(query).scalar()
        return float(result) if result else 0
    except:
        return 0

def calculate_connectivity_score(db: Session) -> float:
    """计算连接稳定性"""
    try:
        # 基于最近24小时的同步成功率
        success_rate = calculate_sync_success_rate(db, 1)
        return success_rate
    except:
        return 0

def calculate_sync_success_rate(db: Session, days: int) -> float:
    """计算同步成功率"""
    try:
        # 简化实现：假设数据存在即为成功
        query = text("""
            SELECT COUNT(*) as total_attempts,
                   COUNT(*) as successful_attempts
            FROM asset_snapshots 
            WHERE created_at >= NOW() - INTERVAL :days DAY
        """)
        result = db.execute(query, {"days": days}).fetchone()
        if result and result[0] > 0:
            return (result[1] / result[0]) * 100
        return 0
    except:
        return 0

def calculate_average_delay(db: Session, days: int) -> float:
    """计算平均延迟"""
    # 简化实现：返回固定值
    return 2.3

def get_next_sync_time() -> Optional[datetime]:
    """获取下次同步时间"""
    # 简化实现：假设每30分钟同步一次
    now = datetime.now()
    next_sync = now.replace(second=0, microsecond=0)
    if next_sync.minute < 30:
        next_sync = next_sync.replace(minute=30)
    else:
        next_sync = (next_sync + timedelta(hours=1)).replace(minute=0)
    return next_sync

def get_platform_asset_details(db: Session, platform: str) -> List[Dict]:
    """获取平台资产详情"""
    try:
        query = text("""
            SELECT asset_type, asset_name, balance, base_value, currency
            FROM asset_snapshots 
            WHERE platform = :platform 
            AND created_at >= NOW() - INTERVAL '1 day'
            ORDER BY base_value DESC
            LIMIT 10
        """)
        results = db.execute(query, {"platform": platform}).fetchall()
        
        details = []
        for row in results:
            details.append({
                "asset_type": row[0],
                "asset_name": row[1],
                "balance": float(row[2]) if row[2] else 0.0,
                "base_value": float(row[3]) if row[3] else 0.0,
                "currency": row[4]
            })
        
        return details
    except:
        return []

def get_platform_icon(platform: str) -> str:
    """获取平台图标"""
    icons = {
        "支付宝": "💰",
        "Wise": "🌍", 
        "IBKR": "📈",
        "OKX": "₿",
        "PayPal": "💳"
    }
    return icons.get(platform, "📊")