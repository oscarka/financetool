# Web3 API 配置说明

## 1. 获取Web3 API密钥

1. 登录OKX Web3官网 (https://web3.okx.com)
2. 进入"开发者中心" -> "API管理"
3. 创建新的API Key，获取以下信息：
   - API Key
   - Secret Key  
   - Passphrase
   - Project ID
   - Account ID

## 2. 配置文件设置

### 方法一：使用环境变量文件（推荐）

在 `backend` 目录下创建 `.env.prod` 文件（生产环境）：

```bash
# 复制示例文件
cp env.prod.example .env.prod
```

然后编辑 `.env.prod` 文件，填入您的Web3 API信息：

```bash
# Web3 API配置
WEB3_API_KEY=你的Web3_APIKey
WEB3_API_SECRET=你的Web3_SecretKey
WEB3_PROJECT_ID=你的Web3_ProjectId
WEB3_ACCOUNT_ID=你的Web3_AccountId
WEB3_PASSPHRASE=你的Web3_Passphrase
```

### 方法二：直接设置环境变量

```bash
export WEB3_API_KEY="你的Web3_APIKey"
export WEB3_API_SECRET="你的Web3_SecretKey"
export WEB3_PROJECT_ID="你的Web3_ProjectId"
export WEB3_ACCOUNT_ID="你的Web3_AccountId"
export WEB3_PASSPHRASE="你的Web3_Passphrase"
```

## 3. 环境说明

- **测试环境**：使用测试网络的Project ID和Account ID
- **生产环境**：使用主网的Project ID和Account ID

## 4. 验证配置

配置完成后，重启后端服务，然后测试以下接口：

### Web3配置信息
```bash
curl "http://localhost:8000/api/v1/okx/web3/config"
```

### Web3连接测试
```bash
curl "http://localhost:8000/api/v1/okx/web3/test"
```

### Web3账户余额
```bash
curl "http://localhost:8000/api/v1/okx/web3/balance"
```

### Web3代币列表
```bash
curl "http://localhost:8000/api/v1/okx/web3/tokens"
```

### Web3交易记录
```bash
curl "http://localhost:8000/api/v1/okx/web3/transactions?limit=10"
```

## 5. 运行测试脚本

```bash
cd backend
python test_web3_api.py
```

## 6. 前端访问

配置完成后，可以在前端OKX管理页面的"Web3账户余额"、"Web3代币列表"和"Web3交易记录"tab页中查看相关数据。

## 7. API接口说明

### 获取账户总价值
- **接口**: `/api/v1/okx/web3/balance`
- **方法**: GET
- **说明**: 获取Web3账户的总代币价值

### 获取代币列表
- **接口**: `/api/v1/okx/web3/tokens`
- **方法**: GET
- **说明**: 获取Web3账户持有的所有代币列表

### 获取交易记录
- **接口**: `/api/v1/okx/web3/transactions`
- **方法**: GET
- **参数**: limit (可选，默认100)
- **说明**: 获取Web3账户的交易记录

## 8. 安全提醒

- 请妥善保管您的Web3 API密钥信息
- 不要将包含真实API密钥的文件提交到版本控制系统
- 建议在生产环境中使用环境变量而不是配置文件
- 定期更换API密钥以提高安全性
- Web3 API密钥与OKX交易API密钥是独立的，需要分别配置 