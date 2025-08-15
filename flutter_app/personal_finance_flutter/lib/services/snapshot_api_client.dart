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

  /// 获取快照状态总览
  static Future<Map<String, dynamic>> getSnapshotStatus() async {
    try {
      print('🔍 [SnapshotApiClient] 获取快照状态总览');
      
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/status'),
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
      print('❌ [SnapshotApiClient] 获取快照状态失败: $e');
      // 返回模拟数据作为fallback
      return _getMockSnapshotStatus();
    }
  }

  /// 获取平台状态列表
  static Future<List<Map<String, dynamic>>> getPlatformStatus() async {
    try {
      print('🔍 [SnapshotApiClient] 获取平台状态列表');
      
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/platforms'),
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
      print('❌ [SnapshotApiClient] 获取平台状态失败: $e');
      // 返回模拟数据作为fallback
      return _getMockPlatformStatus();
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

  /// 手动触发数据同步
  static Future<Map<String, dynamic>> triggerManualSync({
    List<String>? platforms,
  }) async {
    try {
      print('🔍 [SnapshotApiClient] 手动触发数据同步: ${platforms ?? '全平台'}');
      
      final response = await http.post(
        Uri.parse('$baseUrl/snapshot/sync'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'platforms': platforms,
        }),
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return {
            'success': true,
            'message': jsonData['message'],
            'data': jsonData['data'],
          };
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SnapshotApiClient] 手动同步失败: $e');
      // 返回模拟响应
      return {
        'success': false,
        'message': '同步请求失败: $e',
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

  static Map<String, dynamic> _getMockSnapshotStatus() {
    return {
      'last_update': DateTime.now().subtract(Duration(minutes: 3)).toIso8601String(),
      'last_update_text': '3分钟前',
      'status': 'fresh',
      'minutes_ago': 3,
      'total_snapshots_today': 28,
      'platform_count': 3,
      'asset_type_count': 3,
      'health_score': {
        'overall': 92.5,
        'completeness': 95.0,
        'timeliness': 88.0,
        'connectivity': 95.0,
      },
      'next_sync': DateTime.now().add(Duration(minutes: 27)).toIso8601String(),
    };
  }

  static List<Map<String, dynamic>> _getMockPlatformStatus() {
    return [
      {
        'platform': '支付宝',
        'status': 'connected',
        'status_text': '正常',
        'last_update': DateTime.now().subtract(Duration(minutes: 3)).toIso8601String(),
        'time_text': '3分钟前',
        'minutes_ago': 3,
        'total_value': 158460.30,
        'asset_count': 12,
        'asset_types': '基金',
        'currencies': 'CNY',
        'icon': '💰',
        'asset_details': [
          {
            'asset_type': '基金',
            'asset_name': '易方达沪深300ETF',
            'balance': 120580.50,
            'base_value': 120580.50,
            'currency': 'CNY'
          },
          {
            'asset_type': '基金',
            'asset_name': '华夏货币基金',
            'balance': 37879.80,
            'base_value': 37879.80,
            'currency': 'CNY'
          },
        ]
      },
      {
        'platform': 'Wise',
        'status': 'connected',
        'status_text': '正常',
        'last_update': DateTime.now().subtract(Duration(minutes: 5)).toIso8601String(),
        'time_text': '5分钟前',
        'minutes_ago': 5,
        'total_value': 8158.23,
        'asset_count': 4,
        'asset_types': '外汇',
        'currencies': 'USD, EUR, JPY, AUD',
        'icon': '🌍',
        'asset_details': [
          {
            'asset_type': '外汇',
            'asset_name': 'USD余额',
            'balance': 1200.45,
            'base_value': 1200.45,
            'currency': 'USD'
          },
          {
            'asset_type': '外汇',
            'asset_name': 'EUR余额',
            'balance': 890.20,
            'base_value': 890.20,
            'currency': 'EUR'
          },
        ]
      },
      {
        'platform': 'IBKR',
        'status': 'warning',
        'status_text': '数据有点旧',
        'last_update': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
        'time_text': '2小时前',
        'minutes_ago': 120,
        'total_value': 42.03,
        'asset_count': 1,
        'asset_types': '证券',
        'currencies': 'USD',
        'icon': '📈',
        'asset_details': [
          {
            'asset_type': '证券',
            'asset_name': 'IBKR账户',
            'balance': 42.03,
            'base_value': 42.03,
            'currency': 'USD'
          },
        ]
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