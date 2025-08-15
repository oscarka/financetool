import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class UserSettingsApiClient {
  // 获取基础URL
  static String get baseUrl {
    const String? backendUrl = String.fromEnvironment('BACKEND_API_URL');
    if (backendUrl != null && backendUrl.isNotEmpty) {
      return backendUrl;
    }
    return 'https://backend-production-2750.up.railway.app/api/v1';
  }

  /// 获取用户显示偏好设置
  static Future<Map<String, dynamic>> getUserPreferences() async {
    try {
      print('🔍 [UserSettingsApiClient] 获取用户显示偏好');
      
      final response = await http.get(
        Uri.parse('$baseUrl/user/preferences'),
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
      print('❌ [UserSettingsApiClient] 获取用户偏好失败: $e');
      // 返回默认设置作为fallback
      return _getDefaultUserPreferences();
    }
  }

  /// 更新用户显示偏好设置
  static Future<Map<String, dynamic>> updateUserPreferences(
    Map<String, dynamic> preferences,
  ) async {
    try {
      print('🔍 [UserSettingsApiClient] 更新用户显示偏好');
      
      final response = await http.put(
        Uri.parse('$baseUrl/user/preferences'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(preferences),
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
      print('❌ [UserSettingsApiClient] 更新用户偏好失败: $e');
      return {
        'success': false,
        'message': '设置保存失败: $e',
        'data': null,
      };
    }
  }

  /// 获取通知设置
  static Future<Map<String, dynamic>> getNotificationSettings() async {
    try {
      print('🔍 [UserSettingsApiClient] 获取通知设置');
      
      final response = await http.get(
        Uri.parse('$baseUrl/user/notifications'),
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
      print('❌ [UserSettingsApiClient] 获取通知设置失败: $e');
      // 返回默认设置作为fallback
      return _getDefaultNotificationSettings();
    }
  }

  /// 更新通知设置
  static Future<Map<String, dynamic>> updateNotificationSettings(
    Map<String, dynamic> notifications,
  ) async {
    try {
      print('🔍 [UserSettingsApiClient] 更新通知设置');
      
      final response = await http.put(
        Uri.parse('$baseUrl/user/notifications'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(notifications),
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
      print('❌ [UserSettingsApiClient] 更新通知设置失败: $e');
      return {
        'success': false,
        'message': '通知设置保存失败: $e',
        'data': null,
      };
    }
  }

  /// 获取同步设置
  static Future<Map<String, dynamic>> getSyncSettings() async {
    try {
      print('🔍 [UserSettingsApiClient] 获取同步设置');
      
      final response = await http.get(
        Uri.parse('$baseUrl/user/sync-settings'),
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
      print('❌ [UserSettingsApiClient] 获取同步设置失败: $e');
      // 返回默认设置作为fallback
      return _getDefaultSyncSettings();
    }
  }

  /// 更新同步设置
  static Future<Map<String, dynamic>> updateSyncSettings(
    Map<String, dynamic> syncSettings,
  ) async {
    try {
      print('🔍 [UserSettingsApiClient] 更新同步设置');
      
      final response = await http.put(
        Uri.parse('$baseUrl/user/sync-settings'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(syncSettings),
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
      print('❌ [UserSettingsApiClient] 更新同步设置失败: $e');
      return {
        'success': false,
        'message': '同步设置保存失败: $e',
        'data': null,
      };
    }
  }

  /// 获取用户档案信息
  static Future<Map<String, dynamic>> getUserProfile() async {
    try {
      print('🔍 [UserSettingsApiClient] 获取用户档案');
      
      final response = await http.get(
        Uri.parse('$baseUrl/user/profile'),
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
      print('❌ [UserSettingsApiClient] 获取用户档案失败: $e');
      // 返回模拟数据作为fallback
      return _getMockUserProfile();
    }
  }

  /// 导出用户数据
  static Future<Map<String, dynamic>> exportUserData({
    String format = 'excel',
    Map<String, dynamic>? dateRange,
  }) async {
    try {
      print('🔍 [UserSettingsApiClient] 导出用户数据 ($format)');
      
      final response = await http.post(
        Uri.parse('$baseUrl/user/export-data'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'format': format,
          'date_range': dateRange,
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
      print('❌ [UserSettingsApiClient] 数据导出失败: $e');
      return {
        'success': false,
        'message': '数据导出失败: $e',
        'data': null,
      };
    }
  }

  /// 备份用户数据
  static Future<Map<String, dynamic>> backupUserData() async {
    try {
      print('🔍 [UserSettingsApiClient] 备份用户数据');
      
      final response = await http.post(
        Uri.parse('$baseUrl/user/backup-data'),
        headers: {'Content-Type': 'application/json'},
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
      print('❌ [UserSettingsApiClient] 数据备份失败: $e');
      return {
        'success': false,
        'message': '数据备份失败: $e',
        'data': null,
      };
    }
  }

  /// 获取数据摘要
  static Future<Map<String, dynamic>> getDataSummary() async {
    try {
      print('🔍 [UserSettingsApiClient] 获取数据摘要');
      
      final response = await http.get(
        Uri.parse('$baseUrl/user/data-summary'),
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
      print('❌ [UserSettingsApiClient] 获取数据摘要失败: $e');
      // 返回模拟数据作为fallback
      return _getMockDataSummary();
    }
  }

  /// 清除用户缓存
  static Future<Map<String, dynamic>> clearUserCache() async {
    try {
      print('🔍 [UserSettingsApiClient] 清除用户缓存');
      
      final response = await http.post(
        Uri.parse('$baseUrl/user/clear-cache'),
        headers: {'Content-Type': 'application/json'},
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
      print('❌ [UserSettingsApiClient] 清除缓存失败: $e');
      return {
        'success': false,
        'message': '清除缓存失败: $e',
        'data': null,
      };
    }
  }

  /// 获取系统信息
  static Future<Map<String, dynamic>> getSystemInfo() async {
    try {
      print('🔍 [UserSettingsApiClient] 获取系统信息');
      
      final response = await http.get(
        Uri.parse('$baseUrl/user/system-info'),
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
      print('❌ [UserSettingsApiClient] 获取系统信息失败: $e');
      // 返回模拟数据作为fallback
      return _getMockSystemInfo();
    }
  }

  // ========== Default/Mock Data Methods ==========

  static Map<String, dynamic> _getDefaultUserPreferences() {
    return {
      'base_currency': 'USD',
      'data_visibility': true,
      'theme_mode': 'light',
      'number_precision': 2,
      'percentage_precision': 2,
    };
  }

  static Map<String, dynamic> _getDefaultNotificationSettings() {
    return {
      'asset_change_alerts': true,
      'sync_failure_alerts': true,
      'daily_reports': false,
      'weekly_summaries': true,
      'monthly_insights': false,
      'alert_threshold': 5.0,
      'quiet_hours_start': '22:00',
      'quiet_hours_end': '08:00',
    };
  }

  static Map<String, dynamic> _getDefaultSyncSettings() {
    return {
      'auto_sync_enabled': true,
      'sync_frequency': 30,
      'retry_on_failure': true,
      'max_retry_attempts': 3,
      'wifi_only': false,
      'power_saving_mode': false,
    };
  }

  static Map<String, dynamic> _getMockUserProfile() {
    return {
      'user_name': '投资分析师',
      'avatar': null,
      'registration_date': DateTime.now().subtract(Duration(days: 51)).toIso8601String(),
      'usage_days': 51,
      'total_records': 307,
      'annual_return_rate': 8.5,
      'achievements': [
        {
          'id': 'usage_30_days',
          'title': '连续使用30天',
          'description': '坚持记录资产超过30天',
          'icon': '🏆',
          'earned': true
        },
        {
          'id': 'asset_100k',
          'title': '资产超过10万',
          'description': '总资产价值超过10万',
          'icon': '💰',
          'earned': true
        },
        {
          'id': 'platform_master',
          'title': '平台连接达人',
          'description': '连接了3个或以上平台',
          'icon': '🔗',
          'earned': true
        },
        {
          'id': 'good_investor',
          'title': '投资高手',
          'description': '年化收益率超过8%',
          'icon': '📈',
          'earned': true
        }
      ],
      'stats': {
        'total_records': 307,
        'usage_days': 51,
        'total_asset_value': 166660.56,
        'platforms_connected': 3,
        'annual_return_rate': 8.5
      }
    };
  }

  static Map<String, dynamic> _getMockDataSummary() {
    return {
      'date': DateTime.now().toIso8601String().substring(0, 10),
      'total_value': '\$166,660.56',
      'snapshot_count': 13,
      'active_platforms': 3,
      'status': '数据正常更新',
      'summary_text': '今日记录了13笔资产快照，总价值166,660.56美元，涉及3个平台。',
    };
  }

  static Map<String, dynamic> _getMockSystemInfo() {
    return {
      'app_version': '1.0.0',
      'api_version': 'v1.2',
      'last_update': '2025-01-27',
      'environment': 'production',
      'server_time': DateTime.now().toIso8601String(),
      'features': [
        '多平台资产聚合',
        '实时汇率转换',
        '智能数据分析',
        'AI投资建议',
        '自动化同步'
      ],
      'supported_platforms': ['支付宝', 'Wise', 'IBKR', 'OKX'],
      'supported_currencies': ['CNY', 'USD', 'EUR', 'JPY', 'AUD']
    };
  }
}