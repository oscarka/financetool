from sqlalchemy import (
    Column, Integer, String, DateTime, Date, DECIMAL, Text, 
    Boolean, ForeignKey, UniqueConstraint, Index, Float, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class AssetTypeConfig(Base):
    """资产类型配置表"""
    __tablename__ = "asset_type_config"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(32), unique=True, nullable=False, index=True)
    default_currency = Column(String(8), nullable=False)  # 默认基准货币
    asset_category = Column(String(32), nullable=False)  # 资产分类
    region = Column(String(16), nullable=False)  # 资产区域
    precision = Column(Integer, default=8)  # 精度
    is_active = Column(Boolean, default=True)
    extra = Column(JSON)  # 其他扩展信息
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserAssetPreference(Base):
    """用户资产偏好表"""
    __tablename__ = "user_asset_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    asset_type = Column(String(32), nullable=False, index=True)
    preferred_currency = Column(String(8), nullable=False)  # 用户偏好的基准货币
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)  # NULL表示永久有效
    extra = Column(JSON)  # 其他扩展信息
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_asset_effective', 'user_id', 'asset_type', 'effective_from'),
    )


class ExchangeRateTimeline(Base):
    """汇率时间轴表"""
    __tablename__ = "exchange_rate_timeline"
    
    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(8), nullable=False, index=True)
    to_currency = Column(String(8), nullable=False, index=True)
    rate = Column(DECIMAL(32, 8), nullable=False)
    effective_time = Column(DateTime, nullable=False, index=True)
    source = Column(String(32), nullable=False)  # 汇率来源
    extra = Column(JSON)  # 其他扩展信息
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', 'effective_time', name='uq_rate_timeline'),
        Index('idx_rate_lookup', 'from_currency', 'to_currency', 'effective_time'),
    )


class AccountBalanceSnapshot(Base):
    """账户余额快照表"""
    __tablename__ = "account_balance_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    asset_type = Column(String(32), nullable=False, index=True)
    balance = Column(DECIMAL(32, 8), nullable=False)  # 快照时原始币种余额
    snapshot_time = Column(DateTime, nullable=False, index=True)
    extra = Column(JSON)  # 其他扩展信息
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_balance_snapshot_lookup', 'user_id', 'asset_type', 'snapshot_time'),
        Index('idx_snapshot_time', 'snapshot_time'),
    )


class AssetDisplayConfig(Base):
    """资产展示配置表"""
    __tablename__ = "asset_display_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # NULL表示全局配置
    display_name = Column(String(64), nullable=False)
    currencies = Column(JSON, nullable=False)  # 要展示的币种列表
    base_currency = Column(String(8), nullable=False)  # 基准货币
    layout_type = Column(String(32), nullable=False)  # 布局类型
    is_default = Column(Boolean, default=False)
    extra = Column(JSON)  # 其他扩展信息
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WiseAPIConfig(Base):
    """Wise API配置表"""
    __tablename__ = "wise_api_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(255), nullable=False)
    api_url = Column(String(255), nullable=False, default="https://api.wise.com/v1")
    profile_id = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=60)  # 请求频率限制
    last_request = Column(DateTime, nullable=False)
    extra = Column(JSON)  # 其他配置信息
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ExchangeRateSource(Base):
    """汇率来源配置表"""
    __tablename__ = "exchange_rate_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(8), nullable=False, index=True)
    to_currency = Column(String(8), nullable=False, index=True)
    source_type = Column(String(32), nullable=False)  # WISE, AKSHARE, CACHE等
    source_config = Column(JSON, nullable=False)  # 数据源配置
    update_interval = Column(Integer, nullable=False)  # 更新间隔（分钟）
    is_active = Column(Boolean, default=True)
    last_update = Column(DateTime, nullable=True)
    extra = Column(JSON)  # 其他扩展信息
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', 'source_type', name='uq_rate_source'),
    )


class RateUpdateLog(Base):
    """汇率更新日志表"""
    __tablename__ = "rate_update_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(32), nullable=False, index=True)
    from_currency = Column(String(8), nullable=False)
    to_currency = Column(String(8), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, partial
    rate_value = Column(DECIMAL(32, 8), nullable=False)
    error_message = Column(Text, nullable=True)
    request_duration_ms = Column(Integer, nullable=True)
    records_updated = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_rate_update_status', 'source_type', 'status', 'created_at'),
    )
