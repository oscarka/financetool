import 'dart:convert';
import 'package:http/http.dart' as http;

class SchedulerApiClient {
  static const String baseUrl = 'http://localhost:8000/api/v1/scheduler';

  /// 获取调度器状态
  static Future<Map<String, dynamic>> getSchedulerStatus() async {
    try {
      print('🔍 [SchedulerApiClient] 获取调度器状态');
      
      final response = await http.get(
        Uri.parse('$baseUrl/status'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return {
            'success': true,
            'data': jsonData['data'],
          };
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        print('⚠️ [SchedulerApiClient] 后端调度器可能未启动，使用模拟数据');
        return _getMockSchedulerStatus();
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 获取调度器状态失败: $e，使用模拟数据');
      return _getMockSchedulerStatus();
    }
  }

  /// 获取所有插件
  static Future<List<Map<String, dynamic>>> getPlugins() async {
    try {
      print('🔍 [SchedulerApiClient] 获取所有插件');
      
      final response = await http.get(
        Uri.parse('$baseUrl/plugins'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return List<Map<String, dynamic>>.from(jsonData['data'] ?? []);
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        print('⚠️ [SchedulerApiClient] 后端调度器可能未启动，使用模拟数据');
        return _getMockPlugins();
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 获取插件列表失败: $e，使用模拟数据');
      return _getMockPlugins();
    }
  }

  /// 获取所有任务定义
  static Future<List<Map<String, dynamic>>> getTasks() async {
    try {
      print('🔍 [SchedulerApiClient] 获取所有任务定义');
      
      final response = await http.get(
        Uri.parse('$baseUrl/tasks'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return List<Map<String, dynamic>>.from(jsonData ?? []);
      } else {
        print('⚠️ [SchedulerApiClient] 后端调度器可能未启动，使用模拟数据');
        return _getMockTasks();
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 获取任务定义失败: $e，使用模拟数据');
      return _getMockTasks();
    }
  }

  /// 获取所有定时任务
  static Future<List<Map<String, dynamic>>> getJobs() async {
    try {
      print('🔍 [SchedulerApiClient] 获取所有定时任务');
      
      final response = await http.get(
        Uri.parse('$baseUrl/jobs'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return List<Map<String, dynamic>>.from(jsonData['data'] ?? []);
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        print('⚠️ [SchedulerApiClient] 后端调度器可能未启动，使用模拟数据');
        return _getMockJobs();
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 获取定时任务失败: $e，使用模拟数据');
      return _getMockJobs();
    }
  }

  /// 创建定时任务
  static Future<Map<String, dynamic>> createJob(Map<String, dynamic> jobConfig) async {
    try {
      print('🔍 [SchedulerApiClient] 创建定时任务: ${jobConfig['task_id']}');
      
      final response = await http.post(
        Uri.parse('$baseUrl/jobs'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(jobConfig),
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
      print('❌ [SchedulerApiClient] 创建定时任务失败: $e');
      return {
        'success': false,
        'message': '创建定时任务失败: $e',
        'data': null,
      };
    }
  }

  /// 立即执行任务
  static Future<Map<String, dynamic>> executeTaskNow(String taskId, [Map<String, dynamic>? config]) async {
    try {
      print('🔍 [SchedulerApiClient] 立即执行任务: $taskId');
      
      final response = await http.post(
        Uri.parse('$baseUrl/jobs/$taskId/execute'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(config ?? {}),
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
      print('❌ [SchedulerApiClient] 执行任务失败: $e');
      return {
        'success': false,
        'message': '执行任务失败: $e',
        'data': null,
      };
    }
  }

  /// 删除定时任务
  static Future<Map<String, dynamic>> deleteJob(String jobId) async {
    try {
      print('🔍 [SchedulerApiClient] 删除定时任务: $jobId');
      
      final response = await http.delete(
        Uri.parse('$baseUrl/jobs/$jobId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return {
            'success': true,
            'message': jsonData['message'],
          };
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 删除定时任务失败: $e');
      return {
        'success': false,
        'message': '删除定时任务失败: $e',
      };
    }
  }

  /// 暂停定时任务
  static Future<Map<String, dynamic>> pauseJob(String jobId) async {
    try {
      print('🔍 [SchedulerApiClient] 暂停定时任务: $jobId');
      
      final response = await http.post(
        Uri.parse('$baseUrl/jobs/$jobId/pause'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return {
            'success': true,
            'message': jsonData['message'],
          };
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 暂停定时任务失败: $e');
      return {
        'success': false,
        'message': '暂停定时任务失败: $e',
      };
    }
  }

  /// 恢复定时任务
  static Future<Map<String, dynamic>> resumeJob(String jobId) async {
    try {
      print('🔍 [SchedulerApiClient] 恢复定时任务: $jobId');
      
      final response = await http.post(
        Uri.parse('$baseUrl/jobs/$jobId/resume'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return {
            'success': true,
            'message': jsonData['message'],
          };
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 恢复定时任务失败: $e');
      return {
        'success': false,
        'message': '恢复定时任务失败: $e',
      };
    }
  }

  /// 获取事件历史
  static Future<List<Map<String, dynamic>>> getEvents({
    String? eventType,
    int limit = 100,
  }) async {
    try {
      print('🔍 [SchedulerApiClient] 获取事件历史');
      
      String url = '$baseUrl/events?limit=$limit';
      if (eventType != null) {
        url += '&event_type=$eventType';
      }
      
      final response = await http.get(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        if (jsonData['success'] == true) {
          return List<Map<String, dynamic>>.from(jsonData['data'] ?? []);
        } else {
          throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
        }
      } else {
        print('⚠️ [SchedulerApiClient] 后端调度器可能未启动，使用模拟数据');
        return _getMockEvents();
      }
    } catch (e) {
      print('❌ [SchedulerApiClient] 获取事件历史失败: $e，使用模拟数据');
      return _getMockEvents();
    }
  }

  // ============ 模拟数据方法 ============

  static Map<String, dynamic> _getMockSchedulerStatus() {
    return {
      'success': true,
      'data': {
        'running': true,
        'scheduler_id': 'mock_scheduler_001',
        'started_at': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
        'jobs_count': 8,
        'active_jobs': 5,
        'paused_jobs': 2,
        'next_run_time': DateTime.now().add(Duration(minutes: 15)).toIso8601String(),
        'plugin_count': 3,
        'event_count': 42,
      }
    };
  }

  static List<Map<String, dynamic>> _getMockPlugins() {
    return [
      {
        'plugin_id': 'financial_operations',
        'name': '金融操作插件',
        'description': '提供各种金融平台的数据同步和分析功能',
        'version': '1.0.0',
        'enabled': true,
        'task_count': 15,
        'last_update': DateTime.now().subtract(Duration(days: 1)).toIso8601String(),
      },
      {
        'plugin_id': 'data_management',
        'name': '数据管理插件',
        'description': '数据备份、清理和维护功能',
        'version': '1.2.0',
        'enabled': true,
        'task_count': 5,
        'last_update': DateTime.now().subtract(Duration(days: 3)).toIso8601String(),
      },
      {
        'plugin_id': 'notification',
        'name': '通知插件',
        'description': '系统通知和告警功能',
        'version': '0.9.0',
        'enabled': false,
        'task_count': 3,
        'last_update': DateTime.now().subtract(Duration(days: 7)).toIso8601String(),
      },
    ];
  }

  static List<Map<String, dynamic>> _getMockTasks() {
    return [
      {
        'task_id': 'okx_balance_sync',
        'name': 'OKX余额同步',
        'description': '同步OKX平台的账户余额信息',
        'plugin_id': 'financial_operations',
        'category': 'data_sync',
        'enabled': true,
        'config_schema': {
          'properties': {
            'api_key': {'type': 'string', 'description': 'OKX API密钥'},
            'secret_key': {'type': 'string', 'description': 'OKX 密钥'},
            'passphrase': {'type': 'string', 'description': 'OKX API密码'},
          }
        },
      },
      {
        'task_id': 'wise_balance_sync',
        'name': 'Wise余额同步',
        'description': '同步Wise平台的账户余额信息',
        'plugin_id': 'financial_operations',
        'category': 'data_sync',
        'enabled': true,
        'config_schema': {
          'properties': {
            'api_token': {'type': 'string', 'description': 'Wise API令牌'},
          }
        },
      },
      {
        'task_id': 'ibkr_position_sync',
        'name': 'IBKR持仓同步',
        'description': '同步Interactive Brokers的持仓信息',
        'plugin_id': 'financial_operations',
        'category': 'data_sync',
        'enabled': true,
        'config_schema': {
          'properties': {
            'api_key': {'type': 'string', 'description': 'IBKR API密钥'},
            'account_id': {'type': 'string', 'description': '账户ID'},
          }
        },
      },
      {
        'task_id': 'fund_nav_update',
        'name': '基金净值更新',
        'description': '更新基金的最新净值信息',
        'plugin_id': 'financial_operations',
        'category': 'data_update',
        'enabled': true,
        'config_schema': {
          'properties': {
            'fund_codes': {'type': 'array', 'description': '基金代码列表'},
          }
        },
      },
      {
        'task_id': 'data_backup',
        'name': '数据备份',
        'description': '定期备份系统数据',
        'plugin_id': 'data_management',
        'category': 'maintenance',
        'enabled': true,
        'config_schema': {
          'properties': {
            'backup_path': {'type': 'string', 'description': '备份路径'},
            'retention_days': {'type': 'integer', 'description': '保留天数'},
          }
        },
      },
      {
        'task_id': 'data_cleanup',
        'name': '数据清理',
        'description': '清理过期的临时数据',
        'plugin_id': 'data_management',
        'category': 'maintenance',
        'enabled': true,
        'config_schema': {
          'properties': {
            'retention_days': {'type': 'integer', 'description': '数据保留天数'},
          }
        },
      },
    ];
  }

  static List<Map<String, dynamic>> _getMockJobs() {
    return [
      {
        'job_id': 'job_okx_balance_sync_001',
        'task_id': 'okx_balance_sync',
        'name': 'OKX余额同步任务',
        'description': '每30分钟同步一次OKX余额',
        'enabled': true,
        'state': 'running',
        'cron_expression': '*/30 * * * *',
        'next_run_time': DateTime.now().add(Duration(minutes: 15)).toIso8601String(),
        'last_run_time': DateTime.now().subtract(Duration(minutes: 15)).toIso8601String(),
        'last_run_status': 'success',
        'run_count': 48,
        'success_count': 46,
        'failure_count': 2,
        'created_at': DateTime.now().subtract(Duration(days: 5)).toIso8601String(),
        'config': {
          'api_key': '***key***',
          'secret_key': '***secret***',
          'passphrase': '***pass***',
        }
      },
      {
        'job_id': 'job_wise_balance_sync_001',
        'task_id': 'wise_balance_sync',
        'name': 'Wise余额同步任务',
        'description': '每小时同步一次Wise余额',
        'enabled': true,
        'state': 'running',
        'cron_expression': '0 * * * *',
        'next_run_time': DateTime.now().add(Duration(minutes: 45)).toIso8601String(),
        'last_run_time': DateTime.now().subtract(Duration(minutes: 45)).toIso8601String(),
        'last_run_status': 'success',
        'run_count': 24,
        'success_count': 24,
        'failure_count': 0,
        'created_at': DateTime.now().subtract(Duration(days: 3)).toIso8601String(),
        'config': {
          'api_token': '***token***',
        }
      },
      {
        'job_id': 'job_fund_nav_update_001',
        'task_id': 'fund_nav_update',
        'name': '基金净值更新任务',
        'description': '每天更新基金净值',
        'enabled': true,
        'state': 'running',
        'cron_expression': '0 18 * * *',
        'next_run_time': DateTime.now().add(Duration(hours: 5)).toIso8601String(),
        'last_run_time': DateTime.now().subtract(Duration(hours: 19)).toIso8601String(),
        'last_run_status': 'success',
        'run_count': 5,
        'success_count': 5,
        'failure_count': 0,
        'created_at': DateTime.now().subtract(Duration(days: 5)).toIso8601String(),
        'config': {
          'fund_codes': ['000001', '110022', '160706'],
        }
      },
      {
        'job_id': 'job_data_backup_001',
        'task_id': 'data_backup',
        'name': '数据备份任务',
        'description': '每天凌晨备份数据',
        'enabled': true,
        'state': 'paused',
        'cron_expression': '0 2 * * *',
        'next_run_time': null,
        'last_run_time': DateTime.now().subtract(Duration(days: 1)).toIso8601String(),
        'last_run_status': 'success',
        'run_count': 5,
        'success_count': 5,
        'failure_count': 0,
        'created_at': DateTime.now().subtract(Duration(days: 5)).toIso8601String(),
        'config': {
          'backup_path': '/backup',
          'retention_days': 30,
        }
      },
      {
        'job_id': 'job_ibkr_position_sync_001',
        'task_id': 'ibkr_position_sync',
        'name': 'IBKR持仓同步任务',
        'description': '每2小时同步IBKR持仓',
        'enabled': false,
        'state': 'stopped',
        'cron_expression': '0 */2 * * *',
        'next_run_time': null,
        'last_run_time': DateTime.now().subtract(Duration(hours: 6)).toIso8601String(),
        'last_run_status': 'failure',
        'run_count': 12,
        'success_count': 10,
        'failure_count': 2,
        'created_at': DateTime.now().subtract(Duration(days: 3)).toIso8601String(),
        'config': {
          'api_key': '***key***',
          'account_id': 'U1234567',
        }
      },
    ];
  }

  static List<Map<String, dynamic>> _getMockEvents() {
    return [
      {
        'event_id': 'evt_001',
        'event_type': 'job_success',
        'job_id': 'job_okx_balance_sync_001',
        'task_id': 'okx_balance_sync',
        'message': 'OKX余额同步成功',
        'timestamp': DateTime.now().subtract(Duration(minutes: 15)).toIso8601String(),
        'details': {
          'duration': 2.3,
          'records_updated': 5,
        }
      },
      {
        'event_id': 'evt_002',
        'event_type': 'job_success',
        'job_id': 'job_wise_balance_sync_001',
        'task_id': 'wise_balance_sync',
        'message': 'Wise余额同步成功',
        'timestamp': DateTime.now().subtract(Duration(minutes: 45)).toIso8601String(),
        'details': {
          'duration': 1.8,
          'records_updated': 3,
        }
      },
      {
        'event_id': 'evt_003',
        'event_type': 'job_failure',
        'job_id': 'job_ibkr_position_sync_001',
        'task_id': 'ibkr_position_sync',
        'message': 'IBKR持仓同步失败: API连接超时',
        'timestamp': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
        'details': {
          'error': 'Connection timeout',
          'retry_count': 3,
        }
      },
      {
        'event_id': 'evt_004',
        'event_type': 'job_paused',
        'job_id': 'job_data_backup_001',
        'task_id': 'data_backup',
        'message': '数据备份任务已暂停',
        'timestamp': DateTime.now().subtract(Duration(hours: 3)).toIso8601String(),
        'details': {
          'reason': 'manual_pause',
        }
      },
      {
        'event_id': 'evt_005',
        'event_type': 'job_success',
        'job_id': 'job_fund_nav_update_001',
        'task_id': 'fund_nav_update',
        'message': '基金净值更新成功',
        'timestamp': DateTime.now().subtract(Duration(hours: 19)).toIso8601String(),
        'details': {
          'duration': 5.2,
          'funds_updated': 3,
        }
      },
    ];
  }
}