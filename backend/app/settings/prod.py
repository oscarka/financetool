from .base import BaseConfig

class ProdConfig(BaseConfig):
    app_env: str = "prod"
    debug: bool = False
    database_url: str = "sqlite:///./data/personalfinance.db"
    cors_origins: str = '["https://yourdomain.com"]'
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    fund_api_timeout: int = 15
    fund_api_retry_times: int = 5 