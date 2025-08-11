# 🧩 多资产投资记录与收益分析系统

## 📖 项目概述

一个跨平台的个人资产投资记录与收益分析系统，支持基金、数字货币、万能险、银行理财等多种资产类型的管理和分析。

### 🎯 核心功能
- 跨平台资产记录与管理
- 多币种支持，自动折算为基准币种
- 自动计算累计收益、年化收益、资产结构
- 投资决策辅助与行为追踪
- 实时数据同步（OKX、Wise、IBKR等平台）

## 🛠️ 技术栈

### 前端
- **Web端**: React 18 + TypeScript + Ant Design
- **移动端**: Flutter (Web/iOS/Android)
- **样式**: Tailwind CSS + shadcn/ui
- **图表**: Recharts
- **状态管理**: Zustand
- **构建工具**: Vite

### 后端
- **框架**: Python + FastAPI
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **API文档**: Swagger/OpenAPI
- **定时任务**: APScheduler
- **缓存**: Redis + 内存缓存

### 开发工具
- **包管理**: pnpm (前端) + poetry (后端)
- **代码规范**: ESLint + Prettier
- **类型检查**: TypeScript
- **部署**: Railway (后端) + Cloudflare Workers (前端)

## 📁 项目结构

```
financetool/
├── frontend/                 # React前端应用
│   ├── src/
│   │   ├── components/      # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── hooks/          # 自定义Hooks
│   │   ├── stores/         # Zustand状态管理
│   │   ├── types/          # TypeScript类型定义
│   │   └── utils/          # 工具函数
│   ├── public/             # 静态资源
│   └── package.json
├── flutter_app/             # Flutter移动应用
│   ├── lib/
│   │   ├── components/     # Flutter组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   └── models/        # 数据模型
│   └── pubspec.yaml
├── backend/                 # FastAPI后端应用
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # 应用入口
│   ├── data/               # 数据库文件
│   └── requirements.txt
├── docs/                   # 项目文档
│   ├── TECHNICAL_GUIDE.md  # 技术指南
│   └── DEPLOYMENT_GUIDE.md # 部署指南
└── README.md
```

## 🚀 核心特性

### 1. 汇率快照系统
- **多货币支持**: 50+种数字货币 + 传统货币
- **智能汇率转换**: IP → USDT → USD → CNY等复杂路径
- **历史汇率记录**: 完整的汇率快照数据
- **缓存优化**: Redis + 内存缓存提升性能

### 2. 资产快照系统
- **多平台集成**: OKX、Wise、IBKR、支付宝
- **实时数据同步**: 自动和手动触发快照生成
- **智能数据过滤**: 过滤无效和小额数据
- **资产类型映射**: 统一的资产分类标准

### 3. 跨平台支持
- **Web端**: React + TypeScript + Ant Design
- **移动端**: Flutter (iOS/Android/Web)
- **响应式设计**: 支持各种屏幕尺寸
- **统一数据源**: 前后端数据完全一致

### 4. 数据分析功能
- **资产分布分析**: 饼图和柱状图展示
- **趋势分析**: 历史数据趋势图表
- **收益计算**: 累计收益和年化收益率
- **风险评估**: 基于资产结构的风险等级

## 📊 数据统计

### 当前状态
- **汇率快照**: 4,524条记录
- **资产快照**: 307条记录（过滤后）
- **支持货币**: 50+种数字货币 + 传统货币
- **支持平台**: 4个主要平台
- **部署状态**: ✅ Railway后端 + Cloudflare Workers前端

### 资产分布示例
- **基金**: 158,460.30 (95.1%) - 支付宝
- **外汇**: 8,158.23 (4.9%) - Wise
- **证券**: 42.03 (0.03%) - IBKR

## 🏃‍♂️ 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- Flutter 3.24+
- pnpm
- poetry

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/oscarka/financetool.git
cd financetool
```

#### 2. 后端设置
```bash
cd backend
poetry install
poetry run python -m alembic upgrade head
poetry run uvicorn app.main:app --reload
```

#### 3. 前端设置
```bash
cd frontend
pnpm install
pnpm dev
```

#### 4. Flutter设置
```bash
cd flutter_app
flutter pub get
flutter run
```

## 🔧 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
DATABASE_PERSISTENT_PATH=./data

# API配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# 第三方API
OKX_API_KEY=your_okx_api_key
WISE_API_TOKEN=your_wise_token
IBKR_API_KEY=your_ibkr_key
```

### 平台配置
- **OKX**: 数字货币交易平台
- **Wise**: 国际汇款和外汇
- **IBKR**: 国际证券交易
- **支付宝**: 基金投资

## 📚 文档

- **[技术指南](docs/TECHNICAL_GUIDE.md)**: Flutter技术分析、API配置等
- **[部署指南](docs/DEPLOYMENT_GUIDE.md)**: Railway部署、Cloudflare Workers等
- **[API文档](https://backend-production-2750.up.railway.app/docs)**: 后端API接口文档

## 🚀 部署

### 自动部署
- **后端**: 推送到GitHub自动触发Railway部署
- **前端**: 推送到GitHub自动触发Cloudflare Workers部署
- **数据库**: Railway托管的PostgreSQL

### 手动部署
```bash
# 后端部署
railway up

# 前端部署
wrangler publish
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 📄 许可证

MIT License

---

**项目状态**: ✅ 活跃开发
**最后更新**: 2025年8月
**维护状态**: 活跃维护 