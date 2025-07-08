# 投资类保险模块设计方案

## 概述

基于现有系统架构，新增投资类保险模块，支持万能险和港险等投资型保险产品的管理。

## 业务需求分析

### 万能险特点
- **月复利收益**：每月结算收益，复利计算
- **灵活缴费**：可以追加投资，部分提取
- **保险保障**：具有基本保险功能
- **费用结构**：初始费用、管理费、保障成本等

### 港险特点  
- **定期分红**：年度分红或特别分红
- **保单价值增长**：现金价值和保证价值
- **币种多样**：港币、美元等
- **长期投资**：通常为长期储蓄型产品

## 数据模型设计

### 1. 保险产品信息表 (InsuranceProduct)

```python
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
```

### 2. 保险保单表 (InsurancePolicy)

```python
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
```

### 3. 保险操作记录表 (InsuranceOperation)

```python
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
```

### 4. 保险收益记录表 (InsuranceReturn)

```python
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
```

### 5. 保险分红历史表 (InsuranceDividendHistory)

```python
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
```

## API接口设计

### 1. 保险产品管理API

```python
# backend/app/api/v1/insurance.py

@router.post("/products", response_model=BaseResponse)
def create_insurance_product(product: InsuranceProductCreate, db: Session = Depends(get_db)):
    """创建保险产品"""

@router.get("/products", response_model=InsuranceProductListResponse)  
def get_insurance_products(db: Session = Depends(get_db)):
    """获取保险产品列表"""

@router.get("/products/{product_code}", response_model=InsuranceProductResponse)
def get_insurance_product(product_code: str, db: Session = Depends(get_db)):
    """获取保险产品详情"""
```

### 2. 保险保单管理API

```python
@router.post("/policies", response_model=InsurancePolicyResponse)
def create_insurance_policy(policy: InsurancePolicyCreate, db: Session = Depends(get_db)):
    """创建保险保单"""

@router.get("/policies", response_model=InsurancePolicyListResponse)
def get_insurance_policies(
    status: Optional[str] = None,
    company: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取保险保单列表"""

@router.get("/policies/{policy_id}", response_model=InsurancePolicyResponse)
def get_insurance_policy(policy_id: int, db: Session = Depends(get_db)):
    """获取保险保单详情"""

@router.put("/policies/{policy_id}/value", response_model=BaseResponse)
def update_policy_value(
    policy_id: int, 
    value_update: PolicyValueUpdate, 
    db: Session = Depends(get_db)
):
    """更新保单价值"""
```

### 3. 保险操作记录API

```python
@router.post("/operations", response_model=InsuranceOperationResponse)
def create_insurance_operation(operation: InsuranceOperationCreate, db: Session = Depends(get_db)):
    """创建保险操作记录"""

@router.get("/operations", response_model=InsuranceOperationListResponse)
def get_insurance_operations(
    policy_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取保险操作记录"""

@router.post("/operations/{policy_id}/premium", response_model=InsuranceOperationResponse)
def pay_premium(policy_id: int, premium_payment: PremiumPaymentCreate, db: Session = Depends(get_db)):
    """缴费操作"""

@router.post("/operations/{policy_id}/topup", response_model=InsuranceOperationResponse) 
def top_up_policy(policy_id: int, topup: TopUpCreate, db: Session = Depends(get_db)):
    """追加投资"""

@router.post("/operations/{policy_id}/withdrawal", response_model=InsuranceOperationResponse)
def partial_withdrawal(policy_id: int, withdrawal: WithdrawalCreate, db: Session = Depends(get_db)):
    """部分提取"""
```

### 4. 收益管理API

```python
@router.post("/returns", response_model=InsuranceReturnResponse)
def create_insurance_return(return_record: InsuranceReturnCreate, db: Session = Depends(get_db)):
    """创建收益记录"""

@router.get("/returns/{policy_id}", response_model=InsuranceReturnListResponse)
def get_policy_returns(
    policy_id: int,
    return_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取保单收益记录"""

@router.post("/returns/calculate-monthly/{policy_id}", response_model=BaseResponse)
def calculate_monthly_interest(policy_id: int, calculation_date: date, db: Session = Depends(get_db)):
    """计算月度利息（万能险）"""

@router.post("/returns/process-dividend/{policy_id}", response_model=BaseResponse)
def process_annual_dividend(policy_id: int, dividend_data: DividendProcessCreate, db: Session = Depends(get_db)):
    """处理年度分红（港险）"""
```

### 5. 统计分析API

```python
@router.get("/statistics/summary", response_model=InsuranceStatisticsResponse)
def get_insurance_summary(db: Session = Depends(get_db)):
    """获取保险投资汇总"""

@router.get("/statistics/performance/{policy_id}", response_model=PolicyPerformanceResponse)
def get_policy_performance(policy_id: int, db: Session = Depends(get_db)):
    """获取保单投资表现"""

@router.get("/statistics/returns-analysis", response_model=ReturnsAnalysisResponse)
def get_returns_analysis(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """收益分析"""
```

## 业务逻辑服务设计

### 1. 万能险服务 (UniversalLifeService)

```python
class UniversalLifeService:
    """万能险业务服务"""
    
    @staticmethod
    def calculate_monthly_interest(db: Session, policy_id: int, calculation_date: date):
        """计算月度复利收益"""
        # 1. 获取保单信息和当前账户价值
        # 2. 获取当月结算利率
        # 3. 计算利息 = 账户价值 * 月利率
        # 4. 扣除保险成本和管理费
        # 5. 更新账户价值
        # 6. 记录收益操作
    
    @staticmethod
    def process_premium_payment(db: Session, policy_id: int, amount: Decimal, payment_date: date):
        """处理保费缴纳"""
        # 1. 扣除初始费用
        # 2. 计算进入账户金额
        # 3. 更新账户价值
        # 4. 记录操作
    
    @staticmethod
    def process_top_up(db: Session, policy_id: int, amount: Decimal, topup_date: date):
        """处理追加投资"""
        # 1. 扣除相应费用
        # 2. 增加账户价值
        # 3. 记录操作
    
    @staticmethod
    def process_partial_withdrawal(db: Session, policy_id: int, amount: Decimal, withdrawal_date: date):
        """处理部分提取"""
        # 1. 检查可提取金额
        # 2. 扣除账户价值
        # 3. 计算手续费
        # 4. 记录操作
```

### 2. 港险服务 (HongKongInsuranceService)

```python
class HongKongInsuranceService:
    """港险业务服务"""
    
    @staticmethod
    def process_annual_dividend(db: Session, policy_id: int, dividend_rate: Decimal, dividend_year: int):
        """处理年度分红"""
        # 1. 获取保单基本保额
        # 2. 计算分红金额
        # 3. 根据分红方式处理（现金/增额/抵缴保费）
        # 4. 更新保单价值
        # 5. 记录分红操作
    
    @staticmethod
    def calculate_policy_value(db: Session, policy_id: int, valuation_date: date):
        """计算保单价值"""
        # 1. 获取保证现金价值
        # 2. 计算累积分红价值
        # 3. 计算总现金价值
        # 4. 更新保单价值记录
    
    @staticmethod
    def process_premium_payment(db: Session, policy_id: int, amount: Decimal, payment_date: date):
        """处理保费缴纳"""
        # 1. 记录保费缴纳
        # 2. 更新缴费状态
        # 3. 计算对现金价值的影响
```

### 3. 收益计算服务 (InsuranceReturnCalculationService)

```python
class InsuranceReturnCalculationService:
    """收益计算服务"""
    
    @staticmethod
    def calculate_irr(db: Session, policy_id: int):
        """计算内部收益率"""
        # 1. 获取所有现金流（保费支出、分红收入、当前价值）
        # 2. 使用IRR算法计算年化收益率
    
    @staticmethod
    def calculate_total_return(db: Session, policy_id: int):
        """计算总收益"""
        # 1. 总投入 = 所有保费和追加投资
        # 2. 总产出 = 当前价值 + 历史提取 + 历史分红
        # 3. 计算绝对收益和收益率
    
    @staticmethod
    def calculate_annual_return(db: Session, policy_id: int, year: int):
        """计算年度收益"""
        # 1. 获取年初年末价值
        # 2. 计算当年投入产出
        # 3. 计算年度收益率
```

## 自动化任务设计

### 1. 月度利息计算任务
```python
async def monthly_interest_calculation_job():
    """万能险月度利息计算任务"""
    # 每月1日执行，计算上月利息
    
async def update_settlement_rates():
    """更新结算利率任务"""
    # 定期从保险公司官网或API获取最新结算利率
```

### 2. 分红提醒任务
```python
async def dividend_announcement_reminder():
    """分红公告提醒任务"""
    # 监控保险公司分红公告
    
async def policy_anniversary_reminder():
    """保单周年日提醒任务"""
    # 提醒缴费、体检等
```

## 前端界面设计要点

### 1. 保单管理界面
- 保单列表：显示保单基本信息、当前价值、收益情况
- 保单详情：完整的保单信息、价值变化图表、操作历史

### 2. 收益分析界面  
- 收益概览：总投入、总价值、总收益、年化收益率
- 收益图表：价值增长曲线、月度收益柱状图
- 对比分析：与其他投资产品收益对比

### 3. 操作管理界面
- 缴费记录：保费缴纳历史和提醒
- 收益记录：利息、分红记录
- 价值调整：手动调整保单价值

## 数据同步方案

### 1. 保险公司API集成（如果可用）
- 自动同步保单价值
- 自动获取结算利率
- 自动获取分红信息

### 2. 手动数据维护
- 定期从保险公司APP或网站获取数据
- 批量导入Excel数据
- API调用记录保险公司数据

## 风险控制和数据准确性

### 1. 数据验证
- 保单价值变化合理性检查
- 收益率异常告警
- 操作记录一致性验证

### 2. 备份和审计
- 重要操作日志记录
- 数据变更审计轨迹
- 定期数据备份

## 部署和迁移计划

### 1. 数据库迁移
```bash
# 创建新的数据库表
alembic revision --autogenerate -m "add insurance tables"
alembic upgrade head
```

### 2. API部署
- 新增insurance.py API路由
- 更新main.py包含新路由
- 服务层代码部署

### 3. 前端更新
- 新增保险模块页面组件
- 更新导航菜单
- 集成图表组件

这个设计方案充分考虑了万能险和港险的业务特点，与您现有系统架构保持一致，可以无缝集成到现有系统中。