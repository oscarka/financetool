# Railway 日志查看方法指南

## 概述

Railway 提供了多种方式来查看和管理日志，这样你就不需要手动粘贴日志到对话框里了。以下是主要的日志查看方法：

## 1. Railway CLI (命令行工具)

这是最直接的方法，可以在本地直接查看Railway上的日志。

### 安装 Railway CLI

```bash
# 使用 npm 安装
npm install -g @railway/cli

# 使用 Homebrew (macOS)
brew install railway

# 使用脚本安装
bash <(curl -fsSL cli.new)

# 使用 Scoop (Windows)
scoop install railway
```

### 认证和连接项目

```bash
# 登录Railway账户
railway login

# 连接到现有项目
railway link

# 选择特定的服务
railway service
```

### 查看日志命令

```bash
# 查看最新部署的日志
railway logs

# 查看部署日志
railway logs --deployment

# 查看构建日志  
railway logs --build

# 输出JSON格式
railway logs --json
```

## 2. Web界面日志查看

### Log Explorer (推荐)
- 在Railway仪表板中点击顶部导航的 "Observability" 按钮
- 可以查看整个环境的所有服务日志
- 支持日期范围选择
- 支持列显示切换
- 支持强大的过滤功能

### 部署面板
- 在服务窗口中点击特定部署
- 适合调试特定应用程序故障
- 点击 "Build Logs" 标签查看构建日志

## 3. 日志过滤语法

Railway支持强大的自定义过滤语法：

### 基本过滤
```text
# 搜索包含特定词的日志
request

# 精确匹配
"request handled"

# 按日志级别过滤
@level:error
@level:warn
@level:info

# 组合条件
@level:error AND "failed to send batch"
```

### 环境日志过滤
```text
# 按服务过滤
@service:<service_id>

# 排除特定服务
-@service:<postgres_service_id>

# 多服务过滤
@service:<service1_id> OR @service:<service2_id>
```

### HTTP日志过滤
```text
# 按路径过滤
@path:/api/v1/users

# 按HTTP状态码
@httpStatus:500

# 按请求ID
@requestId:<request_id>

# 按IP地址
@srcIp:66.33.22.11

# 组合条件
@path:/api/v1/users AND @httpStatus:500
```

## 4. 第三方集成工具

### Locomotive (Railway Sidecar)
一个开源的Railway边车服务，可以将日志发送到外部服务：

```bash
# 支持的输出目标
- Discord Webhooks
- Slack Webhooks  
- Grafana Loki
- Datadog
- Axiom
- BetterStack
- 自定义Webhook
```

项目地址：https://github.com/FerretCode/locomotive

### Railway-Chord (已归档)
Vector日志导出工具，可以将Railway日志导出到Vector：
- 支持Datadog、Logtail
- 项目已归档但代码仍可参考

## 5. Railway CLI高级用法

### 环境变量认证
```bash
# 项目Token (用于项目级操作)
export RAILWAY_TOKEN=your_project_token
railway logs

# 账户Token (用于所有操作)  
export RAILWAY_API_TOKEN=your_account_token
railway logs
```

### 实时日志流
```bash
# 实时查看日志流
railway logs

# 在CI/CD中使用
railway up --ci  # 只显示构建日志并在完成后退出
```

### 多服务/环境管理
```bash
# 指定环境查看日志
railway logs --environment production

# 切换环境
railway environment

# 查看项目状态
railway status
```

## 6. 结构化日志

Railway支持JSON格式的结构化日志，便于查询和分析：

```javascript
// 结构化日志示例
console.log(JSON.stringify({
  message: "A minimal structured log",
  level: "info", 
  customAttribute: "value",
  userId: 123,
  productId: 456
}));
```

查询结构化日志：
```text
@customAttribute:value
@userId:123
@level:info AND @productId:456
```

## 7. 推荐的日志查看工作流

1. **开发阶段**：使用 `railway logs` CLI命令实时查看日志
2. **调试问题**：使用Web界面的Log Explorer，利用过滤功能定位问题
3. **生产监控**：考虑集成Locomotive等工具，将日志发送到专业监控平台
4. **CI/CD集成**：在自动化流程中使用CLI工具检查部署状态

## 8. 最佳实践

- 使用结构化日志格式，便于查询和分析
- 设置合适的日志级别 (debug, info, warn, error)
- 利用Railway的过滤语法快速定位问题
- 在生产环境考虑集成外部日志监控服务
- 定期查看日志，及时发现潜在问题

## 总结

通过以上方法，你可以：
- 使用CLI在本地直接查看Railway日志
- 在Web界面使用强大的过滤功能
- 集成第三方工具进行日志监控
- 避免手动复制粘贴日志的麻烦

推荐主要使用Railway CLI和Web界面的Log Explorer，这两种方法已经能满足大部分日志查看需求。