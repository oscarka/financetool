import 'dart:async';
import 'package:flutter/foundation.dart';
import 'cache_service.dart';
import 'alipay_fund_service.dart';
import 'wise_service.dart';
import 'ibkr_service.dart';
import 'okx_service.dart';
import 'asset_precache_service.dart';

/// 智能资产服务
/// 优先使用缓存数据，后台更新最新数据，确保快速响应
class SmartAssetService {
  static const String _tag = 'SmartAssetService';
  
  // 缓存配置
  static const int _assetCacheExpiryMinutes = 15; // 资产数据缓存15分钟
  static const int _exchangeRateCacheExpiryMinutes = 5; // 汇率数据缓存5分钟
  
  // 后台更新状态
  static final Map<String, bool> _isUpdatingInBackground = {};
  
  /// 智能获取基金持仓数据
  /// 优先返回缓存数据，后台更新最新数据
  static Future<dynamic> getFundPositions({bool forceRefresh = false}) async {
    final cacheKey = 'fund_positions';
    
    try {
      // 如果不是强制刷新，先尝试从缓存获取
      if (!forceRefresh) {
        final cachedData = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: _assetCacheExpiryMinutes);
        
        if (cachedData != null) {
          print('📱 [$_tag] 基金持仓数据从缓存获取，响应时间: <100ms');
          
          // 后台更新最新数据
          _updateFundPositionsInBackground();
          
          return cachedData;
        }
      }
      
      // 缓存无效或强制刷新，从网络获取
      print('🌐 [$_tag] 基金持仓数据从网络获取...');
      
      // 并行获取基金持仓和汇总数据
      final futures = await Future.wait([
        AlipayFundService.getFundPositions(),
        AlipayFundService.getPositionSummary(),
      ]);
      
      // 构建结构化数据
      final structuredData = {
        'positions': futures[0],
        'summary': futures[1],
      };
      
      // 保存到缓存
      await CacheService.saveToCache('CNY', cacheKey, structuredData);
      
      print('✅ [$_tag] 基金持仓数据获取完成');
      return structuredData;
    } catch (e) {
      print('❌ [$_tag] 获取基金持仓数据失败: $e');
      
      // 网络失败时，尝试使用过期缓存作为备用
      if (!forceRefresh) {
        final expiredCache = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: 60); // 使用1小时内的过期缓存
        
        if (expiredCache != null) {
          print('⚠️ [$_tag] 使用过期缓存作为备用数据');
          return expiredCache;
        }
      }
      
      rethrow;
    }
  }
  
  /// 智能获取Wise余额数据
  static Future<dynamic> getWiseBalances({bool forceRefresh = false}) async {
    final cacheKey = 'wise_balances';
    
    try {
      if (!forceRefresh) {
        final cachedData = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: _assetCacheExpiryMinutes);
        
        if (cachedData != null) {
          print('📱 [$_tag] Wise余额数据从缓存获取，响应时间: <100ms');
          _updateWiseBalancesInBackground();
          return cachedData;
        }
      }
      
      print('🌐 [$_tag] Wise余额数据从网络获取...');
      
      // 并行获取Wise余额和汇总数据
      final futures = await Future.wait([
        WiseService.getAllBalances(),
        WiseService.getWiseSummary(),
      ]);
      
      // 构建结构化数据
      final structuredData = {
        'balances': futures[0],
        'summary': futures[1],
      };
      
      await CacheService.saveToCache('CNY', cacheKey, structuredData);
      
      print('✅ [$_tag] Wise余额数据获取完成');
      return structuredData;
    } catch (e) {
      print('❌ [$_tag] 获取Wise余额数据失败: $e');
      
      if (!forceRefresh) {
        final expiredCache = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: 60);
        
        if (expiredCache != null) {
          print('⚠️ [$_tag] 使用过期缓存作为备用数据');
          return expiredCache;
        }
      }
      
      rethrow;
    }
  }
  
  /// 智能获取IBKR持仓数据
  static Future<dynamic> getIBKRPositions({bool forceRefresh = false}) async {
    final cacheKey = 'ibkr_positions';
    
    try {
      if (!forceRefresh) {
        final cachedData = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: _assetCacheExpiryMinutes);
        
        if (cachedData != null) {
          print('📱 [$_tag] IBKR持仓数据从缓存获取，响应时间: <100ms');
          _updateIBKRPositionsInBackground();
          return cachedData;
        }
      }
      
      print('🌐 [$_tag] IBKR持仓数据从网络获取...');
      
      // 并行获取IBKR持仓、余额和汇总数据
      final futures = await Future.wait([
        IBKRService.getPositions(),
        IBKRService.getBalances(),
        IBKRService.getIBKRSummary(),
      ]);
      
      // 构建结构化数据
      final structuredData = {
        'positions': futures[0],
        'balances': futures[1],
        'summary': futures[2],
      };
      
      await CacheService.saveToCache('CNY', cacheKey, structuredData);
      
      print('✅ [$_tag] IBKR持仓数据获取完成');
      return structuredData;
    } catch (e) {
      print('❌ [$_tag] 获取IBKR持仓数据失败: $e');
      
      if (!forceRefresh) {
        final expiredCache = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: 60);
        
        if (expiredCache != null) {
          print('⚠️ [$_tag] 使用过期缓存作为备用数据');
          return expiredCache;
        }
      }
      
      rethrow;
    }
  }
  
  /// 智能获取OKX余额数据
  static Future<dynamic> getOKXBalances({bool forceRefresh = false}) async {
    final cacheKey = 'okx_balances';
    
    try {
      if (!forceRefresh) {
        final cachedData = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: _assetCacheExpiryMinutes);
        
        if (cachedData != null) {
          print('📱 [$_tag] OKX余额数据从缓存获取，响应时间: <100ms');
          _updateOKXBalancesInBackground();
          return cachedData;
        }
      }
      
      print('🌐 [$_tag] OKX余额数据从网络获取...');
      
      // 并行获取OKX余额和汇总数据
      final futures = await Future.wait([
        OKXService.getAccountBalance(),
        OKXService.getOKXSummary(),
      ]);
      
      // 构建结构化数据
      final structuredData = {
        'balances': futures[0],
        'summary': futures[1],
      };
      
      await CacheService.saveToCache('CNY', cacheKey, structuredData);
      
      print('✅ [$_tag] OKX余额数据获取完成');
      return structuredData;
    } catch (e) {
      print('❌ [$_tag] 获取OKX余额数据失败: $e');
      
      if (!forceRefresh) {
        final expiredCache = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: 60);
        
        if (expiredCache != null) {
          print('⚠️ [$_tag] 使用过期缓存作为备用数据');
          return expiredCache;
        }
      }
      
      rethrow;
    }
  }
  
  /// 智能获取汇率数据
  static Future<dynamic> getExchangeRates({bool forceRefresh = false}) async {
    final cacheKey = 'exchange_rates';
    
    try {
      if (!forceRefresh) {
        final cachedData = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: _exchangeRateCacheExpiryMinutes);
        
        if (cachedData != null) {
          print('📱 [$_tag] 汇率数据从缓存获取，响应时间: <100ms');
          _updateExchangeRatesInBackground();
          return cachedData;
        }
      }
      
      print('🌐 [$_tag] 汇率数据从网络获取...');
      
      // 获取主要货币对的汇率
      final currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'HKD', 'SGD', 'CHF', 'CAD'];
      final futures = currencies.map((currency) => 
        WiseService.getExchangeRates(source: currency, target: 'CNY')).toList();
      
      final results = await Future.wait(futures);
      
      // 构建汇率数据
      final exchangeRates = <String, dynamic>{};
      for (int i = 0; i < currencies.length; i++) {
        exchangeRates['${currencies[i]}_CNY'] = results[i];
      }
      
      await CacheService.saveToCache('CNY', cacheKey, exchangeRates);
      
      print('✅ [$_tag] 汇率数据获取完成');
      return exchangeRates;
    } catch (e) {
      print('❌ [$_tag] 获取汇率数据失败: $e');
      
      if (!forceRefresh) {
        final expiredCache = await CacheService.getFromCache('CNY', cacheKey, 
          expiryMinutes: 60);
        
        if (expiredCache != null) {
          print('⚠️ [$_tag] 使用过期缓存作为备用数据');
          return expiredCache;
        }
      }
      
      rethrow;
    }
  }
  
  /// 后台更新基金持仓数据
  static void _updateFundPositionsInBackground() {
    if (_isUpdatingInBackground['fund_positions'] == true) return;
    
    _isUpdatingInBackground['fund_positions'] = true;
    
    Timer.run(() async {
      try {
        print('🔄 [$_tag] 后台更新基金持仓数据...');
        final data = await AlipayFundService.getFundPositions();
        await CacheService.saveToCache('CNY', 'fund_positions', data);
        print('✅ [$_tag] 基金持仓数据后台更新完成');
      } catch (e) {
        print('❌ [$_tag] 基金持仓数据后台更新失败: $e');
      } finally {
        _isUpdatingInBackground['fund_positions'] = false;
      }
    });
  }
  
  /// 后台更新Wise余额数据
  static void _updateWiseBalancesInBackground() {
    if (_isUpdatingInBackground['wise_balances'] == true) return;
    
    _isUpdatingInBackground['wise_balances'] = true;
    
    Timer.run(() async {
      try {
        print('🔄 [$_tag] 后台更新Wise余额数据...');
        final data = await WiseService.getAllBalances();
        await CacheService.saveToCache('CNY', 'wise_balances', data);
        print('✅ [$_tag] Wise余额数据后台更新完成');
      } catch (e) {
        print('❌ [$_tag] Wise余额数据后台更新失败: $e');
      } finally {
        _isUpdatingInBackground['wise_balances'] = false;
      }
    });
  }
  
  /// 后台更新IBKR持仓数据
  static void _updateIBKRPositionsInBackground() {
    if (_isUpdatingInBackground['ibkr_positions'] == true) return;
    
    _isUpdatingInBackground['ibkr_positions'] = true;
    
    Timer.run(() async {
      try {
        print('🔄 [$_tag] 后台更新IBKR持仓数据...');
        final data = await IBKRService.getPositions();
        await CacheService.saveToCache('CNY', 'ibkr_positions', data);
        print('✅ [$_tag] IBKR持仓数据后台更新完成');
      } catch (e) {
        print('❌ [$_tag] IBKR持仓数据后台更新失败: $e');
      } finally {
        _isUpdatingInBackground['ibkr_positions'] = false;
      }
    });
  }
  
  /// 后台更新OKX余额数据
  static void _updateOKXBalancesInBackground() {
    if (_isUpdatingInBackground['okx_balances'] == true) return;
    
    _isUpdatingInBackground['okx_balances'] = true;
    
    Timer.run(() async {
      try {
        print('🔄 [$_tag] 后台更新OKX余额数据...');
        final data = await OKXService.getAccountBalance();
        await CacheService.saveToCache('CNY', 'okx_balances', data);
        print('✅ [$_tag] OKX余额数据后台更新完成');
      } catch (e) {
        print('❌ [$_tag] OKX余额数据后台更新失败: $e');
      } finally {
        _isUpdatingInBackground['okx_balances'] = false;
      }
    });
  }
  
  /// 后台更新汇率数据
  static void _updateExchangeRatesInBackground() {
    if (_isUpdatingInBackground['exchange_rates'] == true) return;
    
    _isUpdatingInBackground['exchange_rates'] = true;
    
    Timer.run(() async {
      try {
        print('🔄 [$_tag] 后台更新汇率数据...');
        
        final currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'HKD', 'SGD', 'CHF', 'CAD'];
        final futures = currencies.map((currency) => 
          WiseService.getExchangeRates(source: currency, target: 'CNY')).toList();
        
        final results = await Future.wait(futures);
        
        final exchangeRates = <String, dynamic>{};
        for (int i = 0; i < currencies.length; i++) {
          exchangeRates['${currencies[i]}_CNY'] = results[i];
        }
        
        await CacheService.saveToCache('CNY', 'exchange_rates', exchangeRates);
        print('✅ [$_tag] 汇率数据后台更新完成');
      } catch (e) {
        print('❌ [$_tag] 汇率数据后台更新失败: $e');
      } finally {
        _isUpdatingInBackground['exchange_rates'] = false;
      }
    });
  }
  
  /// 预加载所有资产数据
  static Future<void> preloadAllAssets() async {
    print('🚀 [$_tag] 开始预加载所有资产数据...');
    
    try {
      await Future.wait([
        getFundPositions(),
        getWiseBalances(),
        getIBKRPositions(),
        getOKXBalances(),
        getExchangeRates(),
      ]);
      
      print('✅ [$_tag] 所有资产数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] 资产数据预加载失败: $e');
    }
  }
  
  /// 清除所有资产缓存
  static Future<void> clearAllAssetCache() async {
    print('🗑️ [$_tag] 清除所有资产缓存...');
    
    try {
      await Future.wait([
        CacheService.clearCurrencyCache('CNY'),
      ]);
      
      print('✅ [$_tag] 所有资产缓存已清除');
    } catch (e) {
      print('❌ [$_tag] 清除资产缓存失败: $e');
    }
  }
  
  /// 获取缓存状态
  static Future<Map<String, dynamic>> getCacheStatus() async {
    final status = <String, dynamic>{};
    
    try {
      status['fund_positions'] = await CacheService.hasValidCache('CNY', 'fund_positions', 
        expiryMinutes: _assetCacheExpiryMinutes);
      status['wise_balances'] = await CacheService.hasValidCache('CNY', 'wise_balances', 
        expiryMinutes: _assetCacheExpiryMinutes);
      status['ibkr_positions'] = await CacheService.hasValidCache('CNY', 'ibkr_positions', 
        expiryMinutes: _assetCacheExpiryMinutes);
      status['okx_balances'] = await CacheService.hasValidCache('CNY', 'okx_balances', 
        expiryMinutes: _assetCacheExpiryMinutes);
      status['exchange_rates'] = await CacheService.hasValidCache('CNY', 'exchange_rates', 
        expiryMinutes: _exchangeRateCacheExpiryMinutes);
      
      status['isUpdatingInBackground'] = _isUpdatingInBackground;
    } catch (e) {
      print('❌ [$_tag] 获取缓存状态失败: $e');
    }
    
    return status;
  }
}
