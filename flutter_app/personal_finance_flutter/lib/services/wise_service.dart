import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/wise_balance.dart';

class WiseService {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app/api/v1';
  
  /// 获取所有Wise账户余额
  static Future<List<WiseBalance>> getAllBalances() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/wise/all-balances'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> balancesData = data['data'];
          return balancesData.map((json) => WiseBalance.fromJson(json)).toList();
        } else {
          throw Exception('获取Wise余额失败: ${data['message']}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('获取Wise余额异常: $e');
      // 返回模拟数据用于开发测试
      return _getMockWiseBalances();
    }
  }
  
  /// 获取Wise账户汇总信息
  static Future<Map<String, dynamic>> getWiseSummary() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/wise/summary'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          // 转换数值字段为正确的类型
          final summaryData = data['data'];
          return {
            'total_accounts': _parseInt(summaryData['total_accounts']),
            'total_currencies': _parseInt(summaryData['total_currencies']),
            'balance_by_currency': summaryData['balance_by_currency'] ?? {},
            'recent_transactions_count': _parseInt(summaryData['recent_transactions_count']),
            'last_updated': summaryData['last_updated'],
          };
        } else {
          throw Exception('获取Wise汇总信息失败: ${data['message']}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('获取Wise汇总信息异常: $e');
      // 返回模拟数据用于开发测试
      return _getMockWiseSummary();
    }
  }
  
  /// 获取汇率信息
  static Future<Map<String, dynamic>> getExchangeRates({
    String source = 'USD',
    String target = 'CNY',
  }) async {
    try {
      print('🔄 [WiseService] 正在获取汇率: $source -> $target');
      
      final response = await http.get(
        Uri.parse('$baseUrl/wise/exchange-rates?source=$source&target=$target'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [WiseService] 汇率API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [WiseService] 汇率API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final responseData = data['data'];
          
          // 处理不同的数据结构
          Map<String, dynamic>? rateData;
          
          if (responseData is Map<String, dynamic>) {
            // 直接是Map的情况
            rateData = responseData;
          } else if (responseData is List && responseData.isNotEmpty) {
            // 是数组的情况，取第一个元素
            final firstItem = responseData.first;
            if (firstItem is Map<String, dynamic>) {
              rateData = firstItem;
              print('✅ [WiseService] 从数组响应中提取汇率数据: $rateData');
            }
          }
          
          if (rateData != null) {
            // 验证汇率数据的合理性
            final rate = rateData['rate'];
            if (rate != null && rate is num) {
              final rateValue = rate.toDouble();
              if (source == 'USD' && target == 'CNY') {
                // USD/CNY汇率应该在合理范围内
                if (rateValue < 1.0 || rateValue > 10.0) {
                  print('⚠️ [WiseService] USD/CNY汇率异常: $rateValue，使用默认汇率');
                  return _getDefaultExchangeRates(source, target);
                }
              }
              print('✅ [WiseService] 获取到有效汇率: $rateValue');
              return rateData;
            } else {
              print('⚠️ [WiseService] 汇率数据格式异常，使用默认汇率');
              return _getDefaultExchangeRates(source, target);
            }
          } else {
            print('⚠️ [WiseService] 无法解析响应数据结构，使用默认汇率');
            return _getDefaultExchangeRates(source, target);
          }
        } else {
          print('❌ [WiseService] 汇率API返回失败: ${data['message']}');
          return _getDefaultExchangeRates(source, target);
        }
      } else {
        print('❌ [WiseService] 汇率API HTTP错误: ${response.statusCode}');
        return _getDefaultExchangeRates(source, target);
      }
    } catch (e) {
      print('❌ [WiseService] 获取汇率异常: $e');
      // 返回默认汇率数据
      return _getDefaultExchangeRates(source, target);
    }
  }
  
  /// 获取多个货币对的汇率信息
  static Future<Map<String, Map<String, dynamic>>> getMultipleExchangeRates() async {
    print('🔄 [WiseService] 正在获取多个货币对汇率...');
    
    try {
      // 并行获取多个汇率
      final futures = await Future.wait([
        getExchangeRates(source: 'USD', target: 'CNY'),
        getExchangeRates(source: 'EUR', target: 'USD'),
        getExchangeRates(source: 'GBP', target: 'USD'),
        getExchangeRates(source: 'JPY', target: 'USD'),
        getExchangeRates(source: 'AUD', target: 'USD'),
        getExchangeRates(source: 'HKD', target: 'USD'),
      ]);
      
      final rates = <String, Map<String, dynamic>>{};
      rates['USD_CNY'] = futures[0];
      rates['EUR_USD'] = futures[1];
      rates['GBP_USD'] = futures[2];
      rates['JPY_USD'] = futures[3];
      rates['AUD_USD'] = futures[4];
      rates['HKD_USD'] = futures[5];
      
      print('✅ [WiseService] 成功获取多个汇率: ${rates.keys.join(', ')}');
      return rates;
      
    } catch (e) {
      print('❌ [WiseService] 获取多个汇率失败: $e');
      // 返回默认汇率
      return {
        'USD_CNY': _getDefaultExchangeRates('USD', 'CNY'),
        'EUR_USD': _getDefaultExchangeRates('EUR', 'USD'),
        'GBP_USD': _getDefaultExchangeRates('GBP', 'USD'),
        'JPY_USD': _getDefaultExchangeRates('JPY', 'USD'),
        'AUD_USD': _getDefaultExchangeRates('AUD', 'USD'),
        'HKD_USD': _getDefaultExchangeRates('HKD', 'USD'),
      };
    }
  }
  
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
  
  /// 解析整数字段，支持字符串和数字类型
  static int _parseInt(dynamic value) {
    if (value == null) return 0;
    if (value is num) return value.toInt();
    if (value is String) {
      try {
        return int.parse(value);
      } catch (e) {
        print('解析整数值失败: $value, 错误: $e');
        return 0;
      }
    }
    return 0;
  }
  
  /// 获取模拟Wise余额数据（开发测试用）
  static List<WiseBalance> _getMockWiseBalances() {
    return [
      WiseBalance(
        accountId: 'usd_account_001',
        currency: 'USD',
        availableBalance: 5000.0,
        reservedBalance: 0.0,
        totalBalance: 5000.0,
        accountName: '美元账户',
        accountType: 'STANDARD',
        updateTime: DateTime.now().subtract(Duration(minutes: 5)),
      ),
      WiseBalance(
        accountId: 'eur_account_001',
        currency: 'EUR',
        availableBalance: 3000.0,
        reservedBalance: 0.0,
        totalBalance: 3000.0,
        accountName: '欧元账户',
        accountType: 'STANDARD',
        updateTime: DateTime.now().subtract(Duration(minutes: 5)),
      ),
      WiseBalance(
        accountId: 'gbp_account_001',
        currency: 'GBP',
        availableBalance: 2000.0,
        reservedBalance: 0.0,
        totalBalance: 2000.0,
        accountName: '英镑账户',
        accountType: 'STANDARD',
        updateTime: DateTime.now().subtract(Duration(minutes: 5)),
      ),
    ];
  }
  
  /// 获取模拟Wise汇总数据（开发测试用）
  static Map<String, dynamic> _getMockWiseSummary() {
    return {
      'total_accounts': 3,
      'total_currencies': 3,
      'balance_by_currency': {
        'USD': 5000.0,
        'EUR': 3000.0,
        'GBP': 2000.0,
      },
      'recent_transactions_count': 12,
      'last_updated': DateTime.now().toIso8601String(),
    };
  }
  
  /// 获取模拟汇率数据（开发测试用）
  static Map<String, dynamic> _getMockExchangeRates(String source, String target) {
    // 模拟一些常见货币对的汇率
    final rates = {
      'USD_CNY': 7.25,    // 更准确的USD/CNY汇率
      'EUR_CNY': 7.85,    // 更准确的EUR/CNY汇率
      'GBP_CNY': 9.15,    // 更准确的GBP/CNY汇率
      'USD_EUR': 0.92,    // USD/EUR汇率
      'EUR_USD': 1.09,    // EUR/USD汇率
      'GBP_USD': 1.26,    // GBP/USD汇率
    };
    
    final key = '${source}_$target';
    final rate = rates[key] ?? 1.0;
    
    return {
      'source': source,
      'target': target,
      'rate': rate,
      'timestamp': DateTime.now().toIso8601String(),
      'change_24h': 0.02, // 24小时变化
      'change_percent': 0.28, // 变化百分比
    };
  }

  /// 获取默认汇率数据（当API调用失败时使用）
  static Map<String, dynamic> _getDefaultExchangeRates(String source, String target) {
    print('🔄 [WiseService] 使用默认汇率数据: $source -> $target');
    
    // 使用更准确的默认汇率
    final defaultRates = {
      'USD_CNY': 7.25,    // USD/CNY 默认汇率
      'EUR_CNY': 7.85,    // EUR/CNY 默认汇率
      'GBP_CNY': 9.15,    // GBP/CNY 默认汇率
      'JPY_CNY': 0.048,   // JPY/CNY 默认汇率 (1/150 * 7.25)
      'AUD_CNY': 4.79,    // AUD/CNY 默认汇率 (1/0.66 * 7.25)
      'HKD_CNY': 0.93,    // HKD/CNY 默认汇率 (1/7.8 * 7.25)
      
      // 添加交叉汇率
      'EUR_USD': 0.92,    // EUR/USD 默认汇率
      'GBP_USD': 1.26,    // GBP/USD 默认汇率
      'JPY_USD': 0.0067,  // JPY/USD 默认汇率 (1/150)
      'AUD_USD': 0.66,    // AUD/USD 默认汇率
      'HKD_USD': 0.128,   // HKD/USD 默认汇率 (1/7.8)
      'SGD_USD': 0.74,    // SGD/USD 默认汇率 (1/1.35)
      'CHF_USD': 1.14,    // CHF/USD 默认汇率 (1/0.88)
      'CAD_USD': 0.74,    // CAD/USD 默认汇率 (1/1.35)
    };
    
    final key = '${source}_$target';
    final rate = defaultRates[key] ?? 1.0;
    
    return {
      'source': source,
      'target': target,
      'rate': rate,
      'timestamp': DateTime.now().toIso8601String(),
      'change_24h': 0.0, // 24小时变化
      'change_percent': 0.0, // 变化百分比
      'is_default': true, // 标记这是默认汇率
    };
  }
}
