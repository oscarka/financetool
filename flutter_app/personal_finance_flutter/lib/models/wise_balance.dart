import 'package:json_annotation/json_annotation.dart';

part 'wise_balance.g.dart';

@JsonSerializable()
class WiseBalance {
  @JsonKey(name: 'account_id')
  final String accountId;
  
  @JsonKey(name: 'currency')
  final String currency;
  
  @JsonKey(name: 'available_balance', fromJson: _parseDouble)
  final double availableBalance;
  
  @JsonKey(name: 'reserved_balance', fromJson: _parseDouble)
  final double reservedBalance;
  
  @JsonKey(name: 'total_balance', fromJson: _parseDouble)
  final double totalBalance;
  
  @JsonKey(name: 'account_name')
  final String? accountName;
  
  @JsonKey(name: 'account_type')
  final String? accountType;
  
  @JsonKey(name: 'update_time', fromJson: _parseDateTime)
  final DateTime updateTime;

  const WiseBalance({
    required this.accountId,
    required this.currency,
    required this.availableBalance,
    required this.reservedBalance,
    required this.totalBalance,
    this.accountName,
    this.accountType,
    required this.updateTime,
  });

  factory WiseBalance.fromJson(Map<String, dynamic> json) =>
      _$WiseBalanceFromJson(json);

  Map<String, dynamic> toJson() => _$WiseBalanceToJson(this);

  /// 解析数值字段，支持字符串和数字类型
  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        print('解析Wise余额数值失败: $value, 错误: $e');
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
        print('解析Wise余额日期失败: $value, 错误: $e');
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
        return 'JP¥';  // 修复：日元应该显示JP¥而不是¥
      case 'AUD':
        return 'A\$';
      case 'CAD':
        return 'C\$';
      case 'CHF':
        return 'CHF';
      case 'SGD':
        return 'S\$';
      case 'HKD':
        return 'HK\$';
      default:
        return currency;
    }
  }

  /// 格式化余额显示
  String get formattedAvailableBalance {
    if (availableBalance >= 1000) {
      return '${currencySymbol}${(availableBalance / 1000).toStringAsFixed(1)}K';
    } else {
      return '${currencySymbol}${availableBalance.toStringAsFixed(2)}';
    }
  }

  /// 格式化总余额显示
  String get formattedTotalBalance {
    if (totalBalance >= 1000) {
      return '${currencySymbol}${(totalBalance / 1000).toStringAsFixed(1)}K';
    } else {
      return '${currencySymbol}${totalBalance.toStringAsFixed(2)}';
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

  /// 获取账户类型显示名称
  String get accountTypeDisplay {
    switch (accountType?.toUpperCase()) {
      case 'STANDARD':
        return '标准账户';
      case 'SAVINGS':
        return '储蓄账户';
      default:
        return accountType ?? '未知类型';
    }
  }

  /// 获取当前价值（用于排序和显示）
  double get currentValue => availableBalance;
  
  /// 获取当前价值文本（用于显示）
  String get currentValueText => formattedAvailableBalance;
}
