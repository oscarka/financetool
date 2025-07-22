# 🗄️ 金融系统数据库与数据持久化总指南

---

## 目录
1. 前言与适用范围
2. 数据库结构与核心表设计
3. Railway 数据持久化问题分析与修复
4. 数据持久化最佳实践与备份恢复
5. 数据完整性与测试验证
6. 类型转换与前后端兼容
7. 维护建议与常见问题排查

---

## 1. 前言与适用范围
本指南适用于本系统所有数据库相关设计、数据持久化、备份恢复、类型转换、数据完整性验证等环节。内容涵盖 SQLite/容器化部署、Railway 平台、前后端数据兼容等。

---

## 2. 数据库结构与核心表设计

### 2.1 核心表结构
- user_operations（用户操作记录）
- asset_positions（资产持仓）
- fund_info（基金信息）
- fund_nav（基金净值）
- dca_plans（定投计划）
- exchange_rates（汇率信息）
- system_config（系统配置）

详细建表 SQL 及索引设计见原 database_design.md。

### 2.2 表关系与数据流
- user_operations (1) -----> (N) asset_positions
- fund_info (1) -----> (N) fund_nav
- dca_plans (1) -----> (N) user_operations

### 2.3 数据流与同步策略
- 操作录入 → user_operations
- API 获取净值/汇率 → fund_nav, exchange_rates
- 持仓计算 → asset_positions
- 收益分析 → 持仓+净值

---

## 3. Railway 数据持久化问题分析与修复

### 3.1 问题分析
- 容器化部署导致 SQLite 数据文件丢失（未挂载 volume 时）
- railway.toml 缺少 [[deploy.volumes]] 配置
- 数据库路径未指向持久化目录

### 3.2 影响范围
- 基金净值、用户操作、IBKR、Wise、OKX、PayPal 等所有业务模块
- 重要数据丢失后难以恢复

### 3.3 修复方案
- railway.toml 增加：
  ```toml
  [[deploy.volumes]]
  source = "database"
  target = "/app/data"
  ```
- Dockerfile 增加数据目录权限设置
- prod.py 优先使用 DATABASE_URL 环境变量，否则默认 `/app/data/personalfinance.db`
- 备份与恢复脚本完善

### 3.4 验证与测试
- 通过 verify_railway_deployment.py、post_deploy_verify.py 验证 volume 挂载、数据完整性
- 通过 API 检查数据持久化效果

---

## 4. 数据持久化最佳实践与备份恢复

### 4.1 备份策略
- 自动备份：每 24 小时
- 手动备份：`python backup_database.py backup`
- 恢复：`python backup_database.py restore backups/latest_backup.db`
- 备份文件存储于 `/app/backups/`

### 4.2 迁移与恢复流程
- 迁移前先备份所有数据
- 恢复时优先使用最新备份
- 关键数据（基金净值、用户操作、IBKR、Wise、OKX、PayPal）需重点校验

### 4.3 数据完整性检查
- `python check_data_integrity.py` 定期检查
- 关键表数据量、最近 24 小时数据、主键唯一性等

---

## 5. 数据完整性与测试验证

### 5.1 测试分支与验证工具
- fix/railway-data-persistence-complete 分支专用于持久化修复测试
- verify_railway_deployment.py：部署前环境与挂载验证
- post_deploy_verify.py：部署后服务健康与数据完整性验证

### 5.2 测试场景
- 重新部署后数据不丢失
- 数据库文件存在且大小稳定
- API 查询数据一致
- 业务功能正常

### 5.3 报告与结论
- 所有测试通过后，说明持久化问题已彻底解决
- 发现问题时，优先检查 volume 挂载、环境变量、权限

---

## 6. 类型转换与前后端兼容

### 6.1 问题描述
- 后端返回的数字字段为字符串，前端直接 toFixed() 报错

### 6.2 解决方案
- 前端统一用 safeNumber、safeToFixed 等函数做类型转换
- TypeScript 接口定义允许 number | string
- 后端尽量返回纯数字类型，必要时前端兜底

### 6.3 代码示例
```typescript
const safeNumber = (value: number | string) => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    return isNaN(numValue) ? 0 : numValue
}
const safeToFixed = (value: number | string, digits: number = 2) => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0.' + '0'.repeat(digits)
    return numValue.toFixed(digits)
}
```

### 6.4 维护建议
- 前后端共享类型定义，避免接口不一致
- ESLint 规则禁止直接 toFixed，强制使用安全转换

---

## 7. 维护建议与常见问题排查

### 7.1 维护建议
- 定期备份与清理旧备份
- 部署前后均需完整性检查
- 监控磁盘空间与数据增长
- 关键表数据量异常需及时告警

### 7.2 常见问题排查
- 数据丢失：优先检查 volume 挂载、路径、权限
- 服务启动失败：检查 Dockerfile 权限、环境变量、启动日志
- API 报错：检查数据库连接、数据完整性、表结构
- 类型报错：前端类型转换、后端返回类型

### 7.3 应急处理
- 数据丢失时立即停止部署，优先恢复最近备份
- 检查并修复 volume 配置后再重新部署
- 记录所有修复与恢复操作，便于后续追溯

---

> 本文档已合并并精简自原 database 文件夹所有文档，所有关键信息均已保留。如需详细历史变更、特殊场景说明，请查阅原文档备份。 