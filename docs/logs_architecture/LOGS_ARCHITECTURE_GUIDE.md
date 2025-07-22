# 🔍 日志与系统架构总指南

---

## 目录
1. 前言与适用范围
2. 系统整体架构
3. 日志管理系统
4. 自动化日志系统
5. 模块划分与数据流
6. 技术选型与安全设计
7. 性能优化与部署
8. 使用指南与最佳实践

---

## 1. 前言与适用范围

本指南涵盖系统的完整架构设计、日志管理解决方案和自动化日志系统。包括结构化日志记录、Web界面查看、自动化日志工具、系统模块划分、技术选型等完整内容。

---

## 2. 系统整体架构

### 2.1 架构概览
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       └─────────────────┘
```

### 2.2 核心组件
- **前端**: React 18 + TypeScript + Vite
- **后端**: FastAPI + SQLAlchemy + SQLite
- **外部集成**: Wise、PayPal、IBKR、OKX、基金API
- **日志系统**: 结构化日志 + Web界面 + 自动化工具
- **部署**: Railway平台 + Docker容器化

---

## 3. 日志管理系统

### 3.1 系统特性
- 📊 **结构化日志记录** - 按分类和级别组织日志
- 🌐 **Web界面查看** - 美观的在线日志查看器
- 🔍 **强大的过滤功能** - 支持时间、级别、分类、关键词搜索
- 📈 **统计分析** - 日志统计和错误监控
- 🚀 **自动刷新** - 实时监控日志变化

### 3.2 日志分类系统

#### 基础分类
| 分类 | 说明 | 用途 |
|------|------|------|
| 🌐 API | API请求相关 | 跟踪内部API调用和响应 |
| 🗄️ DATABASE | 数据库操作 | 监控数据库查询和事务 |
| ⏰ SCHEDULER | 定时任务 | 跟踪定时任务执行情况 |
| 💼 BUSINESS | 业务逻辑 | 记录业务流程和决策 |
| ❌ ERROR | 错误日志 | 专门记录错误和异常 |
| 🖥️ SYSTEM | 系统运行 | 系统启动、关闭等事件 |
| 🔒 SECURITY | 安全相关 | 安全事件和可疑活动 |

#### 外部服务分类
| 分类 | 说明 | 用途 |
|------|------|------|
| 📈 FUND_API | 基金API调用 | 监控基金数据获取、净值同步等 |
| ₿ OKX_API | OKX交易所API | 监控加密货币交易、账户查询等 |
| 💳 WISE_API | Wise金融API | 监控国际转账、汇率查询等 |
| 💰 PAYPAL_API | PayPal支付API | 监控支付交易、账户余额等 |
| 💱 EXCHANGE_API | 汇率服务API | 监控汇率数据获取和更新 |
| 🔗 EXTERNAL_OTHER | 其他外部API | 监控其他第三方服务调用 |

### 3.3 Web界面功能
- **日志过滤** - 按级别、分类、关键词、时间范围过滤
- **统计信息** - 总日志数量、各级别日志数量、各分类日志数量
- **实用功能** - 自动刷新、详情展开、响应式设计、清理功能

### 3.4 API接口
- `GET /api/v1/logs` - 获取日志列表
- `GET /api/v1/logs/stats` - 获取日志统计
- `GET /api/v1/logs/categories` - 获取所有分类
- `GET /api/v1/logs/recent/{category}` - 获取指定分类的最近日志
- `DELETE /api/v1/logs/cleanup` - 清理旧日志

---

## 4. 自动化日志系统

### 4.1 三种使用方式

#### 方式1: 装饰器 - 一行代码搞定
```python
from app.utils.auto_logger import auto_log

@auto_log("fund")  # 自动记录基金API调用
async def get_fund_nav(fund_code: str):
    return await api_call()

@auto_log("okx")  # 自动记录OKX API调用
async def get_okx_balance():
    return await okx_api_call()
```

**自动获得：**
- 📝 函数调用记录
- ⏱️ 执行时间统计
- 🔍 参数记录（自动隐藏敏感信息）
- ❌ 异常捕获和记录
- 📊 结果记录（可选）

#### 方式2: 上下文管理器 - 记录代码块
```python
from app.utils.auto_logger import log_context

async def process_fund_order():
    with log_context("business", "处理基金订单"):
        with log_context("database", "验证用户"):
            user = await validate_user(user_id)
        with log_context("fund", "获取基金信息"):
            fund_info = await get_fund_info(fund_code)
```

#### 方式3: 便捷函数 - 一行代码记录
```python
from app.utils.auto_logger import quick_log

async def sync_fund_data(fund_code: str):
    try:
        result = await api_call()
        quick_log("基金数据同步成功", "fund", "INFO", 
                 fund_code=fund_code, nav=result["nav"])
        return result
    except Exception as e:
        quick_log("基金数据同步失败", "fund", "ERROR", 
                 fund_code=fund_code, error=str(e))
        raise
```

### 4.2 服务分类映射
| 服务名称 | 日志分类 | 用途 |
|----------|----------|------|
| `"fund"` | 📈 基金API | 基金数据获取、净值同步 |
| `"okx"` | ₿ OKX交易所 | 加密货币交易、账户查询 |
| `"wise"` | 💳 Wise金融 | 国际转账、汇率查询 |
| `"paypal"` | 💰 PayPal支付 | 支付交易、账户余额 |
| `"exchange"` | 💱 汇率服务 | 汇率数据获取 |
| `"api"` | 🌐 API接口 | 内部API调用 |
| `"database"` | 🗄️ 数据库 | 数据库操作 |
| `"business"` | 💼 业务逻辑 | 业务流程处理 |

### 4.3 高级配置
```python
@auto_log(
    service="fund",           # 服务分类
    level="INFO",             # 日志级别
    log_args=True,            # 是否记录参数
    log_result=True,          # 是否记录结果
    log_time=True,            # 是否记录执行时间
    log_exceptions=True       # 是否记录异常
)
async def get_fund_nav(fund_code: str):
    return await api_call()
```

---

## 5. 模块划分与数据流

### 5.1 前端模块 (React + TypeScript)
```
frontend/
├── src/
│   ├── components/           # 可复用组件
│   │   ├── common/          # 通用组件
│   │   ├── forms/           # 表单组件
│   │   ├── tables/          # 表格组件
│   │   └── charts/          # 图表组件
│   ├── pages/               # 页面组件
│   │   ├── Dashboard/       # 总览页面
│   │   ├── Operations/      # 操作记录页面
│   │   ├── Positions/       # 持仓页面
│   │   ├── Funds/           # 基金页面
│   │   └── Analysis/        # 分析页面
│   ├── hooks/               # 自定义Hooks
│   ├── stores/              # Zustand状态管理
│   ├── types/               # TypeScript类型定义
│   ├── utils/               # 工具函数
│   └── services/            # API调用服务
```

### 5.2 后端模块 (FastAPI + Python)
```
backend/
├── app/
│   ├── api/                 # API路由
│   │   ├── v1/             # API版本1
│   │   │   ├── operations.py    # 操作记录API
│   │   │   ├── positions.py     # 持仓API
│   │   │   ├── funds.py         # 基金API
│   │   │   └── analysis.py      # 分析API
│   │   └── dependencies.py      # 依赖注入
│   ├── models/              # 数据模型
│   │   ├── database.py      # 数据库模型
│   │   ├── schemas.py       # Pydantic模型
│   │   └── enums.py         # 枚举定义
│   ├── services/            # 业务逻辑
│   │   ├── operation_service.py    # 操作服务
│   │   ├── position_service.py     # 持仓服务
│   │   ├── fund_service.py         # 基金服务
│   │   ├── calculation_service.py  # 计算服务
│   │   └── sync_service.py         # 同步服务
│   ├── utils/               # 工具函数
│   │   ├── database.py      # 数据库工具
│   │   ├── validators.py    # 验证工具
│   │   └── helpers.py       # 辅助函数
│   └── main.py              # 应用入口
├── data/                    # 数据库文件
├── logs/                    # 日志文件
└── tests/                   # 测试文件
```

### 5.3 数据流设计

#### 操作记录流程
```
用户录入操作 → 前端验证 → API调用 → 后端验证 → 数据库存储 → 持仓重新计算 → 返回结果
```

#### 基金数据同步流程
```
定时任务触发 → 获取基金列表 → 调用外部API → 更新净值表 → 重新计算收益 → 更新持仓
```

#### 持仓计算流程
```
操作记录变更 → 获取最新价格 → 计算平均成本 → 计算当前市值 → 计算收益 → 更新持仓表
```

---

## 6. 技术选型与安全设计

### 6.1 前端技术栈
- **框架**: React 18 + TypeScript
- **状态管理**: Zustand (轻量级)
- **UI组件**: shadcn/ui + Tailwind CSS
- **图表**: Recharts
- **表单**: React Hook Form + Zod
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 6.2 后端技术栈
- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **ORM**: SQLAlchemy 2.0
- **验证**: Pydantic
- **定时任务**: APScheduler
- **HTTP客户端**: httpx
- **日志**: loguru

### 6.3 开发工具
- **包管理**: pnpm (前端) + poetry (后端)
- **代码规范**: ESLint + Prettier + Black
- **类型检查**: TypeScript + mypy
- **测试**: Jest (前端) + pytest (后端)

### 6.4 安全设计
- **数据验证**: Zod schema验证 + Pydantic模型验证
- **错误处理**: 统一错误响应格式 + 详细错误日志记录
- **数据备份**: 定期数据库备份 + 操作日志记录
- **安全监控**: 自动检测可疑请求 + 安全日志记录

---

## 7. 性能优化与部署

### 7.1 性能优化
- **数据库优化**: 合理索引设计 + 查询优化 + 连接池管理
- **前端优化**: 组件懒加载 + 数据缓存 + 虚拟滚动
- **API优化**: 响应缓存 + 批量操作 + 分页查询

### 7.2 部署方案
- **开发环境**: 本地SQLite数据库 + 热重载开发服务器
- **生产环境**: Railway平台 + Docker容器化 + 监控和日志

### 7.3 扩展性设计
- **模块化设计**: 每个资产类型独立模块 + 插件式API集成
- **数据模型扩展**: 版本化API + 向后兼容 + 数据迁移
- **功能扩展**: 新资产类型支持 + 新分析指标 + 新数据源集成

---

## 8. 使用指南与最佳实践

### 8.1 快速开始

#### 访问日志查看器
部署到Railway后，访问以下URL查看日志：
```
https://your-app.railway.app/logs-viewer
```

#### 在代码中使用日志
```python
# 基础分类
from app.utils.logger import (
    log_api, log_database, log_scheduler,
    log_business, log_error, log_system, log_security
)

# 外部服务分类
from app.utils.logger import (
    log_fund_api, log_okx_api, log_wise_api,
    log_paypal_api, log_exchange_api, log_external_other
)

# 使用示例
log_fund_api("获取基金净值", extra_data={"fund_code": "000001", "nav": 1.2345})
log_okx_api("查询OKX账户余额", extra_data={"balance": 1000.0, "currency": "USDT"})
```

### 8.2 自动化日志集成

#### 步骤1: 导入工具
```python
from app.utils.auto_logger import auto_log, log_context, quick_log
```

#### 步骤2: 为关键函数添加装饰器
```python
@auto_log("fund")
async def get_fund_nav(fund_code: str):
    return await api_call()
```

#### 步骤3: 为复杂流程添加上下文
```python
async def process_order():
    with log_context("business", "处理订单"):
        with log_context("database", "验证用户"):
            user = await validate_user()
        with log_context("fund", "获取基金信息"):
            fund = await get_fund_info()
```

### 8.3 配置说明

#### 日志级别控制
```bash
# 生产环境
APP_ENV=prod

# 开发环境
APP_ENV=test
```

#### 日志文件结构
```
backend/logs/
# 基础分类
├── api.log           # 内部API相关日志
├── database.log      # 数据库日志
├── scheduler.log     # 定时任务日志
├── business.log      # 业务逻辑日志
├── error.log         # 错误日志
├── system.log        # 系统日志
├── security.log      # 安全日志
# 外部服务分类
├── fund_api.log      # 基金API调用日志
├── okx_api.log       # OKX交易所API日志
├── wise_api.log      # Wise金融API日志
├── paypal_api.log    # PayPal支付API日志
├── exchange_api.log  # 汇率服务API日志
└── external_other.log # 其他外部API日志
```

### 8.4 最佳实践

#### 合理使用日志级别
- **DEBUG** - 详细的调试信息，仅开发环境
- **INFO** - 常规信息，如操作成功
- **WARNING** - 警告信息，需要注意但不影响功能
- **ERROR** - 错误信息，功能异常
- **CRITICAL** - 严重错误，可能导致系统崩溃

#### 添加有用的上下文
```python
log_api(
    "用户操作失败",
    level="ERROR",
    extra_data={
        "user_id": user.id,
        "operation": "update_profile",
        "error_code": "VALIDATION_FAILED",
        "input_data": sanitized_input
    },
    request_id=request_id
)
```

#### 避免敏感信息
不要在日志中记录：
- 密码
- API密钥
- 个人敏感信息
- 完整的信用卡号

### 8.5 故障排查

#### 常见问题
1. **日志页面打不开** - 检查 `/logs-viewer` 路径和模板文件
2. **API返回404** - 确保日志路由已注册到main.py中
3. **日志不显示** - 检查日志文件或控制台输出
4. **过滤不生效** - 确保使用正确的分类名称

#### 调试技巧
```bash
# 查看API响应
curl "https://your-app.railway.app/api/v1/logs?limit=10"

# 检查日志统计
curl "https://your-app.railway.app/api/v1/logs/stats"

# 获取分类列表
curl "https://your-app.railway.app/api/v1/logs/categories"
```

### 8.6 维护建议
- **定期清理** - 建议每周清理一次旧日志
- **监控重要指标** - 定期检查错误日志数量趋势
- **性能考虑** - 避免在循环中记录大量DEBUG日志

---

## 📞 技术支持

### 现有代码迁移指南
如果你的代码中已经在使用旧的日志方式，可以按照以下步骤快速迁移：

#### 1. 替换导入语句
```python
# 旧的方式
from loguru import logger

# 新的方式
from app.utils.logger import log_fund_api, log_okx_api
```

#### 2. 替换日志调用
```python
# 旧的方式
logger.info("获取基金净值成功")

# 新的方式
log_fund_api("获取基金净值成功", extra_data={"fund_code": "000001"})
```

#### 3. 服务对应关系
| 服务文件 | 推荐使用的日志函数 |
|----------|-------------------|
| `fund_api_service.py` | `log_fund_api` |
| `okx_api_service.py` | `log_okx_api` |
| `wise_api_service.py` | `log_wise_api` |
| `paypal_api_service.py` | `log_paypal_api` |
| `exchange_rate_service.py` | `log_exchange_api` |

**系统现在支持完整的日志管理和自动化日志功能！** 🎊 