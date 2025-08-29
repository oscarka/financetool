import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/fund_operation.dart';

class FundOperationService {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app/api/v1';
  
  /// 创建基金操作记录
  static Future<Map<String, dynamic>> createOperation(FundOperation operation) async {
    try {
      print('🔄 [FundOperationService] 正在创建基金操作记录...');
      
      final response = await http.post(
        Uri.parse('$baseUrl/funds/operations'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(operation.toJson()),
      );
      
      print('📡 [FundOperationService] 创建基金操作API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [FundOperationService] 创建基金操作API响应数据: $data');
        
        if (data['success'] == true) {
          print('✅ [FundOperationService] 成功创建基金操作记录');
          return data;
        } else {
          print('❌ [FundOperationService] 创建基金操作失败: ${data['message']}');
          throw Exception(data['message'] ?? '创建失败');
        }
      } else {
        print('❌ [FundOperationService] 创建基金操作API HTTP错误: ${response.statusCode}');
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [FundOperationService] 创建基金操作异常: $e');
      rethrow;
    }
  }
  
  /// 获取基金操作记录列表
  static Future<List<FundOperation>> getOperations({
    String? assetCode,
    String? operationType,
    String? startDate,
    String? endDate,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      print('🔄 [FundOperationService] 正在获取基金操作记录...');
      
      final queryParams = <String, String>{
        'page': page.toString(),
        'page_size': pageSize.toString(),
      };
      
      if (assetCode != null) queryParams['asset_code'] = assetCode;
      if (operationType != null) queryParams['operation_type'] = operationType;
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;
      
      final uri = Uri.parse('$baseUrl/funds/operations').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [FundOperationService] 获取基金操作API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [FundOperationService] 获取基金操作API响应数据: $data');
        
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> operationsData = data['data'];
          final operations = operationsData.map((json) => FundOperation.fromJson(json)).toList();
          print('✅ [FundOperationService] 成功获取基金操作记录: ${operations.length}条');
          return operations;
        } else {
          print('❌ [FundOperationService] 获取基金操作失败: ${data['message']}');
          return [];
        }
      } else {
        print('❌ [FundOperationService] 获取基金操作API HTTP错误: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('❌ [FundOperationService] 获取基金操作异常: $e');
      return [];
    }
  }
  
  /// 更新基金操作记录
  static Future<Map<String, dynamic>> updateOperation(int operationId, Map<String, dynamic> updateData) async {
    try {
      print('🔄 [FundOperationService] 正在更新基金操作记录: $operationId');
      
      final response = await http.put(
        Uri.parse('$baseUrl/funds/operations/$operationId'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(updateData),
      );
      
      print('📡 [FundOperationService] 更新基金操作API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [FundOperationService] 更新基金操作API响应数据: $data');
        
        if (data['success'] == true) {
          print('✅ [FundOperationService] 成功更新基金操作记录');
          return data;
        } else {
          print('❌ [FundOperationService] 更新基金操作失败: ${data['message']}');
          throw Exception(data['message'] ?? '更新失败');
        }
      } else {
        print('❌ [FundOperationService] 更新基金操作API HTTP错误: ${response.statusCode}');
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [FundOperationService] 更新基金操作异常: $e');
      rethrow;
    }
  }
  
  /// 删除基金操作记录
  static Future<Map<String, dynamic>> deleteOperation(int operationId) async {
    try {
      print('🔄 [FundOperationService] 正在删除基金操作记录: $operationId');
      
      final response = await http.delete(
        Uri.parse('$baseUrl/funds/operations/$operationId'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      print('📡 [FundOperationService] 删除基金操作API响应状态: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('📊 [FundOperationService] 删除基金操作API响应数据: $data');
        
        if (data['success'] == true) {
          print('✅ [FundOperationService] 成功删除基金操作记录');
          return data;
        } else {
          print('❌ [FundOperationService] 删除基金操作失败: ${data['message']}');
          throw Exception(data['message'] ?? '删除失败');
        }
      } else {
        print('❌ [FundOperationService] 删除基金操作API HTTP错误: ${response.statusCode}');
        throw Exception('HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [FundOperationService] 删除基金操作异常: $e');
      rethrow;
    }
  }
  
  /// 获取基金净值信息
  static Future<double?> getLatestNav(String fundCode) async {
    try {
      print('🔄 [FundOperationService] 正在获取基金净值: $fundCode');
      
      final response = await http.get(
        Uri.parse('$baseUrl/funds/nav/$fundCode'),
        headers: {
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          final navHistory = data['data']['nav_history'] as List;
          if (navHistory.isNotEmpty) {
            final latestNav = navHistory.first['nav'] as double?;
            print('✅ [FundOperationService] 获取到最新净值: $latestNav');
            return latestNav;
          }
        }
      }
      
      print('❌ [FundOperationService] 获取基金净值失败');
      return null;
    } catch (e) {
      print('❌ [FundOperationService] 获取基金净值异常: $e');
      return null;
    }
  }
  
  /// 智能建议操作策略
  static String getSmartStrategy({
    required String operationType,
    required double amount,
    double? currentNav,
    double? avgCost,
    String? marketTrend,
  }) {
    List<String> strategies = [];
    
    if (operationType == 'buy') {
      if (amount >= 10000) {
        strategies.add('大额投资');
      } else if (amount >= 5000) {
        strategies.add('中等投资');
      } else {
        strategies.add('小额投资');
      }
      
      if (currentNav != null && avgCost != null) {
        if (currentNav < avgCost * 0.9) {
          strategies.add('低位补仓');
        } else if (currentNav > avgCost * 1.1) {
          strategies.add('追涨买入');
        } else {
          strategies.add('均衡买入');
        }
      }
      
      if (marketTrend == 'up') {
        strategies.add('趋势跟随');
      } else if (marketTrend == 'down') {
        strategies.add('逆势布局');
      }
      
    } else if (operationType == 'sell') {
      if (amount >= 10000) {
        strategies.add('大额赎回');
      } else if (amount >= 5000) {
        strategies.add('中等赎回');
      } else {
        strategies.add('小额赎回');
      }
      
      if (currentNav != null && avgCost != null) {
        if (currentNav > avgCost * 1.2) {
          strategies.add('止盈卖出');
        } else if (currentNav < avgCost * 0.8) {
          strategies.add('止损卖出');
        } else {
          strategies.add('调整仓位');
        }
      }
    }
    
    return strategies.isEmpty ? '常规操作' : strategies.join(' + ');
  }
  
  /// 智能建议情绪评分
  static int getSmartEmotionScore({
    required String operationType,
    required double amount,
    double? currentNav,
    double? avgCost,
    String? marketTrend,
  }) {
    int baseScore = 5; // 中性评分
    
    if (operationType == 'buy') {
      if (currentNav != null && avgCost != null) {
        if (currentNav < avgCost * 0.9) {
          baseScore += 2; // 低位买入，更乐观
        } else if (currentNav > avgCost * 1.1) {
          baseScore -= 1; // 高位买入，稍微谨慎
        }
      }
      
      if (marketTrend == 'up') {
        baseScore += 1; // 上涨趋势，更乐观
      } else if (marketTrend == 'down') {
        baseScore -= 1; // 下跌趋势，更谨慎
      }
      
    } else if (operationType == 'sell') {
      if (currentNav != null && avgCost != null) {
        if (currentNav > avgCost * 1.2) {
          baseScore += 1; // 止盈卖出，满意
        } else if (currentNav < avgCost * 0.8) {
          baseScore -= 2; // 止损卖出，失望
        }
      }
    }
    
    // 根据金额调整情绪
    if (amount >= 10000) {
      baseScore += 1; // 大额操作，情绪更强
    } else if (amount <= 1000) {
      baseScore -= 1; // 小额操作，情绪更弱
    }
    
    // 确保评分在1-10范围内
    return baseScore.clamp(1, 10);
  }
}
