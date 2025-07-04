from pydantic_settings import BaseSettings
from typing import Optional
import os
from app.settings.test import TestConfig
from app.settings.prod import ProdConfig


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "个人财务管理系统"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./data/personalfinance.db"
    
    # API配置
    api_v1_prefix: str = "/api/v1"
    
    # 跨域配置
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # 基金API配置
    fund_api_timeout: int = 10
    fund_api_retry_times: int = 3
    
    # 定时任务配置
    scheduler_timezone: str = "Asia/Shanghai"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


env = os.getenv("APP_ENV", "test")

if env == "prod":
    settings = ProdConfig(_env_file=".env.prod")
else:
    settings = TestConfig(_env_file=".env.test") 