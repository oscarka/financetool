from .base import BaseConfig
import os
from pathlib import Path

class ProdConfig(BaseConfig):
    """生产环境配置"""
    
    app_env: str = "prod"
    debug: bool = False
    
    # 数据库持久化配置
    database_persistent_path: str = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
    database_backup_enabled: bool = os.getenv("DATABASE_BACKUP_ENABLED", "true").lower() == "true"
    database_backup_interval_hours: int = int(os.getenv("DATABASE_BACKUP_INTERVAL_HOURS", "24"))
    
    # 确保数据目录存在并设置数据库URL
    def __init__(self, **kwargs):
        # 确保数据目录存在
        data_path = os.getenv("DATABASE_PERSISTENT_PATH", "/app/data")
        Path(data_path).mkdir(parents=True, exist_ok=True)
        
        # 设置数据库URL
        env_db_url = os.getenv("DATABASE_URL")
        print(f"[CONFIG] DATABASE_URL环境变量: {env_db_url}")
        
        if env_db_url:
            kwargs["database_url"] = env_db_url
            print(f"[CONFIG] 使用PostgreSQL数据库: {env_db_url[:50]}...")
        else:
            # 使用持久化路径构建SQLite URL
            db_path = os.path.join(data_path, "personalfinance.db")
            kwargs["database_url"] = f"sqlite:///{db_path}"
            print(f"[CONFIG] 使用SQLite数据库: {db_path}")
        
        super().__init__(**kwargs)
    
    cors_origins: str = os.getenv("CORS_ORIGINS", '["*"]')
    log_level: str = "WARNING"  # 从INFO调整为WARNING
    log_file: str = "./logs/app.log"
    
    # 基金API配置 - 生产环境使用更长的超时时间
    fund_api_timeout: int = 15
    fund_api_retry_times: int = 5
    
    # OKX API配置
    okx_api_key: str = os.getenv("OKX_API_KEY", "")
    okx_secret_key: str = os.getenv("OKX_SECRET_KEY", "")
    okx_passphrase: str = os.getenv("OKX_PASSPHRASE", "")
    okx_sandbox: bool = os.getenv("OKX_SANDBOX", "false").lower() == "true"
    
    # Wise API配置
    wise_api_token: str = os.getenv("WISE_API_TOKEN", "")
    
    # PayPal API配置
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_api_base_url: str = "https://api-m.paypal.com"  # 生产环境 
    
    # IBKR API配置
    ibkr_api_key: str = os.getenv("IBKR_API_KEY", "")
    ibkr_allowed_ips: str = os.getenv("IBKR_ALLOWED_IPS", "34.60.247.187")
    ibkr_enable_ip_whitelist: bool = os.getenv("IBKR_ENABLE_IP_WHITELIST", "true").lower() == "true"
    ibkr_enable_request_logging: bool = os.getenv("IBKR_ENABLE_REQUEST_LOGGING", "true").lower() == "true"
    
    # 定时任务配置 - 生产环境启用定时任务
    enable_scheduler: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    
    # 性能监控配置 - 生产环境使用采样监控
    performance_monitoring_enabled: bool = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
    performance_sampling_rate: float = float(os.getenv("PERFORMANCE_SAMPLING_RATE", "0.1"))
    
    # 安全配置 - 生产环境启用严格限制
    security_enable_rate_limiting: bool = True
    security_rate_limit_per_minute: int = int(os.getenv("SECURITY_RATE_LIMIT_PER_MINUTE", "100"))
    
    # 数据同步配置 - 生产环境使用大批量
    sync_batch_size: int = int(os.getenv("SYNC_BATCH_SIZE", "100"))
    sync_max_retries: int = int(os.getenv("SYNC_MAX_RETRIES", "3"))
    sync_retry_delay: int = int(os.getenv("SYNC_RETRY_DELAY", "5"))
    
    # 缓存配置 - 生产环境启用缓存
    cache_enabled: bool = True
    cache_default_ttl: int = int(os.getenv("CACHE_DEFAULT_TTL", "300"))
    cache_max_size: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # 通知配置 - 生产环境启用通知
    notification_enabled: bool = os.getenv("NOTIFICATION_ENABLED", "false").lower() == "true"
    
    # 备份配置 - 生产环境启用备份
    backup_enabled: bool = True
    backup_retention_days: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    
    # 数据清理配置 - 生产环境保留更长时间
    data_cleanup_retention_days: int = int(os.getenv("DATA_CLEANUP_RETENTION_DAYS", "90"))
    
    # 系统配置
    upload_db_token: str = os.getenv("UPLOAD_DB_TOKEN", "") 