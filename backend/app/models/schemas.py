from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal


# 基础响应模型
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


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


# IBKR相关模型
class IBKRSyncRequest(BaseModel):
    account_id: str = Field(..., min_length=1, max_length=50, description="IBKR账户ID")
    timestamp: str = Field(..., description="数据时间戳 ISO 8601格式")
    balances: dict = Field(..., description="账户余额信息")
    positions: List[dict] = Field(default_factory=list, description="持仓信息列表")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('时间戳格式无效，请使用ISO 8601格式')
    
    @field_validator('balances')
    @classmethod
    def validate_balances(cls, v):
        required_fields = ['total_cash', 'net_liquidation', 'buying_power', 'currency']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'余额信息缺少必需字段: {field}')
        return v


class IBKRSyncResponse(BaseModel):
    status: str
    message: str
    received_at: str
    records_updated: dict
    sync_id: Optional[int] = None
    errors: List[str] = Field(default_factory=list)


class IBKRAccountBase(BaseModel):
    account_id: str
    account_name: str
    account_type: str = "INDIVIDUAL"
    base_currency: str = "USD"
    status: str = "ACTIVE"


class IBKRAccount(IBKRAccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IBKRBalanceBase(BaseModel):
    account_id: str
    total_cash: Decimal
    net_liquidation: Decimal
    buying_power: Decimal
    currency: str = "USD"
    snapshot_date: date
    snapshot_time: datetime
    sync_source: str = "gcp_scheduler"


class IBKRBalance(IBKRBalanceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IBKRPositionBase(BaseModel):
    account_id: str
    symbol: str
    quantity: Decimal
    market_value: Decimal
    average_cost: Decimal
    unrealized_pnl: Optional[Decimal] = None
    realized_pnl: Optional[Decimal] = None
    currency: str = "USD"
    asset_class: str = "STK"
    snapshot_date: date
    snapshot_time: datetime
    sync_source: str = "gcp_scheduler"


class IBKRPosition(IBKRPositionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IBKRSyncLogBase(BaseModel):
    account_id: Optional[str] = None
    sync_type: str
    status: str
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    error_message: Optional[str] = None
    records_processed: int = 0
    records_updated: int = 0
    records_inserted: int = 0
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    sync_duration_ms: Optional[int] = None


class IBKRSyncLog(IBKRSyncLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# IBKR响应模型
class IBKRAccountResponse(BaseResponse):
    data: Optional[IBKRAccount] = None


class IBKRAccountListResponse(BaseResponse):
    data: Optional[List[IBKRAccount]] = None


class IBKRBalanceResponse(BaseResponse):
    data: Optional[IBKRBalance] = None


class IBKRBalanceListResponse(BaseResponse):
    data: Optional[List[IBKRBalance]] = None


class IBKRPositionResponse(BaseResponse):
    data: Optional[IBKRPosition] = None


class IBKRPositionListResponse(BaseResponse):
    data: Optional[List[IBKRPosition]] = None


class IBKRSyncLogResponse(BaseResponse):
    data: Optional[IBKRSyncLog] = None


class IBKRSyncLogListResponse(BaseResponse):
    data: Optional[List[IBKRSyncLog]] = None 