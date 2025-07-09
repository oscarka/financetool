# 🔍 增强日志系统

## 概述

增强日志系统提供了详细的、分类的日志记录功能，支持JSON格式的结构化日志，便于分析和调试。

## 🚀 功能特性

### 1. **分类日志记录**
- **API日志** (`api`) - API请求相关
- **数据库日志** (`database`) - 数据库操作
- **业务日志** (`business`) - 业务逻辑
- **基金API日志** (`fund_api`) - 基金API调用
- **OKX API日志** (`okx_api`) - OKX加密货币API
- **Wise API日志** (`wise_api`) - Wise金融API
- **PayPal API日志** (`paypal_api`) - PayPal支付API
- **汇率API日志** (`exchange_api`) - 汇率API
- **错误日志** (`error`) - 错误和异常
- **系统日志** (`system`) - 系统运行
- **安全日志** (`security`) - 安全相关
- **定时任务日志** (`scheduler`) - 定时任务

### 2. **详细日志信息**
- 时间戳
- 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 分类
- 模块和函数名
- 行号
- 详细消息
- 额外数据 (JSON格式)
- 异常信息 (包含堆栈跟踪)

### 3. **专用日志函数**
- `log_fund_operation()` - 记录基金操作详情
- `log_fund_api_call()` - 记录基金API调用
- `log_database_operation()` - 记录数据库操作
- `log_api_request()` - 记录API请求

## 📁 日志文件

日志文件按分类存储在 `logs/` 目录下：
```
logs/
├── api.log              # API请求日志
├── database.log         # 数据库操作日志
├── business.log         # 业务逻辑日志
├── fund_api.log         # 基金API日志
├── okx_api.log          # OKX API日志
├── wise_api.log         # Wise API日志
├── paypal_api.log       # PayPal API日志
├── exchange_api.log     # 汇率API日志
├── error.log            # 错误日志
├── system.log           # 系统日志
├── security.log         # 安全日志
└── scheduler.log        # 定时任务日志
```

## 🛠️ 使用方法

### 1. **基本日志记录**
```python
from app.utils.enhanced_logger import log_business_detailed, log_error_detailed

# 记录业务日志
log_business_detailed("用户登录", extra_data={
    "user_id": 123,
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
})

# 记录错误日志
log_error_detailed("数据库连接失败", extra_data={
    "error_type": "ConnectionError",
    "error_message": "无法连接到数据库",
    "retry_count": 3
})
```

### 2. **专用日志函数**
```python
from app.utils.enhanced_logger import log_fund_operation, log_database_operation

# 记录基金操作
log_fund_operation(
    operation_type="buy",
    fund_code="000001",
    amount=1000.0,
    quantity=100.0,
    price=10.0,
    platform="蚂蚁财富",
    operation_id=456
)

# 记录数据库操作
log_database_operation(
    operation="INSERT",
    table="fund_operations",
    record_id=456,
    data={"fund_code": "000001", "amount": 1000.0},
    execution_time=0.02
)
```

### 3. **API日志记录**
```python
from app.utils.enhanced_logger import log_api_request, log_fund_api_detailed

# 记录API请求
log_api_request(
    method="POST",
    path="/api/v1/funds/operations",
    params={"fund_code": "000001"},
    response_status=200,
    execution_time=0.15
)

# 记录基金API调用
log_fund_api_detailed("获取基金净值", extra_data={
    "endpoint": "/api/fund/nav",
    "fund_code": "000001",
    "response_time": 0.5,
    "status_code": 200
})
```

## 🌐 日志查看器

### 1. **基础日志查看器**
访问: `https://your-domain.com/logs-viewer`

### 2. **增强日志查看器**
访问: `https://your-domain.com/enhanced-logs`

特性：
- 按分类过滤日志
- 按级别过滤日志
- 搜索关键词
- 显示详细信息和异常堆栈
- 实时统计信息
- 测试日志生成

### 3. **API接口**
- `GET /api/v1/logs` - 获取基础日志
- `GET /api/v1/logs/detailed` - 获取详细日志
- `GET /api/v1/logs/detailed/stats` - 获取日志统计
- `POST /api/v1/logs/detailed/test` - 测试日志生成

## 🧪 测试

运行测试脚本验证日志系统：
```bash
cd backend
python3 test_enhanced_logs.py
```

## 📊 日志格式示例

### JSON格式日志
```json
{
  "timestamp": "2025-07-09T12:19:37.115433",
  "level": "INFO",
  "category": "business",
  "module": "enhanced_logger",
  "function": "log",
  "line": 148,
  "message": "基金操作: buy",
  "details": {
    "operation_type": "buy",
    "fund_code": "000001",
    "amount": 1000.0,
    "quantity": 100.0,
    "price": 10.0,
    "platform": "蚂蚁财富",
    "operation_time": "2025-07-09T12:19:37.119003",
    "operation_id": 456
  }
}
```

### 异常日志
```json
{
  "timestamp": "2025-07-09T12:19:37.120000",
  "level": "ERROR",
  "category": "error",
  "module": "enhanced_logger",
  "function": "log",
  "line": 148,
  "message": "测试错误日志",
  "details": {
    "error_type": "ValueError",
    "error_message": "这是一个测试错误",
    "stack_trace": "测试堆栈跟踪"
  }
}
```

## 🔧 配置

### 环境变量
- `APP_ENV=prod` - 生产环境，使用结构化JSON格式
- `APP_ENV=dev` - 开发环境，使用可读格式

### 日志级别
- 生产环境: INFO及以上
- 开发环境: DEBUG及以上

## 📈 监控和分析

### 1. **日志统计**
- 总日志数量
- 各分类日志数量
- 各级别日志数量
- 最近错误列表

### 2. **性能监控**
- API响应时间
- 数据库操作时间
- 外部API调用时间

### 3. **错误追踪**
- 异常类型统计
- 错误堆栈分析
- 错误趋势分析

## 🚀 部署

增强日志系统已集成到主应用中，无需额外配置。在Railway上部署后，可以通过以下方式访问：

1. **日志查看器**: `https://your-railway-app.railway.app/enhanced-logs`
2. **API接口**: `https://your-railway-app.railway.app/api/v1/logs/detailed`

## 📝 注意事项

1. **日志文件大小**: 定期清理旧日志文件
2. **敏感信息**: 避免在日志中记录密码、API密钥等敏感信息
3. **性能影响**: 大量日志可能影响应用性能，建议在生产环境中适当调整日志级别
4. **存储空间**: 确保有足够的磁盘空间存储日志文件