// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'asset_snapshot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AssetSnapshot _$AssetSnapshotFromJson(Map<String, dynamic> json) =>
    AssetSnapshot(
      id: (json['id'] as num).toInt(),
      platform: json['platform'] as String,
      assetType: json['asset_type'] as String,
      assetCode: json['asset_code'] as String,
      assetName: json['asset_name'] as String?,
      currency: json['currency'] as String,
      balance: (json['balance'] as num).toDouble(),
      balanceCny: (json['balance_cny'] as num?)?.toDouble(),
      balanceUsd: (json['balance_usd'] as num?)?.toDouble(),
      balanceEur: (json['balance_eur'] as num?)?.toDouble(),
      baseValue: (json['base_value'] as num?)?.toDouble(),
      snapshotTime: DateTime.parse(json['snapshot_time'] as String),
    );

Map<String, dynamic> _$AssetSnapshotToJson(AssetSnapshot instance) =>
    <String, dynamic>{
      'id': instance.id,
      'platform': instance.platform,
      'asset_type': instance.assetType,
      'asset_code': instance.assetCode,
      'asset_name': instance.assetName,
      'currency': instance.currency,
      'balance': instance.balance,
      'balance_cny': instance.balanceCny,
      'balance_usd': instance.balanceUsd,
      'balance_eur': instance.balanceEur,
      'base_value': instance.baseValue,
      'snapshot_time': instance.snapshotTime.toIso8601String(),
    };
