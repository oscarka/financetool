# 基金模块API文档

## 📋 概述

基金模块提供了完整的基金投资管理功能，包括操作记录、净值管理、持仓计算、定投计划等。

## 🔗 基础信息

- **基础URL**: `http://localhost:8000/api/v1/funds`
- **认证**: 暂无（开发阶段）
- **数据格式**: JSON
- **字符编码**: UTF-8

## 📊 响应格式

所有API都使用统一的响应格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

## 🎯 API接口列表

### 1. 基金操作记录

#### 1.1 创建基金操作记录
- **URL**: `POST /operations`
- **描述**: 创建买入、卖出等基金操作记录
- **请求体**:
```json
{
  "operation_date": "2024-01-15T15:00:00",
  "operation_type": "buy",
  "asset_code": "000001",
  "asset_name": "华夏成长混合",
  "amount": 1000.0,
  "strategy": "定投策略",
  "emotion_score": 7,
  "notes": "买入操作"
}
```
- **响应**: 返回创建的操作记录

#### 1.2 获取基金操作记录
- **URL**: `GET /operations`
- **描述**: 获取基金操作历史记录
- **查询参数**:
  - `asset_code`: 基金代码（可选）
  - `operation_type`: 操作类型（可选）
  - `start_date`: 开始日期（可选）
  - `end_date`: 结束日期（可选）
  - `page`: 页码（默认1）
  - `page_size`: 每页数量（默认20）
- **响应**: 返回操作记录列表

#### 1.3 更新基金操作记录
- **URL**: `PUT /operations/{operation_id}`
- **描述**: 更新操作记录的份额、价格等信息
- **请求体**:
```json
{
  "quantity": 1000.0,
  "price": 1.2345,
  "fee": 15.0,
  "status": "confirmed",
  "notes": "确认份额"
}
```

#### 1.4 删除基金操作记录
- **URL**: `DELETE /operations/{operation_id}`
- **描述**: 删除指定的操作记录

### 2. 基金持仓管理

#### 2.1 获取基金持仓列表
- **URL**: `GET /positions`
- **描述**: 获取当前所有基金持仓信息
- **响应**: 返回持仓列表，包含收益计算

#### 2.2 获取持仓汇总信息
- **URL**: `GET /positions/summary`
- **描述**: 获取持仓汇总统计信息
- **响应**:
```json
{
  "total_invested": 50000.0,
  "total_value": 52000.0,
  "total_profit": 2000.0,
  "total_profit_rate": 0.04,
  "asset_count": 5,
  "profitable_count": 3,
  "loss_count": 2
}
```

### 3. 基金净值管理

#### 3.1 手动录入基金净值
- **URL**: `POST /nav`
- **描述**: 手动录入基金净值数据
- **请求体**:
```json
{
  "fund_code": "000001",
  "nav_date": "2024-01-15",
  "nav": 1.2345,
  "accumulated_nav": 2.3456,
  "growth_rate": 0.015,
  "source": "manual"
}
```

#### 3.2 获取基金净值历史
- **URL**: `GET /nav/{fund_code}`
- **描述**: 获取指定基金的净值历史
- **查询参数**:
  - `days`: 获取天数（默认30，最大365）

#### 3.3 获取基金最新净值
- **URL**: `GET /nav/{fund_code}/latest`
- **描述**: 获取指定基金的最新净值

#### 3.4 同步基金净值
- **URL**: `POST /nav/{fund_code}/sync`
- **描述**: 从外部API同步基金净值
- **查询参数**:
  - `nav_date`: 净值日期

### 4. 基金信息管理

#### 4.1 创建基金信息
- **URL**: `POST /info`
- **描述**: 创建基金基本信息
- **请求体**:
```json
{
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "fund_type": "混合型",
  "management_fee": 0.015,
  "purchase_fee": 0.015,
  "redemption_fee": 0.005,
  "min_purchase": 100.0,
  "risk_level": "中风险"
}
```

#### 4.2 获取所有基金信息
- **URL**: `GET /info`
- **描述**: 获取所有基金的基本信息

#### 4.3 获取基金信息
- **URL**: `GET /info/{fund_code}`
- **描述**: 获取指定基金的详细信息

#### 4.4 更新基金信息
- **URL**: `PUT /info/{fund_code}`
- **描述**: 更新基金信息

#### 4.5 同步基金信息
- **URL**: `POST /info/{fund_code}/sync`
- **描述**: 从外部API同步基金信息

### 5. 定投计划管理

#### 5.1 创建定投计划
- **URL**: `POST /dca/plans`
- **描述**: 创建定投计划
- **请求体**:
```json
{
  "plan_name": "华夏成长定投",
  "asset_code": "000001",
  "asset_name": "华夏成长混合",
  "amount": 500.0,
  "currency": "CNY",
  "frequency": "monthly",
  "frequency_value": 30,
  "start_date": "2024-01-15",
  "strategy": "每月定投500元"
}
```

#### 5.2 获取定投计划列表
- **URL**: `GET /dca/plans`
- **描述**: 获取所有定投计划
- **查询参数**:
  - `status`: 计划状态（可选）

#### 5.3 更新定投计划
- **URL**: `PUT /dca/plans/{plan_id}`
- **描述**: 更新定投计划信息

#### 5.4 删除定投计划
- **URL**: `DELETE /dca/plans/{plan_id}`
- **描述**: 删除定投计划

## 🔧 使用示例

### Python示例

```python
import httpx
import asyncio

async def test_fund_api():
    async with httpx.AsyncClient() as client:
        # 创建基金信息
        fund_data = {
            "fund_code": "000001",
            "fund_name": "华夏成长混合",
            "fund_type": "混合型"
        }
        response = await client.post(
            "http://localhost:8000/api/v1/funds/info",
            json=fund_data
        )
        print(response.json())
        
        # 创建操作记录
        operation_data = {
            "operation_date": "2024-01-15T15:00:00",
            "operation_type": "buy",
            "asset_code": "000001",
            "asset_name": "华夏成长混合",
            "amount": 1000.0
        }
        response = await client.post(
            "http://localhost:8000/api/v1/funds/operations",
            json=operation_data
        )
        print(response.json())

# 运行测试
asyncio.run(test_fund_api())
```

### cURL示例

```bash
# 获取基金持仓
curl -X GET "http://localhost:8000/api/v1/funds/positions"

# 创建基金操作
curl -X POST "http://localhost:8000/api/v1/funds/operations" \
  -H "Content-Type: application/json" \
  -d '{
    "operation_date": "2024-01-15T15:00:00",
    "operation_type": "buy",
    "asset_code": "000001",
    "asset_name": "华夏成长混合",
    "amount": 1000.0
  }'

# 同步基金净值
curl -X POST "http://localhost:8000/api/v1/funds/nav/000001/sync?nav_date=2024-01-15"
```

## 🚨 错误处理

### 常见错误码

- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 📝 注意事项

1. **日期格式**: 使用ISO 8601格式（YYYY-MM-DD或YYYY-MM-DDTHH:MM:SS）
2. **金额格式**: 使用Decimal类型，支持4位小数
3. **基金代码**: 6位数字代码
4. **操作类型**: buy（买入）、sell（卖出）、dividend（分红）
5. **数据同步**: 外部API可能不稳定，建议添加重试机制

## 🔄 数据同步

系统支持从以下数据源同步基金数据：

- **天天基金网**: 主要数据源，提供基金净值和基本信息
- **雪球**: 备用数据源，提供基金净值

同步功能通过以下API实现：
- `POST /nav/{fund_code}/sync`: 同步基金净值
- `POST /info/{fund_code}/sync`: 同步基金信息 