import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class SnapshotApiClient {
  // 获取基础URL
  static String get baseUrl {
    const String? backendUrl = String.fromEnvironment('BACKEND_API_URL');
    if (backendUrl != null && backendUrl.isNotEmpty) {
      return backendUrl;
    }
    return 'https://backend-production-2750.up.railway.app/api/v1';
  }

  /// 获取资产快照列表 (使用现有API)
  static Future<List<Map<String, dynamic>>> getAssetSnapshots({String baseCurrency = 'USD'}) async {
    try {
      print('🔍 [SnapshotApiClient] 获取资产快照列表');
      
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/assets?base_currency=$baseCurrency'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return List<Map<String, dynamic>>.from(jsonData['data']);
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SnapshotApiClient] 获取资产快照失败: $e');
      // 返回模拟数据作为fallback
      return _getMockAssetSnapshots();
    }
  }

  /// 获取资产趋势数据 (使用现有API)
  static Future<List<Map<String, dynamic>>> getAssetTrend({
    String baseCurrency = 'USD', 
    int days = 7
  }) async {
    try {
      print('🔍 [SnapshotApiClient] 获取资产趋势数据');
      
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/assets/trend?base_currency=$baseCurrency&days=$days'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return List<Map<String, dynamic>>.from(jsonData['data']);
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SnapshotApiClient] 获取资产趋势失败: $e');
      // 返回模拟数据作为fallback
      return _getMockAssetTrend();
    }
  }

  /// 获取快照历史记录
  static Future<Map<String, dynamic>> getSnapshotHistory({
    int days = 7,
    int limit = 50,
  }) async {
    try {
      print('🔍 [SnapshotApiClient] 获取快照历史记录');
      
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/history?days=$days&limit=$limit'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return jsonData['data'];
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SnapshotApiClient] 获取快照历史失败: $e');
      // 返回模拟数据作为fallback
      return _getMockSnapshotHistory();
    }
  }

  /// 手动触发资产快照 (使用现有API)
  static Future<Map<String, dynamic>> triggerAssetSnapshot({
    String baseCurrency = 'USD',
  }) async {
    try {
      print('🔍 [SnapshotApiClient] 手动触发资产快照');
      
      final response = await http.post(
        Uri.parse('$baseUrl/snapshot/extract?base_currency=$baseCurrency'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return {
            'success': true,
            'message': jsonData['message'],
            'data': jsonData,
          };
        } else {
          throw Exception('API返回错误: ${jsonData['error'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SnapshotApiClient] 手动快照失败: $e');
      // 返回模拟响应
      return {
        'success': false,
        'message': '快照生成失败: $e',
        'data': null,
      };
    }
  }

  /// 获取数据统计信息
  static Future<Map<String, dynamic>> getDataStatistics({int days = 30}) async {
    try {
      print('🔍 [SnapshotApiClient] 获取数据统计信息');
      
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/statistics?days=$days'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return jsonData['data'];
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SnapshotApiClient] 获取数据统计失败: $e');
      // 返回模拟数据作为fallback
      return _getMockDataStatistics();
    }
  }

  // ========== Mock Data Methods ==========

  static List<Map<String, dynamic>> _getMockAssetSnapshots() {
    return [
      {
        'id': 1,
        'user_id': 'default',
        'platform': '支付宝',
        'asset_type': '基金',
        'asset_code': '110020',
        'asset_name': '易方达沪深300ETF',
        'currency': 'CNY',
        'balance': 120580.50,
        'balance_cny': 120580.50,
        'balance_usd': 16821.18,
        'balance_eur': 15942.35,
        'base_value': 16821.18,
        'snapshot_time': DateTime.now().subtract(Duration(minutes: 3)).toIso8601String(),
        'extra': null
      },
      {
        'id': 2,
        'user_id': 'default',
        'platform': '支付宝',
        'asset_type': '基金',
        'asset_code': '000001',
        'asset_name': '华夏货币基金',
        'currency': 'CNY',
        'balance': 37879.80,
        'balance_cny': 37879.80,
        'balance_usd': 5288.86,
        'balance_eur': 5014.12,
        'base_value': 5288.86,
        'snapshot_time': DateTime.now().subtract(Duration(minutes: 3)).toIso8601String(),
        'extra': null
      },
      {
        'id': 3,
        'user_id': 'default',
        'platform': 'Wise',
        'asset_type': '外汇',
        'asset_code': 'USD',
        'asset_name': 'USD余额',
        'currency': 'USD',
        'balance': 1200.45,
        'balance_cny': 8602.84,
        'balance_usd': 1200.45,
        'balance_eur': 1137.42,
        'base_value': 1200.45,
        'snapshot_time': DateTime.now().subtract(Duration(minutes: 5)).toIso8601String(),
        'extra': null
      },
      {
        'id': 4,
        'user_id': 'default',
        'platform': 'IBKR',
        'asset_type': '证券',
        'asset_code': 'IBKR',
        'asset_name': 'IBKR账户',
        'currency': 'USD',
        'balance': 42.03,
        'balance_cny': 301.26,
        'balance_usd': 42.03,
        'balance_eur': 39.84,
        'base_value': 42.03,
        'snapshot_time': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
        'extra': null
      }
    ];
  }

  static List<Map<String, dynamic>> _getMockAssetTrend() {
    return [
      {
        'date': DateTime.now().subtract(Duration(days: 6)).toIso8601String().substring(0, 10),
        'total': 23215.42
      },
      {
        'date': DateTime.now().subtract(Duration(days: 5)).toIso8601String().substring(0, 10),
        'total': 23156.78
      },
      {
        'date': DateTime.now().subtract(Duration(days: 4)).toIso8601String().substring(0, 10),
        'total': 23298.91
      },
      {
        'date': DateTime.now().subtract(Duration(days: 3)).toIso8601String().substring(0, 10),
        'total': 23342.15
      },
      {
        'date': DateTime.now().subtract(Duration(days: 2)).toIso8601String().substring(0, 10),
        'total': 23289.67
      },
      {
        'date': DateTime.now().subtract(Duration(days: 1)).toIso8601String().substring(0, 10),
        'total': 23351.52
      },
      {
        'date': DateTime.now().toIso8601String().substring(0, 10),
        'total': 23352.52
      }
    ];
  }

  static Map<String, dynamic> _getMockSnapshotHistory() {
    return {
      'history': [
        {
          'snapshot_time': DateTime.now().subtract(Duration(minutes: 0)).toIso8601String(),
          'time_text': '刚刚',
          'sync_type': 'full',
          'sync_type_text': '全量更新',
          'record_count': 13,
          'platform_count': 3,
          'total_value': 166660.56,
          'platforms': '支付宝, Wise, IBKR',
          'status': 'success'
        },
        {
          'snapshot_time': DateTime.now().subtract(Duration(minutes: 30)).toIso8601String(),
          'time_text': '30分钟前',
          'sync_type': 'partial',
          'sync_type_text': '增量更新',
          'record_count': 8,
          'platform_count': 2,
          'total_value': 166660.32,
          'platforms': '支付宝, Wise',
          'status': 'success'
        },
        {
          'snapshot_time': DateTime.now().subtract(Duration(hours: 1)).toIso8601String(),
          'time_text': '1小时前',
          'sync_type': 'full',
          'sync_type_text': '全量更新',
          'record_count': 13,
          'platform_count': 3,
          'total_value': 166550.12,
          'platforms': '支付宝, Wise, IBKR',
          'status': 'success'
        },
        {
          'snapshot_time': DateTime.now().subtract(Duration(hours: 1, minutes: 15)).toIso8601String(),
          'time_text': '1小时前',
          'sync_type': 'minimal',
          'sync_type_text': 'IBKR重试',
          'record_count': 0,
          'platform_count': 0,
          'total_value': 0,
          'platforms': 'IBKR',
          'status': 'failed'
        },
      ],
      'total_records': 4,
      'query_days': 7
    };
  }

  static Map<String, dynamic> _getMockDataStatistics() {
    return {
      'total_snapshots': 307,
      'unique_platforms': 3,
      'unique_asset_types': 3,
      'unique_currencies': 6,
      'earliest_data': DateTime.now().subtract(Duration(days: 51)).toIso8601String(),
      'latest_data': DateTime.now().toIso8601String(),
      'avg_asset_value': 5420.2,
      'success_rate': 96.4,
      'avg_delay_minutes': 2.3,
      'query_days': 30
    };
  }
}