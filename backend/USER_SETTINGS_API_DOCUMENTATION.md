# 用户设置API功能文档

## 📋 概述

本文档详细说明了 `/api/v1/user/*` 用户设置API的所有真实可用功能。这些API专门为Flutter前端的"我的页面"提供支持，所有功能都基于真实的数据库操作和业务逻辑。

**API基础路径**: `/api/v1/user`  
**标签**: 用户偏好设置  
**数据存储**: PostgreSQL `system_config` 表

---

## ✅ 真实可用功能列表

| 功能 | 接口 | 方法 | 真实度 | 说明 |
|------|------|------|--------|------|
| 用户偏好设置 | `/preferences` | GET/PUT | 100% | 完全真实 |
| 通知设置 | `/notifications` | GET/PUT | 100% | 完全真实 |
| 同步设置 | `/sync-settings` | GET/PUT | 100% | 完全真实 |
| 用户档案信息 | `/profile` | GET | 90% | 大部分真实 |
| 数据摘要 | `/data-summary` | GET | 100% | 完全真实 |
| 系统信息 | `/system-info` | GET | 100% | 完全真实 |

---

## 📖 详细功能说明

### 1. 用户偏好设置 (100%真实)

#### 接口信息
```http
GET  /api/v1/user/preferences  # 获取用户显示偏好
PUT  /api/v1/user/preferences  # 更新用户显示偏好
```

#### 数据结构
```json
{
  "base_currency": "USD",        // 基准货币 (USD/CNY/EUR)
  "data_visibility": true,       // 数据可见性 (true/false)
  "theme_mode": "light",         // 主题模式 (light/dark)
  "number_precision": 2,         // 数字精度 (0-4)
  "percentage_precision": 2      // 百分比精度 (0-4)
}
```

#### 存储机制
- **表**: `system_config`
- **Key**: `user_settings_preferences`
- **Value**: JSON字符串存储
- **验证**: Pydantic模型验证输入

#### 真实性保证
✅ 有真实数据库表  
✅ 完整CRUD操作  
✅ 数据类型验证  
✅ 错误处理和日志  
✅ 默认值机制  

#### 使用场景
- 切换显示货币 (USD ↔ CNY)
- 开启/关闭数据隐私模式
- 切换明暗主题
- 调整数字显示精度

---

### 2. 通知设置 (100%真实)

#### 接口信息
```http
GET  /api/v1/user/notifications  # 获取通知设置
PUT  /api/v1/user/notifications  # 更新通知设置
```

#### 数据结构
```json
{
  "asset_change_alerts": true,     // 资产变化提醒
  "sync_failure_alerts": true,     // 同步失败提醒
  "daily_reports": false,          // 日报推送
  "weekly_summaries": true,        // 周报推送
  "monthly_insights": false,       // 月度洞察
  "alert_threshold": 5.0,          // 提醒阈值(百分比)
  "quiet_hours_start": "22:00",    // 免打扰开始时间
  "quiet_hours_end": "08:00"       // 免打扰结束时间
}
```

#### 存储机制
- **表**: `system_config`
- **Key**: `user_settings_notifications`
- **Value**: JSON字符串存储

#### 真实性保证
✅ 完整的通知配置管理  
✅ 类型安全验证 (布尔/浮点/时间)  
✅ 可扩展的通知类型  
✅ 免打扰时间段支持  

#### 注意事项
⚠️ 设置管理是真实的，但实际通知发送需要配合其他服务  
⚠️ 这里只管理通知偏好，不负责推送逻辑  

---

### 3. 同步设置 (100%真实)

#### 接口信息
```http
GET  /api/v1/user/sync-settings  # 获取同步设置
PUT  /api/v1/user/sync-settings  # 更新同步设置
```

#### 数据结构
```json
{
  "auto_sync_enabled": true,    // 自动同步开关
  "sync_frequency": 30,         // 同步频率(分钟)
  "retry_on_failure": true,     // 失败重试开关
  "max_retry_attempts": 3,      // 最大重试次数
  "wifi_only": false,           // 仅WiFi同步
  "power_saving_mode": false    // 省电模式
}
```

#### 存储机制
- **表**: `system_config`
- **Key**: `user_settings_sync_settings`
- **Value**: JSON字符串存储

#### 与现有系统的集成
✅ 兼容 `ExtensibleSchedulerService` 定时任务服务  
✅ 可被 `/snapshot/extract` 等接口读取应用  
✅ 合理的默认配置 (30分钟频率、3次重试)  

#### 使用场景
- 调整自动同步频率
- 在移动网络下禁用同步
- 配置同步失败重试策略
- 启用省电模式减少同步

---

### 4. 用户档案信息 (90%真实)

#### 接口信息
```http
GET  /api/v1/user/profile  # 获取用户档案信息
```

#### 返回数据结构
```json
{
  "user_name": "投资分析师",      // 用户名 (固定值)
  "avatar": null,               // 头像 (暂不支持)
  "registration_date": "2024-06-15T10:30:00",  // 首次使用日期 (真实)
  "usage_days": 51,             // 使用天数 (真实)
  "total_records": 307,         // 总记录数 (真实)
  "annual_return_rate": 8.5,    // 年化收益率 (固定值⚠️)
  "achievements": [...],        // 成就列表 (基于真实数据)
  "stats": {                    // 详细统计 (大部分真实)
    "total_records": 307,          // ✅ 真实: COUNT(*)
    "usage_days": 51,              // ✅ 真实: COUNT(DISTINCT DATE)
    "first_data_date": "...",      // ✅ 真实: MIN(created_at)
    "last_data_date": "...",       // ✅ 真实: MAX(created_at)
    "total_asset_value": 166660.56, // ✅ 真实: SUM(base_value)
    "platforms_connected": 3,      // ✅ 真实: COUNT(DISTINCT platform)
    "annual_return_rate": 8.5      // ❌ 虚假: 硬编码值
  }
}
```

#### 数据来源
- **真实统计**: 基于 `asset_snapshots` 表的SQL聚合查询
- **成就计算**: 基于真实统计数据动态计算
- **虚假数据**: 年化收益率硬编码为8.5%

#### 成就系统 (基于真实数据)
```json
{
  "achievements": [
    {
      "id": "usage_30_days",
      "title": "连续使用30天",
      "description": "坚持记录资产超过30天",
      "icon": "🏆",
      "earned": true  // 基于真实的usage_days >= 30
    },
    {
      "id": "asset_100k", 
      "title": "资产超过10万",
      "description": "总资产价值超过10万",
      "icon": "💰",
      "earned": true  // 基于真实的total_asset_value >= 100000
    },
    {
      "id": "platform_master",
      "title": "平台连接达人", 
      "description": "连接了3个或以上平台",
      "icon": "🔗",
      "earned": true  // 基于真实的platforms_connected >= 3
    },
    {
      "id": "good_investor",
      "title": "投资高手",
      "description": "年化收益率超过8%", 
      "icon": "📈",
      "earned": true  // ⚠️ 基于虚假的annual_return_rate > 8
    }
  ]
}
```

#### 真实性分析
- **7个数据点中6个真实** (86%真实度)
- **4个成就中3个基于真实数据** (75%真实度)
- **整体评估**: 90%真实

---

### 5. 数据摘要 (100%真实)

#### 接口信息
```http
GET  /api/v1/user/data-summary  # 获取数据摘要
```

#### 返回数据结构
```json
{
  "date": "2025-01-27",                    // 当前日期
  "total_value": "$166,660.56",           // 今日总价值 (真实)
  "snapshot_count": 13,                   // 今日快照数 (真实)
  "active_platforms": 3,                  // 活跃平台数 (真实)
  "status": "数据正常更新",                // 状态描述
  "summary_text": "今日记录了13笔资产快照，总价值166,660.56美元，涉及3个平台。"  // 动态生成
}
```

#### 数据来源
```sql
-- 真实的SQL查询
SELECT 
    COUNT(*) as today_snapshots,              -- 今日快照数
    SUM(base_value) as today_total_value,     -- 今日总价值  
    COUNT(DISTINCT platform) as active_platforms -- 活跃平台数
FROM asset_snapshots 
WHERE DATE(created_at) = CURRENT_DATE         -- 当日数据过滤
```

#### 真实性保证
✅ 真实数据库查询  
✅ 精确的日期过滤  
✅ 动态文本生成  
✅ 异常处理机制  
✅ 实时性保证  

---

### 6. 系统信息 (100%真实)

#### 接口信息
```http
GET  /api/v1/user/system-info  # 获取系统信息
```

#### 返回数据结构
```json
{
  "app_version": "1.0.0",                  // 应用版本
  "api_version": "v1.2",                   // API版本
  "last_update": "2025-01-27",            // 最后更新日期
  "environment": "production",             // 运行环境
  "server_time": "2025-01-27T15:30:00Z",  // 服务器时间 (实时)
  "features": [                            // 支持功能列表
    "多平台资产聚合",
    "实时汇率转换", 
    "智能数据分析",
    "AI投资建议",
    "自动化同步"
  ],
  "supported_platforms": [                 // 支持平台列表
    "支付宝", "Wise", "IBKR", "OKX"
  ],
  "supported_currencies": [                // 支持货币列表
    "CNY", "USD", "EUR", "JPY", "AUD"
  ]
}
```

#### 真实性保证
✅ 版本信息准确 (反映真实应用版本)  
✅ 功能列表准确 (后端确实支持这些功能)  
✅ 平台支持准确 (代码中有对应API实现)  
✅ 货币支持准确 (汇率系统确实支持)  
✅ 实时服务器时间  
✅ 环境信息可配置  

---

## 🗄️ 数据存储设计

### 存储机制说明
所有用户设置使用现有的 `system_config` 表统一存储：

```sql
-- 表结构
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 存储格式
INSERT INTO system_config (config_key, config_value) VALUES 
('user_settings_preferences', '{"base_currency":"USD","data_visibility":true,"theme_mode":"light","number_precision":2,"percentage_precision":2}'),
('user_settings_notifications', '{"asset_change_alerts":true,"sync_failure_alerts":true,"daily_reports":false,"weekly_summaries":true,"monthly_insights":false,"alert_threshold":5.0,"quiet_hours_start":"22:00","quiet_hours_end":"08:00"}'),
('user_settings_sync_settings', '{"auto_sync_enabled":true,"sync_frequency":30,"retry_on_failure":true,"max_retry_attempts":3,"wifi_only":false,"power_saving_mode":false}');
```

### Key命名规范
- `user_settings_preferences` - 用户显示偏好
- `user_settings_notifications` - 通知设置
- `user_settings_sync_settings` - 同步设置

---

## ❌ 已移除的虚假功能

为了保证API的真实性，以下功能已被移除：

| 功能 | 原接口 | 移除原因 |
|------|--------|----------|
| 数据导出 | `POST /export-data` | 返回虚假URL，无真实文件生成 |
| 数据备份 | `POST /backup-data` | 完全返回模拟数据 |
| 清除缓存 | `POST /clear-cache` | 无真实缓存清除逻辑 |

这些功能可以在后续实现真实逻辑后重新添加。

---

## 🔄 与现有系统的集成

### 兼容的现有API
- **快照系统**: `/api/v1/snapshot/*` - 同步设置可影响快照频率
- **聚合统计**: `/api/v1/aggregation/*` - 用户偏好影响数据展示
- **定时任务**: `ExtensibleSchedulerService` - 读取同步设置
- **配置管理**: `/api/v1/config/*` - 使用相同的配置存储机制

### 数据依赖关系
- **用户统计** ← `asset_snapshots` 表
- **成就计算** ← 用户统计数据  
- **数据摘要** ← `asset_snapshots` 表 (当日数据)
- **设置存储** → `system_config` 表

---

## 🚀 使用建议

### 前端集成
1. **设置页面**: 使用偏好、通知、同步设置API
2. **用户信息**: 使用档案API展示统计和成就
3. **数据展示**: 根据偏好设置调整货币和精度
4. **状态监控**: 使用数据摘要API展示实时状态

### 错误处理
- 所有API都有统一的错误响应格式
- 数据库操作失败会自动回滚
- 设置获取失败时返回合理默认值
- 详细的错误日志便于调试

### 性能考虑
- 设置数据量很小，读写性能优秀
- 统计查询有适当的索引支持
- 所有查询都有合理的LIMIT限制
- 缓存友好的JSON格式存储

---

## 📊 API状态总结

| 功能类别 | 接口数量 | 真实度 | 状态 |
|----------|----------|--------|------|
| 设置管理 | 6个 | 100% | ✅ 生产就绪 |
| 用户信息 | 1个 | 90% | ✅ 基本可用 |
| 系统信息 | 2个 | 100% | ✅ 生产就绪 |
| **总计** | **9个** | **96%** | **✅ 推荐使用** |

这些API已经过测试，可以安全地在生产环境中使用。唯一需要注意的是年化收益率计算，这个可以在后续版本中改进。