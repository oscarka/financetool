from .base import BaseConfig
import os

class TestConfig(BaseConfig):
    app_env: str = "test"
    debug: bool = True
    database_url: str = "sqlite:///./data/personalfinance.db"
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'
    log_level: str = "DEBUG"
    log_file: str = "./logs/app_test.log"
    fund_api_timeout: int = 5
    fund_api_retry_times: int = 2
    
    # OKX API配置
    okx_api_key: str = os.getenv("OKX_API_KEY", "")
    okx_secret_key: str = os.getenv("OKX_SECRET_KEY", "")
    okx_passphrase: str = os.getenv("OKX_PASSPHRASE", "")
    okx_sandbox: bool = os.getenv("OKX_SANDBOX", "true").lower() == "true"
    
    # Wise API配置
    wise_api_token: str = os.getenv("WISE_API_TOKEN", "") 