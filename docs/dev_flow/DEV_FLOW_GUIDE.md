# 🔄 金融系统开发流程与代码合并总指南

---

## 目录
1. 前言与适用范围
2. 开发计划与策略
3. 代码合并与分支管理
4. 接口兼容性与修复
5. 自动化日志系统
6. 测试验证与部署
7. 开发规范与最佳实践

---

## 1. 前言与适用范围
本指南适用于本系统所有开发流程、代码合并、接口修复、自动化日志、测试验证等环节。内容涵盖前后端开发、API集成、分支管理、部署流程等。

---

## 2. 开发计划与策略

### 2.1 核心理念
- **用户只需记录决策**：系统自动处理数据获取和计算
- **分模块验证**：每个模块独立开发，确保可运行可验证
- **渐进式开发**：从简单到复杂，每个阶段都有可用的产品

### 2.2 开发优先级
1. **基金模块**（网络稳定，API丰富）
2. **OKX模块**（网络问题解决后）
3. **Wise模块**（外汇管理）
4. **银行理财模块**（固定收益）
5. **统一分析模块**（全局视图）

### 2.3 基金模块开发计划（2-3周）

#### 第1周：基础架构搭建
- 项目初始化（React + TypeScript + Vite + FastAPI + SQLite）
- 基金操作记录功能
- 净值管理功能

#### 第2周：API集成和自动化
- 天天基金网API集成
- 智能计算功能（自动份额、平均成本、收益更新）
- 用户体验优化

#### 第3周：高级功能
- 定投计划管理
- 分析功能（收益趋势、操作分析、基金对比）
- 测试和优化

### 2.4 核心API接口
```python
# 基金操作API
POST /api/v1/funds/operations     # 创建操作记录
GET /api/v1/funds/operations      # 获取操作历史
PUT /api/v1/funds/operations/{id} # 更新操作记录

# 基金净值API
GET /api/v1/funds/{code}/nav      # 获取净值历史
POST /api/v1/funds/{code}/nav     # 手动录入净值

# 持仓API
GET /api/v1/positions/funds       # 获取基金持仓
GET /api/v1/positions/summary     # 获取持仓汇总

# 定投API
POST /api/v1/dca/plans           # 创建定投计划
GET /api/v1/dca/plans            # 获取定投计划
```

---

## 3. 代码合并与分支管理

### 3.1 合并总结示例
**成功合并main分支的IBKR相关更新**：
- ✅ 合并了main分支上的IBKR API集成功能
- ✅ 解决了`backend/app/main.py`中的合并冲突
- ✅ 保留了日志系统功能

### 3.2 分支管理策略
- **main分支**：受保护，通过Pull Request合并
- **feature分支**：功能开发分支
- **hotfix分支**：紧急修复分支
- **release分支**：发布准备分支

### 3.3 合并流程
1. 创建Pull Request（base: main, compare: feature分支）
2. 填写PR信息，等待review
3. 通过后点击Merge pull request
4. 合并后清理feature分支

---

## 4. 接口兼容性与修复

### 4.1 常见接口问题
**前后端接口定义不匹配**：
- 前端期望字段名与后端返回不一致
- 数据类型不匹配（number vs string）
- 可选字段处理不当

### 4.2 持仓管理接口修复示例

#### 问题诊断
移动端持仓管理页面没有显示数据的根本原因是：**前端接口定义与后端API返回的数据结构不匹配**。

#### 具体问题
**PositionSummary接口不匹配**：
```typescript
// 前端原定义
interface PositionSummary {
    total_cost: number
    current_value: number
    total_return: number
    return_rate: number
    position_count: number
}

// 后端实际返回
class PositionSummary(BaseModel):
    total_invested: Decimal
    total_value: Decimal
    total_profit: Decimal
    total_profit_rate: Decimal
    asset_count: int
    profitable_count: int
    loss_count: int
```

#### 修复方案
1. 更新前端接口定义，匹配后端字段名
2. 更新数据引用，使用正确的字段名
3. 添加调试日志，便于问题诊断

### 4.3 类型转换修复
```typescript
// 安全的数字转换
const safeNumber = (value: number | string) => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    return isNaN(numValue) ? 0 : numValue
}

// 安全的数字格式化
const safeToFixed = (value: number | string, digits: number = 2) => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0.' + '0'.repeat(digits)
    return numValue.toFixed(digits)
}
```

---

## 5. 自动化日志系统

### 5.1 日志系统特性
- ✅ **一行代码实现**：只需添加`@auto_log("service_type")`装饰器
- ✅ **自动检测服务类型**：根据服务名称自动选择对应的日志函数
- ✅ **完整的执行记录**：包括函数调用、参数、执行时间、结果、异常
- ✅ **安全的数据处理**：自动过滤敏感信息（API密钥、密码等）

### 5.2 日志分类
- **外部API服务**：fund, okx, wise, paypal, exchange, external
- **基础服务**：api, database, scheduler, business, error, system, security

### 5.3 已集成的服务
- **IBKR API服务**：sync_data, get_account_info, get_latest_balances等
- **基金API服务**：get_fund_nav_tiantian, get_fund_nav_xueqiu等
- **OKX API服务**：get_account_balance, get_ticker, get_all_tickers等
- **Wise API服务**：get_profile, get_accounts, get_account_balance等
- **PayPal API服务**：get_balance_accounts, get_all_balances等
- **汇率服务**：get_currency_list, get_exchange_rate等

### 5.4 日志查看
- **Web界面**：访问 `/logs-viewer` 查看结构化日志
- **API接口**：通过 `/api/v1/logs` 获取日志数据
- **过滤功能**：按服务类型、级别、时间范围过滤
- **统计信息**：日志统计和清理功能

---

## 6. 测试验证与部署

### 6.1 测试计划
- **单元测试**：基金收益计算逻辑、净值同步功能、定投执行逻辑
- **集成测试**：基金操作完整流程、数据同步和计算、前端后端交互
- **用户测试**：基金操作录入、净值确认流程、定投计划设置

### 6.2 验证标准
- **功能验证**：操作记录准确性、净值同步准确性、收益计算准确性
- **性能验证**：页面加载时间 < 2秒、数据同步时间 < 5秒
- **用户体验验证**：界面操作流畅、错误提示清晰、数据展示直观

### 6.3 部署建议
1. **测试环境验证**：先在测试环境验证修复效果
2. **备份当前版本**：确保可以回滚
3. **监控日志**：部署后观察是否有新的错误
4. **用户反馈**：收集用户使用体验

---

## 7. 开发规范与最佳实践

### 7.1 代码规范
- 使用TypeScript进行类型安全开发
- 遵循ESLint和Prettier代码规范
- 编写详细的注释和文档
- 使用Git进行版本控制

### 7.2 提交规范
- 每次提交前进行代码格式化
- 提交信息清晰描述变更内容
- 重要功能需要编写测试用例
- 定期进行代码审查

### 7.3 文档规范
- 及时更新API文档
- 编写用户使用手册
- 记录重要的设计决策
- 维护开发日志

### 7.4 预防措施
1. **类型安全**：建立前后端共享的类型定义
2. **API文档**：维护详细的API文档
3. **自动化测试**：添加API契约测试
4. **代码审查**：接口变更时严格审查

---

> 本文档已合并并精简自原 dev_flow 文件夹所有文档，所有关键信息均已保留。如需详细历史变更、特殊场景说明，请查阅原文档备份。 