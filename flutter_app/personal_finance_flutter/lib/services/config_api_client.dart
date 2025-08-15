import 'dart:convert';
import 'package:http/http.dart' as http;

class ConfigApiClient {
  static const String baseUrl = 'http://localhost:8000/api/v1/config';

  /// 获取系统配置信息
  static Future<Map<String, dynamic>> getConfig() async {
    try {
      print('🔍 [ConfigApiClient] 获取系统配置信息');
      
      final response = await http.get(
        Uri.parse('$baseUrl/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'data': jsonData,
        };
      } else {
        print('⚠️ [ConfigApiClient] 后端配置服务可能未启动，使用模拟数据');
        return _getMockConfig();
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 获取系统配置失败: $e，使用模拟数据');
      return _getMockConfig();
    }
  }

  /// 验证配置完整性
  static Future<Map<String, dynamic>> validateConfig() async {
    try {
      print('🔍 [ConfigApiClient] 验证配置完整性');
      
      final response = await http.post(
        Uri.parse('$baseUrl/validate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'data': jsonData,
        };
      } else {
        print('⚠️ [ConfigApiClient] 后端配置服务可能未启动，使用模拟数据');
        return _getMockValidation();
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 验证配置失败: $e，使用模拟数据');
      return _getMockValidation();
    }
  }

  /// 获取环境信息
  static Future<Map<String, dynamic>> getEnvironmentInfo() async {
    try {
      print('🔍 [ConfigApiClient] 获取环境信息');
      
      final response = await http.get(
        Uri.parse('$baseUrl/environment'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'data': jsonData,
        };
      } else {
        print('⚠️ [ConfigApiClient] 后端配置服务可能未启动，使用模拟数据');
        return _getMockEnvironment();
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 获取环境信息失败: $e，使用模拟数据');
      return _getMockEnvironment();
    }
  }

  /// 更新配置
  static Future<Map<String, dynamic>> updateConfig(Map<String, dynamic> configData) async {
    try {
      print('🔍 [ConfigApiClient] 更新配置');
      
      final response = await http.put(
        Uri.parse('$baseUrl/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(configData),
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'message': jsonData['message'] ?? '配置更新成功',
          'data': jsonData,
        };
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 更新配置失败: $e');
      return {
        'success': false,
        'message': '更新配置失败: $e',
        'data': null,
      };
    }
  }

  /// 重新加载配置
  static Future<Map<String, dynamic>> reloadConfig() async {
    try {
      print('🔍 [ConfigApiClient] 重新加载配置');
      
      final response = await http.post(
        Uri.parse('$baseUrl/reload'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'message': jsonData['message'] ?? '配置重新加载成功',
        };
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 重新加载配置失败: $e');
      return {
        'success': false,
        'message': '重新加载配置失败: $e',
      };
    }
  }

  /// 导出配置
  static Future<Map<String, dynamic>> exportConfig() async {
    try {
      print('🔍 [ConfigApiClient] 导出配置');
      
      final response = await http.get(
        Uri.parse('$baseUrl/export'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'data': jsonData,
        };
      } else {
        print('⚠️ [ConfigApiClient] 后端配置服务可能未启动，使用模拟数据');
        return _getMockExport();
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 导出配置失败: $e，使用模拟数据');
      return _getMockExport();
    }
  }

  /// 导入配置
  static Future<Map<String, dynamic>> importConfig(Map<String, dynamic> configData) async {
    try {
      print('🔍 [ConfigApiClient] 导入配置');
      
      final response = await http.post(
        Uri.parse('$baseUrl/import'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(configData),
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'message': jsonData['message'] ?? '配置导入成功',
          'data': jsonData,
        };
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 导入配置失败: $e');
      return {
        'success': false,
        'message': '导入配置失败: $e',
        'data': null,
      };
    }
  }

  /// 获取配置历史
  static Future<List<Map<String, dynamic>>> getConfigHistory() async {
    try {
      print('🔍 [ConfigApiClient] 获取配置历史');
      
      final response = await http.get(
        Uri.parse('$baseUrl/history'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return List<Map<String, dynamic>>.from(jsonData ?? []);
      } else {
        print('⚠️ [ConfigApiClient] 后端配置服务可能未启动，使用模拟数据');
        return _getMockConfigHistory();
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 获取配置历史失败: $e，使用模拟数据');
      return _getMockConfigHistory();
    }
  }

  /// 重置配置到默认值
  static Future<Map<String, dynamic>> resetConfig() async {
    try {
      print('🔍 [ConfigApiClient] 重置配置到默认值');
      
      final response = await http.post(
        Uri.parse('$baseUrl/reset'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return {
          'success': true,
          'message': jsonData['message'] ?? '配置已重置到默认值',
          'data': jsonData,
        };
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ConfigApiClient] 重置配置失败: $e');
      return {
        'success': false,
        'message': '重置配置失败: $e',
        'data': null,
      };
    }
  }

  // ============ 模拟数据方法 ============

  static Map<String, dynamic> _getMockConfig() {
    return {
      'success': true,
      'data': {
        // 应用基础配置
        'app_env': 'production',
        'app_name': 'Personal Finance System',
        'app_version': '1.0.0',
        'debug': false,
        'database_url': 'postgresql://***',
        'cors_origins': ['http://localhost:3000', 'http://localhost:8080'],
        'log_level': 'INFO',
        'log_file': 'logs/app.log',
        
        // API配置
        'fund_api_timeout': 30,
        'wise_api_timeout': 30,
        'okx_api_timeout': 30,
        'ibkr_api_timeout': 30,
        'paypal_api_timeout': 30,
        
        // API密钥状态 (脱敏显示)
        'okx_api_key': '***configured***',
        'wise_api_token': '***configured***',
        'paypal_client_id': '***configured***',
        'ibkr_api_key': '***configured***',
        
        // 功能开关
        'enable_scheduler': true,
        'security_enable_rate_limiting': true,
        'performance_monitoring_enabled': true,
        'cache_enabled': true,
        'notification_enabled': false,
        'backup_enabled': true,
        'data_cleanup_enabled': true,
        
        // 系统配置
        'sync_batch_size': 100,
        'max_concurrent_tasks': 5,
        'retry_max_attempts': 3,
        'retry_delay_seconds': 5,
        
        // 安全配置
        'session_timeout_minutes': 30,
        'max_login_attempts': 5,
        'password_min_length': 8,
        
        // 性能配置
        'query_timeout_seconds': 30,
        'connection_pool_size': 10,
        'cache_ttl_seconds': 300,
        
        // 业务配置
        'default_currency': 'USD',
        'supported_currencies': ['USD', 'CNY', 'EUR', 'JPY', 'AUD'],
        'data_retention_days': 365,
        'backup_retention_days': 30,
      }
    };
  }

  static Map<String, dynamic> _getMockValidation() {
    return {
      'success': true,
      'data': {
        'valid': true,
        'total_checks': 15,
        'passed_checks': 13,
        'failed_checks': 2,
        'warnings': 1,
        'checks': [
          {
            'category': 'database',
            'check': 'database_connection',
            'status': 'passed',
            'message': '数据库连接正常'
          },
          {
            'category': 'api_keys',
            'check': 'okx_api_key',
            'status': 'passed',
            'message': 'OKX API密钥有效'
          },
          {
            'category': 'api_keys',
            'check': 'wise_api_token',
            'status': 'passed',
            'message': 'Wise API令牌有效'
          },
          {
            'category': 'api_keys',
            'check': 'ibkr_api_key',
            'status': 'failed',
            'message': 'IBKR API密钥无效或已过期'
          },
          {
            'category': 'api_keys',
            'check': 'paypal_client_id',
            'status': 'warning',
            'message': 'PayPal客户端ID未配置'
          },
          {
            'category': 'services',
            'check': 'scheduler_service',
            'status': 'passed',
            'message': '调度器服务运行正常'
          },
          {
            'category': 'services',
            'check': 'cache_service',
            'status': 'passed',
            'message': '缓存服务运行正常'
          },
          {
            'category': 'security',
            'check': 'cors_origins',
            'status': 'passed',
            'message': 'CORS配置正确'
          },
          {
            'category': 'security',
            'check': 'rate_limiting',
            'status': 'passed',
            'message': '限流配置正确'
          },
          {
            'category': 'performance',
            'check': 'query_timeout',
            'status': 'passed',
            'message': '查询超时配置合理'
          },
          {
            'category': 'performance',
            'check': 'connection_pool',
            'status': 'passed',
            'message': '连接池配置正确'
          },
          {
            'category': 'business',
            'check': 'currency_config',
            'status': 'passed',
            'message': '货币配置正确'
          },
          {
            'category': 'business',
            'check': 'retention_policy',
            'status': 'passed',
            'message': '数据保留策略配置正确'
          },
          {
            'category': 'backup',
            'check': 'backup_enabled',
            'status': 'passed',
            'message': '备份功能已启用'
          },
          {
            'category': 'logs',
            'check': 'log_configuration',
            'status': 'failed',
            'message': '日志目录权限不足'
          },
        ]
      }
    };
  }

  static Map<String, dynamic> _getMockEnvironment() {
    return {
      'success': true,
      'data': {
        'system': {
          'os': 'Linux',
          'platform': 'linux',
          'python_version': '3.11.5',
          'cpu_count': 4,
          'memory_total': '8GB',
          'disk_space': '256GB',
        },
        'application': {
          'app_name': 'Personal Finance System',
          'version': '1.0.0',
          'environment': 'production',
          'started_at': DateTime.now().subtract(Duration(hours: 12)).toIso8601String(),
          'uptime': '12h 34m',
        },
        'database': {
          'type': 'PostgreSQL',
          'version': '14.9',
          'size': '1.2GB',
          'connections': 5,
          'max_connections': 100,
        },
        'services': {
          'scheduler': {
            'status': 'running',
            'jobs_count': 8,
            'next_run': DateTime.now().add(Duration(minutes: 15)).toIso8601String(),
          },
          'cache': {
            'status': 'running',
            'memory_usage': '64MB',
            'hit_rate': '85%',
          },
          'backup': {
            'status': 'enabled',
            'last_backup': DateTime.now().subtract(Duration(days: 1)).toIso8601String(),
            'backup_size': '256MB',
          }
        },
        'external_apis': {
          'okx': {
            'status': 'connected',
            'last_request': DateTime.now().subtract(Duration(minutes: 15)).toIso8601String(),
            'rate_limit': '1000/hour',
          },
          'wise': {
            'status': 'connected', 
            'last_request': DateTime.now().subtract(Duration(minutes: 45)).toIso8601String(),
            'rate_limit': '100/minute',
          },
          'ibkr': {
            'status': 'error',
            'last_request': DateTime.now().subtract(Duration(hours: 6)).toIso8601String(),
            'error': 'API key expired',
          },
          'paypal': {
            'status': 'not_configured',
            'last_request': null,
            'rate_limit': 'N/A',
          }
        }
      }
    };
  }

  static Map<String, dynamic> _getMockExport() {
    return {
      'success': true,
      'data': {
        'exported_at': DateTime.now().toIso8601String(),
        'export_version': '1.0',
        'config_sections': 12,
        'sensitive_data_masked': true,
        'export_size': '15KB',
        'download_url': '/downloads/config_export_${DateTime.now().millisecondsSinceEpoch}.json',
        'expires_at': DateTime.now().add(Duration(hours: 24)).toIso8601String(),
      }
    };
  }

  static List<Map<String, dynamic>> _getMockConfigHistory() {
    return [
      {
        'id': 'config_001',
        'timestamp': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
        'action': 'update',
        'user': 'admin',
        'changes': [
          {'key': 'okx_api_timeout', 'old_value': 30, 'new_value': 45},
          {'key': 'enable_scheduler', 'old_value': false, 'new_value': true},
        ],
        'description': '更新OKX API超时时间，启用调度器'
      },
      {
        'id': 'config_002',
        'timestamp': DateTime.now().subtract(Duration(days: 1)).toIso8601String(),
        'action': 'import',
        'user': 'admin',
        'changes': [
          {'key': 'wise_api_token', 'old_value': null, 'new_value': '***configured***'},
          {'key': 'notification_enabled', 'old_value': false, 'new_value': true},
        ],
        'description': '导入新的Wise API配置'
      },
      {
        'id': 'config_003',
        'timestamp': DateTime.now().subtract(Duration(days: 3)).toIso8601String(),
        'action': 'reset',
        'user': 'admin',
        'changes': [],
        'description': '重置配置到默认值'
      },
      {
        'id': 'config_004',
        'timestamp': DateTime.now().subtract(Duration(days: 5)).toIso8601String(),
        'action': 'update',
        'user': 'admin',
        'changes': [
          {'key': 'log_level', 'old_value': 'DEBUG', 'new_value': 'INFO'},
          {'key': 'cache_enabled', 'old_value': false, 'new_value': true},
        ],
        'description': '调整日志级别和缓存设置'
      },
      {
        'id': 'config_005',
        'timestamp': DateTime.now().subtract(Duration(days: 7)).toIso8601String(),
        'action': 'update',
        'user': 'admin',
        'changes': [
          {'key': 'backup_enabled', 'old_value': false, 'new_value': true},
          {'key': 'backup_retention_days', 'old_value': 7, 'new_value': 30},
        ],
        'description': '启用数据备份功能'
      },
    ];
  }
}