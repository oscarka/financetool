import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  // 动态获取API基础URL
  static String get baseUrl {
    // 检查是否在开发环境
    const bool isDebugMode = bool.fromEnvironment('dart.vm.product') == false;
    
    if (isDebugMode) {
      // 开发环境：连接本地后端
      return 'http://localhost:8000/api/v1';
    } else {
      // 生产环境：使用相对路径，通过nginx代理
      return '/api/v1';
    }
  }
  
  // 获取聚合统计数据
  static Future<Map<String, dynamic>> getAggregatedStats(String baseCurrency) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/aggregation/stats?base_currency=$baseCurrency'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data'] ?? {};
      } else {
        throw Exception('获取聚合统计数据失败: ${response.statusCode}');
      }
    } catch (e) {
      print('API错误: $e');
      // 返回模拟数据作为fallback
      return {
        'total_value': 18573.44,
        'platform_stats': {'test': 1050.0, 'Wise': 10080.77, 'OKX': 7442.67},
        'asset_type_stats': {'fund': 1050.0, '外汇': 10080.77, '数字货币': 7442.67},
        'currency_stats': {'CNY': 1050.0, 'USD': 0.0, 'AUD': 3362.54, 'JPY': 6711.98},
        'asset_count': 18,
        'platform_count': 3,
        'asset_type_count': 3,
        'currency_count': 15,
        'has_default_rates': true
      };
    }
  }
  
  // 获取资产趋势数据
  static Future<List<Map<String, dynamic>>> getAssetTrend(int days, String baseCurrency) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/aggregation/trend?days=$days&base_currency=$baseCurrency'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['data'] ?? []);
      } else {
        throw Exception('获取趋势数据失败: ${response.statusCode}');
      }
    } catch (e) {
      print('API错误: $e');
      // 返回模拟数据作为fallback
      return _generateMockTrendData(days);
    }
  }
  
  // 生成模拟趋势数据
  static List<Map<String, dynamic>> _generateMockTrendData(int days) {
    final List<Map<String, dynamic>> data = [];
    final now = DateTime.now();
    double baseValue = 18573.44;
    
    for (int i = days - 1; i >= 0; i--) {
      final date = now.subtract(Duration(days: i));
      final randomChange = (DateTime.now().millisecondsSinceEpoch % 100 - 50) / 1000.0;
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
      final response = await http.get(
        Uri.parse('$baseUrl/snapshot/assets?base_currency=$baseCurrency'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['data'] ?? []);
      } else {
        throw Exception('获取资产快照失败: ${response.statusCode}');
      }
    } catch (e) {
      print('API错误: $e');
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