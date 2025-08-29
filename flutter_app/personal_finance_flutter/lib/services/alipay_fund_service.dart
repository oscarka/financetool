import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/fund_position.dart';

class AlipayFundService {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app/api/v1';
  
  /// 获取支付宝基金持仓列表
  static Future<List<FundPosition>> getFundPositions() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/funds/positions'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> positionsData = data['data'];
          return positionsData.map((json) => FundPosition.fromJson(json)).toList();
        } else {
          throw Exception('获取基金持仓失败: ${data['message']}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('获取基金持仓异常: $e');
      // 返回模拟数据用于开发测试
      return _getMockFundPositions();
    }
  }
  
  /// 获取基金持仓汇总信息
  static Future<Map<String, dynamic>> getPositionSummary() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/funds/positions/summary'),
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
            'total_invested': _parseDouble(summaryData['total_invested']),
            'total_value': _parseDouble(summaryData['total_value']),
            'total_profit': _parseDouble(summaryData['total_profit']),
            'total_profit_rate': _parseDouble(summaryData['total_profit_rate']),
            'asset_count': _parseInt(summaryData['asset_count']),
            'profitable_count': _parseInt(summaryData['profitable_count']),
            'loss_count': _parseInt(summaryData['loss_count']),
          };
        } else {
          throw Exception('获取持仓汇总失败: ${data['message']}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('获取持仓汇总异常: $e');
      // 返回模拟数据用于开发测试
      return _getMockPositionSummary();
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
  
  /// 获取模拟基金持仓数据（开发测试用）
  static List<FundPosition> _getMockFundPositions() {
    return [
      FundPosition(
        assetCode: '110003',
        assetName: '易方达沪深300ETF',
        totalShares: 1000.0,
        avgCost: 16.82,
        currentNav: 16.82,
        currentValue: 16821.18,
        totalInvested: 16820.0,
        totalProfit: 1.18,
        profitRate: 0.007,
        lastUpdated: DateTime.now().subtract(Duration(minutes: 3)),
      ),
      FundPosition(
        assetCode: '000198',
        assetName: '华夏货币基金',
        totalShares: 5000.0,
        avgCost: 1.0578,
        currentNav: 1.0578,
        currentValue: 5288.86,
        totalInvested: 5289.0,
        totalProfit: -0.14,
        profitRate: -0.0003,
        lastUpdated: DateTime.now().subtract(Duration(minutes: 3)),
      ),
    ];
  }
  
  /// 获取模拟持仓汇总数据（开发测试用）
  static Map<String, dynamic> _getMockPositionSummary() {
    return {
      'total_invested': 22109.0,
      'total_value': 22110.04,
      'total_profit': 1.04,
      'total_profit_rate': 0.0005,
      'asset_count': 2,
      'profitable_count': 1,
      'loss_count': 1,
    };
  }
}
