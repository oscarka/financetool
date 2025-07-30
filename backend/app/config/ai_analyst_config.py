"""
AI分析师API配置文件

包含API密钥管理、限流配置、数据访问权限等设置
"""

from pydantic import BaseSettings, Field
from typing import List, Dict, Optional
from datetime import timedelta
import os

class AIAnalystConfig(BaseSettings):
    """AI分析师API配置"""
    
    # API密钥配置
    api_keys: List[str] = Field(
        default=["ai_analyst_key_2024", "demo_key_12345"],
        description="有效的API密钥列表"
    )
    
    # 限流配置
    rate_limit_requests: int = Field(default=60, description="每分钟请求数限制")
    rate_limit_window: int = Field(default=60, description="限流窗口时间（秒）")
    
    # 数据访问配置
    max_history_days: int = Field(default=365, description="历史数据查询最大天数")
    max_records_per_request: int = Field(default=1000, description="单次请求最大记录数")
    
    # 缓存配置
    cache_ttl_asset_summary: int = Field(default=3600, description="资产总览缓存时间（秒）")
    cache_ttl_exchange_rates: int = Field(default=900, description="汇率数据缓存时间（秒）")
    cache_ttl_market_data: int = Field(default=1800, description="市场数据缓存时间（秒）")
    
    # 数据权限配置
    allow_sensitive_data: bool = Field(default=False, description="是否允许访问敏感数据")
    allowed_currencies: List[str] = Field(
        default=["CNY", "USD", "EUR", "HKD", "GBP"],
        description="支持的货币列表"
    )
    
    # 安全配置
    enable_ip_whitelist: bool = Field(default=False, description="是否启用IP白名单")
    ip_whitelist: List[str] = Field(default=[], description="IP白名单")
    
    # 日志配置
    enable_audit_log: bool = Field(default=True, description="是否启用审计日志")
    audit_log_level: str = Field(default="INFO", description="审计日志级别")
    
    class Config:
        env_prefix = "AI_ANALYST_"
        case_sensitive = False

# 全局配置实例
ai_analyst_config = AIAnalystConfig()

# API密钥验证
def is_valid_api_key(api_key: str) -> bool:
    """验证API密钥是否有效"""
    return api_key in ai_analyst_config.api_keys

# 权限检查
def check_currency_permission(currency: str) -> bool:
    """检查货币访问权限"""
    return currency.upper() in ai_analyst_config.allowed_currencies

def check_date_range_permission(days: int) -> bool:
    """检查日期范围访问权限"""
    return days <= ai_analyst_config.max_history_days

def check_record_limit(limit: int) -> bool:
    """检查记录数限制"""
    return limit <= ai_analyst_config.max_records_per_request

# 限流配置
RATE_LIMIT_CONFIG = {
    "requests": ai_analyst_config.rate_limit_requests,
    "window": ai_analyst_config.rate_limit_window,
    "storage": "memory"  # 可选: redis, memory
}

# 缓存配置
CACHE_CONFIG = {
    "asset_summary": ai_analyst_config.cache_ttl_asset_summary,
    "exchange_rates": ai_analyst_config.cache_ttl_exchange_rates,
    "market_data": ai_analyst_config.cache_ttl_market_data,
    "default": 1800  # 30分钟默认缓存
}

# 审计日志配置
AUDIT_CONFIG = {
    "enabled": ai_analyst_config.enable_audit_log,
    "level": ai_analyst_config.audit_log_level,
    "include_request_body": False,  # 出于隐私考虑，不记录请求体
    "include_response_body": False   # 出于隐私考虑，不记录响应体
}