from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AssetSnapshot(Base):
    __tablename__ = 'asset_snapshot'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    platform = Column(String(50), index=True)
    asset_type = Column(String(50), index=True)
    asset_code = Column(String(50), index=True)
    asset_name = Column(String(100))
    currency = Column(String(10), index=True)
    balance = Column(DECIMAL(20, 8), nullable=False)
    balance_cny = Column(DECIMAL(20, 8))
    balance_usd = Column(DECIMAL(20, 8))
    balance_eur = Column(DECIMAL(20, 8))
    base_value = Column(DECIMAL(20, 8))
    snapshot_time = Column(DateTime, index=True)
    extra = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class ExchangeRateSnapshot(Base):
    __tablename__ = 'exchange_rate_snapshot'
    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(10), index=True)
    to_currency = Column(String(10), index=True)
    rate = Column(DECIMAL(20, 8), nullable=False)
    snapshot_time = Column(DateTime, index=True)
    source = Column(String(50))
    extra = Column(JSON)
    created_at = Column(DateTime, default=func.now())