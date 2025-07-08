# 投资类保险模块使用说明

## 概述

投资类保险模块是多资产投资记录与收益系统的一个重要组成部分，专门用于管理万能险、港险等投资型保险产品。

## 功能特点

### 1. 万能险管理
- **月复利收益**：自动计算月度利息，支持复利计算
- **灵活缴费**：支持追加投资和部分提取
- **费用管理**：自动计算初始费用、管理费、保险成本
- **账户价值跟踪**：实时更新账户价值变化

### 2. 港险管理
- **定期分红**：支持年度分红和特别分红处理
- **多种分红方式**：现金分红、增额分红、抵缴保费
- **保单价值计算**：现金价值和保证价值管理
- **多币种支持**：港币、美元等

### 3. 统计分析
- **投资汇总**：总投入、总价值、总收益统计
- **保单表现**：单个保单的投资收益分析
- **收益对比**：与其他投资产品收益对比

## API 接口

### 保险产品管理
```bash
# 创建保险产品
POST /api/v1/insurance/products

# 获取产品列表
GET /api/v1/insurance/products

# 获取产品详情
GET /api/v1/insurance/products/{product_code}

# 更新产品信息
PUT /api/v1/insurance/products/{product_code}
```

### 保险保单管理
```bash
# 创建保单
POST /api/v1/insurance/policies

# 获取保单列表
GET /api/v1/insurance/policies

# 获取保单详情
GET /api/v1/insurance/policies/{policy_id}

# 更新保单价值
PUT /api/v1/insurance/policies/{policy_id}/value
```

### 保险操作记录
```bash
# 创建操作记录
POST /api/v1/insurance/operations

# 缴费操作
POST /api/v1/insurance/operations/{policy_id}/premium

# 追加投资
POST /api/v1/insurance/operations/{policy_id}/topup

# 部分提取
POST /api/v1/insurance/operations/{policy_id}/withdrawal
```

### 收益管理
```bash
# 计算月度利息（万能险）
POST /api/v1/insurance/returns/calculate-monthly/{policy_id}

# 处理年度分红（港险）
POST /api/v1/insurance/returns/process-dividend/{policy_id}

# 批量计算利息
POST /api/v1/insurance/bulk/calculate-interest
```

### 统计分析
```bash
# 获取投资汇总
GET /api/v1/insurance/statistics/summary

# 获取保单表现
GET /api/v1/insurance/statistics/performance/{policy_id}

# 收益分析
GET /api/v1/insurance/statistics/returns-analysis
```

## 使用示例

### 1. 创建万能险产品
```json
POST /api/v1/insurance/products
{
  "product_code": "UL001",
  "product_name": "XX万能险",
  "insurance_company": "XX保险公司",
  "product_type": "universal",
  "currency": "CNY",
  "initial_charge_rate": 0.03,
  "management_fee_rate": 0.0125,
  "guaranteed_rate": 0.03,
  "current_rate": 0.045,
  "rate_type": "monthly"
}
```

### 2. 创建保单
```json
POST /api/v1/insurance/policies
{
  "policy_number": "P202400001",
  "product_code": "UL001",
  "product_name": "XX万能险",
  "insurance_company": "XX保险公司",
  "policy_holder": "张三",
  "insured_person": "张三",
  "policy_start_date": "2024-01-01",
  "payment_start_date": "2024-01-01",
  "sum_insured": 100000.00,
  "annual_premium": 50000.00,
  "payment_frequency": "annually",
  "currency": "CNY"
}
```

### 3. 缴费操作
```json
POST /api/v1/insurance/operations/1/premium
{
  "payment_date": "2024-01-01T00:00:00",
  "amount": 50000.00,
  "payment_method": "银行转账",
  "notes": "首年保费"
}
```

### 4. 月度利息计算
```bash
POST /api/v1/insurance/returns/calculate-monthly/1?calculation_date=2024-02-01
```

### 5. 处理港险分红
```json
POST /api/v1/insurance/returns/process-dividend/2
{
  "dividend_date": "2024-12-31",
  "dividend_rate": 0.05,
  "dividend_year": 2024,
  "distribution_method": "reinvest",
  "notes": "2024年度分红"
}
```

## 数据库迁移

运行以下命令创建保险相关数据表：

```bash
cd backend
alembic upgrade head
```

或手动执行迁移文件：
```bash
python -m alembic upgrade abc123def456
```

## 定时任务

### 万能险月度利息计算
系统可配置定时任务，每月自动计算万能险的月度利息：

```python
# 每月1日计算上月利息
@scheduler.scheduled_job('cron', day=1, hour=0, minute=0)
async def calculate_monthly_interest():
    # 计算所有万能险保单的月度利息
    pass
```

### 结算利率更新
定期从保险公司获取最新的结算利率：

```python
# 每周五更新结算利率
@scheduler.scheduled_job('cron', day_of_week=4, hour=18, minute=0)
async def update_settlement_rates():
    # 更新产品结算利率
    pass
```

## 业务流程

### 万能险业务流程
1. **产品录入**：创建万能险产品，设置费用率和结算利率
2. **保单创建**：录入保单基本信息
3. **保费缴纳**：记录保费缴纳，扣除初始费用后增加账户价值
4. **月度结算**：每月计算利息，扣除管理费和保险成本
5. **追加投资**：客户可随时追加投资
6. **部分提取**：客户可提取部分账户价值
7. **价值更新**：定期更新保单账户价值

### 港险业务流程
1. **产品录入**：创建港险产品信息
2. **保单创建**：录入保单和保额信息
3. **保费缴纳**：记录保费缴纳历史
4. **分红处理**：年度分红计算和处理
5. **价值增长**：现金价值随时间增长
6. **收益统计**：计算总收益和年化收益率

## 注意事项

1. **数据准确性**：保单价值变化需要定期核对保险公司数据
2. **费用计算**：万能险的费用计算较复杂，需要根据产品条款精确配置
3. **分红处理**：港险分红需要根据保险公司公告及时更新
4. **汇率处理**：外币保单需要考虑汇率变化对收益的影响
5. **备份恢复**：重要操作记录需要定期备份

## 扩展功能

### 未来可扩展的功能
1. **IRR计算**：内部收益率精确计算
2. **保险公司API集成**：自动同步保单价值和分红信息
3. **投资组合分析**：保险产品与其他投资产品的组合分析
4. **风险评估**：保险投资的风险评估和预警
5. **报表生成**：自动生成投资报告和税务文件

## 技术架构

- **后端框架**：FastAPI + SQLAlchemy
- **数据库**：支持 PostgreSQL/MySQL/SQLite
- **API设计**：RESTful API，完整的CRUD操作
- **数据验证**：Pydantic模型验证
- **迁移管理**：Alembic数据库迁移
- **定时任务**：APScheduler异步任务调度

## 支持与维护

如有问题或建议，请参考：
1. API文档：`/docs`（开发环境）
2. 系统日志：查看应用运行日志
3. 数据库监控：定期检查数据一致性
4. 性能优化：监控API响应时间和数据库查询性能