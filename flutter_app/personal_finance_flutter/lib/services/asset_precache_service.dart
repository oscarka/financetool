import 'dart:async';
import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'cache_service.dart';
import 'alipay_fund_service.dart';
import 'wise_service.dart';
import 'ibkr_service.dart';
import 'okx_service.dart';

/// 资产预缓存服务
/// 专门用于预加载资产相关数据，提升资产查看响应速度
class AssetPrecacheService {
  static const String _tag = 'AssetPrecacheService';
  
  // 缓存配置
  static const Duration _assetCacheExpiry = Duration(minutes: 15); // 资产数据缓存15分钟
  static const Duration _exchangeRateCacheExpiry = Duration(minutes: 5); // 汇率数据缓存5分钟
  static const Duration _precacheInterval = Duration(minutes: 10); // 每10分钟预缓存一次
  static const Duration _networkIdleDelay = Duration(seconds: 5); // 网络空闲5秒后开始缓存
  
  // 状态管理
  static Timer? _precacheTimer;
  static Timer? _idleTimer;
  static bool _isRunning = false;
  static bool _isNetworkIdle = false;
  static bool _isPrecaching = false;
  
  // 网络状态监听
  static StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  
  // 缓存统计
  static final Map<String, DateTime> _lastCacheTime = {};
  static final Map<String, int> _cacheHitCount = {};
  
  /// 启动资产预缓存服务
  static Future<void> start() async {
    if (_isRunning) {
      print('🔄 [$_tag] 资产预缓存服务已在运行');
      return;
    }
    
    print('🚀 [$_tag] 启动资产预缓存服务...');
    _isRunning = true;
    
    // 启动网络状态监听
    _startNetworkMonitoring();
    
    // 启动定时预缓存
    _startPeriodicPrecaching();
    
    // 立即执行一次预缓存检查
    _scheduleIdlePrecaching();
    
    print('✅ [$_tag] 资产预缓存服务已启动');
  }
  
  /// 停止资产预缓存服务
  static Future<void> stop() async {
    if (!_isRunning) return;
    
    print('🛑 [$_tag] 停止资产预缓存服务...');
    _isRunning = false;
    
    // 清理定时器
    _precacheTimer?.cancel();
    _idleTimer?.cancel();
    _precacheTimer = null;
    _idleTimer = null;
    
    // 停止网络监听
    _connectivitySubscription?.cancel();
    _connectivitySubscription = null;
    
    print('✅ [$_tag] 资产预缓存服务已停止');
  }
  
  /// 启动网络状态监听
  static void _startNetworkMonitoring() {
    _connectivitySubscription = Connectivity()
        .onConnectivityChanged
        .listen((ConnectivityResult result) {
      if (result == ConnectivityResult.none) {
        print('📡 [$_tag] 网络断开，暂停预缓存');
        _isNetworkIdle = false;
        _idleTimer?.cancel();
      } else {
        print('📡 [$_tag] 网络连接恢复，重新启动预缓存');
        _isNetworkIdle = true;
        _scheduleIdlePrecaching();
      }
    });
  }
  
  /// 启动定时预缓存
  static void _startPeriodicPrecaching() {
    _precacheTimer = Timer.periodic(_precacheInterval, (timer) {
      if (_isRunning && _isNetworkIdle && !_isPrecaching) {
        print('⏰ [$_tag] 定时预缓存触发，开始预加载资产数据...');
        _executeAssetPrecaching();
      }
    });
  }
  
  /// 安排空闲时预缓存
  static void _scheduleIdlePrecaching() {
    _idleTimer?.cancel();
    _idleTimer = Timer(_networkIdleDelay, () {
      if (_isRunning && _isNetworkIdle && !_isPrecaching) {
        print('😴 [$_tag] 网络空闲，开始预加载资产数据...');
        _executeAssetPrecaching();
      }
    });
  }
  
  /// 执行资产预缓存
  static Future<void> _executeAssetPrecaching() async {
    if (!_isRunning || !_isNetworkIdle || _isPrecaching) return;
    
    _isPrecaching = true;
    print('🔄 [$_tag] 开始执行资产预缓存...');
    
    try {
      // 并行预加载所有资产数据
      await Future.wait([
        _preloadFundAssets(),
        _preloadWiseAssets(),
        _preloadIBKRAssets(),
        _preloadOKXAssets(),
        _preloadExchangeRates(),
      ]);
      
      print('✅ [$_tag] 资产预缓存完成');
    } catch (e) {
      print('❌ [$_tag] 资产预缓存过程中出现错误: $e');
    } finally {
      _isPrecaching = false;
    }
  }
  
  /// 预加载基金资产数据
  static Future<void> _preloadFundAssets() async {
    try {
      // 检查是否已有有效缓存
      final hasValidCache = await CacheService.hasValidCache('CNY', 'fund_positions', 
        expiryMinutes: _assetCacheExpiry.inMinutes);
      
      if (hasValidCache) {
        print('✅ [$_tag] 基金资产已有有效缓存，跳过');
        return;
      }
      
      print('🔄 [$_tag] 预加载基金资产数据...');
      
      // 并行获取基金数据
      final futures = await Future.wait([
        AlipayFundService.getFundPositions(),
        AlipayFundService.getPositionSummary(),
      ]);
      
      // 缓存基金持仓数据
      await CacheService.saveToCache('CNY', 'fund_positions', futures[0]);
      await CacheService.saveToCache('CNY', 'fund_summary', futures[1]);
      
      _updateCacheStats('fund_assets');
      print('✅ [$_tag] 基金资产数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] 基金资产数据预加载失败: $e');
    }
  }
  
  /// 预加载Wise资产数据
  static Future<void> _preloadWiseAssets() async {
    try {
      final hasValidCache = await CacheService.hasValidCache('CNY', 'wise_balances', 
        expiryMinutes: _assetCacheExpiry.inMinutes);
      
      if (hasValidCache) {
        print('✅ [$_tag] Wise资产已有有效缓存，跳过');
        return;
      }
      
      print('🔄 [$_tag] 预加载Wise资产数据...');
      
      final futures = await Future.wait([
        WiseService.getAllBalances(),
        WiseService.getWiseSummary(),
      ]);
      
      await CacheService.saveToCache('CNY', 'wise_balances', futures[0]);
      await CacheService.saveToCache('CNY', 'wise_summary', futures[1]);
      
      _updateCacheStats('wise_assets');
      print('✅ [$_tag] Wise资产数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] Wise资产数据预加载失败: $e');
    }
  }
  
  /// 预加载IBKR资产数据
  static Future<void> _preloadIBKRAssets() async {
    try {
      final hasValidCache = await CacheService.hasValidCache('CNY', 'ibkr_positions', 
        expiryMinutes: _assetCacheExpiry.inMinutes);
      
      if (hasValidCache) {
        print('✅ [$_tag] IBKR资产已有有效缓存，跳过');
        return;
      }
      
      print('🔄 [$_tag] 预加载IBKR资产数据...');
      
      final futures = await Future.wait([
        IBKRService.getPositions(),
        IBKRService.getBalances(),
        IBKRService.getIBKRSummary(),
      ]);
      
      await CacheService.saveToCache('CNY', 'ibkr_positions', futures[0]);
      await CacheService.saveToCache('CNY', 'ibkr_balances', futures[1]);
      await CacheService.saveToCache('CNY', 'ibkr_summary', futures[2]);
      
      _updateCacheStats('ibkr_assets');
      print('✅ [$_tag] IBKR资产数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] IBKR资产数据预加载失败: $e');
    }
  }
  
  /// 预加载OKX资产数据
  static Future<void> _preloadOKXAssets() async {
    try {
      final hasValidCache = await CacheService.hasValidCache('CNY', 'okx_balances', 
        expiryMinutes: _assetCacheExpiry.inMinutes);
      
      if (hasValidCache) {
        print('✅ [$_tag] OKX资产已有有效缓存，跳过');
        return;
      }
      
      print('🔄 [$_tag] 预加载OKX资产数据...');
      
      final futures = await Future.wait([
        OKXService.getAccountBalance(),
        OKXService.getOKXSummary(),
      ]);
      
      await CacheService.saveToCache('CNY', 'okx_balances', futures[0]);
      await CacheService.saveToCache('CNY', 'okx_summary', futures[1]);
      
      _updateCacheStats('okx_assets');
      print('✅ [$_tag] OKX资产数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] OKX资产数据预加载失败: $e');
    }
  }
  
  /// 预加载汇率数据
  static Future<void> _preloadExchangeRates() async {
    try {
      final hasValidCache = await CacheService.hasValidCache('CNY', 'exchange_rates', 
        expiryMinutes: _exchangeRateCacheExpiry.inMinutes);
      
      if (hasValidCache) {
        print('✅ [$_tag] 汇率数据已有有效缓存，跳过');
        return;
      }
      
      print('🔄 [$_tag] 预加载汇率数据...');
      
      // 预加载主要货币对的汇率
      final currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'HKD', 'SGD', 'CHF', 'CAD'];
      final futures = currencies.map((currency) => 
        WiseService.getExchangeRates(source: currency, target: 'CNY')).toList();
      
      final results = await Future.wait(futures);
      
      // 构建汇率缓存数据
      final exchangeRates = <String, dynamic>{};
      for (int i = 0; i < currencies.length; i++) {
        exchangeRates['${currencies[i]}_CNY'] = results[i];
      }
      
      await CacheService.saveToCache('CNY', 'exchange_rates', exchangeRates);
      
      _updateCacheStats('exchange_rates');
      print('✅ [$_tag] 汇率数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] 汇率数据预加载失败: $e');
    }
  }
  
  /// 手动触发资产预缓存
  static Future<void> triggerManualPrecaching() async {
    if (!_isRunning) {
      print('⚠️ [$_tag] 资产预缓存服务未运行，无法手动触发');
      return;
    }
    
    if (_isPrecaching) {
      print('⚠️ [$_tag] 正在预缓存中，请稍后再试');
      return;
    }
    
    print('👆 [$_tag] 手动触发资产预缓存...');
    await _executeAssetPrecaching();
  }
  
  /// 预加载特定资产类型
  static Future<void> preloadSpecificAsset(String assetType) async {
    if (!_isRunning) return;
    
    print('🎯 [$_tag] 预加载特定资产: $assetType');
    
    switch (assetType.toLowerCase()) {
      case 'fund':
        await _preloadFundAssets();
        break;
      case 'wise':
        await _preloadWiseAssets();
        break;
      case 'ibkr':
        await _preloadIBKRAssets();
        break;
      case 'okx':
        await _preloadOKXAssets();
        break;
      case 'exchange_rates':
        await _preloadExchangeRates();
        break;
      default:
        print('⚠️ [$_tag] 未知的资产类型: $assetType');
    }
  }
  
  /// 更新缓存统计
  static void _updateCacheStats(String assetType) {
    _lastCacheTime[assetType] = DateTime.now();
    _cacheHitCount[assetType] = (_cacheHitCount[assetType] ?? 0) + 1;
  }
  
  /// 获取服务状态
  static Map<String, dynamic> getServiceStatus() {
    return {
      'isRunning': _isRunning,
      'isNetworkIdle': _isNetworkIdle,
      'isPrecaching': _isPrecaching,
      'lastCacheTime': _lastCacheTime,
      'cacheHitCount': _cacheHitCount,
      'precacheInterval': _precacheInterval.inMinutes,
      'assetCacheExpiry': _assetCacheExpiry.inMinutes,
      'exchangeRateCacheExpiry': _exchangeRateCacheExpiry.inMinutes,
    };
  }
  
  /// 检查是否正在运行
  static bool get isRunning => _isRunning;
  
  /// 检查是否正在预缓存
  static bool get isPrecaching => _isPrecaching;
  
  /// 检查网络是否空闲
  static bool get isNetworkIdle => _isNetworkIdle;
}
