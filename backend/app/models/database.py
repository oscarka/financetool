from sqlalchemy import (
    Column, Integer, String, DateTime, Date, DECIMAL, Text, 
    Boolean, ForeignKey, UniqueConstraint, Index, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class UserOperation(Base):
    """用户操作记录表"""
    __tablename__ = "user_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    operation_date = Column(DateTime, nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    operation_type = Column(String(20), nullable=False)
    asset_code = Column(String(50), nullable=False, index=True)
    asset_name = Column(String(100), nullable=False)
    amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(10), nullable=False)
    quantity = Column(DECIMAL(15, 8))
    price = Column(DECIMAL(15, 4))
    nav = Column(DECIMAL(15, 4))  # 操作时的净值
    fee = Column(DECIMAL(10, 4), default=0)
    strategy = Column(Text)
    emotion_score = Column(Integer)
    tags = Column(Text)  # JSON格式
    notes = Column(Text)
    status = Column(String(20), default="pending")
    
    # 新增字段：定投计划关联
    dca_plan_id = Column(Integer, nullable=True)  # 关联定投计划，暂时去掉外键约束
    dca_execution_type = Column(String(20), nullable=True)  # 定投执行类型：scheduled(定时), manual(手动), smart(智能)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AssetPosition(Base):
    """资产持仓表"""
    __tablename__ = "asset_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    asset_code = Column(String(50), nullable=False, index=True)
    asset_name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)
    quantity = Column(DECIMAL(15, 8), nullable=False)
    avg_cost = Column(DECIMAL(15, 4), nullable=False)
    current_price = Column(DECIMAL(15, 4), nullable=False)
    current_value = Column(DECIMAL(15, 4), nullable=False)
    total_invested = Column(DECIMAL(15, 4), nullable=False)
    total_profit = Column(DECIMAL(15, 4), nullable=False)
    profit_rate = Column(DECIMAL(8, 4), nullable=False)
    last_updated = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('platform', 'asset_code', 'currency', name='uq_position'),
    )


class FundInfo(Base):
    """基金信息表"""
    __tablename__ = "fund_info"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_code = Column(String(20), unique=True, nullable=False, index=True)
    fund_name = Column(String(100), nullable=False)
    fund_type = Column(String(50))
    management_fee = Column(DECIMAL(5, 4))
    purchase_fee = Column(DECIMAL(5, 4))
    redemption_fee = Column(DECIMAL(5, 4))
    min_purchase = Column(DECIMAL(10, 2))
    risk_level = Column(String(20))
    created_at = Column(DateTime, default=func.now())


class FundNav(Base):
    """基金净值表"""
    __tablename__ = "fund_nav"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_code = Column(String(20), nullable=False, index=True)
    nav_date = Column(Date, nullable=False, index=True)
    nav = Column(DECIMAL(10, 4), nullable=False)
    accumulated_nav = Column(DECIMAL(10, 4))
    growth_rate = Column(DECIMAL(8, 4))
    source = Column(String(50), default="api")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('fund_code', 'nav_date', name='uq_fund_nav'),
    )


class FundDividend(Base):
    """基金分红表"""
    __tablename__ = "fund_dividend"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_code = Column(String(10), nullable=False, index=True)
    dividend_date = Column(Date, nullable=False, index=True)
    record_date = Column(Date, nullable=True)
    dividend_amount = Column(DECIMAL(10, 4), nullable=False)
    total_dividend = Column(DECIMAL(15, 2), nullable=True)
    announcement_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('fund_code', 'dividend_date', name='uq_fund_dividend'),
    )


class DCAPlan(Base):
    """定投计划表"""
    __tablename__ = "dca_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    asset_type = Column(String(50), nullable=False, default="基金")
    asset_code = Column(String(50), nullable=False)
    asset_name = Column(String(100), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, custom
    frequency_value = Column(Integer, nullable=False)  # 1, 7, 30等
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(String(20), default="active")  # active, paused, stopped, completed
    strategy = Column(Text)
    
    # 新增字段：执行控制
    execution_time = Column(String(10), default="15:00")  # 执行时间，默认15:00
    next_execution_date = Column(Date)  # 下次执行日期
    last_execution_date = Column(Date)  # 上次执行日期
    execution_count = Column(Integer, default=0)  # 已执行次数
    total_invested = Column(DECIMAL(15, 4), default=0)  # 累计投入金额
    total_shares = Column(DECIMAL(15, 8), default=0)  # 累计获得份额
    
    # 新增字段：智能定投
    smart_dca = Column(Boolean, default=False)  # 是否启用智能定投
    base_amount = Column(DECIMAL(10, 2))  # 基础定投金额
    max_amount = Column(DECIMAL(10, 2))  # 最大定投金额
    increase_rate = Column(DECIMAL(5, 4))  # 跌幅增加比例，如0.1表示跌10%增加10%
    
    # 新增字段：执行条件
    min_nav = Column(DECIMAL(10, 4))  # 最低净值执行条件
    max_nav = Column(DECIMAL(10, 4))  # 最高净值执行条件
    skip_holidays = Column(Boolean, default=True)  # 是否跳过节假日
    
    # 新增字段：通知设置
    enable_notification = Column(Boolean, default=True)  # 是否启用通知
    notification_before = Column(Integer, default=30)  # 提前通知分钟数
    
    # 新增字段：手续费设置
    fee_rate = Column(DECIMAL(5, 4), default=0)  # 手续费率，如0.0015表示0.15%
    
    # 新增字段：排除日期
    exclude_dates = Column(Text)  # JSON格式存储排除日期列表，如["2024-07-01", "2024-07-03"]
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ExchangeRate(Base):
    """汇率表"""
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(10), nullable=False, index=True)
    to_currency = Column(String(10), nullable=False, index=True)
    rate = Column(DECIMAL(15, 6), nullable=False)
    rate_date = Column(Date, nullable=False, index=True)
    source = Column(String(50), default="api")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='uq_exchange_rate'),
    )


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WiseTransaction(Base):
    """Wise交易记录表"""
    __tablename__ = "wise_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String(50), nullable=False, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    transaction_id = Column(String(200), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)  # INTERBALANCE, TRANSFER, etc.
    amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(10), nullable=False)
    description = Column(Text)
    title = Column(Text)
    date = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), nullable=False)
    reference_number = Column(String(100))
    # 新增字段
    primary_amount_value = Column(DECIMAL(15, 4), nullable=True)
    primary_amount_currency = Column(String(10), nullable=True)
    secondary_amount_value = Column(DECIMAL(15, 4), nullable=True)
    secondary_amount_currency = Column(String(10), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('transaction_id', name='uq_wise_transaction'),
        Index('idx_wise_transaction_date', 'date'),
        Index('idx_wise_transaction_profile', 'profile_id'),
        Index('idx_wise_transaction_account', 'account_id'),
    )


class WiseBalance(Base):
    """Wise余额表"""
    __tablename__ = "wise_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), unique=True, nullable=False, index=True)
    currency = Column(String(10), nullable=False, index=True)
    available_balance = Column(DECIMAL(15, 4), nullable=False)
    reserved_balance = Column(DECIMAL(15, 4), nullable=False)
    cash_amount = Column(DECIMAL(15, 4), nullable=False)
    total_worth = Column(DECIMAL(15, 4), nullable=False)
    type = Column(String(50), nullable=False)
    investment_state = Column(String(50), nullable=False)
    creation_time = Column(DateTime, nullable=False)
    modification_time = Column(DateTime, nullable=False)
    visible = Column(Boolean, default=True)
    primary = Column(Boolean, default=False)
    update_time = Column(DateTime, default=func.now())
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('account_id', name='uq_wise_balance'),
        Index('idx_wise_balance_currency', 'currency'),
    )


class WiseExchangeRate(Base):
    __tablename__ = 'wise_exchange_rates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_currency = Column(String(8), nullable=False)
    target_currency = Column(String(8), nullable=False)
    rate = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


# 创建索引
Index('idx_operations_date', UserOperation.operation_date)
Index('idx_operations_platform', UserOperation.platform)
Index('idx_operations_asset', UserOperation.asset_code)

Index('idx_positions_platform', AssetPosition.platform)
Index('idx_positions_asset', AssetPosition.asset_code)

Index('idx_fund_nav_date', FundNav.nav_date)
Index('idx_fund_nav_code', FundNav.fund_code)

Index('idx_exchange_rates_date', ExchangeRate.rate_date)
Index('idx_exchange_rates_currency', ExchangeRate.from_currency, ExchangeRate.to_currency)

Index('idx_fund_dividend_code', FundDividend.fund_code)
Index('idx_fund_dividend_date', FundDividend.dividend_date)


class IBKRAccount(Base):
    """IBKR账户信息表"""
    __tablename__ = "ibkr_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), unique=True, nullable=False, index=True)
    account_name = Column(String(100))
    account_type = Column(String(50), default="INDIVIDUAL")
    base_currency = Column(String(10), default="USD")
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class IBKRBalance(Base):
    """IBKR余额表"""
    __tablename__ = "ibkr_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    total_cash = Column(DECIMAL(15, 2), nullable=False, default=0)
    net_liquidation = Column(DECIMAL(15, 2), nullable=False, default=0)
    buying_power = Column(DECIMAL(15, 2), nullable=False, default=0)
    currency = Column(String(10), nullable=False, default="USD")
    snapshot_date = Column(Date, nullable=False, index=True)
    snapshot_time = Column(DateTime, nullable=False)
    sync_source = Column(String(50), default="gcp_scheduler")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('account_id', 'snapshot_date', 'snapshot_time', name='uq_ibkr_balance'),
    )


class IBKRPosition(Base):
    """IBKR持仓表"""
    __tablename__ = "ibkr_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(DECIMAL(15, 6), nullable=False, default=0)
    market_value = Column(DECIMAL(15, 2), nullable=False, default=0)
    average_cost = Column(DECIMAL(15, 2), nullable=False, default=0)
    unrealized_pnl = Column(DECIMAL(15, 2), default=0)
    realized_pnl = Column(DECIMAL(15, 2), default=0)
    currency = Column(String(10), nullable=False, default="USD")
    asset_class = Column(String(50), default="STK")
    snapshot_date = Column(Date, nullable=False, index=True)
    snapshot_time = Column(DateTime, nullable=False)
    sync_source = Column(String(50), default="gcp_scheduler")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('account_id', 'symbol', 'snapshot_date', 'snapshot_time', name='uq_ibkr_position'),
    )


class IBKRSyncLog(Base):
    """IBKR同步日志表"""
    __tablename__ = "ibkr_sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), index=True)
    sync_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    request_data = Column(Text)
    response_data = Column(Text)
    error_message = Column(Text)
    records_processed = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    source_ip = Column(String(50))
    user_agent = Column(String(200))
    sync_duration_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now(), index=True)


# IBKR索引
Index('idx_ibkr_accounts_id', IBKRAccount.account_id)
Index('idx_ibkr_balances_account', IBKRBalance.account_id)
Index('idx_ibkr_balances_date', IBKRBalance.snapshot_date)
Index('idx_ibkr_positions_account', IBKRPosition.account_id)
Index('idx_ibkr_positions_symbol', IBKRPosition.symbol)
Index('idx_ibkr_positions_date', IBKRPosition.snapshot_date)
Index('idx_ibkr_sync_logs_status', IBKRSyncLog.status)
Index('idx_ibkr_sync_logs_date', IBKRSyncLog.created_at)
Index('idx_ibkr_sync_logs_account', IBKRSyncLog.account_id) 

# OKX相关模型
class OKXBalance(Base):
    """OKX余额表"""
    __tablename__ = "okx_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    currency = Column(String(10), nullable=False, index=True)
    available_balance = Column(DECIMAL(15, 8), nullable=False, default=0)
    frozen_balance = Column(DECIMAL(15, 8), nullable=False, default=0)
    total_balance = Column(DECIMAL(15, 8), nullable=False, default=0)
    account_type = Column(String(20), nullable=False, default="trading")  # trading, funding, savings
    update_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('account_id', 'currency', 'account_type', name='uq_okx_balance'),
        Index('idx_okx_balance_currency', 'currency'),
        Index('idx_okx_balance_account_type', 'account_type'),
    )


class OKXTransaction(Base):
    """OKX交易记录表"""
    __tablename__ = "okx_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    inst_type = Column(String(20), nullable=False)  # SPOT, MARGIN, SWAP, FUTURES
    inst_id = Column(String(50), nullable=False, index=True)  # 产品ID，如BTC-USDT
    trade_id = Column(String(100), nullable=True)
    order_id = Column(String(100), nullable=True)
    bill_id = Column(String(100), nullable=True)
    type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=True)
    amount = Column(DECIMAL(15, 8), nullable=False, default=0)
    currency = Column(String(10), nullable=False, index=True)
    fee = Column(DECIMAL(15, 8), nullable=False, default=0)
    fee_currency = Column(String(10), nullable=True)
    price = Column(DECIMAL(15, 8), nullable=True)
    quantity = Column(DECIMAL(15, 8), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    # 新增bills-archive字段
    bal = Column(String(32))
    bal_chg = Column(String(32))
    ccy = Column(String(10))
    cl_ord_id = Column(String(64))
    exec_type = Column(String(16))
    fill_fwd_px = Column(String(32))
    fill_idx_px = Column(String(32))
    fill_mark_px = Column(String(32))
    fill_mark_vol = Column(String(32))
    fill_px_usd = Column(String(32))
    fill_px_vol = Column(String(32))
    fill_time = Column(String(32))
    from_addr = Column(String(64))
    interest = Column(String(32))
    mgn_mode = Column(String(16))
    notes = Column(Text)
    pnl = Column(String(32))
    pos_bal = Column(String(32))
    pos_bal_chg = Column(String(32))
    sub_type = Column(String(16))
    tag = Column(String(32))
    to_addr = Column(String(64))
    
    __table_args__ = (
        UniqueConstraint('transaction_id', name='uq_okx_transaction'),
        Index('idx_okx_transaction_timestamp', 'timestamp'),
        Index('idx_okx_transaction_inst_id', 'inst_id'),
        Index('idx_okx_transaction_type', 'type'),
    )


class OKXPosition(Base):
    """OKX持仓表"""
    __tablename__ = "okx_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    inst_type = Column(String(20), nullable=False)  # SPOT, MARGIN, SWAP, FUTURES
    inst_id = Column(String(50), nullable=False, index=True)  # 产品ID
    position_side = Column(String(10), nullable=False)  # long, short
    position_id = Column(String(100), nullable=False)
    quantity = Column(DECIMAL(15, 8), nullable=False, default=0)
    avg_price = Column(DECIMAL(15, 8), nullable=False, default=0)
    unrealized_pnl = Column(DECIMAL(15, 8), nullable=False, default=0)
    realized_pnl = Column(DECIMAL(15, 8), nullable=False, default=0)
    margin_ratio = Column(DECIMAL(15, 8), nullable=True)
    leverage = Column(DECIMAL(15, 8), nullable=True)
    mark_price = Column(DECIMAL(15, 8), nullable=True)
    liquidation_price = Column(DECIMAL(15, 8), nullable=True)
    currency = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('account_id', 'inst_id', 'position_side', 'timestamp', name='uq_okx_position'),
        Index('idx_okx_position_inst_id', 'inst_id'),
        Index('idx_okx_position_timestamp', 'timestamp'),
    )


class OKXMarketData(Base):
    """OKX市场数据表"""
    __tablename__ = "okx_market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    inst_id = Column(String(50), nullable=False, index=True)  # 产品ID
    inst_type = Column(String(20), nullable=False)  # SPOT, MARGIN, SWAP, FUTURES
    last_price = Column(DECIMAL(20, 8), nullable=False)  # 增加精度以支持大数值
    bid_price = Column(DECIMAL(20, 8), nullable=True)
    ask_price = Column(DECIMAL(20, 8), nullable=True)
    high_24h = Column(DECIMAL(20, 8), nullable=True)
    low_24h = Column(DECIMAL(20, 8), nullable=True)
    volume_24h = Column(DECIMAL(20, 8), nullable=True)
    change_24h = Column(DECIMAL(20, 8), nullable=True)
    change_rate_24h = Column(DECIMAL(20, 8), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('inst_id', 'inst_type', 'timestamp', name='uq_okx_market_data'),
    )


class OKXAccountOverview(Base):
    """OKX账户总览表"""
    __tablename__ = "okx_account_overview"
    
    id = Column(Integer, primary_key=True, index=True)
    trading_total_usd = Column(DECIMAL(15, 8), nullable=False, default=0)  # 交易账户总资产(USD)
    funding_total_usd = Column(DECIMAL(15, 8), nullable=False, default=0)  # 资金账户总资产(USD)
    savings_total_usd = Column(DECIMAL(15, 8), nullable=False, default=0)  # 储蓄账户总资产(USD)
    total_assets_usd = Column(DECIMAL(15, 8), nullable=False, default=0)  # 总资产(USD)
    total_currencies = Column(Integer, nullable=False, default=0)  # 总币种数
    trading_currencies_count = Column(Integer, nullable=False, default=0)  # 交易账户币种数
    funding_currencies_count = Column(Integer, nullable=False, default=0)  # 资金账户币种数
    savings_currencies_count = Column(Integer, nullable=False, default=0)  # 储蓄账户币种数
    last_update = Column(DateTime, nullable=False, index=True)
    data_source = Column(String(20), nullable=False, default="api")  # api, database
    created_at = Column(DateTime, default=func.now())


class Web3Balance(Base):
    """Web3余额表"""
    __tablename__ = "web3_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), nullable=False, index=True)
    account_id = Column(String(100), nullable=False, index=True)
    total_value = Column(DECIMAL(20, 8), nullable=False, default=0)  # 总价值
    currency = Column(String(10), nullable=False, default="USD")  # 货币单位
    update_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('project_id', 'account_id', 'update_time', name='uq_web3_balance'),
    )


class Web3Token(Base):
    """Web3代币表"""
    __tablename__ = "web3_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), nullable=False, index=True)
    account_id = Column(String(100), nullable=False, index=True)
    token_symbol = Column(String(20), nullable=False, index=True)  # 代币符号
    token_name = Column(String(100), nullable=False)  # 代币名称
    token_address = Column(String(100), nullable=True)  # 代币合约地址
    balance = Column(DECIMAL(20, 8), nullable=False, default=0)  # 余额
    value_usd = Column(DECIMAL(20, 8), nullable=False, default=0)  # USD价值
    price_usd = Column(DECIMAL(20, 8), nullable=True)  # USD价格
    update_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('project_id', 'account_id', 'token_symbol', 'update_time', name='uq_web3_token'),
    )


class Web3Transaction(Base):
    """Web3交易记录表"""
    __tablename__ = "web3_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), nullable=False, index=True)
    account_id = Column(String(100), nullable=False, index=True)
    transaction_hash = Column(String(100), unique=True, nullable=False, index=True)  # 交易哈希
    block_number = Column(Integer, nullable=True)  # 区块号
    from_address = Column(String(100), nullable=True)  # 发送地址
    to_address = Column(String(100), nullable=True)  # 接收地址
    token_symbol = Column(String(20), nullable=True, index=True)  # 代币符号
    amount = Column(DECIMAL(20, 8), nullable=False, default=0)  # 金额
    value_usd = Column(DECIMAL(20, 8), nullable=True)  # USD价值
    gas_used = Column(DECIMAL(20, 8), nullable=True)  # Gas使用量
    gas_price = Column(DECIMAL(20, 8), nullable=True)  # Gas价格
    transaction_type = Column(String(50), nullable=True)  # 交易类型
    status = Column(String(20), nullable=False, default="success")  # 交易状态
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('transaction_hash', name='uq_web3_transaction'),
    )

# Web3钱包相关模型

class Web3Wallet(Base):
    """Web3钱包管理表"""
    __tablename__ = "web3_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    wallet_address = Column(String(42), nullable=False, index=True)
    wallet_name = Column(String(50), nullable=True)
    chain_type = Column(String(20), nullable=False, index=True)
    connection_type = Column(String(20), nullable=False)
    last_sync_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('wallet_address', 'chain_type', name='uq_wallet_chain'),
    )


class Web3WalletBalance(Base):
    """Web3钱包余额表（历史记录模式）"""
    __tablename__ = "web3_wallet_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey('web3_wallets.id', ondelete='CASCADE'), nullable=False, index=True)
    chain = Column(String(20), nullable=False, index=True)
    token_symbol = Column(String(10), nullable=False, index=True)
    token_name = Column(String(100), nullable=True)
    token_address = Column(String(100), nullable=True)
    balance = Column(DECIMAL(30, 18), nullable=False)
    balance_formatted = Column(String(50), nullable=True)
    usdt_price = Column(DECIMAL(15, 8), nullable=True)
    usdt_value = Column(DECIMAL(15, 2), nullable=True)
    is_native_token = Column(Boolean, nullable=True, default=False)
    sync_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_balances_wallet_time', 'wallet_id', 'sync_time'),
    )


class Web3TokenPrice(Base):
    """Web3代币价格缓存表"""
    __tablename__ = "web3_token_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    token_symbol = Column(String(10), nullable=False, index=True)
    token_address = Column(String(100), nullable=True)
    chain = Column(String(20), nullable=False, index=True)
    usdt_price = Column(DECIMAL(15, 8), nullable=False)
    coingecko_id = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('token_symbol', 'chain', 'token_address', name='uq_token_price'),
    )

# OKX索引 - 这些索引已经在__table_args__中定义，这里不需要重复定义 