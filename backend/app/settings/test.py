from .base import BaseConfig
import os

class TestConfig(BaseConfig):
    """测试环境配置"""
    
    app_env: str = "test"
    debug: bool = True
    database_url: str = "sqlite:///./data/personalfinance.db"
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'
    log_level: str = "DEBUG"
    log_file: str = "./logs/app_test.log"
    
    # 基金API配置 - 测试环境使用更短的超时时间
    fund_api_timeout: int = 5
    fund_api_retry_times: int = 2
    
    # OKX API配置
    okx_api_key: str = os.getenv("OKX_API_KEY", "")
    okx_secret_key: str = os.getenv("OKX_SECRET_KEY", "")
    okx_passphrase: str = os.getenv("OKX_PASSPHRASE", "")
    okx_sandbox: bool = os.getenv("OKX_SANDBOX", "true").lower() == "true"
    
    # Wise API配置
    wise_api_token: str = os.getenv("WISE_API_TOKEN", "")
    
    # PayPal API配置
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_api_base_url: str = "https://api-m.sandbox.paypal.com"  # 沙盒环境
    
    # IBKR API配置
    ibkr_api_key: str = os.getenv("IBKR_API_KEY", "")
    ibkr_allowed_ips: str = os.getenv("IBKR_ALLOWED_IPS", "127.0.0.1,::1")
    ibkr_enable_ip_whitelist: bool = os.getenv("IBKR_ENABLE_IP_WHITELIST", "false").lower() == "true"
    ibkr_enable_request_logging: bool = True
    
    # 定时任务配置 - 测试环境禁用定时任务
    enable_scheduler: bool = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
    
    # 性能监控配置 - 测试环境启用详细监控
    performance_monitoring_enabled: bool = True
    performance_sampling_rate: float = 1.0  # 100%
    
    # 安全配置 - 测试环境放宽限制
    security_enable_rate_limiting: bool = False
    security_rate_limit_per_minute: int = 1000
    
    # 数据同步配置 - 测试环境使用小批量
    sync_batch_size: int = 10
    sync_max_retries: int = 1
    sync_retry_delay: int = 1
    
    # 缓存配置 - 测试环境禁用缓存
    cache_enabled: bool = False
    
    # 通知配置 - 测试环境禁用通知
    notification_enabled: bool = False
    
    # 备份配置 - 测试环境禁用备份
    backup_enabled: bool = False
    
    # 数据清理配置 - 测试环境保留更短时间
    data_cleanup_retention_days: int = 7 