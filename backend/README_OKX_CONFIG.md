# OKX API 配置说明

## 1. 获取OKX API密钥

1. 登录OKX官网 (https://www.okx.com)
2. 进入"账户中心" -> "API管理"
3. 创建新的API Key，获取以下信息：
   - API Key
   - Secret Key  
   - Passphrase

## 2. 配置文件设置

### 方法一：使用环境变量文件（推荐）

在 `backend` 目录下创建 `.env.test` 文件（测试环境）：

```bash
# 复制示例文件
cp env.test.example .env.test
```

然后编辑 `.env.test` 文件，填入您的OKX API信息：

```bash
# OKX API配置
OKX_API_KEY=你的APIKey
OKX_SECRET_KEY=你的SecretKey
OKX_PASSPHRASE=你的Passphrase
OKX_SANDBOX=true  # 测试环境使用沙盒
```

### 方法二：直接设置环境变量

```bash
export OKX_API_KEY="你的APIKey"
export OKX_SECRET_KEY="你的SecretKey"
export OKX_PASSPHRASE="你的Passphrase"
export OKX_SANDBOX="true"  # 或 "false"
```

## 3. 环境说明

- **测试环境**：`OKX_SANDBOX=true`，使用OKX沙盒环境
- **生产环境**：`OKX_SANDBOX=false`，使用OKX正式环境

## 4. 验证配置

配置完成后，重启后端服务，然后测试以下接口：

### 公有接口（无需API Key）
```bash
curl "http://localhost:8000/api/v1/funds/okx/ticker?inst_id=BTC-USDT"
```

### 私有接口（需要API Key）
```bash
curl "http://localhost:8000/api/v1/funds/okx/account"
```

## 5. 安全提醒

- 请妥善保管您的API密钥信息
- 不要将包含真实API密钥的文件提交到版本控制系统
- 建议在生产环境中使用环境变量而不是配置文件
- 定期更换API密钥以提高安全性 