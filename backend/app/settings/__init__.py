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
    
    # 设置环境变量文件路径
    if app_env == "prod":
        env_file = ".env.prod"
        print("[CONFIG] 使用生产环境配置")
        config_class = ProdConfig
    else:
        env_file = ".env.test"
        print("[CONFIG] 使用测试环境配置")
        config_class = TestConfig
    
    # 检查环境变量文件是否存在
    if os.path.exists(env_file):
        print(f"[CONFIG] 加载环境变量文件: {env_file}")
        # 手动读取环境变量文件并设置到环境变量中
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"[CONFIG] 设置环境变量: {key} = {value[:10] if len(value) > 10 else value}...")
    else:
        print(f"[CONFIG] 环境变量文件不存在: {env_file}")
    
    return config_class()

# 创建全局配置实例
settings = get_settings()

# 导出配置实例
__all__ = ["settings", "get_settings", "BaseConfig", "TestConfig", "ProdConfig"] 