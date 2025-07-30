# AI分析师API文档

## 概述

本API为外部AI分析师提供全面的资产数据查询和分析功能，包括资产快照、投资历史、绩效分析、风险评估等核心功能。

## 基础信息

- **Base URL**: `https://your-domain.com/api/v1/ai-analyst`
- **认证方式**: API Key (Header: `X-API-Key`)
- **数据格式**: JSON
- **支持的基准货币**: CNY, USD, EUR

## 认证

所有API接口都需要在请求头中包含有效的API Key：

```http
X-API-Key: your_api_key_here
```

### 示例API Keys
- `ai_analyst_key_2024` (生产环境)
- `demo_key_12345` (演示环境)

## 核心接口

### 1. 资产总览 (Asset Summary)

获取最新的资产分布情况和持仓概况。

```http
GET /asset-summary?base_currency=CNY
```

#### 参数
- `base_currency` (optional): 基准货币，默认为 CNY

#### 响应示例
```json
{
  "total_assets": {
    "CNY": 150000.50,
    "USD": 21428.64,
    "EUR": 19285.71
  },
  "platform_breakdown": [
    {
      "platform": "支付宝基金",
      "value": 80000.00,
      "percentage": 53.33
    },
    {
      "platform": "IBKR",
      "value": 45000.50,
      "percentage": 30.00
    }
  ],
  "asset_type_breakdown": [
    {
      "asset_type": "基金",
      "value": 95000.30,
      "percentage": 63.33
    },
    {
      "asset_type": "股票",
      "value": 35000.20,
      "percentage": 23.33
    }
  ],
  "top_holdings": [
    {
      "platform": "支付宝基金",
      "asset_type": "基金",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "value": 25000.00,
      "currency": "CNY",
      "percentage": 16.67
    }
  ],
  "last_update_time": "2024-01-20T15:30:00"
}
```

### 2. 投资历史 (Investment History)

获取详细的投资操作历史和资金流分析。

```http
GET /investment-history?start_date=2024-01-01&end_date=2024-01-31&limit=100
```

#### 参数
- `start_date` (optional): 开始日期 (YYYY-MM-DD)
- `end_date` (optional): 结束日期 (YYYY-MM-DD)
- `platform` (optional): 平台筛选
- `asset_type` (optional): 资产类型筛选
- `limit` (optional): 记录数限制，默认100

#### 响应示例
```json
{
  "operations": [
    {
      "id": 1234,
      "date": "2024-01-15T09:30:00",
      "platform": "支付宝基金",
      "asset_type": "基金",
      "operation_type": "buy",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "amount": 1000.00,
      "currency": "CNY",
      "quantity": 952.38,
      "price": null,
      "nav": 1.0500,
      "fee": 1.50,
      "strategy": "定投计划",
      "emotion_score": 7,
      "notes": "月度定投"
    }
  ],
  "total_invested": {
    "CNY": 50000.00,
    "USD": 7142.86
  },
  "profit_summary": {
    "note": "详细收益计算需要结合当前持仓和历史价格数据",
    "total_operations": 45,
    "buy_operations": 38,
    "sell_operations": 7
  },
  "monthly_flow": [
    {
      "month": "2024-01",
      "currency": "CNY",
      "buy_amount": 5000.00,
      "sell_amount": 0.00,
      "net_flow": 5000.00
    }
  ]
}
```

### 3. 绩效分析 (Performance Analysis)

获取投资绩效分析，包括收益率和趋势分析。

```http
GET /performance-analysis?base_currency=CNY&days=30
```

#### 参数
- `base_currency` (optional): 基准货币，默认CNY
- `days` (optional): 分析天数，默认30

#### 响应示例
```json
{
  "overall_return": {
    "cny": 5.8,
    "period_days": 30,
    "start_value": 145000.00,
    "end_value": 153410.00
  },
  "asset_performance": [
    {
      "platform": "支付宝基金",
      "asset_type": "基金",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "current_value": 25500.00,
      "currency": "CNY"
    }
  ],
  "trend_analysis": {
    "daily_values": [
      {"date": "2024-01-01", "total_value": 145000.00},
      {"date": "2024-01-02", "total_value": 145320.50}
    ],
    "trend_direction": "up",
    "volatility": "low"
  },
  "risk_metrics": {
    "volatility": 0.012,
    "max_drawdown": "需要更多历史数据计算",
    "var_95": "需要更多历史数据计算"
  }
}
```

### 4. 汇率数据 (Exchange Rates)

获取最新汇率信息和支持的货币对。

```http
GET /exchange-rates?base_currency=CNY&target_currencies=USD,EUR
```

#### 参数
- `base_currency` (optional): 基准货币，默认CNY
- `target_currencies` (optional): 目标货币，逗号分隔

#### 响应示例
```json
{
  "rates": [
    {
      "from_currency": "CNY",
      "to_currency": "USD",
      "rate": 0.1429,
      "last_update": "2024-01-20T15:30:00",
      "source": "akshare"
    },
    {
      "from_currency": "CNY", 
      "to_currency": "EUR",
      "rate": 0.1318,
      "last_update": "2024-01-20T15:30:00",
      "source": "akshare"
    }
  ],
  "last_update": "2024-01-20T15:30:00",
  "supported_currencies": ["CNY", "USD", "EUR", "HKD", "GBP"]
}
```

### 5. 市场数据 (Market Data)

获取基金净值等市场相关数据。

```http
GET /market-data?fund_codes=000001,000002&days=7
```

#### 参数
- `fund_codes` (optional): 基金代码，逗号分隔
- `days` (optional): 获取天数，默认7

#### 响应示例
```json
{
  "fund_navs": [
    {
      "fund_code": "000001",
      "nav_date": "2024-01-20",
      "nav": 1.0520,
      "accumulated_nav": 2.8940,
      "growth_rate": 0.0095,
      "source": "api"
    }
  ],
  "market_summary": {
    "total_funds_tracked": 156,
    "active_funds_in_period": 142,
    "data_period_days": 7,
    "last_update": "2024-01-20"
  }
}
```

## 高级分析接口

### 1. 投资组合分析 (Portfolio Analysis)

```http
GET /portfolio-analysis?base_currency=CNY
```

提供全面的投资组合分析，包括集中度风险、分散化评分和再平衡建议。

#### 响应结构
```json
{
  "portfolio_summary": {
    "total_value": 150000.00,
    "currency": "CNY",
    "number_of_assets": 15,
    "number_of_platforms": 3,
    "last_update": "2024-01-20T15:30:00"
  },
  "allocation_analysis": {
    "by_platform": [...],
    "by_asset_type": [...]
  },
  "concentration_risk": {
    "hhi_index": 1250.5,
    "hhi_interpretation": "低",
    "max_holding_weight": 18.5,
    "top5_weight": 65.2,
    "risk_level": "低"
  },
  "diversification_score": 85.5,
  "rebalancing_suggestions": [
    {
      "type": "reduce_position",
      "asset": "某基金",
      "current_weight": 32.0,
      "suggested_weight": 25,
      "reason": "单一资产权重过高，建议降低至25%以下"
    }
  ]
}
```

### 2. 定投计划分析 (DCA Analysis)

```http
GET /dca-analysis
```

分析定投计划的执行情况和成本平均效应。

### 3. 风险评估 (Risk Assessment)

```http
GET /risk-assessment?base_currency=CNY&days=90
```

提供详细的风险指标和评估建议。

#### 响应结构
```json
{
  "risk_metrics": {
    "daily_volatility": 0.012,
    "annual_volatility": 0.192,
    "max_drawdown": 0.08,
    "var_95_daily": -0.018,
    "var_99_daily": -0.032,
    "sharpe_ratio": 1.25,
    "risk_level": "中低风险"
  },
  "analysis_period": {
    "start_date": "2023-10-22",
    "end_date": "2024-01-20",
    "days_analyzed": 90,
    "data_points": 85
  },
  "interpretation": {
    "volatility_interpretation": "中",
    "drawdown_interpretation": "轻微",
    "overall_risk_assessment": "中低风险"
  },
  "recommendations": [
    "当前风险水平适中",
    "风险控制良好",
    "数据样本充足"
  ]
}
```

### 4. 健康检查 (Health Check)

```http
GET /health
```

验证API服务状态。

## 使用示例

### Python示例

```python
import requests
import json

# 配置
API_BASE_URL = "https://your-domain.com/api/v1/ai-analyst"
API_KEY = "ai_analyst_key_2024"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 获取资产总览
def get_asset_summary(base_currency="CNY"):
    url = f"{API_BASE_URL}/asset-summary"
    params = {"base_currency": base_currency}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"错误: {response.status_code} - {response.text}")
        return None

# 获取投资历史
def get_investment_history(days=30):
    from datetime import datetime, timedelta
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/investment-history"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "limit": 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None

# 获取绩效分析
def get_performance_analysis(days=30):
    url = f"{API_BASE_URL}/performance-analysis"
    params = {"days": days, "base_currency": "CNY"}
    
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None

# 使用示例
if __name__ == "__main__":
    # 获取资产概况
    summary = get_asset_summary()
    if summary:
        print("总资产:", summary["total_assets"])
        print("主要持仓:", summary["top_holdings"][:3])
    
    # 获取最近30天的投资历史
    history = get_investment_history(30)
    if history:
        print("总投入:", history["total_invested"])
        print("操作次数:", history["profit_summary"]["total_operations"])
    
    # 获取绩效分析
    performance = get_performance_analysis(30)
    if performance:
        print("整体收益率:", performance["overall_return"])
```

### JavaScript/Node.js示例

```javascript
const axios = require('axios');

const API_BASE_URL = 'https://your-domain.com/api/v1/ai-analyst';
const API_KEY = 'ai_analyst_key_2024';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

// 获取资产总览
async function getAssetSummary(baseCurrency = 'CNY') {
  try {
    const response = await apiClient.get('/asset-summary', {
      params: { base_currency: baseCurrency }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching asset summary:', error.response?.data);
    return null;
  }
}

// 获取投资组合分析
async function getPortfolioAnalysis(baseCurrency = 'CNY') {
  try {
    const response = await apiClient.get('/portfolio-analysis', {
      params: { base_currency: baseCurrency }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio analysis:', error.response?.data);
    return null;
  }
}

// 使用示例
(async () => {
  const summary = await getAssetSummary();
  if (summary) {
    console.log('Total Assets:', summary.total_assets);
    console.log('Platform Breakdown:', summary.platform_breakdown);
  }
  
  const portfolio = await getPortfolioAnalysis();
  if (portfolio) {
    console.log('Portfolio Value:', portfolio.portfolio_summary.total_value);
    console.log('Diversification Score:', portfolio.diversification_score);
  }
})();
```

## 错误处理

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: API Key无效或缺失
- `404 Not Found`: 数据不存在或接口不存在
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误详细信息",
  "status_code": 400,
  "timestamp": "2024-01-20T15:30:00Z"
}
```

## 最佳实践

### 1. 数据缓存
- 资产快照数据通常每日更新，建议缓存1小时
- 汇率数据建议缓存15分钟
- 历史数据可以缓存更长时间

### 2. 请求频率
- 建议每分钟请求不超过60次
- 批量查询时使用参数过滤减少请求次数
- 使用适当的`limit`参数控制返回数据量

### 3. 数据解析
- 注意处理数值为`null`的情况
- 金额字段统一为浮点数格式
- 日期时间使用ISO 8601格式

### 4. 错误重试
- 5xx错误建议指数退避重试
- 4xx错误检查请求参数，不要重试
- 网络错误可以短暂重试

## 数据字典

### 资产类型 (asset_type)
- `基金`: 公募基金、私募基金
- `股票`: A股、港股、美股等
- `债券`: 国债、企业债等
- `现金`: 活期、定期存款
- `数字货币`: 比特币、以太坊等

### 操作类型 (operation_type)
- `buy`: 买入
- `sell`: 卖出
- `dividend`: 分红
- `transfer`: 转账

### 平台标识 (platform)
- `支付宝基金`: 支付宝基金平台
- `IBKR`: Interactive Brokers
- `OKX`: OKX交易所
- `Wise`: Wise汇款平台
- `PayPal`: PayPal账户

### 货币代码 (currency)
- `CNY`: 人民币
- `USD`: 美元
- `EUR`: 欧元
- `HKD`: 港币
- `GBP`: 英镑

## 更新日志

### v1.0.0 (2024-01-20)
- 初始版本发布
- 提供基础资产查询功能
- 支持投资历史和绩效分析
- 添加风险评估和投资组合分析

## 支持与反馈

如有问题或建议，请联系：
- 邮箱: api-support@your-domain.com
- 文档: https://your-domain.com/docs
- 在线演示: https://your-domain.com/api/v1/ai-analyst/docs