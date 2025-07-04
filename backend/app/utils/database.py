from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

from app.config import settings
from app.models.database import Base

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """创建所有数据库表"""
    from app.models.database import (
        UserOperation, AssetPosition, FundInfo, FundNav, 
        DCAPlan, ExchangeRate, SystemConfig
    )
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def drop_tables():
    """删除所有数据库表"""
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成")


def init_database():
    """初始化数据库"""
    create_tables()
    
    # 可以在这里添加初始数据
    with get_db_context() as db:
        # 添加一些系统配置
        from app.models.database import SystemConfig
        
        # 检查是否已有配置
        if not db.query(SystemConfig).filter(SystemConfig.config_key == "system_initialized").first():
            init_config = SystemConfig(
                config_key="system_initialized",
                config_value="true",
                description="系统初始化标记"
            )
            db.add(init_config)
            print("数据库初始化完成") 