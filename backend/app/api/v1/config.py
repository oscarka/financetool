from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import json
import os
from datetime import datetime
from loguru import logger

from app.settings import settings
from app.utils.database import SessionLocal
from app.models.database import SystemConfig

router = APIRouter()

@router.get("/")
async def get_config():
    """获取系统配置信息"""
    try:
        from loguru import logger
        # 精简日志，去掉详细的DEBUG输出
        # logger.info(f"[DEBUG] settings.app_env = {settings.app_env}")
        # logger.info(f"[DEBUG] settings.app_name = {settings.app_name}")
        # logger.info(f"[DEBUG] settings.database_url = {settings.database_url}")
        # logger.info(f"[DEBUG] settings.cors_origins = {settings.cors_origins}")
        # logger.info(f"[DEBUG] settings.log_level = {settings.log_level}")
        # logger.info(f"[DEBUG] settings.fund_api_timeout = {settings.fund_api_timeout}")
        # logger.info(f"[DEBUG] settings.okx_api_key = {getattr(settings, 'okx_api_key', None)}")
        # logger.info(f"[DEBUG] settings.wise_api_token = {getattr(settings, 'wise_api_token', None)}")
        # logger.info(f"[DEBUG] settings.paypal_client_id = {getattr(settings, 'paypal_client_id', None)}")
        # logger.info(f"[DEBUG] settings.ibkr_api_key = {getattr(settings, 'ibkr_api_key', None)}")
        # logger.info(f"[DEBUG] settings.enable_scheduler = {settings.enable_scheduler}")
        # logger.info(f"[DEBUG] settings.security_enable_rate_limiting = {settings.security_enable_rate_limiting}")
        # logger.info(f"[DEBUG] settings.performance_monitoring_enabled = {settings.performance_monitoring_enabled}")
        # logger.info(f"[DEBUG] settings.cache_enabled = {settings.cache_enabled}")
        # logger.info(f"[DEBUG] settings.sync_batch_size = {settings.sync_batch_size}")
        # logger.info(f"[DEBUG] settings.notification_enabled = {settings.notification_enabled}")
        # logger.info(f"[DEBUG] settings.backup_enabled = {settings.backup_enabled}")
        # logger.info(f"[DEBUG] settings.data_cleanup_enabled = {settings.data_cleanup_enabled}")
        # 精简日志，去掉详细的DEBUG输出
        config_info = {
            "app_env": settings.app_env,
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "debug": settings.debug,
            "database_url": settings.database_url,
            "cors_origins": settings.get_cors_origins_list(),
            "log_level": settings.log_level,
            "log_file": settings.log_file,
            
            # API配置
            "fund_api_timeout": settings.fund_api_timeout,
            "fund_api_retry_times": settings.fund_api_retry_times,
            
            # 第三方API配置状态
            "okx_api_configured": bool(settings.okx_api_key),
            "wise_api_configured": bool(settings.wise_api_token),
            "paypal_api_configured": bool(settings.paypal_client_id),
            "ibkr_api_configured": bool(settings.ibkr_api_key),
            "web3_api_configured": bool(settings.web3_api_key),
            
            # 调度器配置
            "enable_scheduler": settings.enable_scheduler,
            "scheduler_timezone": settings.scheduler_timezone,
            
            # 安全配置
            "security_enable_rate_limiting": settings.security_enable_rate_limiting,
            "security_rate_limit_per_minute": settings.security_rate_limit_per_minute,
            
            # 性能配置
            "performance_monitoring_enabled": settings.performance_monitoring_enabled,
            "performance_sampling_rate": settings.performance_sampling_rate,
            "cache_enabled": settings.cache_enabled,
            "cache_default_ttl": settings.cache_default_ttl,
            
            # 数据同步配置
            "sync_batch_size": settings.sync_batch_size,
            "sync_max_retries": settings.sync_max_retries,
            "sync_retry_delay": settings.sync_retry_delay,
            
            # 系统配置
            "notification_enabled": settings.notification_enabled,
            "backup_enabled": settings.backup_enabled,
            "data_cleanup_enabled": settings.data_cleanup_enabled,
            "data_cleanup_retention_days": settings.data_cleanup_retention_days,
        }
        
        return {
            "success": True,
            "data": config_info
        }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.post("/validate")
async def validate_config():
    """验证配置完整性"""
    try:
        errors = []
        warnings = []
        
        # 验证必需配置
        if not settings.database_url:
            errors.append("数据库URL未配置")
        
        if not settings.cors_origins:
            errors.append("CORS配置未设置")
        
        # 验证API配置
        if not settings.okx_api_key:
            warnings.append("OKX API密钥未配置")
        
        if not settings.wise_api_token:
            warnings.append("Wise API Token未配置")
        
        if not settings.paypal_client_id:
            warnings.append("PayPal Client ID未配置")
        
        if not settings.ibkr_api_key:
            warnings.append("IBKR API密钥未配置")
        
        if not settings.web3_api_key:
            warnings.append("Web3 API密钥未配置")
        
        # 验证数据库连接
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
        except Exception as e:
            errors.append(f"数据库连接失败: {str(e)}")
        
        # 验证文件权限
        log_dir = os.path.dirname(settings.log_file)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"日志目录创建失败: {str(e)}")
        
        valid = len(errors) == 0
        
        return {
            "success": True,
            "data": {
                "valid": valid,
                "errors": errors,
                "warnings": warnings
            }
        }
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置验证失败: {str(e)}")

@router.get("/environment")
async def get_environment_info():
    """获取环境信息"""
    try:
        import platform
        import psutil
        
        # 获取系统信息
        system_info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "memory_usage": f"{psutil.virtual_memory().percent}%",
            "disk_usage": f"{psutil.disk_usage('/').percent}%"
        }
        
        # 获取环境变量（过滤敏感信息）
        env_variables = {}
        sensitive_keys = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']
        
        for key, value in os.environ.items():
            if not any(sensitive in key.upper() for sensitive in sensitive_keys):
                env_variables[key] = value
        
        return {
            "success": True,
            "data": {
                "current_env": settings.app_env,
                "available_envs": ["test", "prod"],
                "env_variables": env_variables,
                "system_info": system_info
            }
        }
    except Exception as e:
        logger.error(f"获取环境信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取环境信息失败: {str(e)}")

@router.put("/")
async def update_config(config_data: Dict[str, Any]):
    """更新配置"""
    try:
        # 这里应该实现配置更新逻辑
        # 由于配置是通过环境变量和文件加载的，实际更新需要重启应用
        # 这里只是记录配置变更
        
        db = SessionLocal()
        try:
            # 记录配置变更
            config_record = SystemConfig(
                config_key=f"config_update_{datetime.now().isoformat()}",
                config_value=json.dumps(config_data),
                description="配置更新记录"
            )
            db.add(config_record)
            db.commit()
            
            logger.info(f"配置更新记录已保存: {config_data}")
            
            return {
                "success": True,
                "data": {
                    "message": "配置更新已记录，需要重启应用生效",
                    "updated_at": datetime.now().isoformat()
                }
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

@router.post("/reload")
async def reload_config():
    """重新加载配置"""
    try:
        # 这里应该实现配置重新加载逻辑
        # 由于配置是通过环境变量和文件加载的，实际重载需要重启应用
        
        logger.info("配置重新加载请求已接收")
        
        return {
            "success": True,
            "message": "配置重新加载请求已接收，部分配置可能需要重启应用生效"
        }
    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新加载配置失败: {str(e)}")

@router.get("/export")
async def export_config():
    """导出配置"""
    try:
        config_data = {
            "app_env": settings.app_env,
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "debug": settings.debug,
            "database_url": settings.database_url,
            "cors_origins": settings.get_cors_origins_list(),
            "log_level": settings.log_level,
            "log_file": settings.log_file,
            "fund_api_timeout": settings.fund_api_timeout,
            "fund_api_retry_times": settings.fund_api_retry_times,
            "enable_scheduler": settings.enable_scheduler,
            "scheduler_timezone": settings.scheduler_timezone,
            "security_enable_rate_limiting": settings.security_enable_rate_limiting,
            "security_rate_limit_per_minute": settings.security_rate_limit_per_minute,
            "performance_monitoring_enabled": settings.performance_monitoring_enabled,
            "performance_sampling_rate": settings.performance_sampling_rate,
            "cache_enabled": settings.cache_enabled,
            "cache_default_ttl": settings.cache_default_ttl,
            "sync_batch_size": settings.sync_batch_size,
            "sync_max_retries": settings.sync_max_retries,
            "sync_retry_delay": settings.sync_retry_delay,
            "notification_enabled": settings.notification_enabled,
            "backup_enabled": settings.backup_enabled,
            "data_cleanup_enabled": settings.data_cleanup_enabled,
            "data_cleanup_retention_days": settings.data_cleanup_retention_days,
            "exported_at": datetime.now().isoformat()
        }
        
        return json.dumps(config_data, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"导出配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出配置失败: {str(e)}")

@router.post("/import")
async def import_config(config_data: Dict[str, Any]):
    """导入配置"""
    try:
        # 验证配置数据
        required_fields = ["app_env", "app_name", "database_url"]
        for field in required_fields:
            if field not in config_data:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 记录导入的配置
        db = SessionLocal()
        try:
            config_record = SystemConfig(
                config_key=f"config_import_{datetime.now().isoformat()}",
                config_value=json.dumps(config_data),
                description="配置导入记录"
            )
            db.add(config_record)
            db.commit()
            
            logger.info(f"配置导入记录已保存")
            
            return {
                "success": True,
                "data": {
                    "message": "配置导入已记录，需要重启应用生效",
                    "imported_at": datetime.now().isoformat()
                }
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"导入配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入配置失败: {str(e)}")

@router.get("/history")
async def get_config_history():
    """获取配置历史"""
    try:
        db = SessionLocal()
        try:
            # 获取最近的配置变更记录
            config_records = db.query(SystemConfig).filter(
                SystemConfig.config_key.like("config_%")
            ).order_by(SystemConfig.updated_at.desc()).limit(20).all()
            
            history = []
            for record in config_records:
                try:
                    config_data = json.loads(record.config_value)
                    history.append({
                        "timestamp": record.updated_at.isoformat(),
                        "action": record.config_key.split("_")[1],
                        "description": record.description,
                        "data": config_data
                    })
                except:
                    history.append({
                        "timestamp": record.updated_at.isoformat(),
                        "action": record.config_key.split("_")[1],
                        "description": record.description,
                        "data": "配置数据解析失败"
                    })
            
            return {
                "success": True,
                "data": history
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"获取配置历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置历史失败: {str(e)}")

@router.post("/reset")
async def reset_config():
    """重置配置到默认值"""
    try:
        # 记录重置操作
        db = SessionLocal()
        try:
            config_record = SystemConfig(
                config_key=f"config_reset_{datetime.now().isoformat()}",
                config_value="配置重置到默认值",
                description="配置重置操作"
            )
            db.add(config_record)
            db.commit()
            
            logger.info("配置重置操作已记录")
            
            return {
                "success": True,
                "data": {
                    "message": "配置重置已记录，需要重启应用生效",
                    "reset_at": datetime.now().isoformat()
                }
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"重置配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重置配置失败: {str(e)}") 