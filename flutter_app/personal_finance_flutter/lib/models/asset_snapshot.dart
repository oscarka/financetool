import 'package:json_annotation/json_annotation.dart';

part 'asset_snapshot.g.dart';

@JsonSerializable()
class AssetSnapshot {
  final int id;
  final String platform;
  @JsonKey(name: 'asset_type')
  final String assetType;
  @JsonKey(name: 'asset_code')
  final String assetCode;
  @JsonKey(name: 'asset_name')
  final String? assetName;
  final String currency;
  final double balance;
  @JsonKey(name: 'balance_cny')
  final double? balanceCny;
  @JsonKey(name: 'balance_usd')
  final double? balanceUsd;
  @JsonKey(name: 'balance_eur')
  final double? balanceEur;
  @JsonKey(name: 'base_value')
  final double? baseValue;
  @JsonKey(name: 'snapshot_time')
  final DateTime snapshotTime;

  const AssetSnapshot({
    required this.id,
    required this.platform,
    required this.assetType,
    required this.assetCode,
    this.assetName,
    required this.currency,
    required this.balance,
    this.balanceCny,
    this.balanceUsd,
    this.balanceEur,
    this.baseValue,
    required this.snapshotTime,
  });

  factory AssetSnapshot.fromJson(Map<String, dynamic> json) =>
      _$AssetSnapshotFromJson(json);

  Map<String, dynamic> toJson() => _$AssetSnapshotToJson(this);

  // 获取基准货币值
  double? getBaseValue(String baseCurrency) {
    switch (baseCurrency.toUpperCase()) {
      case 'CNY':
        return balanceCny;
      case 'USD':
        return balanceUsd;
      case 'EUR':
        return balanceEur;
      default:
        return baseValue;
    }
  }

  // 获取基准货币符号
  String getBaseCurrencySymbol(String baseCurrency) {
    switch (baseCurrency.toUpperCase()) {
      case 'CNY':
        return '¥';
      case 'USD':
        return '\$';
      case 'EUR':
        return '€';
      default:
        return '';
    }
  }

  // 格式化显示值
  String getFormattedValue(String baseCurrency) {
    final value = getBaseValue(baseCurrency);
    if (value == null) return '--';
    
    final symbol = getBaseCurrencySymbol(baseCurrency);
    return '$symbol${value.toStringAsFixed(2)}';
  }
}