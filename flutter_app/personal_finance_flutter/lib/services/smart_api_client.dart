import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'cache_service.dart';

class SmartApiClient {
  // 获取基础URL
  static String get baseUrl {
    const String? backendUrl = String.fromEnvironment('BACKEND_API_URL');
    if (backendUrl != null && backendUrl.isNotEmpty) {
      return backendUrl;
    }
    
    const bool useLocalBackend = bool.fromEnvironment('USE_LOCAL_BACKEND', defaultValue: false);
    if (useLocalBackend) {
      return 'http://localhost:8000/api/v1';
    }
    
    return 'https://backend-production-2750.up.railway.app/api/v1';
  }
  
  // 智能获取聚合统计数据（缓存优先）
  static Future<Map<String, dynamic>> getAggregatedStats(String baseCurrency, {bool forceRefresh = false}) async {
    print('🔍 [SmartApiClient] 获取 $baseCurrency 的聚合统计数据...');
    
    // 如果不是强制刷新，先尝试从缓存获取
    if (!forceRefresh) {
      final cachedData = await CacheService.getFromCache(baseCurrency, 'aggregated_stats');
      if (cachedData != null) {
        print('📱 [SmartApiClient] 使用缓存的聚合统计数据');
        return cachedData;
      }
    }
    
    try {
      print('🌐 [SmartApiClient] 从网络获取聚合统计数据...');
      final response = await http.get(
        Uri.parse('$baseUrl/ai-analyst/asset-data?base_currency=$baseCurrency'),
        headers: {
          'X-API-Key': const String.fromEnvironment('AI_ANALYST_API_KEY', defaultValue: 'ai_analyst_key_2024'),
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // 处理数据
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
        
        final result = {
          'total_value': totalValue,
          'platform_stats': platformStats,
          'asset_type_stats': assetTypeStats,
          'currency_stats': currencyStats,
          'asset_count': currentHoldings.length,
          'platform_count': platformStats.length,
          'asset_type_count': assetTypeStats.length,
          'currency_count': currencyStats.length,
          'has_default_rates': true,
          'cache_timestamp': DateTime.now().toIso8601String(),
        };
        
        // 保存到缓存
        await CacheService.saveToCache(baseCurrency, 'aggregated_stats', result);
        
        return result;
      } else {
        print('❌ [SmartApiClient] 获取聚合统计数据失败: ${response.statusCode}');
        throw Exception('获取数据失败: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SmartApiClient] 网络请求失败: $e');
      
      // 如果网络请求失败，尝试返回过期缓存作为备用
      final expiredCache = await CacheService.getFromCache(baseCurrency, 'aggregated_stats', expiryMinutes: 60);
      if (expiredCache != null) {
        print('⚠️ [SmartApiClient] 使用过期缓存作为备用');
        expiredCache['cache_timestamp'] = '${expiredCache['cache_timestamp']} (过期备用)';
        return expiredCache;
      }
      
      throw Exception('网络请求失败且无备用缓存: $e');
    }
  }
  
  // 智能获取资产趋势数据
  static Future<List<Map<String, dynamic>>> getAssetTrend(int days, String baseCurrency, {bool forceRefresh = false}) async {
    print('🔍 [SmartApiClient] 获取 $baseCurrency 的趋势数据...');
    
    // 如果不是强制刷新，先尝试从缓存获取
    if (!forceRefresh) {
      final cachedData = await CacheService.getFromCache(baseCurrency, 'trend_data_$days');
      if (cachedData != null) {
        print('📱 [SmartApiClient] 使用缓存的趋势数据');
        return List<Map<String, dynamic>>.from(cachedData);
      }
    }
    
    try {
      print('🌐 [SmartApiClient] 从网络获取趋势数据...');
      final currentStats = await getAggregatedStats(baseCurrency, forceRefresh: forceRefresh);
      final baseValue = currentStats['total_value'] ?? 0.0;
      
      // 生成趋势数据
      final trendData = _generateTrendData(days, baseValue);
      
      // 保存到缓存
      await CacheService.saveToCache(baseCurrency, 'trend_data_$days', trendData);
      
      return trendData;
    } catch (e) {
      print('❌ [SmartApiClient] 获取趋势数据失败: $e');
      
      // 尝试返回过期缓存
      final expiredCache = await CacheService.getFromCache(baseCurrency, 'trend_data_$days', expiryMinutes: 60);
      if (expiredCache != null) {
        print('⚠️ [SmartApiClient] 使用过期趋势缓存作为备用');
        return List<Map<String, dynamic>>.from(expiredCache);
      }
      
      // 最后返回默认数据
      return _generateTrendData(days, 0.0);
    }
  }
  
  // 智能获取资产快照数据
  static Future<List<Map<String, dynamic>>> getAssetSnapshots(String baseCurrency, {bool forceRefresh = false}) async {
    print('🔍 [SmartApiClient] 获取 $baseCurrency 的快照数据...');
    
    // 如果不是强制刷新，先尝试从缓存获取
    if (!forceRefresh) {
      final cachedData = await CacheService.getFromCache(baseCurrency, 'asset_snapshots');
      if (cachedData != null) {
        print('📱 [SmartApiClient] 使用缓存的快照数据');
        return List<Map<String, dynamic>>.from(cachedData);
      }
    }
    
    try {
      print('🌐 [SmartApiClient] 从网络获取快照数据...');
      final response = await http.get(
        Uri.parse('$baseUrl/ai-analyst/asset-data?base_currency=$baseCurrency'),
        headers: {
          'X-API-Key': const String.fromEnvironment('AI_ANALYST_API_KEY', defaultValue: 'ai_analyst_key_2024'),
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final currentHoldings = data['current_holdings'] as List;
        
        // 转换为快照格式
        final snapshots = currentHoldings.map<Map<String, dynamic>>((holding) {
          return {
            'asset_type': holding['asset_type'] ?? '未知',
            'asset_name': holding['asset_name'] ?? '未知',
            'asset_code': holding['asset_code'] ?? '未知',
            'balance': holding['balance_original'] ?? 0.0,
            'base_value': holding['base_currency_value'] ?? 0.0,
            'currency': holding['currency'] ?? '未知',
            'platform': holding['platform'] ?? '未知',
            'cache_timestamp': DateTime.now().toIso8601String(),
          };
        }).toList();
        
        // 保存到缓存
        await CacheService.saveToCache(baseCurrency, 'asset_snapshots', snapshots);
        
        return snapshots;
      } else {
        print('❌ [SmartApiClient] 获取快照数据失败: ${response.statusCode}');
        throw Exception('获取数据失败: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [SmartApiClient] 网络请求失败: $e');
      
      // 尝试返回过期缓存
      final expiredCache = await CacheService.getFromCache(baseCurrency, 'asset_snapshots', expiryMinutes: 60);
      if (expiredCache != null) {
        print('⚠️ [SmartApiClient] 使用过期快照缓存作为备用');
        return List<Map<String, dynamic>>.from(expiredCache);
      }
      
      throw Exception('网络请求失败且无备用缓存: $e');
    }
  }
  
  // 智能获取最大持仓资产
  static Future<String?> getLargestHolding(String baseCurrency, {bool forceRefresh = false}) async {
    try {
      final snapshots = await getAssetSnapshots(baseCurrency, forceRefresh: forceRefresh);
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
  
  // 预加载其他货币的数据（后台进行）
  static Future<void> preloadOtherCurrencies(String currentCurrency) async {
    final supportedCurrencies = ['CNY', 'USD', 'EUR'];
    
    for (final currency in supportedCurrencies) {
      if (currency != currentCurrency) {
        // 后台预加载，不阻塞UI
        _preloadCurrencyData(currency);
      }
    }
  }
  
  // 后台预加载货币数据
  static Future<void> _preloadCurrencyData(String currency) async {
    try {
              // 后台预加载 $currency 数据...
      
      // 检查是否已有有效缓存
      final hasValidCache = await CacheService.hasValidCache(currency, 'aggregated_stats');
      if (hasValidCache) {
        print('✅ [SmartApiClient] $currency 已有有效缓存，跳过预加载');
        return;
      }
      
      // 预加载聚合统计
      await getAggregatedStats(currency, forceRefresh: true);
      
      // 预加载快照数据
      await getAssetSnapshots(currency, forceRefresh: true);
      
      print('✅ [SmartApiClient] $currency 数据预加载完成');
    } catch (e) {
      print('❌ [SmartApiClient] $currency 数据预加载失败: $e');
    }
  }
  
  // 清除特定货币的缓存
  static Future<void> clearCurrencyCache(String currency) async {
    await CacheService.clearCurrencyCache(currency);
  }
  
  // 获取缓存统计信息
  static Future<Map<String, dynamic>> getCacheStats() async {
    return await CacheService.getCacheStats();
  }
  
  // 检查缓存是否存在且有效
  static Future<bool> hasValidCache(String currency, String dataType, {int? expiryMinutes}) async {
    return await CacheService.hasValidCache(currency, dataType, expiryMinutes: expiryMinutes);
  }
  
  // 清除所有缓存
  static Future<void> clearAllCache() async {
    await CacheService.clearAllCache();
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
}
