from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# 基础响应模型
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


# 基金操作相关模型
class FundOperationBase(BaseModel):
    operation_date: datetime
    operation_type: str = Field(..., description="操作类型: buy, sell, dividend")
    asset_code: str = Field(..., description="基金代码")
    asset_name: str = Field(..., description="基金名称")
    amount: Decimal = Field(..., description="操作金额")
    nav: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    strategy: Optional[str] = None
    emotion_score: Optional[int] = Field(None, ge=1, le=10, description="情绪评分 1-10")
    notes: Optional[str] = None


class FundOperationCreate(BaseModel):
    operation_date: str
    operation_type: str = Field(..., description="操作类型: buy, sell, dividend")
    asset_code: str = Field(..., description="基金代码")
    asset_name: str = Field(..., description="基金名称")
    amount: Decimal = Field(..., description="操作金额")
    fee: Optional[Decimal] = None
    nav: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    strategy: Optional[str] = None
    emotion_score: Optional[int] = Field(None, ge=1, le=10, description="情绪评分 1-10")
    notes: Optional[str] = None
    
    # 新增字段：定投计划关联
    dca_plan_id: Optional[int] = None  # 关联定投计划ID
    dca_execution_type: Optional[str] = None  # 定投执行类型：scheduled, manual, smart


class FundOperationUpdate(BaseModel):
    operation_date: Optional[str] = None
    operation_type: Optional[str] = None
    asset_code: Optional[str] = None
    asset_name: Optional[str] = None
    amount: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    nav: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    strategy: Optional[str] = None
    emotion_score: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    
    # 新增字段：定投计划关联
    dca_plan_id: Optional[int] = None
    dca_execution_type: Optional[str] = None


class FundOperation(FundOperationBase):
    id: int
    platform: str = "支付宝"
    asset_type: str = "基金"
    currency: str = "CNY"
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    nav: Optional[Decimal] = None
    fee: Decimal = Decimal("0")
    tags: Optional[str] = None
    status: str = "pending"
    
    # 新增字段：定投计划关联
    dca_plan_id: Optional[int] = None
    dca_execution_type: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    latest_nav: Optional[float] = None

    class Config:
        from_attributes = True


# 基金信息相关模型
class FundInfoBase(BaseModel):
    fund_code: str
    fund_name: str
    fund_type: Optional[str] = None
    management_fee: Optional[Decimal] = None
    purchase_fee: Optional[Decimal] = None
    redemption_fee: Optional[Decimal] = None
    min_purchase: Optional[Decimal] = None
    risk_level: Optional[str] = None


class FundInfoCreate(FundInfoBase):
    pass


class FundInfo(FundInfoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 基金净值相关模型
class FundNavBase(BaseModel):
    fund_code: str
    nav_date: date
    nav: Decimal
    accumulated_nav: Optional[Decimal] = None
    growth_rate: Optional[Decimal] = None
    source: str = "api"


class FundNavCreate(FundNavBase):
    pass


class FundNav(FundNavBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 基金持仓相关模型
class FundPosition(BaseModel):
    asset_code: str
    asset_name: str
    total_shares: Decimal
    avg_cost: Decimal
    current_nav: Decimal
    current_value: Decimal
    total_invested: Decimal
    total_profit: Decimal
    profit_rate: Decimal
    last_updated: datetime

    class Config:
        from_attributes = True


# 定投计划相关模型
class DCAPlanBase(BaseModel):
    plan_name: str
    asset_code: str
    asset_name: str
    amount: Decimal
    currency: str = "CNY"
    frequency: str = Field(..., description="频率: daily, weekly, monthly, custom")
    frequency_value: int = Field(..., description="频率值: 1, 7, 30等")
    start_date: date
    end_date: Optional[date] = None
    strategy: Optional[str] = None
    
    # 新增字段：执行控制
    execution_time: str = "15:00"  # 执行时间
    smart_dca: bool = False  # 是否启用智能定投
    base_amount: Optional[Decimal] = None  # 基础定投金额
    max_amount: Optional[Decimal] = None  # 最大定投金额
    increase_rate: Optional[Decimal] = None  # 跌幅增加比例
    
    # 新增字段：执行条件
    min_nav: Optional[Decimal] = None  # 最低净值执行条件
    max_nav: Optional[Decimal] = None  # 最高净值执行条件
    skip_holidays: bool = True  # 是否跳过节假日
    
    # 新增字段：通知设置
    enable_notification: bool = True  # 是否启用通知
    notification_before: int = 30  # 提前通知分钟数
    
    # 新增字段：手续费设置
    fee_rate: Optional[Decimal] = Decimal("0")  # 手续费率，如0.0015表示0.15%
    
    # 新增字段：排除日期
    exclude_dates: Optional[List[str]] = None  # 排除日期列表，如["2024-07-01", "2024-07-03"]


class DCAPlanCreate(DCAPlanBase):
    platform: str = "支付宝"
    asset_type: str = "基金"


class DCAPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    amount: Optional[Decimal] = None
    frequency: Optional[str] = None
    frequency_value: Optional[int] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    strategy: Optional[str] = None
    
    # 新增字段更新
    execution_time: Optional[str] = None
    smart_dca: Optional[bool] = None
    base_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    increase_rate: Optional[Decimal] = None
    min_nav: Optional[Decimal] = None
    max_nav: Optional[Decimal] = None
    skip_holidays: Optional[bool] = None
    enable_notification: Optional[bool] = None
    notification_before: Optional[int] = None
    fee_rate: Optional[Decimal] = None
    exclude_dates: Optional[List[str]] = None  # 排除日期列表


class DCAPlan(DCAPlanBase):
    id: int
    platform: str
    asset_type: str
    status: str = "active"
    
    # 执行统计
    next_execution_date: Optional[date] = None
    last_execution_date: Optional[date] = None
    execution_count: Optional[int] = 0
    total_invested: Optional[Decimal] = Decimal("0")
    total_shares: Optional[Decimal] = Decimal("0")
    
    # 可选字段
    execution_time: Optional[str] = "15:00"
    smart_dca: Optional[bool] = False
    skip_holidays: Optional[bool] = True
    enable_notification: Optional[bool] = True
    notification_before: Optional[int] = 30
    fee_rate: Optional[Decimal] = Decimal("0")
    exclude_dates: Optional[List[str]] = None  # 排除日期列表
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 操作历史查询模型
class OperationQuery(BaseModel):
    platform: Optional[str] = None
    asset_type: Optional[str] = None
    asset_code: Optional[str] = None
    operation_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


# 持仓汇总模型
class PositionSummary(BaseModel):
    total_invested: Decimal
    total_value: Decimal
    total_profit: Decimal
    total_profit_rate: Decimal
    asset_count: int
    profitable_count: int
    loss_count: int


# 基金列表响应
class FundListResponse(BaseResponse):
    data: Optional[List[FundInfo]] = None


# 基金操作响应
class FundOperationResponse(BaseResponse):
    data: Optional[FundOperation] = None


# 基金操作列表响应
class FundOperationListResponse(BaseResponse):
    data: Optional[List[FundOperation]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20


# 基金持仓响应
class FundPositionResponse(BaseResponse):
    data: Optional[List[FundPosition]] = None


# 持仓汇总响应
class PositionSummaryResponse(BaseResponse):
    data: Optional[PositionSummary] = None


# 定投计划响应
class DCAPlanResponse(BaseResponse):
    data: Optional[DCAPlan] = None


# 定投计划列表响应
class DCAPlanListResponse(BaseResponse):
    data: Optional[List[DCAPlan]] = None


# 基金分红相关模型
class FundDividendBase(BaseModel):
    fund_code: str
    dividend_date: date
    record_date: Optional[date] = None
    dividend_amount: Decimal
    total_dividend: Optional[Decimal] = None
    announcement_date: Optional[date] = None


class FundDividendCreate(FundDividendBase):
    pass


class FundDividend(FundDividendBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 历史净值查询参数模型
class NavHistoryQuery(BaseModel):
    fund_code: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_dividend: bool = False
    page: int = 1
    page_size: int = 100


# 历史净值返回模型（包含分红信息）
class NavHistoryItem(BaseModel):
    nav_date: date
    nav: Decimal
    accumulated_nav: Optional[Decimal] = None
    growth_rate: Optional[Decimal] = None
    dividend_amount: Optional[Decimal] = None
    dividend_date: Optional[date] = None
    record_date: Optional[date] = None


class NavHistoryResponse(BaseResponse):
    data: Optional[List[NavHistoryItem]] = None
    total: int = 0
    page: int = 1
    page_size: int = 100


class FundDividendResponse(BaseResponse):
    data: Optional[FundDividend] = None


class FundDividendListResponse(BaseResponse):
    data: Optional[List[FundDividend]] = None


# Wise交易记录相关模型
class WiseTransactionBase(BaseModel):
    profile_id: str
    account_id: str
    transaction_id: str
    type: str  # INTERBALANCE, TRANSFER, etc.
    amount: Decimal
    currency: str
    description: str
    title: str
    date: datetime
    status: str
    reference_number: str


class WiseTransactionCreate(WiseTransactionBase):
    pass


class WiseTransactionUpdate(BaseModel):
    profile_id: Optional[str] = None
    account_id: Optional[str] = None
    transaction_id: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None
    date: Optional[datetime] = None
    status: Optional[str] = None
    reference_number: Optional[str] = None


class WiseTransaction(WiseTransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WiseTransactionResponse(BaseResponse):
    data: Optional[WiseTransaction] = None


class WiseTransactionListResponse(BaseResponse):
    data: Optional[List[WiseTransaction]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20


# Wise余额相关模型
class WiseBalanceBase(BaseModel):
    account_id: str
    currency: str
    available_balance: Decimal
    reserved_balance: Decimal
    cash_amount: Decimal
    total_worth: Decimal
    type: str
    investment_state: str
    creation_time: datetime
    modification_time: datetime
    visible: bool
    primary: bool


class WiseBalanceCreate(WiseBalanceBase):
    pass


class WiseBalance(WiseBalanceBase):
    id: int
    update_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class WiseBalanceResponse(BaseResponse):
    data: Optional[WiseBalance] = None


class WiseBalanceListResponse(BaseResponse):
    data: Optional[List[WiseBalance]] = None


# ============ 保险相关模型 ============

# 保险产品相关模型
class InsuranceProductBase(BaseModel):
    product_code: str = Field(..., description="产品代码")
    product_name: str = Field(..., description="产品名称")
    insurance_company: str = Field(..., description="保险公司")
    product_type: str = Field(..., description="产品类型")
    currency: str = Field(..., description="币种")
    min_premium: Optional[Decimal] = None
    max_premium: Optional[Decimal] = None
    payment_frequency: Optional[str] = None
    initial_charge_rate: Optional[Decimal] = None
    management_fee_rate: Optional[Decimal] = None
    surrender_charge_rate: Optional[Decimal] = None
    guaranteed_rate: Optional[Decimal] = None
    current_rate: Optional[Decimal] = None
    rate_type: Optional[str] = None


class InsuranceProductCreate(InsuranceProductBase):
    pass


class InsuranceProductUpdate(BaseModel):
    product_name: Optional[str] = None
    current_rate: Optional[Decimal] = None
    management_fee_rate: Optional[Decimal] = None
    guaranteed_rate: Optional[Decimal] = None


class InsuranceProduct(InsuranceProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 保险保单相关模型
class InsurancePolicyBase(BaseModel):
    policy_number: str = Field(..., description="保单号")
    product_code: str = Field(..., description="产品代码")
    product_name: str = Field(..., description="产品名称")
    insurance_company: str = Field(..., description="保险公司")
    policy_holder: str = Field(..., description="投保人")
    insured_person: str = Field(..., description="被保人")
    beneficiary: Optional[str] = None
    policy_start_date: date = Field(..., description="保单生效日期")
    policy_end_date: Optional[date] = None
    payment_start_date: date = Field(..., description="缴费开始日期")
    payment_end_date: Optional[date] = None
    sum_insured: Decimal = Field(..., description="保险金额")
    annual_premium: Decimal = Field(..., description="年保费")
    payment_frequency: str = Field(..., description="缴费频率")
    currency: str = Field(..., description="币种")


class InsurancePolicyCreate(InsurancePolicyBase):
    current_cash_value: Optional[Decimal] = Decimal("0")
    guaranteed_cash_value: Optional[Decimal] = Decimal("0")
    account_value: Optional[Decimal] = Decimal("0")


class InsurancePolicyUpdate(BaseModel):
    policy_holder: Optional[str] = None
    insured_person: Optional[str] = None
    beneficiary: Optional[str] = None
    policy_end_date: Optional[date] = None
    payment_end_date: Optional[date] = None
    annual_premium: Optional[Decimal] = None
    status: Optional[str] = None
    current_cash_value: Optional[Decimal] = None
    guaranteed_cash_value: Optional[Decimal] = None
    account_value: Optional[Decimal] = None


class PolicyValueUpdate(BaseModel):
    current_cash_value: Optional[Decimal] = None
    guaranteed_cash_value: Optional[Decimal] = None
    account_value: Optional[Decimal] = None
    valuation_date: date = Field(..., description="估值日期")
    notes: Optional[str] = None


class InsurancePolicy(InsurancePolicyBase):
    id: int
    status: str = "active"
    current_cash_value: Decimal = Decimal("0")
    guaranteed_cash_value: Decimal = Decimal("0")
    account_value: Decimal = Decimal("0")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 保险操作相关模型
class InsuranceOperationBase(BaseModel):
    policy_id: int
    operation_date: datetime
    operation_type: str = Field(..., description="操作类型")
    amount: Decimal = Field(..., description="金额")
    currency: str = Field(..., description="币种")
    exchange_rate: Optional[Decimal] = None
    amount_cny: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None


class InsuranceOperationCreate(InsuranceOperationBase):
    cash_value_before: Optional[Decimal] = None
    cash_value_after: Optional[Decimal] = None
    account_value_before: Optional[Decimal] = None
    account_value_after: Optional[Decimal] = None
    initial_charge: Optional[Decimal] = Decimal("0")
    management_fee: Optional[Decimal] = Decimal("0")
    insurance_cost: Optional[Decimal] = Decimal("0")


class PremiumPaymentCreate(BaseModel):
    payment_date: datetime
    amount: Decimal
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class TopUpCreate(BaseModel):
    topup_date: datetime
    amount: Decimal
    notes: Optional[str] = None


class WithdrawalCreate(BaseModel):
    withdrawal_date: datetime
    amount: Decimal
    withdrawal_reason: Optional[str] = None
    notes: Optional[str] = None


class InsuranceOperation(InsuranceOperationBase):
    id: int
    policy_number: str
    cash_value_before: Optional[Decimal] = None
    cash_value_after: Optional[Decimal] = None
    account_value_before: Optional[Decimal] = None
    account_value_after: Optional[Decimal] = None
    initial_charge: Decimal = Decimal("0")
    management_fee: Decimal = Decimal("0")
    insurance_cost: Decimal = Decimal("0")
    status: str = "confirmed"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 保险收益相关模型
class InsuranceReturnBase(BaseModel):
    policy_id: int
    return_date: date
    return_type: str = Field(..., description="收益类型")
    return_amount: Decimal = Field(..., description="收益金额")
    return_rate: Optional[Decimal] = None
    base_amount: Optional[Decimal] = None
    currency: str = Field(..., description="币种")
    distribution_method: Optional[str] = None
    description: Optional[str] = None


class InsuranceReturnCreate(InsuranceReturnBase):
    cash_value_change: Optional[Decimal] = Decimal("0")
    account_value_change: Optional[Decimal] = Decimal("0")
    source: str = "manual"


class DividendProcessCreate(BaseModel):
    dividend_date: date
    dividend_rate: Decimal
    dividend_year: int
    distribution_method: str = "reinvest"  # reinvest, cash, premium_offset
    notes: Optional[str] = None


class InsuranceReturn(InsuranceReturnBase):
    id: int
    policy_number: str
    cash_value_change: Decimal = Decimal("0")
    account_value_change: Decimal = Decimal("0")
    source: str = "manual"
    created_at: datetime

    class Config:
        from_attributes = True


# 保险分红历史相关模型
class InsuranceDividendHistoryBase(BaseModel):
    product_code: str
    policy_year: int
    dividend_year: int
    dividend_rate: Optional[Decimal] = None
    dividend_amount_per_1000: Optional[Decimal] = None
    bonus_rate: Optional[Decimal] = None
    announcement_date: Optional[date] = None
    distribution_date: Optional[date] = None
    description: Optional[str] = None


class InsuranceDividendHistoryCreate(InsuranceDividendHistoryBase):
    source: str = "company_announcement"


class InsuranceDividendHistory(InsuranceDividendHistoryBase):
    id: int
    source: str = "company_announcement"
    created_at: datetime

    class Config:
        from_attributes = True


# 保险统计相关模型
class InsuranceStatistics(BaseModel):
    total_policies: int
    total_invested: Decimal
    total_current_value: Decimal
    total_profit: Decimal
    total_profit_rate: Decimal
    universal_life_count: int
    whole_life_count: int
    endowment_count: int


class PolicyPerformance(BaseModel):
    policy_id: int
    policy_number: str
    total_premium_paid: Decimal
    current_value: Decimal
    total_profit: Decimal
    profit_rate: Decimal
    irr: Optional[Decimal] = None  # 内部收益率
    years_held: Decimal


# 响应模型
class InsuranceProductResponse(BaseResponse):
    data: Optional[InsuranceProduct] = None


class InsuranceProductListResponse(BaseResponse):
    data: Optional[List[InsuranceProduct]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20


class InsurancePolicyResponse(BaseResponse):
    data: Optional[InsurancePolicy] = None


class InsurancePolicyListResponse(BaseResponse):
    data: Optional[List[InsurancePolicy]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20


class InsuranceOperationResponse(BaseResponse):
    data: Optional[InsuranceOperation] = None


class InsuranceOperationListResponse(BaseResponse):
    data: Optional[List[InsuranceOperation]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20


class InsuranceReturnResponse(BaseResponse):
    data: Optional[InsuranceReturn] = None


class InsuranceReturnListResponse(BaseResponse):
    data: Optional[List[InsuranceReturn]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20


class InsuranceStatisticsResponse(BaseResponse):
    data: Optional[InsuranceStatistics] = None


class PolicyPerformanceResponse(BaseResponse):
    data: Optional[PolicyPerformance] = None


class ReturnsAnalysisResponse(BaseResponse):
    data: Optional[dict] = None 