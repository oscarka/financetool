import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/okx_balance.dart';

class OKXService {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app/api/v1';
  
  /// 获取OKX账户余额
  static Future<List<OKXBalance>> getAccountBalance() async {
    try {
      print('🔄 [OKXService] 正在获取OKX账户余额...');
      
      // 调用账户总览API，这个API会返回三个账户类型的数据
      final response = await http.get(
        Uri.parse('$baseUrl/okx/account-overview'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [OKXService] OKX账户总览API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [OKXService] OKX账户总览API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final overviewData = data['data'];
          
          final balances = <OKXBalance>[];
          
          // 处理交易账户数据
          if (overviewData['trading_account'] != null && 
              overviewData['trading_account']['currencies'] != null) {
            for (final currency in overviewData['trading_account']['currencies']) {
              final balance = OKXBalance(
                currency: currency['currency'] ?? '',
                totalBalance: _parseDouble(currency['balance'] ?? 0),
                availableBalance: _parseDouble(currency['available'] ?? 0),
                frozenBalance: _parseDouble(currency['frozen'] ?? 0),
                updateTime: DateTime.now(), // 使用当前时间
                accountType: 'trading',
              );
              
              print('🔍 [OKXService] 解析交易账户余额: ${balance.currency}, 账户类型: ${balance.accountType}, 余额: ${balance.totalBalance}');
              
              if (balance.totalBalance > 0) {
                balances.add(balance);
              }
            }
          }
          
          // 处理资金账户数据
          if (overviewData['funding_account'] != null && 
              overviewData['funding_account']['currencies'] != null) {
            for (final currency in overviewData['funding_account']['currencies']) {
              final balance = OKXBalance(
                currency: currency['currency'] ?? '',
                totalBalance: _parseDouble(currency['balance'] ?? 0),
                availableBalance: _parseDouble(currency['available'] ?? 0),
                frozenBalance: _parseDouble(currency['frozen'] ?? 0),
                updateTime: DateTime.now(), // 使用当前时间
                accountType: 'funding',
              );
              
              print('🔍 [OKXService] 解析资金账户余额: ${balance.currency}, 账户类型: ${balance.accountType}, 余额: ${balance.totalBalance}');
              
              if (balance.totalBalance > 0) {
                balances.add(balance);
              }
            }
          }
          
          // 处理储蓄账户数据
          if (overviewData['savings_account'] != null && 
              overviewData['savings_account']['currencies'] != null) {
            for (final currency in overviewData['savings_account']['currencies']) {
              final balance = OKXBalance(
                currency: currency['currency'] ?? '',
                totalBalance: _parseDouble(currency['balance'] ?? 0),
                availableBalance: _parseDouble(currency['available'] ?? 0),
                frozenBalance: _parseDouble(currency['frozen'] ?? 0),
                updateTime: DateTime.now(), // 使用当前时间
                accountType: 'savings',
              );
              
              print('🔍 [OKXService] 解析储蓄账户余额: ${balance.currency}, 账户类型: ${balance.accountType}, 余额: ${balance.totalBalance}');
              
              if (balance.totalBalance > 0) {
                balances.add(balance);
              }
            }
          }
          
          print('✅ [OKXService] 成功获取OKX账户总览: ${balances.length}条');
          print('📊 [OKXService] 余额详情: ${balances.map((b) => '${b.currency}(${b.accountType}): ${b.totalBalance}').join(', ')}');
          return balances;
          
        } else {
          print('❌ [OKXService] OKX账户总览API返回失败: ${data['message']}');
          print('🔄 [OKXService] 使用模拟数据');
          return _getMockOKXBalances();
        }
      } else {
        print('❌ [OKXService] OKX账户总览API HTTP错误: ${response.statusCode}');
        print('🔄 [OKXService] 使用模拟数据');
        return _getMockOKXBalances();
      }
    } catch (e) {
      print('❌ [OKXService] 获取OKX账户总览异常: $e');
      print('🔄 [OKXService] 使用模拟数据');
      return _getMockOKXBalances();
    }
  }
  
  /// 获取OKX持仓信息
  static Future<List<Map<String, dynamic>>> getPositions() async {
    try {
      print('🔄 [OKXService] 正在获取OKX持仓信息...');
      
      final response = await http.get(
        Uri.parse('$baseUrl/okx/positions'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [OKXService] OKX持仓API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [OKXService] OKX持仓API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> positionsData = data['data'];
          print('✅ [OKXService] 成功获取OKX持仓: ${positionsData.length}条');
          return positionsData.cast<Map<String, dynamic>>();
        } else {
          print('❌ [OKXService] OKX持仓API返回失败: ${data['message']}');
          return _getMockOKXPositions();
        }
      } else {
        print('❌ [OKXService] OKX持仓API HTTP错误: ${response.statusCode}');
        return _getMockOKXPositions();
      }
    } catch (e) {
      print('❌ [OKXService] 获取OKX持仓异常: $e');
      return _getMockOKXPositions();
    }
  }
  
  /// 获取OKX汇总信息
  static Future<Map<String, dynamic>> getOKXSummary() async {
    try {
      print('🔄 [OKXService] 正在获取OKX汇总信息...');
      
      final response = await http.get(
        Uri.parse('$baseUrl/okx/summary'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [OKXService] OKX汇总API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [OKXService] OKX汇总API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final summaryData = data['data'];
          print('✅ [OKXService] 成功获取OKX汇总信息');
          return summaryData;
        } else {
          print('❌ [OKXService] OKX汇总API返回失败: ${data['message']}');
          return _getMockOKXSummary();
        }
      } else {
        print('❌ [OKXService] OKX汇总API HTTP错误: ${response.statusCode}');
        return _getMockOKXSummary();
      }
    } catch (e) {
      print('❌ [OKXService] 获取OKX汇总信息异常: $e');
      return _getMockOKXSummary();
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
        print('解析OKX数值失败: $value, 错误: $e');
        return 0.0;
      }
    }
    return 0.0;
  }

  /// 解析时间戳字段
  static DateTime _parseDateTime(dynamic value) {
    if (value == null) return DateTime.now();
    if (value is DateTime) return value;
    if (value is String) {
      try {
        // 先尝试解析ISO格式
        return DateTime.parse(value);
      } catch (e) {
        // 如果ISO格式解析失败，尝试解析数字时间戳
        try {
          final timestamp = int.tryParse(value);
          if (timestamp != null) {
            // 判断是秒级还是毫秒级时间戳
            if (timestamp > 1000000000000) {
              // 毫秒级时间戳（13位）
              return DateTime.fromMillisecondsSinceEpoch(timestamp);
            } else {
              // 秒级时间戳（10位）
              return DateTime.fromMillisecondsSinceEpoch(timestamp * 1000);
            }
          }
        } catch (e2) {
          print('解析OKX字符串时间戳失败: $value, 错误: $e2');
        }
        print('解析OKX日期失败: $value, 错误: $e');
        return DateTime.now();
      }
    }
    if (value is int) {
      try {
        // 判断是秒级还是毫秒级时间戳
        if (value > 1000000000000) {
          // 毫秒级时间戳（13位）
          return DateTime.fromMillisecondsSinceEpoch(value);
        } else {
          // 秒级时间戳（10位）
          return DateTime.fromMillisecondsSinceEpoch(value * 1000);
        }
      } catch (e) {
        print('解析OKX时间戳失败: $value, 错误: $e');
        return DateTime.now();
      }
    }
    return DateTime.now();
  }
  
  /// 获取模拟OKX余额数据（开发测试用）
  static List<OKXBalance> _getMockOKXBalances() {
    print('🔄 [OKXService] 使用模拟OKX余额数据');
    
    // 模拟真实的OKX API数据结构
    print('🔍 [OKXService] 模拟数据结构分析:');
    print('🔍 [OKXService] 模拟数据包含:');
    print('  - Trading账户: BTC, ETH');
    print('  - Funding账户: USDT, USDC');
    print('  - Savings账户: SOL, ADA, DOT, LINK');
    
    return [
      // Trading账户
      OKXBalance(
        currency: 'BTC',
        totalBalance: 0.125,
        availableBalance: 0.125,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'trading',
      ),
      OKXBalance(
        currency: 'ETH',
        totalBalance: 2.5,
        availableBalance: 2.5,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'trading',
      ),
      // Funding账户
      OKXBalance(
        currency: 'USDT',
        totalBalance: 5000.0,
        availableBalance: 5000.0,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'funding',
      ),
      OKXBalance(
        currency: 'USDC',
        totalBalance: 2500.0,
        availableBalance: 2500.0,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'funding',
      ),
      // Savings账户
      OKXBalance(
        currency: 'SOL',
        totalBalance: 50.0,
        availableBalance: 50.0,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'savings',
      ),
      OKXBalance(
        currency: 'ADA',
        totalBalance: 10000.0,
        availableBalance: 10000.0,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'savings',
      ),
      // 添加更多savings账户资产
      OKXBalance(
        currency: 'DOT',
        totalBalance: 200.0,
        availableBalance: 200.0,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'savings',
      ),
      OKXBalance(
        currency: 'LINK',
        totalBalance: 150.0,
        availableBalance: 150.0,
        frozenBalance: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 1)),
        accountType: 'savings',
      ),
    ];
  }
  
  /// 获取模拟OKX持仓数据（开发测试用）
  static List<Map<String, dynamic>> _getMockOKXPositions() {
    print('🔄 [OKXService] 使用模拟OKX持仓数据');
    return [
      {
        'inst_id': 'BTC-USDT-SWAP',
        'pos_side': 'long',
        'pos': '0.1',
        'avg_px': '45000',
        'upl': '500',
        'currency': 'USDT',
        'update_time': DateTime.now().subtract(Duration(hours: 1)).toIso8601String(),
      },
      {
        'inst_id': 'ETH-USDT-SWAP',
        'pos_side': 'short',
        'pos': '1.0',
        'avg_px': '3000',
        'upl': '-100',
        'currency': 'USDT',
        'update_time': DateTime.now().subtract(Duration(hours: 1)).toIso8601String(),
      },
    ];
  }
  
  /// 获取模拟OKX汇总数据（开发测试用）
  static Map<String, dynamic> _getMockOKXSummary() {
    print('🔄 [OKXService] 使用模拟OKX汇总数据');
    return {
      'total_balance_by_currency': {
        'BTC': 0.125,
        'ETH': 2.5,
        'USDT': 5000.0,
        'USDC': 2500.0,
      },
      'position_count': 2,
      'transaction_count_24h': 15,
      'unrealized_pnl': 400.0,
      'realized_pnl': 150.0,
      'latest_market_data_count': 10,
      'last_update': DateTime.now().toIso8601String(),
      'source': 'mock',
    };
  }
}
