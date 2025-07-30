# AI分析师API集成方案

## 项目概述

本项目为外部AI分析师提供了一套完整的资产数据查询和分析API接口，基于现有的个人投资管理系统构建。通过这套API，AI分析师可以获取全面的资产快照、投资历史、绩效分析、风险评估等数据，为用户提供智能化的投资建议。

## 核心特性

### 📊 数据获取能力
- **资产总览**: 实时资产分布、平台配置、持仓概况
- **投资历史**: 详细操作记录、资金流分析、月度统计
- **绩效分析**: 收益率计算、趋势分析、资产表现
- **风险评估**: 波动率分析、最大回撤、风险指标
- **汇率数据**: 多货币支持、实时汇率、历史趋势

### 🔐 安全机制
- **API密钥认证**: 支持多密钥管理和权限控制
- **请求限流**: 防止API滥用，保护系统稳定性
- **数据权限**: 细粒度的数据访问控制
- **审计日志**: 完整的API调用记录和监控

### 📈 高级分析
- **投资组合分析**: 集中度风险、分散化评分、再平衡建议
- **定投计划分析**: 执行统计、成本平均效应
- **市场数据**: 基金净值、市场概况信息

## 项目结构

```
backend/
├── app/
│   ├── api/v1/
│   │   └── ai_analyst.py          # 主API接口模块
│   ├── config/
│   │   └── ai_analyst_config.py   # 配置管理
│   └── models/
│       ├── database.py            # 数据库模型
│       └── asset_snapshot.py      # 快照模型
├── examples/
│   └── ai_analyst_client.py       # Python客户端示例
└── docs/
    ├── ai_analyst_api_documentation.md   # 详细API文档
    └── ai_analyst_api_readme.md          # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.9+
- FastAPI
- SQLAlchemy
- PostgreSQL/SQLite
- 现有的个人投资管理系统

### 2. 安装和配置

#### 第一步：激活API模块

确保在 `backend/app/main.py` 中已正确注册AI分析师路由：

```python
from app.api.v1 import ai_analyst

# 注册AI分析师接口
app.include_router(
    ai_analyst.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["AI分析师"]
)
```

#### 第二步：配置API密钥

设置环境变量或修改配置文件：

```bash
# 环境变量方式
export AI_ANALYST_API_KEYS='["your_production_key", "your_test_key"]'
export AI_ANALYST_RATE_LIMIT_REQUESTS=60
export AI_ANALYST_MAX_HISTORY_DAYS=365
```

或修改 `backend/app/config/ai_analyst_config.py`：

```python
ai_analyst_config = AIAnalystConfig(
    api_keys=["your_production_key", "your_test_key"],
    rate_limit_requests=60,
    max_history_days=365
)
```

#### 第三步：启动服务

```bash
cd backend
python run.py
```

### 3. API测试

```bash
# 健康检查
curl -X GET "http://localhost:8000/api/v1/ai-analyst/health" \
     -H "X-API-Key: your_api_key"

# 获取资产总览
curl -X GET "http://localhost:8000/api/v1/ai-analyst/asset-summary?base_currency=CNY" \
     -H "X-API-Key: your_api_key"
```

## API接口清单

### 核心数据接口
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 资产总览 | GET | `/asset-summary` | 获取最新资产分布和持仓概况 |
| 投资历史 | GET | `/investment-history` | 获取投资操作历史和资金流 |
| 绩效分析 | GET | `/performance-analysis` | 获取收益率和趋势分析 |
| 汇率数据 | GET | `/exchange-rates` | 获取汇率信息和货币支持 |
| 市场数据 | GET | `/market-data` | 获取基金净值等市场数据 |

### 高级分析接口
| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 投资组合分析 | GET | `/portfolio-analysis` | 集中度风险和分散化分析 |
| 定投计划分析 | GET | `/dca-analysis` | 定投执行情况和效果分析 |
| 风险评估 | GET | `/risk-assessment` | 波动率、回撤等风险指标 |
| 健康检查 | GET | `/health` | API服务状态检查 |

## 使用示例

### Python客户端

```python
from examples.ai_analyst_client import AIAnalystClient

# 初始化客户端
client = AIAnalystClient(
    base_url="http://localhost:8000/api/v1/ai-analyst",
    api_key="your_api_key"
)

# 获取资产总览
summary = client.get_asset_summary(base_currency="CNY")
print(f"总资产: {summary['total_assets']}")

# 获取投资组合分析
portfolio = client.get_portfolio_analysis()
print(f"分散化评分: {portfolio['diversification_score']}%")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1/ai-analyst',
  headers: { 'X-API-Key': 'your_api_key' }
});

// 获取绩效分析
const performance = await client.get('/performance-analysis?days=30');
console.log('30天收益率:', performance.data.overall_return);
```

### cURL命令行

```bash
# 获取风险评估
curl -X GET "http://localhost:8000/api/v1/ai-analyst/risk-assessment?days=90" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json"
```

## 数据结构说明

### 关键数据模型

#### 资产快照 (AssetSnapshot)
- `platform`: 平台标识（支付宝基金、IBKR、OKX等）
- `asset_type`: 资产类型（基金、股票、现金等）
- `balance_cny/usd/eur`: 多币种余额
- `snapshot_time`: 快照时间

#### 用户操作 (UserOperation)
- `operation_type`: 操作类型（buy、sell、dividend）
- `amount`: 操作金额
- `nav`: 净值/价格
- `emotion_score`: 情绪评分

#### 定投计划 (DCAPlan)
- `frequency`: 定投频率
- `smart_dca`: 智能定投标识
- `execution_count`: 执行次数

### 数据逻辑说明

#### 1. 资产聚合逻辑
- 按最新快照时间聚合所有平台资产
- 支持多基准货币（CNY/USD/EUR）显示
- 自动过滤小额资产（<0.01）

#### 2. 收益率计算
- 基于历史快照数据计算时间段收益
- 支持日收益率、累计收益率
- 考虑分红和操作影响

#### 3. 风险指标计算
- 年化波动率 = 日波动率 × √252
- 最大回撤基于历史净值峰谷计算
- 夏普比率假设无风险利率2%

#### 4. 投资组合分析
- 赫芬达尔指数(HHI)衡量集中度
- 分散化评分综合考虑平台和资产类型
- 再平衡建议基于权重阈值触发

## 部署和监控

### 生产环境部署

#### 1. 环境变量配置

```bash
# 生产环境API密钥
AI_ANALYST_API_KEYS='["prod_key_xxx", "backup_key_yyy"]'

# 严格的限流设置
AI_ANALYST_RATE_LIMIT_REQUESTS=30
AI_ANALYST_RATE_LIMIT_WINDOW=60

# 数据访问限制
AI_ANALYST_MAX_HISTORY_DAYS=180
AI_ANALYST_MAX_RECORDS_PER_REQUEST=500

# 安全设置
AI_ANALYST_ENABLE_IP_WHITELIST=true
AI_ANALYST_IP_WHITELIST='["192.168.1.0/24", "10.0.0.0/8"]'
```

#### 2. 缓存配置

为提高性能，建议配置Redis缓存：

```python
# 缓存设置
AI_ANALYST_CACHE_TTL_ASSET_SUMMARY=1800  # 30分钟
AI_ANALYST_CACHE_TTL_EXCHANGE_RATES=900   # 15分钟
AI_ANALYST_CACHE_TTL_MARKET_DATA=3600     # 1小时
```

#### 3. 监控指标

建议监控以下关键指标：
- API请求量和响应时间
- 错误率和状态码分布
- 数据库查询性能
- 缓存命中率
- API密钥使用情况

### 日志和审计

系统提供完整的审计日志：

```json
{
  "timestamp": "2024-01-20T15:30:00Z",
  "api_key": "masked_key_xxx",
  "endpoint": "/asset-summary",
  "parameters": {"base_currency": "CNY"},
  "response_time_ms": 245,
  "status_code": 200,
  "client_ip": "192.168.1.100"
}
```

## 安全考虑

### 1. 认证授权
- 使用强API密钥（至少32字符）
- 定期轮换API密钥
- 为不同客户分配不同密钥

### 2. 数据保护
- 敏感数据脱敏处理
- 不在日志中记录完整请求/响应
- 支持数据访问权限控制

### 3. 网络安全
- 建议使用HTTPS传输
- 配置IP白名单限制访问
- 实施请求限流防止滥用

### 4. 数据备份
- 定期备份数据库
- 保留历史快照数据
- 建立数据恢复流程

## 故障排除

### 常见问题

#### 1. API密钥无效
```
Error: 401 Unauthorized - 无效的API密钥
```
**解决方案**: 检查 `X-API-Key` 请求头和配置文件中的密钥设置

#### 2. 请求频率超限
```
Error: 429 Too Many Requests
```
**解决方案**: 降低请求频率或联系管理员提高限额

#### 3. 数据不存在
```
Error: 404 Not Found - 没有找到资产快照数据
```
**解决方案**: 确保数据库中有资产快照数据，检查数据同步服务

#### 4. 查询超时
```
Error: 请求超时
```
**解决方案**: 减少查询时间范围，优化数据库索引，检查服务器性能

### 调试工具

#### 1. 健康检查
```bash
curl -X GET "http://localhost:8000/api/v1/ai-analyst/health" \
     -H "X-API-Key: your_api_key"
```

#### 2. 数据库连接测试
```python
from app.utils.database import get_db
from app.models.asset_snapshot import AssetSnapshot

# 测试数据库连接
db = next(get_db())
count = db.query(AssetSnapshot).count()
print(f"资产快照总数: {count}")
```

#### 3. 配置检查
```python
from app.config.ai_analyst_config import ai_analyst_config
print(f"配置: {ai_analyst_config.dict()}")
```

## 性能优化

### 1. 数据库优化
- 为常用查询字段添加索引
- 使用连接池管理数据库连接
- 定期清理历史数据

### 2. 缓存策略
- 对频繁访问的数据启用缓存
- 使用Redis集群提高缓存性能
- 合理设置缓存过期时间

### 3. API优化
- 使用分页减少单次数据量
- 异步处理复杂计算
- 压缩响应数据

## 扩展开发

### 1. 添加新接口

在 `backend/app/api/v1/ai_analyst.py` 中添加新的路由：

```python
@router.get("/new-analysis", response_model=NewAnalysisResponse)
def get_new_analysis(
    param1: str = Query(..., description="参数1"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """新的分析接口"""
    # 实现分析逻辑
    return result
```

### 2. 自定义数据格式

创建新的Pydantic模型：

```python
class CustomAnalysisResponse(BaseModel):
    """自定义分析响应模型"""
    metric1: float = Field(..., description="指标1")
    metric2: List[Dict] = Field(..., description="指标2")
    recommendations: List[str] = Field(..., description="建议")
```

### 3. 集成外部数据

```python
async def fetch_external_data():
    """获取外部数据源"""
    # 集成股票API、基金API等
    pass
```

## 许可和支持

### 开源许可
本项目基于现有的个人投资管理系统开发，遵循相同的开源许可协议。

### 技术支持
- 技术文档: 见 `docs/ai_analyst_api_documentation.md`
- 示例代码: 见 `examples/` 目录
- 问题反馈: 通过GitHub Issues或邮件联系

### 贡献指南
欢迎提交Pull Request和Issue，请确保：
- 代码符合项目规范
- 添加适当的测试用例
- 更新相关文档

---

**最后更新**: 2024年1月20日  
**API版本**: v1.0.0  
**文档版本**: 1.0