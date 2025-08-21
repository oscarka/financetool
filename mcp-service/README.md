# MCP智能服务

独立部署的MCP协议服务，提供AI分析和智能图表功能。

## 🚀 功能特性

- **AI分析**: 集成DeepSeek AI，支持自然语言查询转SQL
- **智能图表**: 自动生成适合的图表配置
- **数据库查询**: 支持PostgreSQL数据库查询
- **模板匹配**: 预定义查询模板，提高响应速度
- **模拟数据**: 开发测试时支持模拟数据

## 🏗️ 架构设计

```
MCP服务 (端口3001)
├── AI分析服务 (DeepSeek AI)
├── 图表生成服务
├── 数据库查询服务
└── MCP协议处理
```

## 📦 部署方式

### Railway部署

1. 在Railway中创建新服务
2. 连接GitHub仓库
3. 设置环境变量
4. 部署到端口3001

### 环境变量配置

```bash
# 必需配置
DEEPSEEK_API_KEY=your_api_key
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# 可选配置
USE_MOCK_DATA=false
DEBUG=false
```

## 🔧 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 3001
```

### 使用模拟数据

```bash
USE_MOCK_DATA=true python -m uvicorn app.main:app --host 0.0.0.0 --port 3001
```

## 📡 API接口

### 健康检查
- `GET /health` - 服务健康状态

### MCP查询
- `POST /query` - 执行SQL查询
- `POST /nl-query` - 自然语言查询
- `POST /schema` - 获取数据库Schema
- `POST /generate-chart` - 生成图表配置

## 🔗 与主后端集成

主后端通过环境变量`MCP_SERVER_URL`配置MCP服务地址：

```bash
MCP_SERVER_URL=http://your-mcp-service-url:3001
```

## 🧪 测试

### 测试连接

```bash
curl http://localhost:3001/health
```

### 测试自然语言查询

```bash
curl -X POST http://localhost:3001/nl-query \
  -H "Content-Type: application/json" \
  -d '{"question": "显示各平台的资产分布"}'
```

## 📊 性能优化

- 使用异步处理
- 连接池管理
- 智能缓存
- 资源限制

## 🚨 注意事项

1. 确保DeepSeek API Key有效
2. 数据库连接配置正确
3. 生产环境设置适当的资源限制
4. 监控服务性能和内存使用
