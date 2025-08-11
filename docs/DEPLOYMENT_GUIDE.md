# 🚀 部署和运维指南

## 🌐 Railway部署

### 后端部署
- **项目**: financetool
- **环境**: production
- **服务**: zesty-flexibility
- **状态**: ✅ 部署成功

### 部署配置
- **数据库**: PostgreSQL (Railway托管)
- **环境变量**: 自动从Railway配置加载
- **CORS配置**: 允许所有来源 `["*"]`
- **健康检查**: `/health` 端点

### 部署流程
1. 代码推送到GitHub
2. Railway自动检测变更
3. 重新构建和部署
4. 健康检查验证

## ☁️ Cloudflare Workers

### 概述
Cloudflare Workers用于前端应用的边缘部署和CDN加速。

### 设置指南
1. **安装Wrangler CLI**
   ```bash
   npm install -g wrangler
   ```

2. **配置项目**
   ```bash
   wrangler init
   ```

3. **部署配置**
   - 复制 `wrangler.toml.template` 为 `wrangler.toml`
   - 配置必要的环境变量
   - 设置路由规则

### 功能特性
- **边缘计算**: 全球分布式部署
- **CDN加速**: 静态资源全球分发
- **API代理**: 前端API请求代理
- **安全防护**: DDoS防护和WAF

## 🗄️ 数据库管理

### 动态迁移检查

#### 迁移状态监控
- **版本同步**: 确保数据库结构与alembic版本一致
- **自动检测**: 检测表结构变更
- **迁移建议**: 提供迁移路径建议

#### 常见问题处理
1. **版本不一致**
   ```bash
   # 强制同步版本号
   alembic stamp head
   ```

2. **重复字段错误**
   - 检查数据库实际结构
   - 对比alembic迁移文件
   - 必要时重新生成迁移

3. **表结构错位**
   - 备份当前数据
   - 重新运行迁移
   - 验证数据完整性

### 数据备份策略
- **自动备份**: 每日自动备份
- **手动备份**: 重要操作前手动备份
- **备份验证**: 定期验证备份完整性
- **恢复测试**: 定期测试恢复流程

## 🔧 环境配置

### 开发环境
```bash
# 数据库配置
DATABASE_URL=sqlite:///./data/personalfinance.db
DATABASE_PERSISTENT_PATH=./data

# API配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 测试环境
```bash
# 数据库配置
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/financetool_test

# API配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 生产环境
```bash
# 数据库配置
DATABASE_URL=postgresql://financetool_user:financetool_pass@localhost:5432/financetool_prod

# API配置
CORS_ORIGINS=["*"]

# 性能配置
PERFORMANCE_MONITORING_ENABLED=true
CACHE_ENABLED=true
```

## 📊 监控和日志

### 性能监控
- **响应时间**: API响应时间监控
- **吞吐量**: 请求处理能力监控
- **错误率**: 错误请求比例监控
- **资源使用**: CPU、内存、数据库连接监控

### 日志管理
- **结构化日志**: JSON格式日志输出
- **日志级别**: DEBUG、INFO、WARNING、ERROR
- **日志轮转**: 自动日志文件轮转
- **日志聚合**: 集中日志收集和分析

### 健康检查
- **API健康**: `/health` 端点检查
- **数据库连接**: 数据库连接状态检查
- **外部服务**: 第三方API服务状态检查
- **系统资源**: 系统资源使用情况检查

## 🚨 故障处理

### 常见故障
1. **API无响应**
   - 检查服务状态
   - 查看错误日志
   - 重启服务

2. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串
   - 检查网络连接

3. **CORS错误**
   - 验证CORS配置
   - 检查请求来源
   - 更新CORS策略

### 应急响应
- **快速响应**: 15分钟内响应
- **问题分类**: 按严重程度分类
- **解决方案**: 提供临时和永久解决方案
- **事后分析**: 故障原因分析和改进措施

## 📈 性能优化

### 前端优化
- **代码分割**: 按需加载组件
- **资源压缩**: CSS/JS文件压缩
- **图片优化**: WebP格式和懒加载
- **缓存策略**: 静态资源缓存

### 后端优化
- **数据库查询**: 优化SQL查询
- **API缓存**: Redis缓存热点数据
- **连接池**: 数据库连接池管理
- **异步处理**: 非阻塞异步处理

### 网络优化
- **CDN加速**: 全球内容分发
- **HTTP/2**: 多路复用和头部压缩
- **Gzip压缩**: 响应数据压缩
- **连接复用**: Keep-Alive连接

---

**文档版本**: 1.0
**最后更新**: 2025年8月
**维护状态**: 活跃维护
**适用环境**: 开发、测试、生产
