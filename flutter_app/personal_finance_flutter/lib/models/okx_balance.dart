import 'package:json_annotation/json_annotation.dart';

part 'okx_balance.g.dart';

@JsonSerializable()
class OKXBalance {
  @JsonKey(name: 'currency')
  final String currency;
  
  @JsonKey(name: 'total_balance', fromJson: _parseDouble)
  final double totalBalance;
  
  @JsonKey(name: 'available_balance', fromJson: _parseDouble)
  final double availableBalance;
  
  @JsonKey(name: 'frozen_balance', fromJson: _parseDouble)
  final double frozenBalance;
  
  @JsonKey(name: 'update_time', fromJson: _parseDateTime)
  final DateTime updateTime;

  @JsonKey(name: 'account_type', defaultValue: 'trading')
  final String accountType;

  const OKXBalance({
    required this.currency,
    required this.totalBalance,
    required this.availableBalance,
    required this.frozenBalance,
    required this.updateTime,
    this.accountType = 'trading',
  });

  factory OKXBalance.fromJson(Map<String, dynamic> json) =>
      _$OKXBalanceFromJson(json);

  Map<String, dynamic> toJson() => _$OKXBalanceToJson(this);

  /// 解析数值字段，支持字符串和数字类型
  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        print('解析OKX余额数值失败: $value, 错误: $e');
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
        print('解析OKX余额日期失败: $value, 错误: $e');
        return DateTime.now();
      }
    }
    return DateTime.now();
  }

  /// 获取货币符号
  String get currencySymbol {
    switch (currency.toUpperCase()) {
      case 'BTC':
        return '₿';
      case 'ETH':
        return 'Ξ';
      case 'USDT':
        return 'USDT ';
      case 'USDC':
        return 'USDC ';
      case 'USD':
        return '\$';
      case 'CNY':
        return '¥';
      case 'EUR':
        return '€';
      case 'GBP':
        return '£';
      case 'JPY':
        return 'JP¥';
      case 'HKD':
        return 'HK\$';
      default:
        return currency;
    }
  }

  /// 格式化余额显示
  String get formattedTotalBalance {
    if (totalBalance >= 1000) {
      return '${currencySymbol}${(totalBalance / 1000).toStringAsFixed(1)}K';
    } else if (totalBalance >= 1) {
      return '${currencySymbol}${totalBalance.toStringAsFixed(2)}';
    } else {
      return '${currencySymbol}${totalBalance.toStringAsFixed(6)}';
    }
  }

  /// 格式化可用余额显示
  String get formattedAvailableBalance {
    if (availableBalance >= 1000) {
      return '${currencySymbol}${(availableBalance / 1000).toStringAsFixed(1)}K';
    } else if (availableBalance >= 1) {
      return '${currencySymbol}${availableBalance.toStringAsFixed(2)}';
    } else {
      return '${currencySymbol}${availableBalance.toStringAsFixed(6)}';
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

  /// 获取账户状态
  String get accountStatus {
    if (frozenBalance > 0) {
      return '部分冻结';
    } else if (availableBalance > 0) {
      return '正常';
    } else {
      return '无余额';
    }
  }

  /// 获取状态颜色
  String get statusColor {
    switch (accountStatus) {
      case '正常':
        return 'green';
      case '部分冻结':
        return 'orange';
      case '无余额':
        return 'gray';
      default:
        return 'gray';
    }
  }
}
