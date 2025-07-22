# 🚀 金融系统部署与运维总指南（Railway/主干合并/CI/CD/数据持久化）

---

## 目录
1. 前言与适用范围
2. Railway Volume 设置与数据持久化
3. Railway 部署全流程
4. 环境变量与关键配置
5. CI/CD Token 配置与常见问题
6. 安全部署与回滚方案
7. 主干合并与分支管理
8. PayPal/移动端等特殊场景说明
9. 技术支持与排障建议

---

## 1. 前言与适用范围
本指南适用于本系统在 Railway 平台的部署、数据持久化、CI/CD 自动化、主干合并、API 兼容性验证等所有关键环节。内容涵盖后端、前端、移动端、PayPal 等业务模块。

---

## 2. Railway Volume 设置与数据持久化

### 2.1 问题诊断与原理
- 数据丢失多因 volume 未正确创建/挂载、路径不一致或权限问题。
- 代码期望数据路径：`/app/data`，volume 名称：`database`。

### 2.2 创建与挂载 Volume 步骤
1. 登录 Railway Dashboard，进入你的后端项目。
2. 左侧菜单 Settings → Volumes → New Volume。
   - Name: `database`（必须一致）
   - Path: `/app/data`（必须一致）
   - Size: 推荐 2GB
3. 等待 Volume 状态变为 Active。

### 2.3 验证 Volume 挂载与权限
在 Railway 控制台运行：
```bash
ls -la /app/data
df -h /app/data
echo "test" > /app/data/test.txt
cat /app/data/test.txt
rm /app/data/test.txt
```

### 2.4 环境变量设置
在 Railway 控制台设置：
```
DATABASE_PERSISTENT_PATH=/app/data
RAILWAY_ENVIRONMENT=production
APP_ENV=prod
```

### 2.5 关键配置文件示例
**railway.toml**
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
[[deploy.volumes]]
source = "database"
target = "/app/data"
```

**Dockerfile**
```dockerfile
RUN mkdir -p data logs backups && \
    chmod 755 data logs backups
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chmod -R 755 /app/data /app/logs /app/backups
ENV DATABASE_PERSISTENT_PATH=/app/data
ENV DATABASE_BACKUP_ENABLED=true
ENV DATABASE_BACKUP_INTERVAL_HOURS=24
ENV RAILWAY_ENVIRONMENT=production
```

### 2.6 数据持久化验证
- 运行 `python verify_railway_deployment.py` 验证 volume 挂载和权限。
- 运行 `python post_deploy_verify.py` 验证服务健康和数据完整性。
- 通过 API 检查数据是否持久化：
```bash
curl -X GET "https://your-app.railway.app/api/v1/funds/nav" | jq '.data | length'
```

### 2.7 备份与恢复
- 自动备份：每 24 小时
- 手动备份：`python backup_database.py backup`
- 恢复：`python backup_database.py restore backups/latest_backup.db`

---

## 3. Railway 部署全流程

### 3.1 代码准备
确保以下文件存在：
- backend/railway.toml
- backend/Dockerfile
- backend/verify_railway_deployment.py
- backend/post_deploy_verify.py

### 3.2 部署步骤
1. 创建并挂载 volume（见上文）。
2. 配置环境变量。
3. 提交并推送代码：
```bash
git add .
git commit -m "Fix Railway data persistence - complete solution"
git push origin main
```
4. Railway 控制台点击 Redeploy。
5. 部署完成后运行验证脚本。

### 3.3 关键验证命令
```bash
python verify_railway_deployment.py
python post_deploy_verify.py
```

---

## 4. 环境变量与关键配置
- DATABASE_PERSISTENT_PATH=/app/data
- RAILWAY_ENVIRONMENT=production
- APP_ENV=prod
- VITE_API_BASE_URL=https://your-backend-service.railway.app/api/v1
- NODE_ENV=production

---

## 5. CI/CD Token 配置与常见问题

### 5.1 Railway Token 配置（GitHub Actions）
1. 登录 Railway 控制台，Settings → Tokens → Create Token，选择 Deploy/Admin 权限。
2. 复制 token（只显示一次）。
3. 打开 GitHub 仓库，Settings → Secrets and variables → Actions → New repository secret。
   - Name: RAILWAY_TOKEN
   - Secret: 粘贴 token

### 5.2 触发部署
- 推送新 commit 或在 GitHub Actions 页面 Re-run jobs。

### 5.3 常见问题与解决
- Token 缺失导致部署失败：补充 RAILWAY_TOKEN。
- 临时禁用自动部署：注释 .github/workflows/deploy.yml 中相关步骤，或本地用 Railway CLI 手动部署。

---

## 6. 安全部署与回滚方案

### 6.1 推荐安全部署流程
1. 备份当前分支：
```bash
git branch backup-$(date +%Y%m%d)
```
2. 拉取最新 main 并合并：
```bash
git fetch origin
git checkout main
git pull origin main
git checkout <feature-branch>
git merge main
```
3. 构建并测试，确认无误后推送。

### 6.2 回滚方案
- 快速回滚到上一个稳定版本：
```bash
git checkout main
git push origin main --force-with-lease
```
- 回滚到指定 commit：
```bash
git reset --hard <commit>
git push origin main --force-with-lease
```

---

## 7. 主干合并与分支管理

### 7.1 Pull Request 合并（推荐）
1. 在 GitHub 创建 Pull Request，base: main，compare: feature 分支。
2. 填写 PR 信息，等待 review。
3. 通过后点击 Merge pull request。

### 7.2 直接推送（有权限时）
```bash
git checkout main
git pull origin main
git merge <feature-branch>
git push origin main
```

### 7.3 合并后清理
```bash
git branch -d <feature-branch>
git push origin --delete <feature-branch>
```

---

## 8. PayPal/移动端等特殊场景说明

### 8.1 PayPal 集成合并
- 需通过 Pull Request 合并到 main，详见 MERGE_TO_MAIN_INSTRUCTIONS.md。
- 合并后清理本地和远程 feature 分支。
- 相关 API 路由和前端页面需同步验证。

### 8.2 移动端兼容性部署
- 前后端 API 路由需兼容移动端新功能。
- 前端环境变量 VITE_API_BASE_URL 必须指向正确后端。
- 推荐分阶段部署与验证，逐步集成移动端 UI。

---

## 9. 技术支持与排障建议

### 9.1 常见问题排查
- Volume 未挂载/权限异常：检查 /app/data 权限和挂载状态。
- Pydantic 配置报错：确保 prod.py 中 database_url 不是 property，见 RAILWAY_DEPLOYMENT_FIX_UPDATE.md。
- Token 缺失：补充 GitHub Secrets。
- API 404 或 CORS 问题：检查前后端环境变量和路由。

### 9.2 验证与监控脚本
- python verify_railway_deployment.py
- python post_deploy_verify.py
- python check_data_integrity.py
- python backup_database.py backup/list/restore

### 9.3 技术支持信息收集
- Railway 控制台截图（Volume、环境变量、部署日志）
- 验证脚本输出
- 服务健康检查 API 输出

---

> 本文档已合并并精简自原 deployment 文件夹所有文档，所有关键信息均已保留。如需详细历史变更、特殊场景说明，请查阅原文档备份。 