import 'package:json_annotation/json_annotation.dart';

part 'fund_position.g.dart';

@JsonSerializable()
class FundPosition {
  @JsonKey(name: 'asset_code')
  final String assetCode;
  
  @JsonKey(name: 'asset_name')
  final String assetName;
  
  @JsonKey(name: 'total_shares', fromJson: _parseDouble)
  final double totalShares;
  
  @JsonKey(name: 'avg_cost', fromJson: _parseDouble)
  final double avgCost;
  
  @JsonKey(name: 'current_nav', fromJson: _parseDouble)
  final double currentNav;
  
  @JsonKey(name: 'current_value', fromJson: _parseDouble)
  final double currentValue;
  
  @JsonKey(name: 'total_invested', fromJson: _parseDouble)
  final double totalInvested;
  
  @JsonKey(name: 'total_profit', fromJson: _parseDouble)
  final double totalProfit;
  
  @JsonKey(name: 'profit_rate', fromJson: _parseDouble)
  final double profitRate;
  
  @JsonKey(name: 'last_updated', fromJson: _parseDateTime)
  final DateTime lastUpdated;

  const FundPosition({
    required this.assetCode,
    required this.assetName,
    required this.totalShares,
    required this.avgCost,
    required this.currentNav,
    required this.currentValue,
    required this.totalInvested,
    required this.totalProfit,
    required this.profitRate,
    required this.lastUpdated,
  });

  factory FundPosition.fromJson(Map<String, dynamic> json) =>
      _$FundPositionFromJson(json);

  Map<String, dynamic> toJson() => _$FundPositionToJson(this);

  /// 解析数值字段，支持字符串和数字类型
  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        print('解析数值失败: $value, 错误: $e');
        return 0.0;
      }
    }
    return 0.0;
  }

  /// 解析日期时间字段
  static DateTime _parseDateTime(dynamic value) {
    if (value == null) return DateTime.now();
    if (value is DateTime) return value;
    if (value is String) {
      try {
        return DateTime.parse(value);
      } catch (e) {
        print('解析日期失败: $value, 错误: $e');
        return DateTime.now();
      }
    }
    return DateTime.now();
  }

  /// 获取收益变化百分比
  String get profitRateText {
    if (profitRate >= 0) {
      return '+${(profitRate * 100).toStringAsFixed(2)}%';
    } else {
      return '${(profitRate * 100).toStringAsFixed(2)}%';
    }
  }

  /// 获取收益变化颜色
  bool get isProfitable => profitRate >= 0;

  /// 获取最后更新时间文本
  String get lastUpdatedText {
    final now = DateTime.now();
    final difference = now.difference(lastUpdated);
    
    if (difference.inMinutes < 1) {
      return '刚刚更新';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前更新';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}小时前更新';
    } else {
      return '${difference.inDays}天前更新';
    }
  }

  /// 格式化货币显示
  String formatCurrency(double amount) {
    if (amount >= 10000) {
      return '¥${(amount / 10000).toStringAsFixed(2)}万';
    } else {
      return '¥${amount.toStringAsFixed(2)}';
    }
  }

  /// 获取当前价值文本
  String get currentValueText => formatCurrency(currentValue);

  /// 获取总投资金额文本
  String get totalInvestedText => formatCurrency(totalInvested);

  /// 获取总收益文本
  String get totalProfitText => formatCurrency(totalProfit.abs());
}
