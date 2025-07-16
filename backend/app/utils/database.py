from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os
from pathlib import Path

from app.settings import settings
from app.models.database import Base

# 获取数据目录路径
def get_data_directory():
    """获取数据目录路径，优先使用环境变量配置的路径"""
    data_dir = os.getenv("DATABASE_PERSISTENT_PATH", "./data")
    # 确保目录存在
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return data_dir

# 获取数据库文件路径
def get_database_path():
    """获取数据库文件路径"""
    data_dir = get_data_directory()
    return os.path.join(data_dir, "personalfinance.db")

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
    data_dir = get_data_directory()
    print(f"使用数据目录: {data_dir}")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def drop_tables():
    """删除所有数据库表"""
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成")


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 确保数据目录存在
    data_dir = get_data_directory()
    print(f"数据目录: {data_dir}")
    
    # 只在SQLite环境下检查数据库文件
    if settings.database_url.startswith("sqlite://"):
        db_path = get_database_path()
        db_exists = os.path.exists(db_path)
        print(f"数据库文件: {db_path} (存在: {db_exists})")
    
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
        else:
            print("数据库已初始化，跳过初始化步骤")
    
    # 创建IBKR审计表和触发器
    if os.getenv("RAILWAY_ENVIRONMENT"):
        setup_ibkr_audit_trigger()

# === 自动创建IBKR审计表和触发器 ===
def setup_ibkr_audit_trigger():
    """分步为ibkr相关表创建审计表和触发器，每步都打印异常"""
    from sqlalchemy import text
    if not settings.database_url.startswith("postgresql://"):
        print("非PostgreSQL数据库，跳过IBKR审计触发器创建")
        return
    # 1. 创建审计表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS audit_log (
        id serial PRIMARY KEY,
        table_name text,
        operation text,
        old_data jsonb,
        new_data jsonb,
        source_ip inet,
        user_agent text,
        api_key text,
        request_id text,
        session_id text,
        changed_at timestamp default now()
    );
    """
    # 2. 创建触发器函数
    create_func_sql = """
    CREATE OR REPLACE FUNCTION log_ibkr_audit() RETURNS trigger AS $$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO audit_log(table_name, operation, old_data, new_data, source_ip, user_agent, api_key, request_id, session_id)
            VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), NULL, NULL, NULL, NULL, NULL, NULL);
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO audit_log(table_name, operation, old_data, new_data, source_ip, user_agent, api_key, request_id, session_id)
            VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), NULL, NULL, NULL, NULL, NULL);
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO audit_log(table_name, operation, old_data, new_data, source_ip, user_agent, api_key, request_id, session_id)
            VALUES (TG_TABLE_NAME, TG_OP, NULL, row_to_json(NEW), NULL, NULL, NULL, NULL, NULL);
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """
    # 3. 分别为每个表创建触发器（如果已存在则忽略报错）
    trigger_sqls = [
        """
        DO $$ BEGIN BEGIN CREATE TRIGGER ibkr_accounts_audit AFTER INSERT OR UPDATE OR DELETE ON ibkr_accounts FOR EACH ROW EXECUTE FUNCTION log_ibkr_audit(); EXCEPTION WHEN duplicate_object THEN NULL; END; END $$;
        """,
        """
        DO $$ BEGIN BEGIN CREATE TRIGGER ibkr_balances_audit AFTER INSERT OR UPDATE OR DELETE ON ibkr_balances FOR EACH ROW EXECUTE FUNCTION log_ibkr_audit(); EXCEPTION WHEN duplicate_object THEN NULL; END; END $$;
        """,
        """
        DO $$ BEGIN BEGIN CREATE TRIGGER ibkr_positions_audit AFTER INSERT OR UPDATE OR DELETE ON ibkr_positions FOR EACH ROW EXECUTE FUNCTION log_ibkr_audit(); EXCEPTION WHEN duplicate_object THEN NULL; END; END $$;
        """,
        """
        DO $$ BEGIN BEGIN CREATE TRIGGER ibkr_sync_logs_audit AFTER INSERT OR UPDATE OR DELETE ON ibkr_sync_logs FOR EACH ROW EXECUTE FUNCTION log_ibkr_audit(); EXCEPTION WHEN duplicate_object THEN NULL; END; END $$;
        """
    ]
    with engine.connect() as conn:
        # 步骤1：建表
        try:
            conn.execute(text(create_table_sql))
            conn.commit()  # 提交事务
            print("audit_log表创建成功或已存在")
        except Exception as e:
            print(f"建表SQL执行失败: {e}\nSQL: {create_table_sql}\n")
        # 步骤2：建函数
        try:
            conn.execute(text(create_func_sql))
            conn.commit()  # 提交事务
            print("log_ibkr_audit函数创建成功或已存在")
        except Exception as e:
            print(f"建函数SQL执行失败: {e}\nSQL: {create_func_sql}\n")
        # 步骤3：建触发器
        for stmt in trigger_sqls:
            try:
                conn.execute(text(stmt))
                conn.commit()  # 提交事务
                print("触发器创建成功或已存在")
            except Exception as e:
                print(f"建触发器SQL执行失败: {e}\nSQL: {stmt}\n")
    print("IBKR审计表和触发器分步创建流程已执行")

def set_audit_context(source_ip: str = None, user_agent: str = None, api_key: str = None, 
                     request_id: str = None, session_id: str = None):
    """设置审计上下文，用于触发器记录操作来源"""
    if not settings.database_url.startswith("postgresql://"):
        return
    
    try:
        with engine.connect() as conn:
            # 设置会话变量
            if source_ip:
                conn.execute(text(f"SET audit.source_ip = '{source_ip}'"))
            if user_agent:
                conn.execute(text(f"SET audit.user_agent = '{user_agent}'"))
            if api_key:
                conn.execute(text(f"SET audit.api_key = '{api_key}'"))
            if request_id:
                conn.execute(text(f"SET audit.request_id = '{request_id}'"))
            if session_id:
                conn.execute(text(f"SET audit.session_id = '{session_id}'"))
            conn.commit()
    except Exception as e:
        print(f"设置审计上下文失败: {e}")

def clear_audit_context():
    """清除审计上下文"""
    if not settings.database_url.startswith("postgresql://"):
        return
    
    try:
        with engine.connect() as conn:
            # 清除会话变量
            conn.execute(text("RESET audit.source_ip"))
            conn.execute(text("RESET audit.user_agent"))
            conn.execute(text("RESET audit.api_key"))
            conn.execute(text("RESET audit.request_id"))
            conn.execute(text("RESET audit.session_id"))
            conn.commit()
    except Exception as e:
        print(f"清除审计上下文失败: {e}") 