import 'package:json_annotation/json_annotation.dart';

part 'fund_operation.g.dart';

@JsonSerializable()
class FundOperation {
  @JsonKey(name: 'id')
  final int? id;
  
  @JsonKey(name: 'operation_date')
  final String operationDate;
  
  @JsonKey(name: 'operation_type')
  final String operationType;
  
  @JsonKey(name: 'asset_code')
  final String assetCode;
  
  @JsonKey(name: 'asset_name')
  final String assetName;
  
  @JsonKey(name: 'amount', fromJson: _parseDouble)
  final double amount;
  
  @JsonKey(name: 'nav', fromJson: _parseDouble)
  final double? nav;
  
  @JsonKey(name: 'fee', fromJson: _parseDouble)
  final double? fee;
  
  @JsonKey(name: 'quantity', fromJson: _parseDouble)
  final double? quantity;
  
  @JsonKey(name: 'strategy')
  final String? strategy;
  
  @JsonKey(name: 'emotion_score')
  final int? emotionScore;
  
  @JsonKey(name: 'notes')
  final String? notes;
  
  @JsonKey(name: 'status')
  final String status;
  
  @JsonKey(name: 'dca_plan_id')
  final int? dcaPlanId;
  
  @JsonKey(name: 'dca_execution_type')
  final String? dcaExecutionType;
  
  @JsonKey(name: 'created_at')
  final String? createdAt;
  
  @JsonKey(name: 'updated_at')
  final String? updatedAt;

  const FundOperation({
    this.id,
    required this.operationDate,
    required this.operationType,
    required this.assetCode,
    required this.assetName,
    required this.amount,
    this.nav,
    this.fee,
    this.quantity,
    this.strategy,
    this.emotionScore,
    this.notes,
    this.status = 'pending',
    this.dcaPlanId,
    this.dcaExecutionType,
    this.createdAt,
    this.updatedAt,
  });

  factory FundOperation.fromJson(Map<String, dynamic> json) =>
      _$FundOperationFromJson(json);

  Map<String, dynamic> toJson() => _$FundOperationToJson(this);

  /// 解析数值字段，支持字符串和数字类型
  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        print('解析基金操作数值失败: $value, 错误: $e');
        return 0.0;
      }
    }
    return 0.0;
  }

  /// 获取操作类型的中文名称
  String get operationTypeDisplay {
    switch (operationType.toLowerCase()) {
      case 'buy':
        return '买入';
      case 'sell':
        return '卖出';
      case 'dividend':
        return '分红';
      default:
        return operationType;
    }
  }

  /// 获取操作类型的图标
  String get operationTypeIcon {
    switch (operationType.toLowerCase()) {
      case 'buy':
        return '📈';
      case 'sell':
        return '📉';
      case 'dividend':
        return '💰';
      default:
        return '📊';
    }
  }

  /// 获取操作类型的颜色
  String get operationTypeColor {
    switch (operationType.toLowerCase()) {
      case 'buy':
        return 'green';
      case 'sell':
        return 'red';
      case 'dividend':
        return 'blue';
      default:
        return 'gray';
    }
  }

  /// 获取状态的中文名称
  String get statusDisplay {
    switch (status.toLowerCase()) {
      case 'pending':
        return '待确认';
      case 'confirmed':
        return '已确认';
      case 'processed':
        return '已处理';
      case 'cancelled':
        return '已取消';
      default:
        return status;
    }
  }

  /// 获取状态的颜色
  String get statusColor {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'orange';
      case 'confirmed':
        return 'green';
      case 'processed':
        return 'blue';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  }

  /// 获取情绪评分的显示文本
  String get emotionScoreDisplay {
    if (emotionScore == null) return '未评分';
    switch (emotionScore!) {
      case 1:
        return '😰 极度恐慌';
      case 2:
        return '😨 恐慌';
      case 3:
        return '😟 担忧';
      case 4:
        return '😐 中性';
      case 5:
        return '😊 乐观';
      case 6:
        return '😄 积极';
      case 7:
        return '😃 兴奋';
      case 8:
        return '🤩 狂热';
      case 9:
        return '🚀 极度乐观';
      case 10:
        return '💎 钻石手';
      default:
        return '未评分';
    }
  }

  /// 获取定投执行类型的显示文本
  String get dcaExecutionTypeDisplay {
    switch (dcaExecutionType?.toLowerCase()) {
      case 'scheduled':
        return '定时执行';
      case 'manual':
        return '手动执行';
      case 'smart':
        return '智能执行';
      default:
        return '手动';
    }
  }

  /// 计算数量（如果有净值和金额）
  double? get calculatedQuantity {
    if (nav != null && nav! > 0 && amount > 0) {
      return amount / nav!;
    }
    return quantity;
  }

  /// 获取操作日期
  DateTime get operationDateTime {
    try {
      return DateTime.parse(operationDate);
    } catch (e) {
      return DateTime.now();
    }
  }

  /// 获取操作日期的格式化文本
  String get operationDateDisplay {
    final date = operationDateTime;
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays == 0) {
      return '今天';
    } else if (difference.inDays == 1) {
      return '昨天';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return '${date.month}-${date.day}';
    }
  }
}
