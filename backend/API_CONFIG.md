# API配置说明

## 🎯 配置概述

系统已配置了完整的基金API集成，支持从多个数据源获取基金数据。

## 📊 已配置的API

### 1. 天天基金网API
- **净值API**: `https://fundgz.1234567.com.cn/js/{fund_code}.js`
- **基金信息API**: `https://fund.eastmoney.com/pingzhongdata/{fund_code}.js`
- **状态**: ✅ 正常工作
- **数据格式**: JSONP

### 2. 雪球API
- **API地址**: `https://stock.xueqiu.com/v5/stock/chart/kline.json`
- **状态**: ⚠️ 需要登录认证
- **用途**: 备用数据源

## ⚙️ 配置参数

### 测试环境配置
```python
# 基金API配置
fund_api_timeout: 5秒
fund_api_retry_times: 2次

# 天天基金网API
tiantian_fund_api_base_url: https://fundgz.1234567.com.cn
tiantian_fund_info_base_url: https://fund.eastmoney.com/pingzhongdata

# 雪球API
xueqiu_api_base_url: https://stock.xueqiu.com/v5/stock/chart/kline.json
```

### 生产环境配置
```python
# 基金API配置
fund_api_timeout: 15秒
fund_api_retry_times: 5次

# 其他配置与测试环境相同
```

## 🔧 使用方法

### 1. 获取基金净值
```python
from app.services.fund_api_service import FundAPIService

async with FundAPIService() as api:
    nav_data = await api.get_fund_nav("000001", date.today())
    if nav_data:
        print(f"净值: {nav_data['nav']}")
```

### 2. 获取基金信息
```python
async with FundAPIService() as api:
    fund_info = await api.get_fund_info("000001")
    if fund_info:
        print(f"基金名称: {fund_info['fund_name']}")
```

### 3. 同步基金数据
```python
from app.services.fund_api_service import FundSyncService

sync_service = FundSyncService()
await sync_service.sync_fund_nav(db, "000001", date.today())
await sync_service.sync_fund_info(db, "000001")
```

## 🧪 测试配置

运行配置测试：
```bash
python test_api_config.py
```

## 📝 注意事项

1. **天天基金网API**：
   - 提供实时净值和基金信息
   - 响应格式为JSONP，需要特殊解析
   - 支持估算净值和实际净值

2. **雪球API**：
   - 需要登录认证
   - 可作为备用数据源
   - 响应格式为JSON

3. **错误处理**：
   - 系统会自动重试失败的请求
   - 支持多数据源降级
   - 详细的错误日志记录

## 🔄 数据同步策略

1. **净值同步**：
   - 优先使用天天基金网API
   - 如果失败，尝试雪球API
   - 支持手动录入作为备选

2. **基金信息同步**：
   - 主要使用天天基金网API
   - 支持手动维护基金信息

3. **定时同步**：
   - 可配置定时任务自动同步
   - 支持批量同步多个基金

## 🚀 扩展建议

1. **添加更多数据源**：
   - 蚂蚁财富API
   - 腾讯理财通API
   - 其他基金数据提供商

2. **优化性能**：
   - 添加缓存机制
   - 实现并发请求
   - 优化重试策略

3. **增强监控**：
   - API可用性监控
   - 数据质量检查
   - 异常告警机制 