from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class BaseConfig(BaseSettings):
    """基础配置类"""
    
    # 应用基础配置
    app_env: str = "test"
    app_name: str = "个人财务管理系统"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    # 数据库配置
    database_url: str = "sqlite:///./data/personalfinance.db"
    
    # 跨域配置
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'
    
    # 日志配置
    log_level: str = "WARNING"  # 从INFO调整为WARNING
    log_file: str = "./logs/app.log"
    
    # 基金API配置
    fund_api_timeout: int = 10
    fund_api_retry_times: int = 3
    
    # 天天基金网API配置
    tiantian_fund_api_base_url: str = "https://fundgz.1234567.com.cn"
    tiantian_fund_info_base_url: str = "https://fund.eastmoney.com/pingzhongdata"
    
    # 雪球API配置
    xueqiu_api_base_url: str = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
    
    # OKX API配置
    okx_api_base_url: str = "https://www.okx.com"
    okx_api_key: str = ""
    okx_secret_key: str = ""
    okx_passphrase: str = ""
    okx_sandbox: bool = True  # 是否使用沙盒环境
    
    # Wise API配置
    wise_api_token: str = ""
    wise_api_base_url: str = "https://api.transferwise.com"
    
    # PayPal API配置
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_api_base_url: str = "https://api-m.sandbox.paypal.com"  # 沙盒环境
    
    # IBKR API配置
    ibkr_api_key: str = ""
    ibkr_allowed_ips: str = "34.60.247.187"  # Google Cloud VM IP
    ibkr_sync_timeout: int = 30
    ibkr_max_request_size: int = 1024 * 1024  # 1MB
    ibkr_rate_limit_per_minute: int = 60
    ibkr_enable_ip_whitelist: bool = True
    ibkr_enable_request_logging: bool = True
    
    # 定时任务配置
    scheduler_timezone: str = "Asia/Shanghai"
    enable_scheduler: bool = True
    
    # 系统配置
    upload_db_token: Optional[str] = None
    
    # 可扩展调度器配置
    scheduler_job_defaults: dict = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 300
    }
    
    # 事件总线配置
    event_bus_max_listeners: int = 100
    event_bus_enable_persistence: bool = False
    
    # 插件管理器配置
    plugin_auto_discovery: bool = True
    plugin_discovery_path: str = "app/plugins"
    
    # 任务引擎配置
    task_engine_max_workers: int = 10
    task_engine_default_timeout: int = 300
    
    # 存储层配置
    storage_enable_cache: bool = True
    storage_cache_ttl: int = 3600  # 1小时
    
    # 健康检查配置
    health_check_enabled: bool = True
    health_check_interval: int = 60  # 60秒
    
    # 性能监控配置
    performance_monitoring_enabled: bool = False
    performance_sampling_rate: float = 0.1  # 10%
    
    # 安全配置
    security_enable_rate_limiting: bool = True
    security_rate_limit_per_minute: int = 100
    security_enable_request_logging: bool = True
    
    # 数据同步配置
    sync_batch_size: int = 100
    sync_max_retries: int = 3
    sync_retry_delay: int = 5  # 秒
    
    # 缓存配置
    cache_enabled: bool = True
    cache_default_ttl: int = 300  # 5分钟
    cache_max_size: int = 1000
    
    # 通知配置
    notification_enabled: bool = False
    notification_channels: List[str] = ["email", "webhook"]
    
    # 备份配置
    backup_enabled: bool = True
    backup_retention_days: int = 30
    backup_schedule: str = "0 2 * * *"  # 每天凌晨2点
    
    # 报表配置
    report_generation_enabled: bool = True
    report_default_format: str = "json"
    report_include_charts: bool = True
    
    # 数据清理配置
    data_cleanup_enabled: bool = True
    data_cleanup_retention_days: int = 90
    data_cleanup_schedule: str = "0 3 * * 0"  # 每周日凌晨3点

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def get_cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        import json
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000", "http://localhost:5173"]
    
    def get_allowed_ips_list(self) -> List[str]:
        """获取允许的IP列表"""
        return [ip.strip() for ip in self.ibkr_allowed_ips.split(',') if ip.strip()]
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.app_env.lower() == "prod"
    
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.app_env.lower() in ["test", "dev", "development"]
    
    def get_database_url(self) -> str:
        """获取数据库URL，支持环境变量覆盖"""
        return self.database_url
    
    def validate_config(self) -> bool:
        """验证配置完整性"""
        required_fields = [
            "database_url",
            "cors_origins"
        ]
        
        for field in required_fields:
            if not getattr(self, field, None):
                print(f"❌ 配置验证失败: {field} 不能为空")
                return False
        
        print("✅ 配置验证通过")
        return True 