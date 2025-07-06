# Wise API 配置说明

## 概述

Wise API集成提供了以下功能：
- 获取账户余额信息
- 获取交易记录
- 获取实时汇率和历史汇率
- 获取可用货币列表

## 配置步骤

### 1. 获取Wise API Token

1. 登录您的Wise账户
2. 进入设置页面
3. 找到API选项
4. 创建新的API Token
5. 复制Token到配置文件中

### 2. 环境变量配置

在 `.env.test` 或 `.env.prod` 文件中添加：

```bash
WISE_API_TOKEN=your_actual_wise_api_token
```

### 3. 验证配置

运行测试脚本验证配置：

```bash
cd backend
python test_wise_api.py
```

## API端点

### 基础信息
- `GET /api/v1/wise/config` - 获取API配置信息
- `GET /api/v1/wise/test` - 测试API连接

### 账户管理
- `GET /api/v1/wise/profiles` - 获取用户资料
- `GET /api/v1/wise/accounts/{profile_id}` - 获取账户列表
- `GET /api/v1/wise/balance/{profile_id}/{account_id}` - 获取账户余额
- `GET /api/v1/wise/all-balances` - 获取所有账户余额

### 交易记录
- `GET /api/v1/wise/transactions/{profile_id}/{account_id}` - 获取交易记录
- `GET /api/v1/wise/recent-transactions` - 获取最近交易记录

### 汇率服务
- `GET /api/v1/wise/exchange-rates` - 获取汇率信息
- `GET /api/v1/wise/historical-rates` - 获取历史汇率
- `GET /api/v1/wise/currencies` - 获取可用货币列表

### 汇总信息
- `GET /api/v1/wise/summary` - 获取账户汇总信息

## 使用示例

### 获取所有账户余额
```bash
curl "http://localhost:8000/api/v1/wise/all-balances"
```

### 获取最近交易记录
```bash
curl "http://localhost:8000/api/v1/wise/recent-transactions?days=7"
```

### 获取汇率信息
```bash
curl "http://localhost:8000/api/v1/wise/exchange-rates?source=USD&target=CNY"
```

## 注意事项

1. **API限制**：Wise API有请求频率限制，请合理使用
2. **数据安全**：API Token具有访问账户数据的权限，请妥善保管
3. **沙盒环境**：建议先在沙盒环境中测试
4. **错误处理**：API调用失败时会返回相应的错误信息

## 故障排除

### 常见错误

1. **401 Unauthorized**
   - 检查API Token是否正确
   - 确认Token是否已激活

2. **403 Forbidden**
   - 检查API Token权限
   - 确认账户状态

3. **429 Too Many Requests**
   - 降低请求频率
   - 实现请求限流

### 调试方法

1. 查看日志文件：`./logs/app.log`
2. 运行测试脚本：`python test_wise_api.py`
3. 检查API文档：https://api-docs.wise.com/

## 集成到定时任务

可以将Wise数据同步添加到定时任务中：

```python
# 在 scheduler_service.py 中添加
async def sync_wise_data():
    """同步Wise数据"""
    wise_service = WiseAPIService()
    
    # 同步账户余额
    balances = await wise_service.get_all_account_balances()
    # 保存到数据库...
    
    # 同步交易记录
    transactions = await wise_service.get_recent_transactions(1)
    # 保存到数据库...
```

## 相关文档

- [Wise API官方文档](https://api-docs.wise.com/)
- [项目开发文档](../多资产投资记录与收益系统_开发说明文档.md)
- [API配置文档](API_CONFIG.md) 