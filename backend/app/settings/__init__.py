"""
统一配置管理入口
"""
import os
from typing import Union
from .base import BaseConfig
from .test import TestConfig
from .prod import ProdConfig

# 调试日志
print(f"[CONFIG] 环境变量 APP_ENV = {os.environ.get('APP_ENV', 'test')}")

def get_settings() -> Union[TestConfig, ProdConfig]:
    """
    根据环境变量获取配置实例
    """
    app_env = os.environ.get("APP_ENV", "test").lower()
    
    if app_env == "prod":
        print("[CONFIG] 使用生产环境配置")
        return ProdConfig()
    else:
        print("[CONFIG] 使用测试环境配置")
        return TestConfig()

# 创建全局配置实例
settings = get_settings()

# 导出配置实例
__all__ = ["settings", "get_settings", "BaseConfig", "TestConfig", "ProdConfig"] 