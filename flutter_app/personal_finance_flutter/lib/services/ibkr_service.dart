import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/ibkr_position.dart';

class IBKRService {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app/api/v1';
  
  /// 获取IBKR持仓信息
  static Future<List<IBKRPosition>> getPositions() async {
    try {
      print('🔄 [IBKRService] 正在获取IBKR持仓信息...');
      
      final response = await http.get(
        Uri.parse('$baseUrl/ibkr/positions'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [IBKRService] IBKR持仓API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [IBKRService] IBKR持仓API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> positionsData = data['data'];
          final positions = positionsData.map((json) => IBKRPosition.fromJson(json)).toList();
          print('✅ [IBKRService] 成功获取IBKR持仓: ${positions.length}条');
          return positions;
        } else {
          print('❌ [IBKRService] IBKR持仓API返回失败: ${data['message']}');
          return _getMockIBKRPositions();
        }
      } else {
        print('❌ [IBKRService] IBKR持仓API HTTP错误: ${response.statusCode}');
        return _getMockIBKRPositions();
      }
    } catch (e) {
      print('❌ [IBKRService] 获取IBKR持仓异常: $e');
      return _getMockIBKRPositions();
    }
  }
  
  /// 获取IBKR余额信息
  static Future<List<Map<String, dynamic>>> getBalances() async {
    try {
      print('🔄 [IBKRService] 正在获取IBKR余额信息...');
      
      final response = await http.get(
        Uri.parse('$baseUrl/ibkr/balances'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [IBKRService] IBKR余额API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [IBKRService] IBKR余额API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> balancesData = data['data'];
          print('✅ [IBKRService] 成功获取IBKR余额: ${balancesData.length}条');
          return balancesData.cast<Map<String, dynamic>>();
        } else {
          print('❌ [IBKRService] IBKR余额API返回失败: ${data['message']}');
          return _getMockIBKRBalances();
        }
      } else {
        print('❌ [IBKRService] IBKR余额API HTTP错误: ${response.statusCode}');
        return _getMockIBKRBalances();
      }
    } catch (e) {
      print('❌ [IBKRService] 获取IBKR余额异常: $e');
      return _getMockIBKRBalances();
    }
  }
  
  /// 获取IBKR汇总信息
  static Future<Map<String, dynamic>> getIBKRSummary() async {
    try {
      print('🔄 [IBKRService] 正在获取IBKR汇总信息...');
      
      final response = await http.get(
        Uri.parse('$baseUrl/ibkr/summary'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [IBKRService] IBKR汇总API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [IBKRService] IBKR汇总API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final summaryData = data['data'];
          print('✅ [IBKRService] 成功获取IBKR汇总信息');
          return summaryData;
        } else {
          print('❌ [IBKRService] IBKR汇总API返回失败: ${data['message']}');
          return _getMockIBKRSummary();
        }
      } else {
        print('❌ [IBKRService] IBKR汇总API HTTP错误: ${response.statusCode}');
        return _getMockIBKRSummary();
      }
    } catch (e) {
      print('❌ [IBKRService] 获取IBKR汇总信息异常: $e');
      return _getMockIBKRSummary();
    }
  }
  
  /// 获取模拟IBKR持仓数据（开发测试用）
  static List<IBKRPosition> _getMockIBKRPositions() {
    print('🔄 [IBKRService] 使用模拟IBKR持仓数据');
    return [
      IBKRPosition(
        accountId: 'U13638726',
        symbol: 'TSLA',
        quantity: 0.01,
        marketValue: 2.96,
        averageCost: 0.0,
        currency: 'USD',
        unrealizedPnl: 0.22,
        realizedPnl: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 2)),
      ),
      IBKRPosition(
        accountId: 'U13638726',
        symbol: 'AAPL',
        quantity: 5.0,
        marketValue: 850.0,
        averageCost: 800.0,
        currency: 'USD',
        unrealizedPnl: 50.0,
        realizedPnl: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 2)),
      ),
      IBKRPosition(
        accountId: 'U13638726',
        symbol: 'NVDA',
        quantity: 2.0,
        marketValue: 1200.0,
        averageCost: 1100.0,
        currency: 'USD',
        unrealizedPnl: 100.0,
        realizedPnl: 0.0,
        updateTime: DateTime.now().subtract(Duration(hours: 2)),
      ),
    ];
  }
  
  /// 获取模拟IBKR余额数据（开发测试用）
  static List<Map<String, dynamic>> _getMockIBKRBalances() {
    print('🔄 [IBKRService] 使用模拟IBKR余额数据');
    return [
      {
        'account_id': 'U13638726',
        'total_cash': 2.74,
        'net_liquidation': 2053.70,
        'buying_power': 2.74,
        'currency': 'USD',
        'update_time': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
      },
    ];
  }
  
  /// 获取模拟IBKR汇总数据（开发测试用）
  static Map<String, dynamic> _getMockIBKRSummary() {
    print('🔄 [IBKRService] 使用模拟IBKR汇总数据');
    return {
      'total_accounts': 1,
      'total_positions': 3,
      'total_net_liquidation': 2053.70,
      'total_cash': 2.74,
      'last_sync_status': 'success',
      'last_sync_time': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
      'last_updated': DateTime.now().toIso8601String(),
    };
  }
}
