# 🔗 金融系统API集成总指南

---

## 目录
1. 前言与适用范围
2. Wise API集成
3. PayPal API集成
4. IBKR API集成
5. 基金模块集成
6. 汇率管理集成
7. 通用集成规范
8. 故障排查与维护

---

## 1. 前言与适用范围

本指南涵盖系统所有第三方API集成，包括Wise、PayPal、IBKR、基金数据、汇率服务等。每个集成都包含完整的配置、使用、故障排查指南。

---

## 2. Wise API集成

### 2.1 功能概述
- **账户余额管理** - 多币种账户余额查询和同步
- **交易记录查询** - 完整的交易历史记录
- **汇率服务** - 实时汇率和历史汇率数据
- **数据落库** - 完整的数据持久化存储

### 2.2 核心组件
```python
# 服务层
backend/app/services/wise_api_service.py
# API路由
backend/app/api/v1/wise.py
# 前端组件
frontend/src/components/WiseManagement.tsx
```

### 2.3 主要API端点
- `GET /api/v1/wise/config` - 获取配置信息
- `GET /api/v1/wise/test` - 测试API连接
- `GET /api/v1/wise/all-balances` - 获取所有账户余额
- `GET /api/v1/wise/recent-transactions` - 获取最近交易记录
- `GET /api/v1/wise/exchange-rates` - 获取汇率信息
- `POST /api/v1/wise/sync-balances` - 同步余额到数据库
- `POST /api/v1/wise/sync-transactions` - 同步交易到数据库

### 2.4 配置要求
```bash
# 环境变量配置
WISE_API_TOKEN=your_actual_wise_api_token
```

### 2.5 数据落库功能
- **WiseBalance表** - 存储账户余额信息
- **WiseTransaction表** - 存储交易记录
- **WiseExchangeRate表** - 存储汇率数据
- **去重机制** - 避免重复数据插入
- **事务处理** - 确保数据一致性

### 2.6 技术特性
- **安全数值转换** - `_safe_float`方法处理异常数据
- **primaryAmount解析修复** - 支持带逗号的数字格式
- **余额解析优化** - 完善的错误处理机制
- **定时同步** - 每日16:30自动同步数据

---

## 3. PayPal API集成

### 3.1 功能概述
- **OAuth 2.0认证** - 客户端凭证流认证
- **账户余额查询** - 多币种余额管理
- **交易记录查询** - 详细的交易历史
- **模拟数据支持** - 权限不足时的降级方案

### 3.2 核心组件
```python
# 服务层
backend/app/services/paypal_api_service.py
# API路由
backend/app/api/v1/paypal.py
# 前端组件
frontend/src/components/PayPalManagement.tsx
```

### 3.3 主要API端点
- `GET /api/v1/paypal/config` - 获取配置信息
- `GET /api/v1/paypal/test` - 测试API连接
- `GET /api/v1/paypal/all-balances` - 获取所有账户余额
- `GET /api/v1/paypal/recent-transactions` - 获取最近交易记录
- `GET /api/v1/paypal/summary` - 获取账户汇总信息

### 3.4 配置要求
```bash
# 环境变量配置
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
```

### 3.5 权限配置指南
**必需权限范围(Scopes)**：
- `openid` - 基础身份验证
- `profile` - 用户配置文件访问
- `email` - 邮箱访问
- `https://uri.paypal.com/services/wallet/payment-tokens/read` - 钱包访问
- `https://uri.paypal.com/services/reporting/search/read` - 交易报告访问

### 3.6 模拟数据方案
当API权限不足时，系统自动提供模拟数据：
- PayPal USD 账户：$1,300.50
- PayPal EUR 账户：€916.00
- 包含5条模拟交易记录

---

## 4. IBKR API集成

### 4.1 功能概述
- **数据同步接收** - 接收Google Cloud VM推送的数据
- **账户余额管理** - 完整的余额数据存储和查询
- **持仓信息管理** - 详细的持仓数据管理
- **同步日志审计** - 完整的操作审计记录

### 4.2 核心组件
```python
# 服务层
backend/app/services/ibkr_api_service.py
# API路由
backend/app/api/v1/ibkr.py
# 前端组件
frontend/src/components/IBKRManagement.tsx
```

### 4.3 数据库设计
```sql
-- IBKR账户信息表
CREATE TABLE ibkr_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    account_type VARCHAR(50),
    base_currency VARCHAR(10),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- IBKR余额表
CREATE TABLE ibkr_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id VARCHAR(50),
    total_cash DECIMAL(20, 6),
    net_liquidation DECIMAL(20, 6),
    buying_power DECIMAL(20, 6),
    currency VARCHAR(10),
    snapshot_time TIMESTAMP,
    sync_source VARCHAR(50),
    created_at TIMESTAMP,
    UNIQUE(account_id, snapshot_time, currency)
);

-- IBKR持仓表
CREATE TABLE ibkr_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id VARCHAR(50),
    symbol VARCHAR(50),
    quantity DECIMAL(20, 6),
    market_value DECIMAL(20, 6),
    average_cost DECIMAL(20, 6),
    unrealized_pnl DECIMAL(20, 6),
    currency VARCHAR(10),
    asset_class VARCHAR(50),
    snapshot_time TIMESTAMP,
    sync_source VARCHAR(50),
    created_at TIMESTAMP,
    UNIQUE(account_id, symbol, snapshot_time)
);

-- IBKR同步日志表
CREATE TABLE ibkr_sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id VARCHAR(50),
    sync_type VARCHAR(50),
    status VARCHAR(50),
    request_data TEXT,
    response_data TEXT,
    records_processed INTEGER,
    records_inserted INTEGER,
    error_message TEXT,
    sync_duration_ms INTEGER,
    source_ip VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP
);
```

### 4.4 主要API端点
- `POST /api/v1/ibkr/sync` - 主要数据同步端点
- `GET /api/v1/ibkr/config` - 获取配置信息
- `GET /api/v1/ibkr/test` - 连接测试
- `GET /api/v1/ibkr/balances` - 获取余额数据
- `GET /api/v1/ibkr/positions` - 获取持仓数据
- `GET /api/v1/ibkr/logs` - 获取同步日志
- `GET /api/v1/ibkr/summary` - 获取汇总信息

### 4.5 配置要求
```bash
# 环境变量配置
IBKR_API_KEY=ibkr_sync_key_2024_production_secret
IBKR_ALLOWED_IPS=34.60.247.187,10.0.0.0/8
IBKR_SYNC_TIMEOUT=30
IBKR_MAX_REQUEST_SIZE=1048576
IBKR_RATE_LIMIT_PER_MINUTE=60
IBKR_ENABLE_IP_WHITELIST=true
IBKR_ENABLE_REQUEST_LOGGING=true
```

### 4.6 安全机制
- **API密钥认证** - X-API-Key头部验证
- **IP白名单验证** - 仅允许指定IP访问
- **数据验证** - Pydantic模型验证
- **审计日志** - 完整的操作记录

### 4.7 数据同步格式
```json
{
  "account_id": "U13638726",
  "timestamp": "2024-12-19T08:00:00Z",
  "balances": {
    "total_cash": 2.74,
    "net_liquidation": 5.70,
    "buying_power": 2.74,
    "currency": "USD"
  },
  "positions": [
    {
      "symbol": "TSLA",
      "quantity": 0.01,
      "market_value": 2.96,
      "average_cost": 0.0,
      "currency": "USD"
    }
  ]
}
```

---

## 5. 基金模块集成

### 5.1 功能概述
- **基金操作记录** - 买入、卖出、分红等操作管理
- **净值自动同步** - 从外部API获取基金净值
- **收益自动计算** - 基于操作记录和净值数据计算收益
- **定投计划管理** - 支持设置和执行定投计划

### 5.2 核心组件
```python
# 服务层
backend/app/services/fund_service.py
# API路由
backend/app/api/v1/funds.py
# 前端组件
frontend/src/components/FundOperations.tsx
```

### 5.3 主要API端点
- `POST /api/v1/funds/operations` - 创建基金操作记录
- `GET /api/v1/funds/operations` - 获取基金操作历史
- `GET /api/v1/funds/positions` - 获取基金持仓列表
- `POST /api/v1/funds/nav` - 手动录入基金净值
- `GET /api/v1/funds/nav/{fund_code}` - 获取基金净值历史
- `POST /api/v1/funds/dca/plans` - 创建定投计划
- `GET /api/v1/funds/dca/plans` - 获取定投计划列表

### 5.4 数据源集成
- **天天基金网API** - 主要数据源
- **雪球API** - 备用数据源
- **蚂蚁财富API** - 扩展数据源
- **腾讯理财通API** - 扩展数据源

### 5.5 基金操作流程
```
买入操作流程：
1. 用户录入买入信息
2. 系统获取当天净值（预估）
3. 计算预估份额
4. 记录操作状态为"pending"
5. 第二天获取实际净值
6. 用户确认或修正份额
7. 更新操作状态为"confirmed"
```

### 5.6 收益计算逻辑
```python
def calculate_profit(avg_cost, current_nav, shares):
    """计算收益"""
    total_cost = avg_cost * shares
    current_value = current_nav * shares
    profit = current_value - total_cost
    profit_rate = profit / total_cost if total_cost > 0 else 0
    return profit, profit_rate
```

---

## 6. 汇率管理集成

### 6.1 功能概述
- **实时汇率查询** - 基于akshare库的汇率数据
- **货币转换计算** - 支持多种货币间的转换
- **历史汇率查询** - 汇率历史数据查询
- **货币列表管理** - 支持货币信息管理

### 6.2 核心组件
```python
# 服务层
backend/app/services/exchange_rate_service.py
# API路由
backend/app/api/v1/exchange_rates.py
# 前端组件
frontend/src/pages/ExchangeRates.tsx
```

### 6.3 主要API端点
- `GET /api/v1/exchange-rates/currencies` - 获取货币列表
- `GET /api/v1/exchange-rates/rates` - 获取所有汇率
- `GET /api/v1/exchange-rates/rates/{currency}` - 获取指定货币汇率
- `GET /api/v1/exchange-rates/rates/{currency}/history` - 获取历史汇率
- `GET /api/v1/exchange-rates/convert` - 货币转换

### 6.4 数据源说明
- **数据源**: akshare库 (`ak.currency_boc_sina()`)
- **更新频率**: 每日更新
- **支持货币**: 主要货币对人民币
- **数据字段**: 现汇买入价、现汇卖出价、现钞买入价、现钞卖出价、央行中间价

### 6.5 数据结构
```python
{
    "currency": "USD",
    "currency_name": "美元",
    "spot_buy": 691.8,      # 现汇买入价
    "spot_sell": 694.73,    # 现汇卖出价
    "cash_buy": 686.17,     # 现钞买入价
    "cash_sell": 694.73,    # 现钞卖出价
    "middle_rate": 689.51,  # 央行中间价
    "update_time": "2025-07-05T23:59:52.083494"
}
```

---

## 7. 通用集成规范

### 7.1 响应格式标准
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

### 7.2 错误处理规范
```json
{
  "detail": "错误描述信息"
}
```

### 7.3 认证机制
- **API密钥认证** - 适用于IBKR等需要高安全性的API
- **OAuth 2.0认证** - 适用于PayPal等标准OAuth流程
- **Token认证** - 适用于Wise等Token-based认证

### 7.4 数据验证
- **Pydantic模型验证** - 请求和响应数据格式验证
- **类型检查** - 确保数据类型正确
- **空值处理** - 安全处理None和空字符串
- **数值转换** - 安全的浮点数转换

### 7.5 日志记录
- **操作日志** - 记录所有API调用
- **错误日志** - 记录异常和错误信息
- **性能日志** - 记录响应时间和性能指标
- **审计日志** - 记录敏感操作和权限验证

---

## 8. 故障排查与维护

### 8.1 常见问题排查

#### Wise API问题
- **余额解析错误**: 检查`_safe_float`方法实现
- **primaryAmount解析失败**: 确认正则表达式支持逗号格式
- **API连接失败**: 验证Token有效性和网络连接

#### PayPal API问题
- **403权限错误**: 检查API权限配置
- **OAuth认证失败**: 验证Client ID和Secret
- **模拟数据使用**: 确认是否启用了模拟数据模式

#### IBKR API问题
- **同步失败**: 检查API密钥和IP白名单
- **数据重复**: 验证数据库唯一约束
- **VM连接问题**: 确认Google Cloud VM网络连接

#### 基金API问题
- **净值同步失败**: 检查外部API可用性
- **份额计算错误**: 验证计算逻辑和数据类型
- **定投执行失败**: 检查调度器配置

#### 汇率API问题
- **数据获取失败**: 检查akshare库安装和网络连接
- **货币转换错误**: 验证汇率数据完整性
- **历史数据缺失**: 确认数据源限制

### 8.2 监控指标
- **API响应时间** - 监控各API的响应性能
- **错误率统计** - 跟踪API调用成功率
- **数据同步状态** - 监控定时同步任务状态
- **数据库性能** - 监控查询和写入性能

### 8.3 维护建议
- **定期检查日志** - 及时发现和处理异常
- **API密钥轮换** - 定期更新API密钥
- **数据备份** - 定期备份重要数据
- **性能优化** - 根据使用情况优化查询和缓存

### 8.4 扩展计划
- **多货币支持** - 扩展汇率服务支持更多货币
- **数据分析功能** - 添加收益分析和趋势预测
- **通知系统** - 实现异常告警和重要事件通知
- **数据导出** - 支持多种格式的数据导出

---

## 📞 技术支持

如有问题，请查看：
- 详细API文档: `http://localhost:8000/docs`
- 测试文件: 各模块对应的test_*.py文件
- 配置说明: 各模块的README_*.md文件

**系统现在支持 Wise + PayPal + IBKR + 基金 + 汇率 五大平台的完整数据管理！** 🎊 