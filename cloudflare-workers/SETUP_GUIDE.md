# 🚀 Cloudflare Workers 设置指南

## 📋 快速开始

### 1. 安装依赖
```bash
cd cloudflare-workers
npm install
```

### 2. 配置 Worker
```bash
# 复制模板文件
cp wrangler.toml.template wrangler.toml

# 编辑配置文件，修改您的 Railway 后端地址
nano wrangler.toml
```

### 3. 修改配置
在 `wrangler.toml` 中修改：
```toml
[vars]
RAILWAY_API_URL = "https://your-railway-backend.up.railway.app"  # 替换为您的地址
```

### 4. 部署 Worker
```bash
wrangler deploy
```

## 🔧 配置说明

### 重要文件
- ✅ `src/index.js` - Worker 核心代码（Git 跟踪）
- ✅ `wrangler.toml.template` - 配置模板（Git 跟踪）
- ❌ `wrangler.toml` - 个人配置（Git 忽略）
- ❌ `node_modules/` - 依赖文件（Git 忽略）
- ❌ `.wrangler/` - 本地缓存（Git 忽略）

### 环境变量
- `RAILWAY_API_URL`: 您的 Railway 后端地址
- `CORS_ORIGINS`: 跨域设置（通常保持 "*"）
- `ENABLE_CACHE`: 是否启用缓存
- `CACHE_TTL`: 缓存时间（秒）

## 🚨 注意事项

1. **不要提交个人配置** - `wrangler.toml` 已加入 .gitignore
2. **修改后端地址** - 确保指向正确的 Railway 后端
3. **测试部署** - 部署后测试 API 代理是否正常工作

## 🔗 相关链接

- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Wrangler CLI 文档](https://developers.cloudflare.com/workers/wrangler/)
