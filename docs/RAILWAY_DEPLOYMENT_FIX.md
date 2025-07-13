# Railway部署Token配置修复指南

## 问题分析

当前部署失败的原因是GitHub Actions找不到Railway项目token：

```
Project Token not found
Error: Process completed with exit code 1
```

这是因为GitHub Actions需要`RAILWAY_TOKEN`来连接Railway部署服务，但这个token没有在GitHub仓库的secrets中配置。

## 解决方案

### 步骤1：获取Railway Token

1. **登录Railway控制台**：
   - 访问：https://railway.app/dashboard

2. **获取项目Token**：
   - 进入你的项目页面
   - 点击右上角设置图标 → "Settings"
   - 在左侧菜单选择 "Tokens"
   - 点击 "Create Token"
   - 选择权限类型：`Deploy` 或 `Admin`
   - 复制生成的token（注意：只显示一次）

### 步骤2：配置GitHub Secrets

1. **访问GitHub仓库设置**：
   - 前往：https://github.com/oscarka/financetool
   - 点击 "Settings" 标签

2. **添加Secret**：
   - 在左侧菜单选择 "Secrets and variables" → "Actions"
   - 点击 "New repository secret"
   - Name: `RAILWAY_TOKEN`
   - Secret: 粘贴从Railway复制的token
   - 点击 "Add secret"

### 步骤3：重新触发部署

配置完成后，有几种方式重新触发部署：

#### 方式1：推送新的提交
```bash
git add .
git commit -m "trigger deployment after railway token setup" --allow-empty
git push origin main
```

#### 方式2：重新运行GitHub Actions
- 在GitHub仓库页面点击 "Actions" 标签
- 找到失败的workflow
- 点击 "Re-run jobs"

## 临时绕过方案

如果暂时无法获取Railway token，可以禁用自动部署：

### 方式1：注释掉部署步骤

编辑 `.github/workflows/deploy.yml`：

```yaml
name: Smart Deploy to Railway

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      frontend-changed: ${{ steps.changes.outputs.frontend }}
      backend-changed: ${{ steps.changes.outputs.backend }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      
      - name: Detect changes
        id: changes
        run: |
          if git diff --name-only HEAD~1 | grep -q "^frontend/"; then
            echo "frontend=true" >> $GITHUB_OUTPUT
          else
            echo "frontend=false" >> $GITHUB_OUTPUT
          fi
          
          if git diff --name-only HEAD~1 | grep -q "^backend/"; then
            echo "backend=true" >> $GITHUB_OUTPUT
          else
            echo "backend=false" >> $GITHUB_OUTPUT
          fi

  # 临时禁用部署任务
  # deploy-frontend:
  #   needs: detect-changes
  #   if: needs.detect-changes.outputs.frontend-changed == 'true'
  #   runs-on: ubuntu-latest
  #   container: ghcr.io/railwayapp/cli:latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - name: Deploy Frontend to Railway
  #       run: |
  #         cd frontend
  #         railway up
  #       env:
  #         RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  # deploy-backend:
  #   needs: detect-changes
  #   if: needs.detect-changes.outputs.backend-changed == 'true'
  #   runs-on: ubuntu-latest
  #   container: ghcr.io/railwayapp/cli:latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - name: Deploy Backend to Railway
  #       run: |
  #         cd backend
  #         railway up
  #       env:
  #         RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### 方式2：手动本地部署

如果你有Railway CLI工具：

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录Railway
railway login

# 部署前端
cd frontend
railway up

# 部署后端
cd ../backend
railway up
```

## 验证修复

配置token后，可以通过以下方式验证：

1. **查看GitHub Actions**：
   - 访问：https://github.com/oscarka/financetool/actions
   - 确认最新的workflow运行成功

2. **检查Railway部署状态**：
   - 在Railway控制台查看部署日志
   - 确认前端和后端都正常运行

3. **测试PayPal功能**：
   - 访问部署后的前端URL
   - 检查PayPal菜单是否显示
   - 测试PayPal页面功能

## 总结

**根本原因**：GitHub Actions缺少Railway部署token

**解决方案**：在GitHub仓库secrets中配置`RAILWAY_TOKEN`

**预防措施**：确保所有部署相关的token和密钥都正确配置在GitHub secrets中

配置完成后，PayPal功能将正常部署到Railway平台！🚀