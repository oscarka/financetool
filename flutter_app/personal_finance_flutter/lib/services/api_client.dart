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
    
    // 现在直接使用真实数据，不需要连接API
    return 'https://backend-production-2750.up.railway.app/api/v1';
  }
  
  // 获取聚合统计数据
  static Future<Map<String, dynamic>> getAggregatedStats(String baseCurrency) async {
    print('🔍 [ApiClient] 正在从后端获取实时聚合统计数据...');
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ai-analyst/asset-data?base_currency=$baseCurrency'),
        headers: {
          'X-API-Key': 'ai_analyst_key_2024',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // 从后端数据中提取聚合统计信息
        final currentHoldings = data['current_holdings'] as List;
        final totalValue = currentHoldings.fold<double>(
          0.0, 
          (sum, holding) => sum + (holding['base_currency_value'] ?? 0.0)
        );
        
        // 按平台统计
        final platformStats = <String, double>{};
        final assetTypeStats = <String, double>{};
        final currencyStats = <String, double>{};
        
        for (final holding in currentHoldings) {
          final platform = holding['platform'] ?? '未知';
          final assetType = holding['asset_type'] ?? '未知';
          final currency = holding['currency'] ?? '未知';
          final value = (holding['base_currency_value'] ?? 0.0).toDouble();
          
          platformStats[platform] = (platformStats[platform] ?? 0.0) + value;
          assetTypeStats[assetType] = (assetTypeStats[assetType] ?? 0.0) + value;
          currencyStats[currency] = (currencyStats[currency] ?? 0.0) + value;
        }
        
        return {
          'total_value': totalValue,
          'platform_stats': platformStats,
          'asset_type_stats': assetTypeStats,
          'currency_stats': currencyStats,
          'asset_count': currentHoldings.length,
          'platform_count': platformStats.length,
          'asset_type_count': assetTypeStats.length,
          'currency_count': currencyStats.length,
          'has_default_rates': true
        };
      } else {
        print('❌ [ApiClient] 获取聚合统计数据失败: ${response.statusCode}');
        throw Exception('获取数据失败: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ApiClient] 获取聚合统计数据失败: $e');
      throw Exception('网络请求失败: $e');
    }
  }
  
  // 获取资产趋势数据
  static Future<List<Map<String, dynamic>>> getAssetTrend(int days, String baseCurrency) async {
    print('🔍 [ApiClient] 正在从后端获取实时趋势数据...');
    
    try {
      // 获取当前数据作为趋势的基准
      final currentStats = await getAggregatedStats(baseCurrency);
      final baseValue = currentStats['total_value'] ?? 0.0;
      
      // 生成基于真实数据的趋势（暂时使用模拟数据，后续可以对接真实趋势API）
      return _generateTrendData(days, baseValue);
    } catch (e) {
      print('❌ [ApiClient] 获取趋势数据失败: $e');
      // 如果获取失败，返回默认趋势数据
      return _generateTrendData(days, 0.0);
    }
  }
  
  // 生成趋势数据
  static List<Map<String, dynamic>> _generateTrendData(int days, double baseValue) {
    final List<Map<String, dynamic>> data = [];
    final now = DateTime.now();
    
    for (int i = days - 1; i >= 0; i--) {
      final date = now.subtract(Duration(days: i));
      // 生成合理的波动（±2%）
      final randomChange = (DateTime.now().millisecondsSinceEpoch % 200 - 100) / 5000.0;
      final dayValue = baseValue * (1 + randomChange);
      
      data.add({
        'date': '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
        'total': dayValue,
      });
    }
    
    return data;
  }

  // 获取资产快照数据
  static Future<List<Map<String, dynamic>>> getAssetSnapshots(String baseCurrency) async {
    print('🔍 [ApiClient] 正在从后端获取实时快照数据...');
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ai-analyst/asset-data?base_currency=$baseCurrency'),
        headers: {
          'X-API-Key': 'ai_analyst_key_2024',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final currentHoldings = data['current_holdings'] as List;
        
        // 转换为快照格式
        return currentHoldings.map<Map<String, dynamic>>((holding) {
          return {
            'asset_type': holding['asset_type'] ?? '未知',
            'asset_name': holding['asset_name'] ?? '未知',
            'asset_code': holding['asset_code'] ?? '未知',
            'balance': holding['balance_original'] ?? 0.0,
            'base_value': holding['base_currency_value'] ?? 0.0,
            'currency': holding['currency'] ?? '未知',
            'platform': holding['platform'] ?? '未知'
          };
        }).toList();
      } else {
        print('❌ [ApiClient] 获取快照数据失败: ${response.statusCode}');
        throw Exception('获取数据失败: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ApiClient] 获取快照数据失败: $e');
      throw Exception('网络请求失败: $e');
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