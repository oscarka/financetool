from .base import BaseConfig

class TestConfig(BaseConfig):
    app_env: str = "test"
    debug: bool = True
    database_url: str = "sqlite:///./data/personalfinance.db"
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'
    log_level: str = "DEBUG"
    log_file: str = "./logs/app_test.log"
    fund_api_timeout: int = 5
    fund_api_retry_times: int = 2 