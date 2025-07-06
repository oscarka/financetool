from .base import BaseConfig
import os

class ProdConfig(BaseConfig):
    app_env: str = "prod"
    debug: bool = False
    database_url: str = "sqlite:///./data/personalfinance.db"
    cors_origins: str = '["https://yourdomain.com"]'
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    fund_api_timeout: int = 15
    fund_api_retry_times: int = 5
    
    # OKX API配置
    okx_api_key: str = os.getenv("OKX_API_KEY", "")
    okx_secret_key: str = os.getenv("OKX_SECRET_KEY", "")
    okx_passphrase: str = os.getenv("OKX_PASSPHRASE", "")
    okx_sandbox: bool = os.getenv("OKX_SANDBOX", "false").lower() == "true" 