# 汇率管理模块文档

## 📋 概述

汇率管理模块基于akshare库提供实时汇率数据查询和货币转换功能，支持多种货币对人民币的汇率查询。

## 🔗 基础信息

- **基础URL**: `http://localhost:8000/api/v1/exchange-rates`
- **数据源**: akshare (中国银行外汇牌价)
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

### 1. 货币管理

#### 1.1 获取货币列表
- **URL**: `GET /currencies`
- **描述**: 获取系统支持的货币列表
- **响应示例**:
```json
{
  "success": true,
  "message": "获取到 1 种货币",
  "data": {
    "currencies": [
      {
        "code": "USD",
        "name": "美元",
        "symbol": "$",
        "rate": 691.8,
        "update_time": "2025-07-05T23:59:52.083494"
      }
    ]
  }
}
```

### 2. 汇率查询

#### 2.1 获取所有汇率
- **URL**: `GET /rates`
- **描述**: 获取所有货币的实时汇率
- **响应示例**:
```json
{
  "success": true,
  "message": "获取到 1 种货币的汇率",
  "data": {
    "rates": [
      {
        "currency": "USD",
        "currency_name": "美元",
        "spot_buy": 691.8,
        "spot_sell": 694.73,
        "cash_buy": 686.17,
        "cash_sell": 694.73,
        "middle_rate": 689.51,
        "update_time": "2025-07-05T23:59:52.083494"
      }
    ]
  }
}
```

#### 2.2 获取指定货币汇率
- **URL**: `GET /rates/{currency}`
- **描述**: 获取指定货币的汇率信息
- **路径参数**:
  - `currency`: 货币代码（如USD、EUR等）
- **响应示例**:
```json
{
  "success": true,
  "message": "获取 USD 汇率成功",
  "data": {
    "rate": {
      "currency": "USD",
      "currency_name": "美元",
      "spot_buy": 691.8,
      "spot_sell": 694.73,
      "cash_buy": 686.17,
      "cash_sell": 694.73,
      "middle_rate": 689.51,
      "update_time": "2025-07-05T23:59:52.083494"
    }
  }
}
```

#### 2.3 获取历史汇率
- **URL**: `GET /rates/{currency}/history`
- **描述**: 获取指定货币的历史汇率数据
- **查询参数**:
  - `start_date`: 开始日期（可选，格式：YYYY-MM-DD）
  - `end_date`: 结束日期（可选，格式：YYYY-MM-DD）
- **响应示例**:
```json
{
  "success": true,
  "message": "获取 USD 历史汇率成功",
  "data": {
    "history": [
      {
        "date": "2023-03-06",
        "currency": "USD",
        "rate": 689.51,
        "change": 0.0,
        "change_pct": 0.0
      }
    ]
  }
}
```

### 3. 货币转换

#### 3.1 货币转换
- **URL**: `GET /convert`
- **描述**: 进行货币转换计算
- **查询参数**:
  - `amount`: 转换金额（必需）
  - `from_currency`: 源货币（必需）
  - `to_currency`: 目标货币（可选，默认CNY）
- **响应示例**:
```json
{
  "success": true,
  "message": "货币转换成功",
  "data": {
    "original_amount": 100,
    "original_currency": "USD",
    "converted_amount": 68951.0,
    "target_currency": "CNY"
  }
}
```

## 🔧 使用示例

### Python示例

```python
import requests

# 获取所有汇率
response = requests.get("http://localhost:8000/api/v1/exchange-rates/rates")
if response.status_code == 200:
    data = response.json()
    print(f"美元汇率: {data['data']['rates'][0]['middle_rate']}")

# 货币转换
response = requests.get(
    "http://localhost:8000/api/v1/exchange-rates/convert",
    params={
        "amount": 100,
        "from_currency": "USD",
        "to_currency": "CNY"
    }
)
if response.status_code == 200:
    data = response.json()
    print(f"100美元 = {data['data']['converted_amount']} 人民币")
```

### cURL示例

```bash
# 获取所有汇率
curl -X GET "http://localhost:8000/api/v1/exchange-rates/rates"

# 获取美元汇率
curl -X GET "http://localhost:8000/api/v1/exchange-rates/rates/USD"

# 货币转换
curl -X GET "http://localhost:8000/api/v1/exchange-rates/convert?amount=100&from_currency=USD&to_currency=CNY"
```

## 🎨 前端界面

### 功能特性

1. **实时汇率显示**: 显示当前美元对人民币的实时汇率
2. **货币转换器**: 支持多种货币之间的转换
3. **汇率统计**: 显示主要货币的汇率统计信息
4. **历史汇率**: 查看历史汇率走势
5. **数据刷新**: 支持手动刷新汇率数据

### 界面组件

- **货币转换器**: 输入金额和选择货币进行转换
- **汇率表格**: 显示详细的汇率信息（现汇买入价、现汇卖出价等）
- **统计卡片**: 显示支持货币数量、主要货币汇率等统计信息
- **历史数据表格**: 显示历史汇率数据

## 🚨 错误处理

### 常见错误码

- `400`: 请求参数错误
- `404`: 货币不存在
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 📝 注意事项

1. **数据源**: 汇率数据来源于akshare库的中国银行外汇牌价
2. **更新频率**: 汇率数据每日更新
3. **货币支持**: 目前主要支持美元对人民币的汇率
4. **历史数据**: 历史汇率数据可能有限制
5. **转换精度**: 货币转换使用中行折算价进行计算

## 🔄 数据同步

系统通过akshare库自动获取最新的汇率数据：

- **数据源**: `ak.currency_boc_sina()`
- **更新策略**: 每次API调用时获取最新数据
- **缓存策略**: 暂不缓存，实时获取

## 🛠️ 技术实现

### 后端实现

- **服务类**: `ExchangeRateService`
- **API路由**: `exchange_rates.py`
- **数据源**: akshare库
- **错误处理**: 统一的异常处理机制

### 前端实现

- **页面组件**: `ExchangeRates.tsx`
- **API服务**: `exchangeRateAPI`
- **UI框架**: Ant Design
- **状态管理**: React Hooks

## 📈 扩展计划

1. **多货币支持**: 扩展支持更多货币的汇率查询
2. **汇率预警**: 添加汇率变动预警功能
3. **图表展示**: 添加汇率走势图表
4. **数据缓存**: 实现汇率数据缓存机制
5. **定时更新**: 添加定时更新汇率数据的功能 