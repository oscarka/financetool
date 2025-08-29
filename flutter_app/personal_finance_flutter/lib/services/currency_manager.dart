import 'package:flutter/foundation.dart';

/// 全局货币管理服务
class CurrencyManager extends ChangeNotifier {
  static final CurrencyManager _instance = CurrencyManager._internal();
  factory CurrencyManager() => _instance;
  CurrencyManager._internal();

  String _selectedCurrency = 'CNY'; // 默认使用CNY
  
  /// 获取当前选择的基准货币
  String get selectedCurrency => _selectedCurrency;
  
  /// 设置基准货币
  void setCurrency(String currency) {
    if (_selectedCurrency != currency) {
      _selectedCurrency = currency;
      notifyListeners();
    }
  }
  
  /// 获取货币符号
  String getCurrencySymbol(String currency) {
    switch (currency.toUpperCase()) {
      case 'CNY':
        return '¥';
      case 'USD':
        return '\$';
      case 'EUR':
        return '€';
      case 'USDT':
        return 'USDT ';
      case 'BTC':
        return '₿';
      case 'GBP':
        return '£';
      case 'JPY':
        return '¥';
      case 'AUD':
        return 'A\$';
      case 'HKD':
        return 'HK\$';
      case 'SGD':
        return 'S\$';
      case 'CHF':
        return 'CHF';
      case 'CAD':
        return 'C\$';
      default:
        return '\$';
    }
  }
  
  /// 获取货币的中文名称
  String getCurrencyDisplayName(String currency) {
    switch (currency.toUpperCase()) {
      case 'CNY':
        return '人民币';
      case 'USD':
        return '美元';
      case 'EUR':
        return '欧元';
      case 'USDT':
        return 'USDT';
      case 'BTC':
        return '比特币';
      case 'GBP':
        return '英镑';
      case 'JPY':
        return '日元';
      case 'AUD':
        return '澳元';
      case 'HKD':
        return '港币';
      case 'SGD':
        return '新加坡元';
      case 'CHF':
        return '瑞士法郎';
      case 'CAD':
        return '加拿大元';
      default:
        return currency;
    }
  }
  
  /// 获取基准货币的完整显示名称
  String get baseCurrencyDisplayName => getCurrencyDisplayName(_selectedCurrency);
  
  /// 获取基准货币符号
  String get baseCurrencySymbol => getCurrencySymbol(_selectedCurrency);
}
