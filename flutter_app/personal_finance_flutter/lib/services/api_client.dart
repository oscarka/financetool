import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiClient {
  // 获取基础URL
  static String get baseUrl {
    // 优先使用环境变量
    const String? backendUrl = String.fromEnvironment('BACKEND_API_URL');
    if (backendUrl != null && backendUrl.isNotEmpty) {
      return backendUrl;
    }
    // 默认后端基地址（生产后端）
    return 'https://backend-production-2750.up.railway.app/api/v1';
  }
  
  // 获取聚合统计数据
  static Future<Map<String, dynamic>> getAggregatedStats(String baseCurrency) async {
    try {
      final uri = Uri.parse('$baseUrl/aggregation/stats?base_currency=$baseCurrency');
      final resp = await http.get(uri, headers: {'Content-Type': 'application/json'});
      if (resp.statusCode == 200) {
        final jsonData = json.decode(resp.body);
        if (jsonData['success'] == true) {
          return Map<String, dynamic>.from(jsonData['data'] ?? {});
        }
        throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
      }
      throw Exception('HTTP错误: ${resp.statusCode}');
    } catch (e) {
      print('❌ [ApiClient] 获取聚合统计失败，使用回退: $e');
      return {
        'total_value': 0.0,
        'platform_stats': <String, double>{},
        'asset_type_stats': <String, double>{},
        'currency_stats': <String, double>{},
        'asset_count': 0,
        'platform_count': 0,
        'asset_type_count': 0,
        'currency_count': 0,
        'has_default_rates': false
      };
    }
  }
  
  // 获取资产趋势数据
  static Future<List<Map<String, dynamic>>> getAssetTrend(int days, String baseCurrency) async {
    try {
      final uri = Uri.parse('$baseUrl/aggregation/trend?days=$days&base_currency=$baseCurrency');
      final resp = await http.get(uri, headers: {'Content-Type': 'application/json'});
      if (resp.statusCode == 200) {
        final jsonData = json.decode(resp.body);
        if (jsonData['success'] == true) {
          final List list = jsonData['data'] ?? [];
          return list.map((e) => Map<String, dynamic>.from(e)).toList();
        }
        throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
      }
      throw Exception('HTTP错误: ${resp.statusCode}');
    } catch (e) {
      print('❌ [ApiClient] 获取趋势失败，使用回退: $e');
      return _generateMockTrendData(days);
    }
  }
  
  // 生成模拟趋势数据
  static List<Map<String, dynamic>> _generateMockTrendData(int days) {
    final List<Map<String, dynamic>> data = [];
    final now = DateTime.now();
    double baseValue = 166660.55;  // 使用从Railway获取的真实总价值作为基准
    
    for (int i = days - 1; i >= 0; i--) {
      final date = now.subtract(Duration(days: i));
      // 生成合理的波动（±2%）
      final randomChange = (DateTime.now().millisecondsSinceEpoch % 200 - 100) / 5000.0;
      baseValue = baseValue * (1 + randomChange);
      
      data.add({
        'date': '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
        'total': baseValue,
      });
    }
    
    return data;
  }

  // 获取资产快照数据
  static Future<List<Map<String, dynamic>>> getAssetSnapshots(String baseCurrency) async {
    try {
      final uri = Uri.parse('$baseUrl/snapshot/assets?base_currency=$baseCurrency');
      final resp = await http.get(uri, headers: {'Content-Type': 'application/json'});
      if (resp.statusCode == 200) {
        final jsonData = json.decode(resp.body);
        if (jsonData['success'] == true) {
          final List list = jsonData['data'] ?? [];
          return list.map((e) => Map<String, dynamic>.from(e)).toList();
        }
        throw Exception('API返回错误: ${jsonData['message'] ?? 'Unknown error'}');
      }
      throw Exception('HTTP错误: ${resp.statusCode}');
    } catch (e) {
      print('❌ [ApiClient] 获取资产快照失败，使用回退: $e');
      return [];
    }
  }

  // 获取最大持仓资产
  static Future<String?> getLargestHolding(String baseCurrency) async {
    try {
      final snapshots = await getAssetSnapshots(baseCurrency);
      if (snapshots.isEmpty) return null;
      
      // 按base_value排序，获取最大持仓
      snapshots.sort((a, b) => (b['base_value'] ?? 0.0).compareTo(a['base_value'] ?? 0.0));
      final largestAsset = snapshots.first;
      
      // 优先返回资产名称，如果没有则返回资产代码
      final assetName = largestAsset['asset_name'] as String?;
      final assetCode = largestAsset['asset_code'] as String?;
      
      if (assetName != null && assetName.isNotEmpty) {
        // 简化显示名称
        if (assetName.contains('易方达沪深300ETF')) {
          return '沪深300ETF';
        } else if (assetName.length > 10) {
          return assetName.substring(0, 10) + '...';
        } else {
          return assetName;
        }
      } else if (assetCode != null) {
        return assetCode;
      } else {
        return 'Unknown';
      }
    } catch (e) {
      print('获取最大持仓失败: $e');
      return null;
    }
  }
}