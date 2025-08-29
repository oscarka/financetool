import 'dart:async';
import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'smart_api_client.dart';

/// 智能后台缓存服务
/// 在网络空闲时自动预加载所有货币数据
class BackgroundCacheService {
  static const String _tag = 'BackgroundCacheService';
  
  // 支持的货币列表
  static const List<String> _supportedCurrencies = ['CNY', 'USD', 'EUR', 'USDT', 'BTC'];
  
  // 缓存间隔配置
  static const Duration _cacheInterval = Duration(minutes: 30); // 30分钟缓存一次
  static const Duration _networkIdleDelay = Duration(seconds: 10); // 网络空闲10秒后开始缓存
  
  // 定时器和状态管理
  static Timer? _cacheTimer;
  static Timer? _idleTimer;
  static bool _isRunning = false;
  static bool _isNetworkIdle = false;
  
  // 网络状态监听
  static StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  
  /// 启动后台缓存服务
  static Future<void> start() async {
    if (_isRunning) {
      print('🔄 [$_tag] 后台缓存服务已在运行');
      return;
    }
    
    print('🚀 [$_tag] 启动智能后台缓存服务...');
    _isRunning = true;
    
    // 启动网络状态监听
    _startNetworkMonitoring();
    
    // 启动定时缓存
    _startPeriodicCaching();
    
    // 立即执行一次缓存检查
    _scheduleIdleCaching();
    
    print('✅ [$_tag] 智能后台缓存服务已启动');
  }
  
  /// 停止后台缓存服务
  static Future<void> stop() async {
    if (!_isRunning) return;
    
    print('🛑 [$_tag] 停止智能后台缓存服务...');
    _isRunning = false;
    
    // 清理定时器
    _cacheTimer?.cancel();
    _idleTimer?.cancel();
    _cacheTimer = null;
    _idleTimer = null;
    
    // 停止网络监听
    _connectivitySubscription?.cancel();
    _connectivitySubscription = null;
    
    print('✅ [$_tag] 智能后台缓存服务已停止');
  }
  
  /// 启动网络状态监听
  static void _startNetworkMonitoring() {
    _connectivitySubscription = Connectivity()
        .onConnectivityChanged
        .listen((ConnectivityResult result) {
      if (result == ConnectivityResult.none) {
        print('📡 [$_tag] 网络断开，暂停后台缓存');
        _isNetworkIdle = false;
        _idleTimer?.cancel();
      } else {
        print('📡 [$_tag] 网络连接恢复，重新启动后台缓存');
        _isNetworkIdle = true;
        _scheduleIdleCaching();
      }
    });
  }
  
  /// 启动定时缓存
  static void _startPeriodicCaching() {
    _cacheTimer = Timer.periodic(_cacheInterval, (timer) {
      if (_isRunning && _isNetworkIdle) {
        print('⏰ [$_tag] 定时缓存触发，开始后台预加载...');
        _executeBackgroundCaching();
      }
    });
  }
  
  /// 安排空闲时缓存
  static void _scheduleIdleCaching() {
    _idleTimer?.cancel();
    _idleTimer = Timer(_networkIdleDelay, () {
      if (_isRunning && _isNetworkIdle) {
        print('😴 [$_tag] 网络空闲，开始后台预加载...');
        _executeBackgroundCaching();
      }
    });
  }
  
  /// 执行后台缓存
  static Future<void> _executeBackgroundCaching() async {
    if (!_isRunning || !_isNetworkIdle) return;
    
    print('🔄 [$_tag] 开始执行后台缓存...');
    
    // 并行预加载所有货币数据
    final futures = <Future<void>>[];
    
    for (final currency in _supportedCurrencies) {
      futures.add(_preloadCurrencyInBackground(currency));
    }
    
    try {
      await Future.wait(futures);
      print('✅ [$_tag] 后台缓存完成');
    } catch (e) {
      print('❌ [$_tag] 后台缓存过程中出现错误: $e');
    }
  }
  
  /// 后台预加载单个货币数据
  static Future<void> _preloadCurrencyInBackground(String currency) async {
    try {
      // 检查是否已有有效缓存
      final hasValidCache = await SmartApiClient.hasValidCache(currency, 'aggregated_stats');
      if (hasValidCache) {
        print('✅ [$_tag] $currency 已有有效缓存，跳过');
        return;
      }
      
              // 后台预加载 $currency 数据...
      
      // 预加载核心数据
      await Future.wait([
        SmartApiClient.getAggregatedStats(currency, forceRefresh: true),
        SmartApiClient.getAssetSnapshots(currency, forceRefresh: true),
      ]);
      
      print('✅ [$_tag] $currency 数据预加载完成');
    } catch (e) {
      print('❌ [$_tag] $currency 数据预加载失败: $e');
    }
  }
  
  /// 手动触发后台缓存
  static Future<void> triggerManualCaching() async {
    if (!_isRunning) {
      print('⚠️ [$_tag] 后台缓存服务未运行，无法手动触发');
      return;
    }
    
    print('👆 [$_tag] 手动触发后台缓存...');
    await _executeBackgroundCaching();
  }
  
  /// 获取服务状态
  static Map<String, dynamic> getServiceStatus() {
    return {
      'isRunning': _isRunning,
      'isNetworkIdle': _isNetworkIdle,
      'supportedCurrencies': _supportedCurrencies,
      'cacheInterval': _cacheInterval.inMinutes,
      'networkIdleDelay': _networkIdleDelay.inSeconds,
    };
  }
  
  /// 检查是否正在运行
  static bool get isRunning => _isRunning;
  
  /// 检查网络是否空闲
  static bool get isNetworkIdle => _isNetworkIdle;
}
