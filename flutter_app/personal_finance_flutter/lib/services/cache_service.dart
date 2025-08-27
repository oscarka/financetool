import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class CacheService {
  static const String _cachePrefix = 'asset_cache_';
  static const String _cacheTimestampPrefix = 'cache_timestamp_';
  static const int _defaultCacheExpiryMinutes = 10; // 默认缓存10分钟
  
  // 缓存键生成器
  static String _getCacheKey(String currency, String dataType) {
    return '$_cachePrefix${currency}_$dataType';
  }
  
  static String _getTimestampKey(String currency, String dataType) {
    return '$_cacheTimestampPrefix${currency}_$dataType';
  }
  
  // 保存数据到缓存
  static Future<void> saveToCache(String currency, String dataType, dynamic data) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = _getCacheKey(currency, dataType);
      final timestampKey = _getTimestampKey(currency, dataType);
      
      // 保存数据
      await prefs.setString(cacheKey, jsonEncode(data));
      // 保存时间戳
      await prefs.setInt(timestampKey, DateTime.now().millisecondsSinceEpoch);
      
      print('💾 [CacheService] 已缓存 $currency 的 $dataType 数据');
    } catch (e) {
      print('❌ [CacheService] 缓存保存失败: $e');
    }
  }
  
  // 从缓存获取数据
  static Future<dynamic> getFromCache(String currency, String dataType, {int? expiryMinutes}) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = _getCacheKey(currency, dataType);
      final timestampKey = _getTimestampKey(currency, dataType);
      
      // 检查数据是否存在
      if (!prefs.containsKey(cacheKey) || !prefs.containsKey(timestampKey)) {
        return null;
      }
      
      // 检查缓存是否过期
      final timestamp = prefs.getInt(timestampKey) ?? 0;
      final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
      final expiry = expiryMinutes ?? _defaultCacheExpiryMinutes;
      
      if (DateTime.now().difference(cacheTime).inMinutes > expiry) {
        print('⏰ [CacheService] $currency 的 $dataType 缓存已过期');
        return null;
      }
      
      // 获取缓存数据
      final cachedData = prefs.getString(cacheKey);
      if (cachedData != null) {
        final data = jsonDecode(cachedData);
        print('📱 [CacheService] 从缓存获取 $currency 的 $dataType 数据');
        return data;
      }
      
      return null;
    } catch (e) {
      print('❌ [CacheService] 缓存读取失败: $e');
      return null;
    }
  }
  
  // 检查缓存是否存在且有效
  static Future<bool> hasValidCache(String currency, String dataType, {int? expiryMinutes}) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = _getCacheKey(currency, dataType);
      final timestampKey = _getTimestampKey(currency, dataType);
      
      if (!prefs.containsKey(cacheKey) || !prefs.containsKey(timestampKey)) {
        return false;
      }
      
      final timestamp = prefs.getInt(timestampKey) ?? 0;
      final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
      final expiry = expiryMinutes ?? _defaultCacheExpiryMinutes;
      
      return DateTime.now().difference(cacheTime).inMinutes <= expiry;
    } catch (e) {
      return false;
    }
  }
  
  // 清除特定货币的缓存
  static Future<void> clearCurrencyCache(String currency) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys();
      
      for (final key in keys) {
        if (key.startsWith('$_cachePrefix$currency') || key.startsWith('$_cacheTimestampPrefix$currency')) {
          await prefs.remove(key);
        }
      }
      
      print('🗑️ [CacheService] 已清除 $currency 的所有缓存');
    } catch (e) {
      print('❌ [CacheService] 清除缓存失败: $e');
    }
  }
  
  // 清除所有缓存
  static Future<void> clearAllCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys();
      
      for (final key in keys) {
        if (key.startsWith(_cachePrefix) || key.startsWith(_cacheTimestampPrefix)) {
          await prefs.remove(key);
        }
      }
      
      print('🗑️ [CacheService] 已清除所有缓存');
    } catch (e) {
      print('❌ [CacheService] 清除所有缓存失败: $e');
    }
  }
  
  // 获取缓存统计信息
  static Future<Map<String, dynamic>> getCacheStats() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys();
      
      int cacheCount = 0;
      int timestampCount = 0;
      final currencies = <String>{};
      
      for (final key in keys) {
        if (key.startsWith(_cachePrefix)) {
          cacheCount++;
          // 提取货币信息
          final parts = key.replaceFirst(_cachePrefix, '').split('_');
          if (parts.isNotEmpty) {
            currencies.add(parts[0]);
          }
        } else if (key.startsWith(_cacheTimestampPrefix)) {
          timestampCount++;
        }
      }
      
      return {
        'cache_entries': cacheCount,
        'timestamp_entries': timestampCount,
        'cached_currencies': currencies.toList(),
        'total_keys': keys.length,
      };
    } catch (e) {
      return {'error': e.toString()};
    }
  }
}
