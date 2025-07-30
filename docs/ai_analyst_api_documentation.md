# AI分析师数据API文档

## 概述

本API为外部AI分析师提供**原始资产数据和基础计算结果**，供AI分析师进行独立分析和决策。我们**不提供投资建议或分析结论**，而是专注于提供准确、完整的数据支撑。

## 设计理念

### 数据优先，分析交给AI
- **提供原始数据**: 完整的资产快照、交易记录、历史数据
- **基础计算**: 简单的统计和汇总，不做复杂分析
- **保持中性**: 不提供投资建议、风险评估结论或再平衡建议
- **数据完整性**: 确保数据的准确性和时效性

### AI分析师的职责
- **数据解读**: 基于提供的原始数据进行分析
- **模式识别**: 发现数据中的投资模式和趋势
- **风险评估**: 根据历史数据计算风险指标
- **建议生成**: 基于分析结果提供个性化建议

## 基础信息

- **Base URL**: `https://your-domain.com/api/v1/ai-analyst`
- **认证方式**: API Key (Header: `X-API-Key`)
- **数据格式**: JSON
- **更新频率**: 资产数据每日更新，汇率数据每15分钟更新

## 认证

所有API接口都需要在请求头中包含有效的API Key：

```http
X-API-Key: your_api_key_here
```

### 示例API Keys
- `ai_analyst_key_2024` (生产环境)
- `demo_key_12345` (演示环境)

## 核心数据接口

### 1. 当前资产数据 (Asset Data)

获取用户最新的资产持仓原始数据。

```http
GET /asset-data?base_currency=CNY&include_small_amounts=false
```

#### 参数
- `base_currency` (optional): 基准货币，默认为 CNY
- `include_small_amounts` (optional): 是否包含小额资产(<0.01)，默认false

#### 响应示例
```json
{
  "current_holdings": [
    {
      "id": 12345,
      "platform": "支付宝基金",
      "asset_type": "基金",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "currency": "CNY",
      "balance_original": 25000.00,
      "balance_cny": 25000.00,
      "balance_usd": 3571.43,
      "balance_eur": 3289.47,
      "base_currency_value": 25000.00,
      "snapshot_time": "2024-01-20T15:30:00",
      "extra_data": {
        "fund_type": "混合型",
        "risk_level": "中高风险"
      }
    }
  ],
  "total_value_by_currency": {
    "CNY": 150000.50,
    "USD": 21428.64,
    "EUR": 19285.71
  },
  "platform_summary": [
    {
      "platform": "支付宝基金",
      "asset_count": 15,
      "total_value": 80000.00,
      "currencies": ["CNY"]
    }
  ],
  "asset_type_summary": [
    {
      "asset_type": "基金",
      "asset_count": 18,
      "total_value": 95000.30,
      "unique_assets": 12
    }
  ],
  "snapshot_time": "2024-01-20T15:30:00"
}
```

### 2. 交易数据 (Transaction Data)

获取用户的交易操作历史记录。

```http
GET /transaction-data?start_date=2024-01-01&end_date=2024-01-31&limit=1000
```

#### 参数
- `start_date` (optional): 开始日期 (YYYY-MM-DD)
- `end_date` (optional): 结束日期 (YYYY-MM-DD)
- `platform` (optional): 平台筛选
- `asset_type` (optional): 资产类型筛选
- `operation_type` (optional): 操作类型筛选 (buy/sell/dividend)
- `limit` (optional): 记录数限制，默认1000

#### 响应示例
```json
{
  "transactions": [
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
      "notes": "月度定投",
      "status": "completed",
      "dca_plan_id": 5,
      "dca_execution_type": "scheduled"
    }
  ],
  "summary_stats": {
    "total_operations": 156,
    "operation_types": {
      "buy": {"count": 130, "total_amount": 95000.00},
      "sell": {"count": 20, "total_amount": 15000.00},
      "dividend": {"count": 6, "total_amount": 2500.00}
    },
    "currencies": {
      "CNY": {"count": 140, "total_amount": 105000.00},
      "USD": {"count": 16, "total_amount": 7500.00}
    },
    "platforms": {
      "支付宝基金": {"count": 120},
      "IBKR": {"count": 36}
    },
    "date_range": {
      "start": "2023-01-15T09:30:00",
      "end": "2024-01-20T15:30:00"
    }
  },
  "time_series_data": [
    {
      "period": "2024-01",
      "operation_count": 12
    }
  ]
}
```

### 3. 历史数据 (Historical Data)

获取资产价值的历史变化数据。

```http
GET /historical-data?days=90&asset_codes=000001,000002&base_currency=CNY
```

#### 参数
- `days` (optional): 历史天数，默认90
- `asset_codes` (optional): 资产代码，逗号分隔
- `base_currency` (optional): 基准货币，默认CNY

#### 响应示例
```json
{
  "asset_values": [
    {
      "date": "2024-01-20T15:30:00",
      "platform": "支付宝基金",
      "asset_type": "基金",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "currency": "CNY",
      "balance_original": 25000.00,
      "balance_cny": 25000.00,
      "balance_usd": 3571.43,
      "balance_eur": null,
      "base_value": 25000.00,
      "extra_data": {}
    }
  ],
  "nav_data": [
    {
      "date": "2024-01-20",
      "fund_code": "000001",
      "nav": 1.0520,
      "accumulated_nav": 2.8940,
      "growth_rate": 0.0095,
      "source": "api"
    }
  ],
  "price_data": [
    {
      "date": "2024-01-15T09:30:00",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "price": 1.0500,
      "nav": 1.0500,
      "operation_type": "buy",
      "platform": "支付宝基金"
    }
  ]
}
```

### 4. 市场数据 (Market Data)

获取市场环境相关的基础数据。

```http
GET /market-data
```

#### 响应示例
```json
{
  "exchange_rates": [
    {
      "from_currency": "CNY",
      "to_currency": "USD",
      "rate": 0.1429,
      "snapshot_time": "2024-01-20T15:30:00",
      "source": "akshare",
      "extra_data": {}
    }
  ],
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
  "market_indicators": {
    "total_funds_tracked": 156,
    "active_funds_last_week": 142,
    "total_user_operations": 1247,
    "operations_last_30_days": 45,
    "data_freshness": {
      "latest_snapshot": "2024-01-20T15:30:00",
      "latest_exchange_rate": "2024-01-20T15:25:00",
      "latest_fund_nav": "2024-01-20"
    }
  }
}
```

### 5. 定投数据 (DCA Data)

获取定投计划和执行相关的原始数据。

```http
GET /dca-data
```

#### 响应示例
```json
{
  "dca_plans": [
    {
      "id": 5,
      "plan_name": "华夏成长定投",
      "platform": "支付宝基金",
      "asset_type": "基金",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "amount": 1000.00,
      "currency": "CNY",
      "frequency": "monthly",
      "frequency_value": 30,
      "start_date": "2023-01-01",
      "end_date": null,
      "status": "active",
      "strategy": "长期定投",
      "execution_time": "15:00",
      "next_execution_date": "2024-02-01",
      "last_execution_date": "2024-01-01",
      "execution_count": 12,
      "total_invested": 12000.00,
      "total_shares": 11428.57,
      "smart_dca": false,
      "base_amount": null,
      "max_amount": null,
      "increase_rate": null
    }
  ],
  "execution_history": [
    {
      "operation_id": 1234,
      "dca_plan_id": 5,
      "execution_date": "2024-01-15T15:00:00",
      "amount": 1000.00,
      "quantity": 952.38,
      "nav": 1.0500,
      "fee": 1.50,
      "execution_type": "scheduled",
      "asset_code": "000001",
      "platform": "支付宝基金"
    }
  ],
  "statistics": {
    "total_plans": 8,
    "active_plans": 5,
    "total_invested": 45000.00,
    "total_operations": 156,
    "plan_statistics": {
      "5": {
        "operation_count": 12,
        "total_invested": 12000.00,
        "avg_nav": [1.0500, 1.0520, 1.0480]
      }
    }
  }
}
```

### 6. 健康检查 (Health Check)

```http
GET /health
```

验证API服务状态。

## 数据使用指南

### 为AI分析师提供的数据解读

#### 1. **资产配置分析**
基于`current_holdings`数据：
- 计算各平台、资产类型的权重分布
- 分析集中度风险(HHI指数等)
- 评估分散化程度

#### 2. **投资行为分析**
基于`transactions`数据：
- 分析买卖频率和时间模式
- 计算平均持仓周期
- 识别投资策略偏好
- 评估情绪评分趋势

#### 3. **绩效计算**
基于`historical_data`：
- 计算时间加权收益率
- 分析波动率和最大回撤
- 计算夏普比率等风险调整收益指标
- 对比基准指数表现

#### 4. **定投效果评估**
基于`dca_data`：
- 计算成本平均效应
- 分析定投纪律性
- 评估智能定投效果
- 比较不同频率的定投表现

#### 5. **市场环境分析**
基于`market_data`：
- 汇率波动对投资组合的影响
- 基金净值变化趋势
- 市场整体表现评估

### 数据质量说明

#### 数据来源
- **资产快照**: 每日自动抓取各平台数据
- **交易记录**: 用户手动输入 + 部分自动同步
- **净值数据**: 第三方API实时获取
- **汇率数据**: akshare等数据源，15分钟更新

#### 数据完整性
- 所有货币金额精确到2位小数
- 数量/份额精确到8位小数
- 时间戳使用ISO 8601格式
- 缺失数据标记为`null`

#### 数据一致性
- 多币种余额基于快照时汇率计算
- 历史数据与当前持仓可能存在时间差
- 定投执行记录与交易记录关联

## 使用示例

### Python分析示例

```python
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class InvestmentAnalyzer:
    def __init__(self, api_base_url, api_key):
        self.base_url = api_base_url
        self.headers = {"X-API-Key": api_key}
    
    def get_asset_data(self):
        """获取当前资产数据"""
        response = requests.get(
            f"{self.base_url}/asset-data",
            headers=self.headers
        )
        return response.json()
    
    def calculate_portfolio_metrics(self):
        """计算投资组合指标"""
        data = self.get_asset_data()
        holdings = data['current_holdings']
        
        # 计算权重分布
        total_value = sum(h['base_currency_value'] for h in holdings)
        weights = [h['base_currency_value'] / total_value for h in holdings]
        
        # 计算集中度(HHI)
        hhi = sum(w**2 for w in weights) * 10000
        
        # 平台分散度
        platforms = set(h['platform'] for h in holdings)
        platform_diversity = len(platforms)
        
        return {
            "total_value": total_value,
            "hhi_concentration": hhi,
            "platform_diversity": platform_diversity,
            "max_holding_weight": max(weights) * 100,
            "number_of_holdings": len(holdings)
        }
    
    def analyze_trading_patterns(self, days=90):
        """分析交易模式"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        response = requests.get(
            f"{self.base_url}/transaction-data",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "limit": 1000
            },
            headers=self.headers
        )
        
        data = response.json()
        transactions = data['transactions']
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        
        # 计算交易频率
        monthly_freq = df.groupby(df['date'].dt.to_period('M')).size()
        
        # 买卖比例
        operation_counts = df['operation_type'].value_counts()
        
        # 平均情绪评分
        avg_emotion = df['emotion_score'].mean() if 'emotion_score' in df else None
        
        return {
            "total_transactions": len(transactions),
            "monthly_frequency": monthly_freq.to_dict(),
            "operation_breakdown": operation_counts.to_dict(),
            "average_emotion_score": avg_emotion
        }
    
    def calculate_performance_metrics(self, days=90):
        """计算绩效指标"""
        response = requests.get(
            f"{self.base_url}/historical-data",
            params={"days": days, "base_currency": "CNY"},
            headers=self.headers
        )
        
        data = response.json()
        asset_values = data['asset_values']
        
        # 按日期聚合总资产
        df = pd.DataFrame(asset_values)
        df['date'] = pd.to_datetime(df['date']).dt.date
        daily_totals = df.groupby('date')['base_value'].sum()
        
        # 计算日收益率
        returns = daily_totals.pct_change().dropna()
        
        # 计算指标
        total_return = (daily_totals.iloc[-1] / daily_totals.iloc[0] - 1) * 100
        volatility = returns.std() * np.sqrt(252) * 100  # 年化波动率
        max_drawdown = self._calculate_max_drawdown(daily_totals) * 100
        sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        
        return {
            "total_return_pct": total_return,
            "annual_volatility_pct": volatility,
            "max_drawdown_pct": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "number_of_data_points": len(daily_totals)
        }
    
    def _calculate_max_drawdown(self, values):
        """计算最大回撤"""
        peak = values.expanding().max()
        drawdown = (values - peak) / peak
        return drawdown.min()

# 使用示例
analyzer = InvestmentAnalyzer(
    "http://localhost:8000/api/v1/ai-analyst",
    "ai_analyst_key_2024"
)

# 获取投资组合指标
portfolio_metrics = analyzer.calculate_portfolio_metrics()
print("投资组合指标:", portfolio_metrics)

# 分析交易模式
trading_patterns = analyzer.analyze_trading_patterns()
print("交易模式分析:", trading_patterns)

# 计算绩效指标
performance = analyzer.calculate_performance_metrics()
print("绩效指标:", performance)
```

### JavaScript分析示例

```javascript
class InvestmentAnalyzer {
    constructor(apiBaseUrl, apiKey) {
        this.baseUrl = apiBaseUrl;
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }
    
    async analyzePortfolioConcentration() {
        const response = await fetch(`${this.baseUrl}/asset-data`, {
            headers: this.headers
        });
        const data = await response.json();
        
        const holdings = data.current_holdings;
        const totalValue = holdings.reduce((sum, h) => sum + h.base_currency_value, 0);
        
        // 计算权重和集中度
        const weights = holdings.map(h => h.base_currency_value / totalValue);
        const hhi = weights.reduce((sum, w) => sum + w * w, 0) * 10000;
        
        // 平台分布
        const platformValues = {};
        holdings.forEach(h => {
            if (!platformValues[h.platform]) platformValues[h.platform] = 0;
            platformValues[h.platform] += h.base_currency_value;
        });
        
        return {
            totalValue,
            concentrationHHI: hhi,
            maxHoldingWeight: Math.max(...weights) * 100,
            platformDistribution: platformValues
        };
    }
    
    async analyzeDCAEffectiveness() {
        const response = await fetch(`${this.baseUrl}/dca-data`, {
            headers: this.headers
        });
        const data = await response.json();
        
        const executionHistory = data.execution_history;
        
        // 按计划分组分析
        const planAnalysis = {};
        executionHistory.forEach(exec => {
            const planId = exec.dca_plan_id;
            if (!planAnalysis[planId]) {
                planAnalysis[planId] = {
                    executions: [],
                    totalInvested: 0,
                    totalShares: 0
                };
            }
            
            planAnalysis[planId].executions.push(exec);
            planAnalysis[planId].totalInvested += exec.amount;
            planAnalysis[planId].totalShares += exec.quantity || 0;
        });
        
        // 计算平均成本
        Object.keys(planAnalysis).forEach(planId => {
            const plan = planAnalysis[planId];
            plan.averageCost = plan.totalInvested / plan.totalShares;
            plan.executionCount = plan.executions.length;
        });
        
        return planAnalysis;
    }
}

// 使用示例
const analyzer = new InvestmentAnalyzer(
    'http://localhost:8000/api/v1/ai-analyst',
    'ai_analyst_key_2024'
);

// 分析投资组合集中度
analyzer.analyzePortfolioConcentration()
    .then(result => console.log('组合集中度:', result));

// 分析定投效果
analyzer.analyzeDCAEffectiveness()
    .then(result => console.log('定投分析:', result));
```

## 最佳实践

### 1. 数据获取策略
- **增量更新**: 定期获取最新数据，避免重复拉取历史数据
- **错误处理**: 实现重试机制和降级策略
- **数据缓存**: 对不经常变化的数据进行本地缓存

### 2. 分析方法建议
- **多维度分析**: 结合资产、交易、历史数据进行综合分析
- **基准对比**: 使用市场指数作为业绩基准
- **风险调整**: 考虑风险调整后的收益指标

### 3. 数据质量检查
- **异常值检测**: 识别明显不合理的数据点
- **完整性验证**: 检查关键字段的缺失情况
- **一致性校验**: 验证不同接口数据的一致性

## 错误处理

### 常见错误码
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: API Key无效或缺失
- `404 Not Found`: 数据不存在
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

## 更新日志

### v1.0.0 (2024-01-20)
- 重新设计API，专注于提供原始数据
- 移除投资建议和分析结论
- 增强数据完整性和准确性
- 提供更详细的数据字段和元信息

## 技术支持

- **API文档**: 本文档提供完整的接口说明
- **示例代码**: 提供Python和JavaScript使用示例
- **问题反馈**: 通过指定渠道报告API问题或数据质量问题

---

**重要提醒**: 本API仅提供数据，不构成投资建议。AI分析师应基于自身的算法和模型对数据进行分析，并为用户提供个性化的投资建议。