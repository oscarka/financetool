class AssetStats {
  final double totalValue;
  final Map<String, double> platformStats;
  final Map<String, double> assetTypeStats;
  final Map<String, double> currencyStats;
  final int assetCount;
  final int platformCount;
  final int assetTypeCount;
  final int currencyCount;
  final bool hasDefaultRates;
  final double? dailyChangePercentage;
  final double? dailyProfit;
  final double? availableBalance;
  final double? frozenAssets;

  AssetStats({
    required this.totalValue,
    required this.platformStats,
    required this.assetTypeStats,
    required this.currencyStats,
    required this.assetCount,
    required this.platformCount,
    required this.assetTypeCount,
    required this.currencyCount,
    required this.hasDefaultRates,
    this.dailyChangePercentage,
    this.dailyProfit,
    this.availableBalance,
    this.frozenAssets,
  });

  factory AssetStats.fromJson(Map<String, dynamic> json) {
    return AssetStats(
      totalValue: (json['total_value'] ?? 0.0).toDouble(),
      platformStats: Map<String, double>.from(json['platform_stats'] ?? {}),
      assetTypeStats: Map<String, double>.from(json['asset_type_stats'] ?? {}),
      currencyStats: Map<String, double>.from(json['currency_stats'] ?? {}),
      assetCount: json['asset_count'] ?? 0,
      platformCount: json['platform_count'] ?? 0,
      assetTypeCount: json['asset_type_count'] ?? 0,
      currencyCount: json['currency_count'] ?? 0,
      hasDefaultRates: json['has_default_rates'] ?? false,
      dailyChangePercentage: json['daily_change_percentage']?.toDouble(),
      dailyProfit: json['daily_profit']?.toDouble(),
      availableBalance: json['available_balance']?.toDouble(),
      frozenAssets: json['frozen_assets']?.toDouble(),
    );
  }

  // 格式化货币显示
  String formatCurrency(double value, String currency) {
    final symbol = _getCurrencySymbol(currency);
    return '$symbol${value.toStringAsFixed(2)}';
  }

  String _getCurrencySymbol(String currency) {
    switch (currency.toUpperCase()) {
      case 'CNY':
        return '¥';
      case 'USD':
        return '\$';
      case 'EUR':
        return '€';
      case 'USDT':
        return '\$';
      case 'BTC':
        return '₿';
      default:
        return '';
    }
  }

  // 获取24小时变化百分比
  double? get dailyChangePercent => dailyChangePercentage;

  // 获取今日收益
  double? get todayProfit => dailyProfit;

  // 获取可用余额
  double? get availableBalanceValue => availableBalance;

  // 获取冻结资产
  double? get frozenAssetsValue => frozenAssets;

  // 计算可用余额（如果没有单独统计，使用总资产）
  double get calculatedAvailableBalance {
    return availableBalance ?? totalValue;
  }

  // 计算冻结资产（如果没有单独统计，使用0）
  double get calculatedFrozenAssets {
    return frozenAssets ?? 0.0;
  }

  // 计算风险等级
  String calculateRiskLevel() {
    if (totalValue == 0) return "无数据";
    
    // 计算各资产类型占比
    final digitalCurrencyRatio = (assetTypeStats['数字货币'] ?? 0) / totalValue;
    final stockRatio = (assetTypeStats['证券'] ?? 0) / totalValue;
    final fundRatio = (assetTypeStats['基金'] ?? assetTypeStats['fund'] ?? 0) / totalValue;
    final forexRatio = (assetTypeStats['外汇'] ?? 0) / totalValue;
    
    // 风险评分算法
    double riskScore = 0;
    
    // 数字货币权重最高 (高风险)
    riskScore += digitalCurrencyRatio * 0.8;
    
    // 股票投资权重较高 (中高风险)
    riskScore += stockRatio * 0.6;
    
    // 基金投资权重中等 (中风险)
    riskScore += fundRatio * 0.4;
    
    // 外汇权重较低 (中低风险)
    riskScore += forexRatio * 0.3;
    
    // 根据风险评分返回等级
    if (riskScore >= 0.6) return "高风险";
    if (riskScore >= 0.4) return "中高风险";
    if (riskScore >= 0.2) return "中等";
    if (riskScore >= 0.1) return "中低风险";
    return "低风险";
  }
}
