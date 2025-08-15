from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict
from datetime import datetime
from pydantic import BaseModel
from app.utils.database import get_db
from app.utils.logger import log_system
import json

router = APIRouter(prefix="/user", tags=["用户偏好设置"])

# Pydantic 模型
class UserPreferences(BaseModel):
    base_currency: str = "USD"
    data_visibility: bool = True
    theme_mode: str = "light"  # light, dark
    number_precision: int = 2
    percentage_precision: int = 2

class NotificationSettings(BaseModel):
    asset_change_alerts: bool = True
    sync_failure_alerts: bool = True
    daily_reports: bool = False
    weekly_summaries: bool = True
    monthly_insights: bool = False
    alert_threshold: float = 5.0  # 资产变化提醒阈值(百分比)
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"

class SyncSettings(BaseModel):
    auto_sync_enabled: bool = True
    sync_frequency: int = 30  # 分钟
    retry_on_failure: bool = True
    max_retry_attempts: int = 3
    wifi_only: bool = False
    power_saving_mode: bool = False

@router.get("/preferences")
def get_user_preferences(db: Session = Depends(get_db)):
    """获取用户显示偏好设置"""
    try:
        # 从数据库获取用户设置
        settings = get_user_settings_from_db(db, "preferences")
        
        if settings:
            return {
                "success": True,
                "data": settings
            }
        else:
            # 返回默认设置
            default_prefs = UserPreferences()
            return {
                "success": True,
                "data": default_prefs.dict()
            }
            
    except Exception as e:
        log_system(f"获取用户偏好失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户偏好失败: {str(e)}")

@router.put("/preferences")
def update_user_preferences(
    preferences: UserPreferences,
    db: Session = Depends(get_db)
):
    """更新用户显示偏好设置"""
    try:
        # 保存用户设置到数据库
        save_user_settings_to_db(db, "preferences", preferences.dict())
        
        log_system(f"用户偏好已更新: {preferences.dict()}")
        
        return {
            "success": True,
            "message": "偏好设置已保存",
            "data": preferences.dict()
        }
        
    except Exception as e:
        log_system(f"更新用户偏好失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新用户偏好失败: {str(e)}")

@router.get("/notifications")
def get_notification_settings(db: Session = Depends(get_db)):
    """获取通知设置"""
    try:
        settings = get_user_settings_from_db(db, "notifications")
        
        if settings:
            return {
                "success": True,
                "data": settings
            }
        else:
            # 返回默认设置
            default_notifications = NotificationSettings()
            return {
                "success": True,
                "data": default_notifications.dict()
            }
            
    except Exception as e:
        log_system(f"获取通知设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取通知设置失败: {str(e)}")

@router.put("/notifications")
def update_notification_settings(
    notifications: NotificationSettings,
    db: Session = Depends(get_db)
):
    """更新通知设置"""
    try:
        save_user_settings_to_db(db, "notifications", notifications.dict())
        
        log_system(f"通知设置已更新: {notifications.dict()}")
        
        return {
            "success": True,
            "message": "通知设置已保存",
            "data": notifications.dict()
        }
        
    except Exception as e:
        log_system(f"更新通知设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新通知设置失败: {str(e)}")

@router.get("/sync-settings")
def get_sync_settings(db: Session = Depends(get_db)):
    """获取同步设置"""
    try:
        settings = get_user_settings_from_db(db, "sync_settings")
        
        if settings:
            return {
                "success": True,
                "data": settings
            }
        else:
            # 返回默认设置
            default_sync = SyncSettings()
            return {
                "success": True,
                "data": default_sync.dict()
            }
            
    except Exception as e:
        log_system(f"获取同步设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取同步设置失败: {str(e)}")

@router.put("/sync-settings")
def update_sync_settings(
    sync_settings: SyncSettings,
    db: Session = Depends(get_db)
):
    """更新同步设置"""
    try:
        save_user_settings_to_db(db, "sync_settings", sync_settings.dict())
        
        log_system(f"同步设置已更新: {sync_settings.dict()}")
        
        return {
            "success": True,
            "message": "同步设置已保存",
            "data": sync_settings.dict()
        }
        
    except Exception as e:
        log_system(f"更新同步设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新同步设置失败: {str(e)}")

@router.get("/profile")
def get_user_profile(db: Session = Depends(get_db)):
    """获取用户档案信息"""
    try:
        # 计算用户统计信息
        stats = calculate_user_stats(db)
        
        # 获取用户成就
        achievements = get_user_achievements(db, stats)
        
        return {
            "success": True,
            "data": {
                "user_name": "投资分析师",  # 可以后续改为可配置
                "avatar": None,
                "registration_date": stats.get("first_data_date"),
                "usage_days": stats.get("usage_days", 0),
                "total_records": stats.get("total_records", 0),
                "achievements": achievements,
                "annual_return_rate": stats.get("annual_return_rate", 0.0),
                "stats": stats
            }
        }
        
    except Exception as e:
        log_system(f"获取用户档案失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户档案失败: {str(e)}")

# 数据导出和备份功能已移除 - 这些功能需要完整实现后再添加

@router.get("/data-summary")
def get_data_summary(db: Session = Depends(get_db)):
    """获取数据摘要"""
    try:
        summary = generate_data_summary(db)
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        log_system(f"获取数据摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据摘要失败: {str(e)}")

# 清除缓存功能已移除 - 需要实现真实的缓存清除逻辑后再添加

@router.get("/system-info")
def get_system_info():
    """获取系统信息"""
    try:
        return {
            "success": True,
            "data": {
                "app_version": "1.0.0",
                "api_version": "v1.2",
                "last_update": "2025-01-27",
                "environment": "production",
                "server_time": datetime.now().isoformat(),
                "features": [
                    "多平台资产聚合",
                    "实时汇率转换",
                    "智能数据分析",
                    "AI投资建议",
                    "自动化同步"
                ],
                "supported_platforms": ["支付宝", "Wise", "IBKR", "OKX"],
                "supported_currencies": ["CNY", "USD", "EUR", "JPY", "AUD"]
            }
        }
        
    except Exception as e:
        log_system(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")

# 辅助函数
def get_user_settings_from_db(db: Session, setting_type: str) -> Optional[Dict]:
    """从数据库获取用户设置"""
    try:
        # 简化实现：使用配置表存储用户设置
        query = text("""
            SELECT config_value 
            FROM system_config 
            WHERE config_key = :key
        """)
        result = db.execute(query, {"key": f"user_settings_{setting_type}"}).scalar()
        
        if result:
            return json.loads(result)
        return None
    except:
        return None

def save_user_settings_to_db(db: Session, setting_type: str, settings: Dict):
    """保存用户设置到数据库"""
    try:
        # 简化实现：使用配置表存储用户设置
        query = text("""
            INSERT INTO system_config (config_key, config_value, updated_at) 
            VALUES (:key, :value, NOW())
            ON CONFLICT (config_key) 
            DO UPDATE SET config_value = :value, updated_at = NOW()
        """)
        db.execute(query, {
            "key": f"user_settings_{setting_type}",
            "value": json.dumps(settings)
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def calculate_user_stats(db: Session) -> Dict:
    """计算用户统计信息"""
    try:
        stats_query = text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT DATE(created_at)) as usage_days,
                MIN(created_at) as first_data_date,
                MAX(created_at) as last_data_date,
                SUM(base_value) as total_asset_value,
                COUNT(DISTINCT platform) as platforms_connected
            FROM asset_snapshots
        """)
        result = db.execute(stats_query).fetchone()
        
        if result:
            first_date = result[2]
            usage_days = result[1] if result[1] else 0
            
            # 计算年化收益率 (模拟)
            annual_return_rate = 8.5  # 简化实现
            
            return {
                "total_records": result[0] or 0,
                "usage_days": usage_days,
                "first_data_date": first_date,
                "last_data_date": result[3],
                "total_asset_value": float(result[4]) if result[4] else 0.0,
                "platforms_connected": result[5] or 0,
                "annual_return_rate": annual_return_rate
            }
        else:
            return {"total_records": 0, "usage_days": 0, "annual_return_rate": 0.0}
    except:
        return {"total_records": 0, "usage_days": 0, "annual_return_rate": 0.0}

def get_user_achievements(db: Session, stats: Dict) -> List[Dict]:
    """获取用户成就"""
    achievements = []
    
    # 基于统计数据计算成就
    if stats.get("usage_days", 0) >= 30:
        achievements.append({
            "id": "usage_30_days",
            "title": "连续使用30天",
            "description": "坚持记录资产超过30天",
            "icon": "🏆",
            "earned": True
        })
    
    if stats.get("total_asset_value", 0) >= 100000:
        achievements.append({
            "id": "asset_100k",
            "title": "资产超过10万",
            "description": "总资产价值超过10万",
            "icon": "💰",
            "earned": True
        })
    
    if stats.get("platforms_connected", 0) >= 3:
        achievements.append({
            "id": "platform_master",
            "title": "平台连接达人",
            "description": "连接了3个或以上平台",
            "icon": "🔗",
            "earned": True
        })
    
    if stats.get("annual_return_rate", 0) > 8:
        achievements.append({
            "id": "good_investor",
            "title": "投资高手",
            "description": "年化收益率超过8%",
            "icon": "📈",
            "earned": True
        })
    
    return achievements

# 已移除的虚假函数：get_export_data, generate_export_url, create_data_backup
# 这些函数在真实实现数据导出和备份功能时需要重新添加

def generate_data_summary(db: Session) -> Dict:
    """生成数据摘要"""
    try:
        # 获取今日摘要数据
        today_query = text("""
            SELECT 
                COUNT(*) as today_snapshots,
                SUM(base_value) as today_total_value,
                COUNT(DISTINCT platform) as active_platforms
            FROM asset_snapshots 
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        result = db.execute(today_query).fetchone()
        
        if result:
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_value": f"${result[1]:,.2f}" if result[1] else "$0.00",
                "snapshot_count": result[0] or 0,
                "active_platforms": result[2] or 0,
                "status": "数据正常更新",
                "summary_text": f"今日记录了{result[0] or 0}笔资产快照，总价值{result[1]:,.2f}美元，涉及{result[2] or 0}个平台。"
            }
        else:
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "status": "暂无今日数据",
                "summary_text": "今日还没有记录任何资产数据。"
            }
    except:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "数据获取失败"
        }