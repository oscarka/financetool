# Wise Balance updated_at 属性错误修复总结

## 问题描述
页面显示错误：`获取数据库状态失败: type object 'WiseBalance' has no attribute 'updated_at'`

## 根本原因
代码中尝试访问 `WiseBalance.updated_at` 和 `WiseExchangeRate.updated_at` 字段，但这些模型类中实际没有定义这些属性。

## 修复内容

### 1. 修复 `backend/app/api/v1/wise.py` 文件
**修复前：**
```python
latest_balance = db.query(WiseBalance).order_by(WiseBalance.updated_at.desc()).first()
latest_rate = db.query(WiseExchangeRate).order_by(WiseExchangeRate.updated_at.desc()).first()

"latest_update": latest_balance.updated_at.isoformat() if latest_balance else None
"latest_update": latest_rate.updated_at.isoformat() if latest_rate else None
```

**修复后：**
```python
latest_balance = db.query(WiseBalance).order_by(WiseBalance.update_time.desc()).first()
latest_rate = db.query(WiseExchangeRate).order_by(WiseExchangeRate.created_at.desc()).first()

"latest_update": latest_balance.update_time.isoformat() if latest_balance else None
"latest_update": latest_rate.created_at.isoformat() if latest_rate else None
```

### 2. 修复 `backend/app/services/wise_api_service.py` 文件
**修复前：**
```python
existing.updated_at = datetime.now()  # WiseBalance 更新
existing.updated_at = datetime.now()  # WiseExchangeRate 更新
```

**修复后：**
```python
existing.update_time = datetime.now()  # WiseBalance 更新
# 移除 WiseExchangeRate 的 updated_at 设置
```

### 3. 环境配置修复
- 创建了 `backend/.env.test` 配置文件
- 创建了必要的 `data/` 和 `logs/` 目录
- 移除了不支持的 `ENABLE_SCHEDULER` 配置项

## 验证结果

✅ **后端服务成功启动**
✅ **数据库初始化正常**
✅ **API 正常响应**：`/api/v1/wise/db-status` 返回正确的 JSON 数据
✅ **查询使用正确字段**：
- WiseBalance: `update_time`
- WiseExchangeRate: `created_at`
- WiseTransaction: `created_at`

## API 测试结果
```bash
curl -X GET "http://localhost:8000/api/v1/wise/db-status"
```

返回：
```json
{
  "success": true,
  "data": {
    "transactions": {
      "count": 10,
      "latest_update": "2025-07-06T14:32:35"
    },
    "balances": {
      "count": 0,
      "latest_update": null
    },
    "exchange_rates": {
      "count": ...,
      ...
    }
  }
}
```

## 修复时间
2025年7月8日 09:44

## 状态
✅ **已修复并验证**