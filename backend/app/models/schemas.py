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