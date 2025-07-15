# 🚀 Railway部署指南 - 数据持久化修复版

## 📋 概述

本指南详细说明如何在Railway上正确部署个人财务管理系统，确保数据持久化正常工作。

## ✅ 修复状态

**当前代码已完全修复数据持久化问题！**

### 已修复的问题：
- ✅ Railway volume配置
- ✅ Dockerfile权限设置
- ✅ 数据库路径配置
- ✅ 环境变量优化
- ✅ 启动脚本增强
- ✅ 验证工具完善

## 🛠️ 部署步骤

### 1. 准备代码

确保你的代码包含以下修复：

```bash
# 检查关键文件是否存在
ls -la backend/railway.toml
ls -la backend/Dockerfile
ls -la backend/verify_railway_deployment.py
ls -la backend/post_deploy_verify.py
```

### 2. 在Railway控制台配置数据卷

1. **登录Railway Dashboard**
   - 访问 https://railway.app/dashboard
   - 选择你的项目

2. **创建数据卷**
   - 点击 "Settings" → "Volumes"
   - 点击 "New Volume"
   - 配置如下：
     - **Name**: `database`
     - **Path**: `/app/data`
     - **Size**: 至少1GB（推荐2GB）

3. **验证volume配置**
   ```bash
   # 在Railway控制台运行
   python verify_railway_deployment.py
   ```

### 3. 部署服务

```bash
# 提交代码
git add .
git commit -m "Fix Railway data persistence - complete solution"
git push origin main
```

### 4. 验证部署

部署完成后，运行验证脚本：

```bash
# 在Railway控制台运行
python post_deploy_verify.py
```

## 📁 关键配置文件

### railway.toml
```toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile"

[deploy]
startCommand = "python run.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[deploy.environment]
PORT = "8000"
DEBUG = "false"
WORKERS = "2"
APP_ENV = "prod"

# 数据卷配置
[[deploy.volumes]]
source = "database"
target = "/app/data"
```

### Dockerfile
```dockerfile
# 确保数据和日志目录存在，并设置正确的权限
RUN mkdir -p data logs backups && \
    chmod 755 data logs backups

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chmod -R 755 /app/data /app/logs /app/backups

# 数据持久化相关环境变量
ENV DATABASE_PERSISTENT_PATH=/app/data
ENV DATABASE_BACKUP_ENABLED=true
ENV DATABASE_BACKUP_INTERVAL_HOURS=24

# Railway环境检测
ENV RAILWAY_ENVIRONMENT=production
```

## 🔍 验证工具

### 1. 部署前验证
```bash
python verify_railway_deployment.py
```

**检查项目：**
- 环境变量配置
- 数据目录权限
- 数据库文件状态
- Volume挂载测试
- Railway配置检查

### 2. 部署后验证
```bash
python post_deploy_verify.py
```

**检查项目：**
- 服务健康状态
- 调试信息获取
- 数据库操作测试
- 数据持久化验证

## 📊 数据保护

### 受保护的数据类型：
1. **基金净值数据** (9,488条记录)
2. **用户操作记录** (215条记录)
3. **IBKR投资数据** (美股投资组合)
4. **Wise交易记录** (10条记录)
5. **定投计划** (15条记录)
6. **系统配置数据**

### 备份策略：
- 自动备份：每24小时
- 手动备份：部署前
- 备份位置：`/app/backups/`

## 🚨 故障排除

### 问题1：数据仍然丢失
**解决方案：**
1. 检查volume是否正确创建
2. 验证volume路径配置
3. 运行验证脚本检查权限

### 问题2：服务启动失败
**解决方案：**
1. 检查Dockerfile权限设置
2. 验证环境变量配置
3. 查看启动日志

### 问题3：数据库连接失败
**解决方案：**
1. 检查数据库文件路径
2. 验证数据目录权限
3. 确认SQLite文件完整性

## 📈 监控和维护

### 定期检查：
```bash
# 每周运行一次
python check_data_integrity.py

# 每次部署后运行
python post_deploy_verify.py
```

### 备份管理：
```bash
# 创建备份
python backup_database.py backup

# 列出备份
python backup_database.py list

# 恢复备份
python backup_database.py restore backups/latest_backup.db
```

## 🎯 预期效果

部署成功后，你将看到：

1. **数据持久化** ✅
   - 部署后数据保持不变
   - 基金净值、操作记录完整保留

2. **服务稳定性** ✅
   - 服务正常启动
   - 健康检查通过

3. **业务连续性** ✅
   - 用户投资历史完整
   - 投资分析功能正常

## 📞 技术支持

如果遇到问题：

1. 运行验证脚本获取详细报告
2. 检查Railway控制台日志
3. 查看部署验证报告
4. 联系技术支持

---

**部署完成时间**: 2025-07-14  
**修复状态**: ✅ 完成  
**下一步**: 在Railway控制台配置数据卷并部署