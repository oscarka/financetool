import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../models/asset_snapshot.dart';
import '../services/api_client.dart';

// Dio Provider
final dioProvider = Provider<Dio>((ref) {
  return createDio();
});

// API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = ref.read(dioProvider);
  return ApiClient(dio);
});

// 筛选参数类
class AssetFilter {
  final String baseCurrency;
  final String platform;
  final String assetType;
  final String searchText;
  final DateTime? startDate;
  final DateTime? endDate;

  const AssetFilter({
    this.baseCurrency = 'CNY',
    this.platform = '',
    this.assetType = '',
    this.searchText = '',
    this.startDate,
    this.endDate,
  });

  AssetFilter copyWith({
    String? baseCurrency,
    String? platform,
    String? assetType,
    String? searchText,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    return AssetFilter(
      baseCurrency: baseCurrency ?? this.baseCurrency,
      platform: platform ?? this.platform,
      assetType: assetType ?? this.assetType,
      searchText: searchText ?? this.searchText,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
    );
  }
}

// 筛选状态 Provider
class AssetFilterNotifier extends StateNotifier<AssetFilter> {
  AssetFilterNotifier() : super(const AssetFilter());

  void updateBaseCurrency(String currency) {
    state = state.copyWith(baseCurrency: currency);
  }

  void updatePlatform(String platform) {
    state = state.copyWith(platform: platform);
  }

  void updateAssetType(String assetType) {
    state = state.copyWith(assetType: assetType);
  }

  void updateSearchText(String text) {
    state = state.copyWith(searchText: text);
  }

  void updateDateRange(DateTime? start, DateTime? end) {
    state = state.copyWith(startDate: start, endDate: end);
  }

  void reset() {
    state = const AssetFilter();
  }
}

final assetFilterProvider = StateNotifierProvider<AssetFilterNotifier, AssetFilter>((ref) {
  return AssetFilterNotifier();
});

// 资产快照数据 Provider
final assetSnapshotsProvider = FutureProvider<List<AssetSnapshot>>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  final filter = ref.watch(assetFilterProvider);
  
  try {
    final snapshots = await apiClient.getAssetSnapshots(
      filter.startDate?.toIso8601String(),
      filter.endDate?.toIso8601String(),
      filter.platform.isEmpty ? null : filter.platform,
      filter.baseCurrency,
    );
    
    // 客户端筛选
    return snapshots.where((snapshot) {
      // 搜索筛选
      if (filter.searchText.isNotEmpty) {
        final searchLower = filter.searchText.toLowerCase();
        final matchesCode = snapshot.assetCode.toLowerCase().contains(searchLower);
        final matchesName = snapshot.assetName?.toLowerCase().contains(searchLower) ?? false;
        if (!matchesCode && !matchesName) return false;
      }
      
      // 资产类型筛选
      if (filter.assetType.isNotEmpty && snapshot.assetType != filter.assetType) {
        return false;
      }
      
      return true;
    }).toList();
  } catch (e) {
    throw Exception('加载资产数据失败: $e');
  }
});

// 资产统计 Provider
final assetStatsProvider = Provider<Map<String, dynamic>>((ref) {
  final asyncSnapshots = ref.watch(assetSnapshotsProvider);
  
  return asyncSnapshots.when(
    data: (snapshots) {
      if (snapshots.isEmpty) {
        return {
          'totalValue': 0.0,
          'totalAssets': 0,
          'platforms': 0,
          'assetTypes': 0,
        };
      }
      
      final filter = ref.read(assetFilterProvider);
      final baseCurrency = filter.baseCurrency;
      
      double totalValue = 0;
      final platforms = <String>{};
      final assetTypes = <String>{};
      
      for (final snapshot in snapshots) {
        final value = snapshot.getBaseValue(baseCurrency);
        if (value != null) {
          totalValue += value;
        }
        platforms.add(snapshot.platform);
        assetTypes.add(snapshot.assetType);
      }
      
      return {
        'totalValue': totalValue,
        'totalAssets': snapshots.length,
        'platforms': platforms.length,
        'assetTypes': assetTypes.length,
        'currency': baseCurrency,
      };
    },
    loading: () => {
      'totalValue': 0.0,
      'totalAssets': 0,
      'platforms': 0,
      'assetTypes': 0,
    },
    error: (_, __) => {
      'totalValue': 0.0,
      'totalAssets': 0,
      'platforms': 0,
      'assetTypes': 0,
    },
  );
});

// 平台列表 Provider
final platformsProvider = Provider<List<String>>((ref) {
  final asyncSnapshots = ref.watch(assetSnapshotsProvider);
  
  return asyncSnapshots.when(
    data: (snapshots) {
      final platforms = snapshots.map((s) => s.platform).toSet().toList();
      platforms.sort();
      return platforms;
    },
    loading: () => [],
    error: (_, __) => [],
  );
});

// 资产类型列表 Provider
final assetTypesProvider = Provider<List<String>>((ref) {
  final asyncSnapshots = ref.watch(assetSnapshotsProvider);
  
  return asyncSnapshots.when(
    data: (snapshots) {
      final types = snapshots.map((s) => s.assetType).toSet().toList();
      types.sort();
      return types;
    },
    loading: () => [],
    error: (_, __) => [],
  );
});