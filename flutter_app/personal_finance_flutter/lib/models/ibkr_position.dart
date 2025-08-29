import 'package:json_annotation/json_annotation.dart';

part 'ibkr_position.g.dart';

@JsonSerializable()
class IBKRPosition {
  @JsonKey(name: 'account_id')
  final String accountId;
  
  @JsonKey(name: 'symbol')
  final String symbol;
  
  @JsonKey(name: 'quantity', fromJson: _parseDouble)
  final double quantity;
  
  @JsonKey(name: 'market_value', fromJson: _parseDouble)
  final double marketValue;
  
  @JsonKey(name: 'average_cost', fromJson: _parseDouble)
  final double averageCost;
  
  @JsonKey(name: 'currency')
  final String currency;
  
  @JsonKey(name: 'unrealized_pnl', fromJson: _parseDouble)
  final double unrealizedPnl;
  
  @JsonKey(name: 'realized_pnl', fromJson: _parseDouble)
  final double realizedPnl;
  
  @JsonKey(name: 'update_time', fromJson: _parseDateTime)
  final DateTime updateTime;

  const IBKRPosition({
    required this.accountId,
    required this.symbol,
    required this.quantity,
    required this.marketValue,
    required this.averageCost,
    required this.currency,
    required this.unrealizedPnl,
    required this.realizedPnl,
    required this.updateTime,
  });

  factory IBKRPosition.fromJson(Map<String, dynamic> json) =>
      _$IBKRPositionFromJson(json);

  Map<String, dynamic> toJson() => _$IBKRPositionToJson(this);

  /// 解析数值字段，支持字符串和数字类型
  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        print('解析IBKR持仓数值失败: $value, 错误: $e');
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
        print('解析IBKR持仓日期失败: $value, 错误: $e');
        return DateTime.now();
      }
    }
    return DateTime.now();
  }

  /// 获取货币符号
  String get currencySymbol {
    switch (currency.toUpperCase()) {
      case 'USD':
        return '\$';
      case 'EUR':
        return '€';
      case 'GBP':
        return '£';
      case 'CNY':
        return '¥';
      case 'JPY':
        return 'JP¥';
      case 'HKD':
        return 'HK\$';
      default:
        return currency;
    }
  }

  /// 格式化市值显示
  String get formattedMarketValue {
    if (marketValue >= 1000) {
      return '${currencySymbol}${(marketValue / 1000).toStringAsFixed(1)}K';
    } else {
      return '${currencySymbol}${marketValue.toStringAsFixed(2)}';
    }
  }

  /// 格式化数量显示
  String get formattedQuantity {
    if (quantity >= 1000) {
      return '${(quantity / 1000).toStringAsFixed(1)}K';
    } else {
      return quantity.toStringAsFixed(2);
    }
  }

  /// 获取最后更新时间文本
  String get lastUpdatedText {
    final now = DateTime.now();
    final difference = now.difference(updateTime);
    
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

  /// 获取盈亏状态
  bool get isProfitable => unrealizedPnl >= 0;

  /// 获取盈亏颜色
  String get pnlColor => isProfitable ? 'green' : 'red';

  /// 获取盈亏符号
  String get pnlSign => isProfitable ? '+' : '';
}
