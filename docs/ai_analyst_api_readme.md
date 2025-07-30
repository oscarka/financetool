# AI分析师数据API项目

## 概述

本项目为外部AI分析师提供**原始资产数据和基础计算结果**，专注于数据提供而非分析结论。AI分析师可以基于这些高质量的数据进行独立分析和决策。

## 🎯 核心特点

- **数据优先**: 提供原始数据，不做主观分析
- **多维度**: 支持资产、交易、历史、市场、定投等多类数据
- **实时性**: 基于最新快照的准确数据
- **完整性**: 跨平台、多币种、多资产类型整合
- **简洁API**: 内部使用，接口设计简化实用

## 🚀 快速开始

### 1. 启动服务
```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问测试页面
打开浏览器访问：
```
http://localhost:8000/api/v1/ai-analyst/playground
```

这个内置的测试页面提供了：
- 🎮 **可视化测试界面**: 直观的API测试工具
- 📊 **实时数据预览**: 立即查看API返回的数据结构
- 🔧 **参数调整**: 简单修改API参数进行测试
- 📋 **一键复制**: 快速获取API调用示例

### 3. API认证
使用内置测试密钥：
- `ai_analyst_key_2024` (主要测试密钥)
- `demo_key_12345` (备用密钥)

## 📡 API接口概览

### 核心数据接口

| 接口 | 描述 | 用途 |
|------|------|------|
| `/asset-data` | 当前资产持仓快照 | 投资组合分析、配置评估 |
| `/transaction-data` | 交易历史记录 | 行为分析、策略识别 |
| `/historical-data` | 历史价值数据 | 绩效计算、趋势分析 |
| `/market-data` | 市场环境数据 | 汇率影响、基准对比 |
| `/dca-data` | 定投计划数据 | 成本平均效应分析 |
| `/health` | 服务健康检查 | 系统状态监控 |

### 内置工具

| 路径 | 描述 |
|------|------|
| `/playground` | 🎮 **API测试页面** - 可视化测试工具 |
| `/docs` | 📚 自动生成的OpenAPI文档 |

## 🔍 数据结构示例

### 资产数据 (`/asset-data`)
```json
{
  "current_holdings": [
    {
      "platform": "支付宝基金",
      "asset_code": "000001",
      "asset_name": "华夏成长混合",
      "balance_cny": 25000.00,
      "balance_usd": 3571.43,
      "extra_data": {
        "fund_type": "混合型",
        "risk_level": "中高风险"
      }
    }
  ],
  "platform_summary": [...],
  "asset_type_summary": [...]
}
```

### 交易数据 (`/transaction-data`)
```json
{
  "transactions": [
    {
      "date": "2024-01-15T09:30:00",
      "operation_type": "buy",
      "amount": 1000.00,
      "emotion_score": 7,
      "strategy": "定投计划"
    }
  ],
  "summary_stats": {...},
  "time_series_data": [...]
}
```

## 🤖 AI分析师使用指南

### 1. **投资组合分析**
```python
# 获取资产数据
asset_data = api_client.get('/asset-data')

# 计算集中度风险 (HHI指数)
holdings = asset_data['current_holdings'] 
total_value = sum(h['base_currency_value'] for h in holdings)
weights = [h['base_currency_value'] / total_value for h in holdings]
hhi = sum(w**2 for w in weights) * 10000

# 评估分散化程度
platform_count = len(asset_data['platform_summary'])
risk_level = "低" if hhi < 1500 else "中" if hhi < 2500 else "高"
```

### 2. **行为模式分析**
```python
# 获取交易数据
tx_data = api_client.get('/transaction-data')

# 分析投资纪律性
buy_ops = [t for t in tx_data['transactions'] if t['operation_type'] == 'buy']
amounts = [t['amount'] for t in buy_ops]
consistency = 1 - (std(amounts) / mean(amounts))

# 情绪趋势分析
emotions = [t['emotion_score'] for t in tx_data['transactions']]
emotion_trend = analyze_linear_trend(emotions)
```

### 3. **绩效计算**
```python
# 获取历史数据
hist_data = api_client.get('/historical-data?days=90')

# 计算收益率和波动率
values = [d['base_value'] for d in hist_data['asset_values']]
total_return = (values[-1] - values[0]) / values[0]
daily_returns = calculate_daily_returns(values)
volatility = std(daily_returns) * sqrt(252)
```

## 🛠️ 开发和部署

### 项目结构
```
backend/
├── app/
│   ├── api/v1/
│   │   └── ai_analyst.py      # 核心API接口
│   ├── models/
│   │   ├── database.py        # 数据库模型
│   │   └── asset_snapshot.py  # 快照模型
│   └── main.py               # FastAPI应用
├── examples/
│   ├── ai_analyst_client.py  # Python客户端示例
│   └── ai_analyst_client.js  # JavaScript客户端示例
└── docs/
    ├── ai_analyst_api_documentation.md  # 详细API文档
    └── ai_analyst_api_readme.md         # 项目说明
```

### 技术栈
- **后端**: FastAPI + SQLAlchemy + Pydantic
- **数据库**: PostgreSQL (推荐) / MySQL / SQLite
- **认证**: API Key (Header: X-API-Key)
- **文档**: 自动生成OpenAPI文档

### 环境要求
```bash
pip install fastapi uvicorn sqlalchemy pydantic-settings
```

## 🔒 安全考虑

### API Key管理
- 内部使用，密钥相对简单
- 生产环境请更换为复杂密钥
- 考虑添加IP白名单限制

### 数据访问
- 当前无用户隔离，返回所有数据
- 生产环境可根据需要添加用户权限控制
- 敏感数据可在extra_data中控制返回

## 📈 数据质量

### 数据来源
- **资产快照**: 每日自动抓取各平台数据
- **交易记录**: 用户手动输入 + 部分自动同步  
- **净值数据**: 第三方API实时获取
- **汇率数据**: akshare等数据源，15分钟更新

### 数据完整性
- 所有货币金额精确到2位小数
- 数量/份额精确到8位小数
- 时间戳使用ISO 8601格式
- 缺失数据标记为`null`

## 🔧 故障排除

### 常见问题

**1. API返回404错误**
- 检查数据库中是否有AssetSnapshot数据
- 确认数据库连接配置正确

**2. 空数据返回**
- 检查时间范围参数是否合理
- 确认筛选条件不会过度限制结果

**3. 性能问题**
- 适当使用limit参数限制返回数据量
- 考虑为大表添加索引

### 日志监控
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 🚀 使用建议

### 最佳实践
1. **测试优先**: 使用`/playground`页面快速验证接口
2. **参数优化**: 根据需要调整`days`、`limit`等参数
3. **错误处理**: 实现重试机制和降级策略
4. **数据缓存**: 对不经常变化的数据进行本地缓存

### 性能优化
- 使用合理的时间范围查询
- 批量处理多个资产的数据请求
- 考虑异步调用提高效率

## 📞 技术支持

- **API测试**: 访问 `/playground` 页面
- **API文档**: 访问 `/docs` 查看详细接口文档
- **示例代码**: 参考 `examples/` 目录下的客户端实现

---

**重要提醒**: 本API专注于数据提供，不包含投资建议。AI分析师应基于自身算法和模型对数据进行分析，为用户提供个性化服务。