# 系统架构设计

## 🏗️ 整体架构

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

## 📦 模块划分

### 1. 前端模块 (React + TypeScript)

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

### 2. 后端模块 (FastAPI + Python)

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

## 🔄 数据流设计

### 1. 操作记录流程

```
用户录入操作 → 前端验证 → API调用 → 后端验证 → 数据库存储 → 持仓重新计算 → 返回结果
```

### 2. 基金数据同步流程

```
定时任务触发 → 获取基金列表 → 调用外部API → 更新净值表 → 重新计算收益 → 更新持仓
```

### 3. 持仓计算流程

```
操作记录变更 → 获取最新价格 → 计算平均成本 → 计算当前市值 → 计算收益 → 更新持仓表
```

## 🛠️ 技术选型

### 前端技术栈
- **框架**: React 18 + TypeScript
- **状态管理**: Zustand (轻量级)
- **UI组件**: shadcn/ui + Tailwind CSS
- **图表**: Recharts
- **表单**: React Hook Form + Zod
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 后端技术栈
- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **ORM**: SQLAlchemy 2.0
- **验证**: Pydantic
- **定时任务**: APScheduler
- **HTTP客户端**: httpx
- **日志**: loguru

### 开发工具
- **包管理**: pnpm (前端) + poetry (后端)
- **代码规范**: ESLint + Prettier + Black
- **类型检查**: TypeScript + mypy
- **测试**: Jest (前端) + pytest (后端)

## 🔐 安全设计

### 1. 数据验证
- 前端：Zod schema验证
- 后端：Pydantic模型验证
- 数据库：约束和触发器

### 2. 错误处理
- 统一错误响应格式
- 详细错误日志记录
- 用户友好的错误提示

### 3. 数据备份
- 定期数据库备份
- 操作日志记录
- 数据导出功能

## 📊 性能优化

### 1. 数据库优化
- 合理索引设计
- 查询优化
- 连接池管理

### 2. 前端优化
- 组件懒加载
- 数据缓存
- 虚拟滚动

### 3. API优化
- 响应缓存
- 批量操作
- 分页查询

## 🚀 部署方案

### 开发环境
- 本地SQLite数据库
- 热重载开发服务器
- 本地文件存储

### 生产环境
- 云数据库（可选）
- Docker容器化
- 反向代理
- 监控和日志

## 📈 扩展性设计

### 1. 模块化设计
- 每个资产类型独立模块
- 插件式API集成
- 配置驱动

### 2. 数据模型扩展
- 版本化API
- 向后兼容
- 数据迁移

### 3. 功能扩展
- 新资产类型支持
- 新分析指标
- 新数据源集成 