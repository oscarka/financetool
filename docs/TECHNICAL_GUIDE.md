# 🔧 技术指南

## 📱 Flutter技术深度分析

### 关键组件分析

#### AssetSnapshotOverview组件分析

**当前React实现特点**
```typescript
// 核心数据类型
type AssetSnapshot = {
  id: number;
  platform: string;
  asset_type: string;
  asset_code: string;
  asset_name?: string;
  currency: string;
  balance: number;
  balance_cny?: number;
  balance_usd?: number;
  balance_eur?: number;
  base_value?: number;
  snapshot_time: string;
};
```

**功能特性**
- **多币种支持**: CNY、USD、EUR基准货币切换
- **高级筛选**: 平台、资产类型、币种、搜索功能
- **日期范围选择**: DatePicker组件
- **数据可视化**: 集成趋势图和柱状图
- **响应式设计**: Ant Design组件
- **实时数据**: 手动刷新和自动加载

#### Flutter迁移策略
```dart
// Dart数据模型
class AssetSnapshot {
  final int id;
  final String platform;
  final String assetType;
  final String assetCode;
  final String? assetName;
  final String currency;
  final double balance;
  final double? balanceCny;
  final double? balanceUsd;
  final double? balanceEur;
  final double? baseValue;
  final DateTime snapshotTime;

  AssetSnapshot({
    required this.id,
    required this.platform,
    required this.assetType,
    required this.assetCode,
    this.assetName,
    required this.currency,
    required this.balance,
    this.balanceCny,
    this.balanceUsd,
    this.balanceEur,
    this.baseValue,
    required this.snapshotTime,
  });

  factory AssetSnapshot.fromJson(Map<String, dynamic> json) {
    return AssetSnapshot(
      id: json['id'],
      platform: json['platform'],
      assetType: json['asset_type'],
      assetCode: json['asset_code'],
      assetName: json['asset_name'],
      currency: json['currency'],
      balance: json['balance'].toDouble(),
      balanceCny: json['balance_cny']?.toDouble(),
      balanceUsd: json['balance_usd']?.toDouble(),
      balanceEur: json['balance_eur']?.toDouble(),
      baseValue: json['base_value']?.toDouble(),
      snapshotTime: DateTime.parse(json['snapshot_time']),
    );
  }
}
```

## 🌐 API配置指南

### 后端API配置

#### 核心API端点
- **资产快照API**: `/api/snapshot/assets` - 获取资产快照数据
- **汇率快照API**: `/api/snapshot/exchange-rates` - 获取汇率快照数据
- **手动触发API**: `/api/snapshot/extract` - 手动生成资产快照
- **汇率生成API**: `/api/snapshot/extract-exchange-rates` - 手动生成汇率快照
- **趋势分析API**: `/api/snapshot/trends` - 获取资产趋势数据

#### 汇率计算系统
- **传统货币汇率**: 从WiseExchangeRate表获取
- **数字货币汇率**: 支持50+种数字货币，通过OKX API获取
- **多层汇率转换**: 支持IP → USDT → USD → CNY等复杂转换路径
- **缓存机制**: Redis缓存 + 内存缓存，提高性能
- **汇率快照生成**: 自动记录历史汇率数据

### OKX配置指南

#### API集成配置
- **API密钥管理**: 安全的密钥存储和轮换机制
- **沙盒环境**: 支持测试和生产环境切换
- **错误处理**: 完善的错误处理和重试机制
- **数据同步**: 自动同步余额、交易和行情数据

## 🔄 数据模型设计

### 核心数据表
- **AssetSnapshot**: 资产快照表，记录各平台资产的历史数据
- **ExchangeRateSnapshot**: 汇率快照表，记录汇率历史数据
- **支持多基准货币**: CNY、USD、EUR
- **完整的数据库迁移文件**

### 资产类型映射
- **OKX** → "数字货币"
- **Wise** → "外汇"
- **IBKR** → "证券"
- **支付宝** → "基金"

## 📊 性能优化

### 缓存策略
- **Redis缓存**: 汇率数据和API响应缓存
- **内存缓存**: 热点数据内存缓存
- **数据库优化**: 索引优化，查询性能提升

### 数据完整性
- **汇率计算**: 确保所有资产都有正确的基准货币价值
- **数据过滤**: 智能过滤无效和小额数据
- **错误恢复**: 完善的错误处理和回滚机制

## 🚀 部署和运维

### 环境配置
- **开发环境**: 本地开发配置
- **测试环境**: 集成测试配置
- **生产环境**: Railway部署配置

### 监控和日志
- **性能监控**: 响应时间和吞吐量监控
- **错误日志**: 详细的错误日志记录
- **健康检查**: 系统健康状态检查

---

**文档版本**: 1.0
**最后更新**: 2025年8月
**维护状态**: 活跃维护
