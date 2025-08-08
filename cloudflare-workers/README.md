# FinanceTool Cloudflare Worker 代理

这是一个 Cloudflare Worker 项目，用于代理 Railway 后端 API 请求，解决国内访问 Railway 需要 VPN 的问题。

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

编辑 `wrangler.toml` 文件，更新以下配置：

```toml
[vars]
RAILWAY_API_URL = "https://your-app.railway.app"  # 替换为您的 Railway 应用 URL
CORS_ORIGINS = "*"
ENABLE_CACHE = "true"
CACHE_TTL = "300"
```

### 3. 本地开发

```bash
npm run dev
```

### 4. 部署到 Cloudflare

```bash
# 部署到生产环境
npm run deploy:production

# 部署到测试环境
npm run deploy:staging
```

## 📋 配置说明

### 域名配置

在 Cloudflare Dashboard 中配置您的域名：

1. 进入 Cloudflare Dashboard
2. 选择您的域名
3. 进入 "Workers" 部分
4. 创建新的 Worker 路由：
   - `api.yourdomain.com/*` → 指向您的 Worker
   - `*.yourdomain.com/api/*` → 指向您的 Worker

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `RAILWAY_API_URL` | Railway 后端 API URL | 必需 |
| `CORS_ORIGINS` | CORS 允许的源 | `*` |
| `ENABLE_CACHE` | 是否启用缓存 | `true` |
| `CACHE_TTL` | 缓存时间（秒） | `300` |

## 🔧 功能特性

### 1. 智能缓存
- GET 请求自动缓存 5 分钟
- 同步和执行操作不缓存
- 提高响应速度，减少 Railway 负载

### 2. CORS 支持
- 自动处理跨域请求
- 支持所有必要的 HTTP 方法
- 支持自定义请求头

### 3. 健康检查
- 访问 `/health` 路径进行健康检查
- 返回 Worker 状态信息

### 4. 错误处理
- 友好的错误信息
- 详细的日志记录
- 自动重试机制

## 📊 性能优化

### 缓存策略
```javascript
// 缓存条件
const shouldCache = ENABLE_CACHE && 
                   request.method === 'GET' && 
                   !path.includes('/sync') && 
                   !path.includes('/execute');
```

### 请求优化
- 移除不必要的请求头
- 添加代理标识
- 保持原始请求体

## 🔍 监控和调试

### 查看日志
在 Cloudflare Dashboard 的 Workers 部分查看实时日志。

### 测试健康检查
```bash
curl https://api.yourdomain.com/health
```

### 测试 API 代理
```bash
curl https://api.yourdomain.com/api/v1/funds/info
```

## 🛠️ 故障排除

### 常见问题

1. **Worker 部署失败**
   - 检查 `wrangler.toml` 配置
   - 确认 Cloudflare 账户权限

2. **API 请求失败**
   - 检查 `RAILWAY_API_URL` 是否正确
   - 确认 Railway 应用是否正常运行

3. **缓存不生效**
   - 检查 `ENABLE_CACHE` 设置
   - 确认请求路径是否被缓存策略排除

### 调试模式

启用详细日志：
```javascript
// 在 index.js 中添加
console.log('Request URL:', targetUrl.toString());
console.log('Request headers:', Object.fromEntries(headers));
```

## 📈 成本分析

### Cloudflare Workers 免费计划
- 每天 100,000 次请求
- 无带宽限制
- 全球 CDN 加速

### 使用建议
- 对于个人项目完全免费
- 监控请求量，避免超出限制
- 合理使用缓存减少请求次数

## 🔄 更新和维护

### 更新 Worker
```bash
npm run deploy:production
```

### 回滚版本
在 Cloudflare Dashboard 中可以查看和回滚到之前的版本。

### 监控使用量
在 Cloudflare Dashboard 中监控：
- 请求数量
- 响应时间
- 错误率
- 缓存命中率
