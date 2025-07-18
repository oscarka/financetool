# API配置说明

## 🎯 配置概述

系统已配置了完整的基金API集成，支持从多个数据源获取基金数据。

## 📊 已配置的API

### 1. 天天基金网API ✅ 正常工作
- **净值API**: `https://fundgz.1234567.com.cn/js/{fund_code}.js`
  - 提供实时净值数据
  - 支持估算净值(gsz)和实际净值(dwjz)
  - 响应格式: JSONP
  - 更新频率: 实时
  
- **基金信息API**: `https://fund.eastmoney.com/pingzhongdata/{fund_code}.js`
  - 提供基金详细信息
  - 包含基金名称、费率、最小申购额等
  - 响应格式: JavaScript变量
  - 更新频率: 每日

- **状态**: ✅ 正常工作
- **数据格式**: JSONP/JavaScript
- **推荐使用**: 主要数据源

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
        print(f"估算净值: {nav_data.get('gsz')}")
        print(f"更新时间: {nav_data.get('gztime')}")
```

### 2. 获取基金信息
```python
async with FundAPIService() as api:
    fund_info = await api.get_fund_info("000001")
    if fund_info:
        print(f"基金名称: {fund_info['fund_name']}")
        print(f"管理费率: {fund_info['management_fee']}%")
        print(f"申购费率: {fund_info['purchase_fee']}%")
```

### 3. 同步基金数据
```python
from app.services.fund_api_service import FundSyncService

sync_service = FundSyncService()
await sync_service.sync_fund_nav(db, "000001", date.today())
await sync_service.sync_fund_info(db, "000001")
```

### 4. 手动触发基金更新
```bash
# 通过API手动触发基金净值更新
curl -X POST "http://localhost:8000/api/v1/scheduler/jobs/fund_nav_update/execute" \
  -H "Content-Type: application/json" \
  -d '{"update_all": true, "data_source": "tiantian"}'
```

## 🧪 测试配置

### 1. 测试天天基金网接口
```bash
# 测试净值接口
curl -s "https://fundgz.1234567.com.cn/js/000001.js" | head -5

# 测试基金信息接口
curl -s "https://fund.eastmoney.com/pingzhongdata/000001.js" | grep -o "fS_name[^;]*" | head -1
```

### 2. 运行配置测试
```bash
python test_api_config.py
```

## 📝 注意事项

### 1. 天天基金网API特点
- **实时性**: 净值数据实时更新，估算净值每15分钟更新一次
- **稳定性**: 接口稳定，响应速度快
- **数据完整性**: 提供净值、增长率、累计净值等完整信息
- **解析要求**: JSONP格式需要特殊解析处理

### 2. 雪球API特点
- **认证要求**: 需要登录认证
- **数据质量**: 数据质量较高
- **备用方案**: 可作为天天基金网的备用数据源

### 3. 错误处理
- **自动重试**: 系统会自动重试失败的请求
- **多数据源降级**: 支持多数据源自动切换
- **详细日志**: 完整的错误日志记录

## 🔄 数据同步策略

### 1. 净值同步策略
- **主要数据源**: 天天基金网API
- **备用数据源**: 雪球API
- **手动录入**: 支持手动录入作为备选
- **更新频率**: 
  - 工作日: 9:00, 15:00, 20:00
  - 周末: 10:00

### 2. 基金信息同步策略
- **主要数据源**: 天天基金网API
- **手动维护**: 支持手动维护基金信息
- **更新频率**: 每日一次

### 3. 定时同步配置
```json
{
    "fund_nav_update_morning": "0 9 * * 1-5",    // 工作日早盘
    "fund_nav_update_afternoon": "0 15 * * 1-5", // 工作日午盘
    "fund_nav_update_evening": "0 20 * * 1-5",   // 工作日晚盘
    "fund_nav_update_weekend": "0 10 * * 6,0"    // 周末
}
```

## 🚀 优化建议

### 1. 性能优化
- **缓存机制**: 添加Redis缓存，减少API调用
- **并发请求**: 实现批量并发请求
- **智能重试**: 根据错误类型调整重试策略

### 2. 数据源扩展
- **蚂蚁财富API**: 添加蚂蚁财富作为数据源
- **腾讯理财通API**: 添加腾讯理财通作为数据源
- **其他基金数据提供商**: 考虑添加更多数据源

### 3. 监控告警
- **API可用性监控**: 实时监控API状态
- **数据质量检查**: 检查数据完整性和准确性
- **异常告警机制**: 及时告警异常情况

### 4. 用户体验优化
- **实时推送**: 实现净值变化实时推送
- **数据可视化**: 提供净值走势图表
- **个性化设置**: 支持用户自定义更新频率

## 🔍 故障排查

### 1. 接口无法访问
- 检查网络连接
- 验证API地址是否正确
- 检查防火墙设置

### 2. 数据解析失败
- 检查响应格式是否变化
- 验证解析逻辑是否正确
- 查看详细错误日志

### 3. 定时任务不执行
- 检查调度器是否启动
- 验证任务配置是否正确
- 查看调度器日志

### 4. 数据更新不及时
- 检查定时任务执行状态
- 验证API响应时间
- 查看数据同步日志 