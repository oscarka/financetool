# PayPal API 权限配置指南

## 当前问题
PayPal API集成遇到403权限错误：
```
NOT_AUTHORIZED - Authorization failed due to insufficient permissions
```

## 解决步骤

### 1. 登录PayPal开发者控制台
访问：https://developer.paypal.com/developer/applications/

### 2. 选择你的应用程序
找到Client ID为 `Ae89JqKPrJ6lLJz1dfIHqZr2VLbjrMCuT7A7Ul99NTWSJrDA93T5R-GZQ45ZkSBgZZDSUCIJVgnanqbE` 的应用

### 3. 检查并启用所需权限
确保以下权限已启用：

#### 必需的权限范围(Scopes)：
- ✅ **openid** - 基础身份验证
- ✅ **profile** - 用户配置文件访问
- ✅ **email** - 邮箱访问
- ✅ **address** - 地址信息
- ✅ **phone** - 电话信息
- ✅ **https://uri.paypal.com/services/wallet/payment-tokens/read** - 钱包访问
- ✅ **https://uri.paypal.com/services/reporting/search/read** - 交易报告访问
- ✅ **https://uri.paypal.com/services/wallet/payment-tokens/readwrite** - 钱包读写

#### 特别重要的权限：
- **Transaction Search** - 用于获取交易记录
- **Wallet Management** - 用于获取账户余额

### 4. API访问权限
确保你的应用具有以下API访问权限：
- **Wallet API** - 用于余额查询
- **Reporting API** - 用于交易记录查询
- **Identity API** - 用于身份验证

### 5. 环境配置
确认你使用的是正确的环境：
- **Sandbox环境**：测试用途，权限相对宽松
- **Live环境**：生产环境，需要完整审核

### 6. 企业账户要求
某些API可能需要企业账户：
- 个人账户可能无法访问全部API
- 考虑升级到企业账户以获得完整权限

## 临时解决方案

如果权限问题无法立即解决，可以：

### 1. 使用模拟数据
```python
# 在 paypal_api_service.py 中添加
def get_mock_data(self):
    return {
        "balance_accounts": [
            {
                "account_id": "mock_account_1",
                "currency": "USD",
                "available_balance": 1250.50,
                "reserved_balance": 50.00,
                "total_balance": 1300.50
            }
        ],
        "transactions": [
            {
                "transaction_id": "mock_txn_1",
                "date": "2025-01-07T10:00:00Z",
                "amount": 100.00,
                "currency": "USD",
                "type": "credit",
                "status": "completed"
            }
        ]
    }
```

### 2. 降级API调用
使用基础的PayPal API，避免需要高权限的接口。

## 联系支持

如果权限问题持续存在：
1. 联系PayPal开发者支持
2. 提供应用ID和错误详情
3. 说明你需要的具体权限

## 验证修复

修复权限后，重新测试：
```bash
# 测试后端API
curl http://localhost:8000/api/v1/paypal/test

# 测试前端页面
访问：http://localhost:5173/paypal
```