# 🧩 多资产投资记录与收益分析系统

## 📖 项目概述

一个跨平台的个人资产投资记录与收益分析系统，支持基金、数字货币、万能险、银行理财等多种资产类型的管理和分析。

### 🎯 核心功能
- 跨平台资产记录与管理
- 多币种支持，自动折算为基准币种
- 自动计算累计收益、年化收益、资产结构
- 投资决策辅助与行为追踪
- 实时数据同步（OKX、Wise等平台）

## 🛠️ 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS + shadcn/ui
- **图表**: Recharts
- **状态管理**: Zustand
- **构建工具**: Vite

### 后端
- **框架**: Python + FastAPI
- **数据库**: SQLite
- **API文档**: Swagger/OpenAPI
- **定时任务**: APScheduler

### 开发工具
- **包管理**: pnpm (前端) + poetry (后端)
- **代码规范**: ESLint + Prettier
- **类型检查**: TypeScript

## 📁 项目结构

```
personalfinance/
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
└── README.md
```

## 🚀 开发阶段规划

### 阶段一：MVP基础功能 (1-2周)
- [x] 项目初始化与基础架构
- [ ] 数据库设计与模型定义
- [ ] 基础API开发（CRUD操作）
- [ ] 前端基础界面搭建
- [ ] 资产交易记录录入功能
- [ ] 基础持仓计算逻辑

### 阶段二：核心分析功能 (1-2周)
- [ ] 收益计算算法实现
- [ ] 资产结构分析
- [ ] 基础图表展示
- [ ] 操作日志模块
- [ ] 数据导出功能

### 阶段三：API集成 (1-2周)
- [ ] OKX API集成
- [ ] Wise API集成
- [ ] 汇率转换功能
- [ ] 自动数据同步
- [ ] 定时任务配置

### 阶段四：高级功能 (1周)
- [ ] 风险分析指标
- [ ] 投资目标追踪
- [ ] 提醒功能
- [ ] 性能优化
- [ ] 用户体验优化

## 🏃‍♂️ 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- pnpm
- poetry

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd personalfinance
```

2. **安装前端依赖**
```bash
cd frontend
pnpm install
```

3. **安装后端依赖**
```bash
cd backend
poetry install
```

4. **启动开发服务器**
```bash
# 启动后端
cd backend
poetry run uvicorn app.main:app --reload

# 启动前端
cd frontend
pnpm dev
```

## 📝 开发规范

- 使用TypeScript进行类型安全开发
- 遵循ESLint和Prettier代码规范
- 提交前进行代码格式化
- 重要功能需要编写测试用例

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## �� 许可证

MIT License 