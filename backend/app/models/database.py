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


class InsuranceProduct(Base):
    """保险产品信息表"""
    __tablename__ = "insurance_products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    insurance_company = Column(String(100), nullable=False)
    product_type = Column(String(50), nullable=False)  # universal(万能险), whole_life(终身寿险), endowment(养老险)
    currency = Column(String(10), nullable=False)
    
    # 产品特性
    min_premium = Column(DECIMAL(15, 4))  # 最低保费
    max_premium = Column(DECIMAL(15, 4))  # 最高保费
    payment_frequency = Column(String(20))  # 缴费频率: monthly, quarterly, annually, single
    
    # 费用结构
    initial_charge_rate = Column(DECIMAL(5, 4))  # 初始费用率
    management_fee_rate = Column(DECIMAL(5, 4))  # 管理费率
    surrender_charge_rate = Column(DECIMAL(5, 4))  # 退保费用率
    
    # 收益相关
    guaranteed_rate = Column(DECIMAL(5, 4))  # 保证利率
    current_rate = Column(DECIMAL(5, 4))  # 当前结算利率
    rate_type = Column(String(20))  # 结算类型: monthly(月结), annually(年结)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class InsurancePolicy(Base):
    """保险保单表"""
    __tablename__ = "insurance_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(100), unique=True, nullable=False, index=True)
    product_code = Column(String(50), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    insurance_company = Column(String(100), nullable=False)
    
    # 保单基本信息
    policy_holder = Column(String(100), nullable=False)  # 投保人
    insured_person = Column(String(100), nullable=False)  # 被保人
    beneficiary = Column(String(200))  # 受益人
    
    # 保单时间
    policy_start_date = Column(Date, nullable=False)
    policy_end_date = Column(Date)
    payment_start_date = Column(Date, nullable=False)
    payment_end_date = Column(Date)
    
    # 保单金额
    sum_insured = Column(DECIMAL(15, 4), nullable=False)  # 保险金额
    annual_premium = Column(DECIMAL(15, 4), nullable=False)  # 年保费
    payment_frequency = Column(String(20), nullable=False)  # 缴费频率
    currency = Column(String(10), nullable=False)
    
    # 保单状态
    status = Column(String(20), default="active")  # active, suspended, surrendered, matured
    
    # 当前价值
    current_cash_value = Column(DECIMAL(15, 4), default=0)  # 当前现金价值
    guaranteed_cash_value = Column(DECIMAL(15, 4), default=0)  # 保证现金价值
    account_value = Column(DECIMAL(15, 4), default=0)  # 账户价值（万能险）
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class InsuranceOperation(Base):
    """保险操作记录表"""
    __tablename__ = "insurance_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, nullable=False, index=True)
    policy_number = Column(String(100), nullable=False, index=True)
    
    operation_date = Column(DateTime, nullable=False, index=True)
    operation_type = Column(String(50), nullable=False)  # premium_payment, top_up, partial_withdrawal, dividend_received, interest_credited, fee_charged
    
    # 金额信息
    amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(10), nullable=False)
    exchange_rate = Column(DECIMAL(15, 6))  # 汇率（如有）
    amount_cny = Column(DECIMAL(15, 4))  # 人民币金额
    
    # 详细信息
    description = Column(Text)
    notes = Column(Text)
    reference_number = Column(String(100))  # 参考号码
    
    # 影响的价值
    cash_value_before = Column(DECIMAL(15, 4))  # 操作前现金价值
    cash_value_after = Column(DECIMAL(15, 4))  # 操作后现金价值
    account_value_before = Column(DECIMAL(15, 4))  # 操作前账户价值
    account_value_after = Column(DECIMAL(15, 4))  # 操作后账户价值
    
    # 费用明细
    initial_charge = Column(DECIMAL(15, 4), default=0)  # 初始费用
    management_fee = Column(DECIMAL(15, 4), default=0)  # 管理费
    insurance_cost = Column(DECIMAL(15, 4), default=0)  # 保险成本
    
    status = Column(String(20), default="confirmed")  # pending, confirmed, cancelled
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class InsuranceReturn(Base):
    """保险收益记录表"""
    __tablename__ = "insurance_returns"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, nullable=False, index=True)
    policy_number = Column(String(100), nullable=False, index=True)
    
    return_date = Column(Date, nullable=False, index=True)
    return_type = Column(String(50), nullable=False)  # interest(利息), dividend(分红), bonus(特别红利)
    
    # 收益信息
    return_amount = Column(DECIMAL(15, 4), nullable=False)
    return_rate = Column(DECIMAL(8, 6))  # 收益率
    base_amount = Column(DECIMAL(15, 4))  # 计息基数
    currency = Column(String(10), nullable=False)
    
    # 处理方式
    distribution_method = Column(String(50))  # reinvest(再投资), cash(现金), premium_offset(抵扣保费)
    
    # 价值变化
    cash_value_change = Column(DECIMAL(15, 4), default=0)
    account_value_change = Column(DECIMAL(15, 4), default=0)
    
    description = Column(Text)
    source = Column(String(50), default="manual")  # manual, api, calculated
    
    created_at = Column(DateTime, default=func.now())


class InsuranceDividendHistory(Base):
    """保险分红历史表"""
    __tablename__ = "insurance_dividend_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), nullable=False, index=True)
    policy_year = Column(Integer, nullable=False)  # 保单年度
    dividend_year = Column(Integer, nullable=False, index=True)  # 分红年度
    
    # 分红信息
    dividend_rate = Column(DECIMAL(8, 6))  # 分红率
    dividend_amount_per_1000 = Column(DECIMAL(10, 4))  # 每1000元保额分红
    bonus_rate = Column(DECIMAL(8, 6))  # 特别红利率
    
    announcement_date = Column(Date)  # 公布日期
    distribution_date = Column(Date)  # 派发日期
    
    description = Column(Text)
    source = Column(String(50), default="company_announcement")
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('product_code', 'policy_year', 'dividend_year', name='uq_dividend_history'),
    )


# 保险相关索引
Index('idx_insurance_product_company', InsuranceProduct.insurance_company)
Index('idx_insurance_product_type', InsuranceProduct.product_type)

Index('idx_insurance_policy_company', InsurancePolicy.insurance_company)
Index('idx_insurance_policy_status', InsurancePolicy.status)
Index('idx_insurance_policy_start_date', InsurancePolicy.policy_start_date)

Index('idx_insurance_operation_date', InsuranceOperation.operation_date)
Index('idx_insurance_operation_type', InsuranceOperation.operation_type)
Index('idx_insurance_operation_policy', InsuranceOperation.policy_id)

Index('idx_insurance_return_date', InsuranceReturn.return_date)
Index('idx_insurance_return_type', InsuranceReturn.return_type)
Index('idx_insurance_return_policy', InsuranceReturn.policy_id)

Index('idx_insurance_dividend_product', InsuranceDividendHistory.product_code)
Index('idx_insurance_dividend_year', InsuranceDividendHistory.dividend_year) 