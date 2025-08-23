import 'package:flutter/material.dart';
import 'chart_design_system.dart';
import 'dart:convert';
import 'dart:math';
import 'package:http/http.dart' as http;
import 'package:fl_chart/fl_chart.dart';

/// MCP图表适配器 - 将MCP返回的数据转换为设计系统格式
class MCPChartAdapter {
  static const String baseUrl = 'https://backend-production-2750.up.railway.app'; // 使用正确的后端API地址
  
  // 全局变量存储最新的图表数据
  static List<dynamic>? _lastChartData;
  static List<CustomPieChartData>? _lastChartDataWithPercentage;
  
  /// 获取最新的图表数据
  static List<dynamic>? get lastChartData => _lastChartData;
  
  /// 获取最新的图表数据（带百分比）
  static List<CustomPieChartData>? get lastChartDataWithPercentage => _lastChartDataWithPercentage;

  /// 生成图表响应
  static Future<Widget> generateChartResponse(String question) async {
    try {
      print('🎯 ===== 开始生成图表响应 =====');
      print('❓ 用户问题: $question');
      print('⏰ 时间: ${DateTime.now()}');
      
      // 禁用mock模式，使用真实API
      final useMock = false; // 强制使用真实API
      print('🔧 Mock模式: $useMock');
      
      if (useMock) {
        // Mock模式（已禁用）
        print('🎭 使用Mock模式生成图表');
        return _buildMockChart(question);
      }
      
      // 真实API调用
      print('🌐 ===== 开始调用真实AI API =====');
      final response = await _callMCPAPI(question);
      
      print('📊 ===== AI API响应结果 =====');
      print('📊 响应状态: ${response != null ? '成功' : '失败'}');
      print('📊 响应内容: $response');
      
      if (response != null && response['success'] == true) {
        final chartConfig = response['chart_config'] ?? {};
        final chartType = chartConfig['chart_type'] ?? 'table';
        final data = chartConfig['data'] ?? [];
        final sql = response['sql'] ?? '';
        final method = response['method'] ?? 'unknown';
        
        print('✅ ===== AI调用成功 =====');
        print('📈 图表类型: $chartType');
        print('📊 数据条数: ${data.length}');
        print('🔍 SQL查询: $sql');
        print('🤖 AI方法: $method');
        print('📊 数据预览: ${data.take(3).map((e) => '${e['label']}:${e['value']}').join(', ')}');
        
        return _buildRealChart(chartType, data, question, sql);
      } else {
        // API调用失败，返回错误信息
        final error = response?['error'] ?? '未知错误';
        final statusCode = response?['status_code'];
        print('❌ ===== AI调用失败 =====');
        print('❌ 错误信息: $error');
        print('❌ 状态码: $statusCode');
        print('❌ 完整响应: $response');
        return _buildErrorWidget(question, error);
      }
    } catch (e) {
      print('💥 ===== 图表生成异常 =====');
      print('💥 异常类型: ${e.runtimeType}');
      print('💥 异常信息: $e');
      print('💥 异常堆栈: ${StackTrace.current}');
      return _buildErrorWidget(question, '请求异常: $e');
    }
  }

  /// 调用MCP API
  static Future<Map<String, dynamic>?> _callMCPAPI(String question) async {
    try {
      print('🚀 ===== 开始调用MCP API =====');
      print('📍 API地址: $baseUrl/api/v1/mcp-smart-chart/generate');
      print('❓ 用户问题: $question');
      print('⏰ 请求时间: ${DateTime.now()}');
      print('🔍 网络诊断开始...');
      
      // 测试网络连接
      final uri = Uri.parse('$baseUrl/api/v1/mcp-smart-chart/generate');
      print('🔗 URI解析结果: $uri');
      print('🌐 主机: ${uri.host}');
      print('🔌 端口: ${uri.port}');
      print('📡 协议: ${uri.scheme}');
      
      // 尝试建立连接
      print('🔌 开始建立HTTP连接...');
      
      // 先尝试简单的GET请求测试连接
      try {
        print('🧪 测试连接性...');
        final testResponse = await http.get(Uri.parse('$baseUrl/health'));
        print('✅ 连接测试成功: ${testResponse.statusCode}');
        print('✅ 健康检查响应: ${testResponse.body}');
      } catch (e) {
        print('❌ 连接测试失败: $e');
        print('⚠️  但继续尝试主要API调用...');
      }
      
      print('📤 发送POST请求...');
      print('📤 请求体: ${jsonEncode({'question': question})}');
      
      final stopwatch = Stopwatch()..start();
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'question': question}),
      );
      stopwatch.stop();

      print('📡 ===== HTTP响应结果 =====');
      print('📡 响应状态码: ${response.statusCode}');
      print('📡 响应时间: ${stopwatch.elapsedMilliseconds}ms');
      print('📡 响应头: ${response.headers}');
      print('📄 响应内容: ${response.body}');

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        print('✅ ===== MCP API调用成功 =====');
        print('✅ 响应数据: $result');
        print('✅ 数据大小: ${response.body.length} 字符');
        return result;
      } else {
        print('❌ ===== MCP API调用失败 =====');
        print('❌ 状态码: ${response.statusCode}');
        print('❌ 错误响应: ${response.body}');
        print('❌ 响应头: ${response.headers}');
        return null;
      }
    } catch (e) {
      print('💥 ===== MCP API调用异常 =====');
      print('💥 异常类型: ${e.runtimeType}');
      print('💥 异常详情: ${e.toString()}');
      print('💥 异常堆栈: ${StackTrace.current}');
      
      // 如果是网络异常，提供更多诊断信息
      if (e.toString().contains('SocketException')) {
        print('🌐 ===== 网络诊断信息 =====');
        print('   - 尝试连接: $baseUrl');
        print('   - 可能原因: 网络权限、防火墙、端口被占用');
        print('   - 建议: 检查Flutter网络权限设置');
        print('   - 检查: 后端服务是否在8000端口运行');
      } else if (e.toString().contains('TimeoutException')) {
        print('⏰ ===== 超时诊断信息 =====');
        print('   - 请求超时，可能原因:');
        print('   - 1. 后端处理时间过长');
        print('   - 2. 网络延迟过高');
        print('   - 3. AI服务响应慢');
      }
      
      return null;
    }
  }

  /// 构建真实图表
  static Widget _buildRealChart(String chartType, List<dynamic> data, String question, String sql) {
    print('🔧 _buildRealChart 开始构建图表');
    print('📊 图表类型: $chartType');
    print('📈 数据条数: ${data.length}');
    print('❓ 问题: $question');
    
    Widget result;
    switch (chartType.toLowerCase()) {
      case 'pie':
        print('🥧 选择构建饼图组件');
        result = _buildRealPieChart(data, question);
        print('✅ 饼图组件构建完成');
        break;
      case 'bar':
        print('📊 选择构建柱状图组件');
        result = _buildRealBarChart(data, question);
        print('✅ 柱状图组件构建完成');
        break;
      case 'line':
        print('📈 选择构建折线图组件');
        result = _buildRealLineChart(data, question);
        print('✅ 折线图组件构建完成');
        break;
      case 'table':
      default:
        print('📋 选择构建表格组件');
        result = _buildRealTable(data, question, sql);
        print('✅ 表格组件构建完成');
        break;
    }
    
    print('🎯 最终返回的组件类型: ${result.runtimeType}');
    return result;
  }

  /// 构建真实饼图
  static Widget _buildRealPieChart(List<dynamic> data, String question) {
    print('🥧 _buildRealPieChart 开始构建饼图');
    print('📊 输入数据: $data');

    // 转换数据格式
    final chartData = data.map((item) {
      final label = item['label'] ?? item['platform'] ?? '未知';
      final value = (item['value'] ?? item['total_value'] ?? 0.0).toDouble();
      final color = _getRandomColor();
      final formattedValue = _formatValue(item['value'] ?? item['total_value'] ?? 0.0);
      
      print('  📝 转换数据项: label=$label, value=$value, color=$color');
      
      return CustomPieChartData(
        label: label,
        value: value,
        percentage: 0.0, // 稍后计算
        color: color,
        formattedValue: formattedValue,
      );
    }).toList();

    print('📊 转换后的图表数据: ${chartData.map((e) => '${e.label}:${e.value}').join(', ')}');

    // 计算百分比
    final total = chartData.fold(0.0, (sum, item) => sum + item.value);
    print('💰 数据总值: $total');
    
    final chartDataWithPercentage = chartData.map((item) {
      final percentage = total > 0 ? (item.value / total * 100) : 0.0;
      print('  📊 ${item.label}: ${item.value} / $total = ${percentage.toStringAsFixed(1)}%');
      
      return CustomPieChartData(
        label: item.label,
        value: item.value,
        percentage: percentage,
        color: item.color,
        formattedValue: item.formattedValue,
      );
    }).toList();

    print('🎨 开始构建缩略图组件');
    
    // 构建缩略图（聊天中显示）
    final result = Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题区域
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        question,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '基于真实数据生成',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // 缩略图区域
          Container(
            height: 200,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                // 饼图缩略图
                Expanded(
                  flex: 3,
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    child: PieChart(
                      PieChartData(
                        centerSpaceRadius: 20,
                        sectionsSpace: 1,
                        startDegreeOffset: -90,
                        sections: chartDataWithPercentage.asMap().entries.map((entry) {
                          final index = entry.key;
                          final data = entry.value;
                          final radius = 60.0;
                          
                          return PieChartSectionData(
                            color: data.color,
                            value: data.value,
                            title: '${data.percentage.toStringAsFixed(1)}%',
                            radius: radius,
                            titleStyle: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                              shadows: [
                                Shadow(
                                  color: Colors.black54,
                                  blurRadius: 2,
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ),
                ),
                
                // 图例缩略图
                if (chartDataWithPercentage.isNotEmpty) ...[
                  const SizedBox(width: 16),
                  Expanded(
                    flex: 2,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: chartDataWithPercentage.take(3).map((item) => Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          children: [
                            Container(
                              width: 12,
                              height: 12,
                              decoration: BoxDecoration(
                                color: item.color,
                                borderRadius: BorderRadius.circular(6),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                item.label,
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w500,
                                  color: Colors.black87,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      )).toList(),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
    
    print('✅ 缩略图组件构建完成');
    print('🎯 _buildRealPieChart 返回组件类型: ${result.runtimeType}');
    
    // 将数据存储到全局变量中，供后续使用
    _lastChartData = data;
    _lastChartDataWithPercentage = chartDataWithPercentage;
    
    return result;
  }

  /// 构建全屏饼图组件
  static Widget buildFullscreenPieChart(List<CustomPieChartData> data, String question) {
    return PieChart(
      PieChartData(
        centerSpaceRadius: 20, // 减少中心空间，适合更扁的布局
        sectionsSpace: 0.8, // 减少切片间距
        startDegreeOffset: -90,
        sections: data.asMap().entries.map((entry) {
      final index = entry.key;
      final item = entry.value;
          final radius = 50.0; // 减少半径，确保在200px高度内显示
          
          return PieChartSectionData(
            color: item.color,
            value: item.value,
            title: '${item.percentage.toStringAsFixed(1)}%',
            radius: radius,
            titleStyle: const TextStyle(
              fontSize: 10, // 减小字体大小
              fontWeight: FontWeight.w600,
              color: Colors.white,
              shadows: [
                Shadow(
                  color: Colors.black54,
                  blurRadius: 2,
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
  
  /// 构建操作按钮
  static Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建真实柱状图
  static Widget _buildRealBarChart(List<dynamic> data, String question) {
    print('📊 _buildRealBarChart 开始构建柱状图');
    print('📊 输入数据: $data');
    
    final chartData = data.map((item) {
      final label = item['label'] ?? item['platform'] ?? '未知';
      final value = (item['value'] ?? item['total_value'] ?? 0.0).toDouble();
      final color = _getRandomColor();
      final formattedValue = _formatValue(item['value'] ?? item['total_value'] ?? 0.0);
      
      print('  📝 转换数据项: label=$label, value=$value, color=$color');
      
      return CustomBarChartData(
        label: label,
        value: value,
        color: color,
        formattedValue: formattedValue,
      );
    }).toList();

    print('📊 转换后的图表数据: ${chartData.map((e) => '${e.label}:${e.value}').join(', ')}');

    print('🎨 开始构建ProfessionalBarChart组件');
    final barChart = ProfessionalBarChart(
      data: chartData,
      title: '数据对比',
      subtitle: '各平台资产价值分析',
      showValues: true,
    );
    print('✅ ProfessionalBarChart组件构建完成');

    print('📦 开始构建StandardChartContainer');
    final result = StandardChartContainer(
      title: question,
      subtitle: '基于真实数据生成',
      child: barChart,
    );
    print('✅ StandardChartContainer构建完成');
    
    print('🎯 _buildRealBarChart 返回组件类型: ${result.runtimeType}');
    return result;
  }

  /// 构建真实折线图
  static Widget _buildRealLineChart(List<dynamic> data, String question) {
    final chartData = data.map((item) {
      return CustomLineChartData(
        label: item['label'] ?? item['date'] ?? '未知',
        value: (item['value'] ?? item['total_value'] ?? 0.0).toDouble(),
        formattedValue: _formatValue(item['value'] ?? item['total_value'] ?? 0.0),
      );
    }).toList();

    return StandardChartContainer(
      title: question,
      subtitle: '基于真实数据生成',
      child: ProfessionalLineChart(
      data: chartData,
        title: '趋势分析',
        subtitle: '资产价值变化趋势',
        showValues: true,
      ),
    );
  }

  /// 构建真实表格
  static Widget _buildRealTable(List<dynamic> data, String question, String sql) {
    return StandardChartContainer(
      title: question,
      subtitle: '基于真实数据生成',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 数据概览
          Row(
            children: [
              Expanded(
                child: _buildDataCard(
                  '数据条数',
                  '${data.length}',
                  const Color(0xFF10B981),
                  Icons.analytics,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildDataCard(
                  '查询方式',
                  'DeepSeek AI',
                  const Color(0xFF3B82F6),
                  Icons.psychology,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // 数据表格
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[200]!),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                // 表头
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[50],
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                  ),
                  child: Row(
                    children: [
                      Expanded(flex: 2, child: Text('平台/类型', style: TextStyle(fontWeight: FontWeight.bold))),
                      Expanded(flex: 1, child: Text('数值', style: TextStyle(fontWeight: FontWeight.bold))),
                      Expanded(flex: 1, child: Text('详情', style: TextStyle(fontWeight: FontWeight.bold))),
                    ],
                  ),
                ),
                // 数据行
                ...data.take(5).map((item) => Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: Border(top: BorderSide(color: Colors.grey[200]!)),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: Text(
                          item['platform'] ?? item['label'] ?? '未知',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ),
                      Expanded(
                        flex: 1,
                        child: Text(
                          _formatValue(item['total_value'] ?? item['value'] ?? 0.0),
                          style: TextStyle(
                            color: Colors.green[700],
        fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      Expanded(
                        flex: 1,
                        child: Text(
                          item['asset_count']?.toString() ?? '1项',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ),
                    ],
                  ),
                )).toList(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建错误组件
  static Widget _buildErrorWidget(String question, String error) {
    return StandardChartContainer(
      title: '查询失败',
      subtitle: '请检查问题描述或稍后重试',
        child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
          children: [
          Row(
            children: [
              Icon(Icons.error_outline, color: ChartDesignSystem.danger, size: 20),
              const SizedBox(width: 8),
            Text(
                question,
              style: ChartDesignSystem.subtitleStyle,
              ),
            ],
            ),
            const SizedBox(height: 8),
            Text(
            '错误信息: $error',
              style: ChartDesignSystem.labelStyle.copyWith(
              color: ChartDesignSystem.danger,
              ),
            ),
          ],
      ),
    );
  }

  /// 构建模拟图表（当API不可用时）
  static Widget _buildMockChart(String question) {
    final questionLower = question.toLowerCase();
    
    if (questionLower.contains('分布') || questionLower.contains('占比')) {
      return _buildMockPieChart(question);
    } else if (questionLower.contains('趋势') || questionLower.contains('变化')) {
      return _buildMockLineChart(question);
    } else if (questionLower.contains('对比') || questionLower.contains('排行')) {
      return _buildMockBarChart(question);
    } else {
      return _buildMockTable(question);
    }
  }

  /// 构建模拟饼图
  static Widget _buildMockPieChart(String question) {
    final mockData = [
      CustomPieChartData(
        label: 'OKX',
        value: 10.0,
        percentage: 52.6,
        color: const Color(0xFF10B981),
        formattedValue: '¥7,437.49',
      ),
      CustomPieChartData(
        label: 'Wise',
        value: 7.0,
        percentage: 36.8,
        color: const Color(0xFF3B82F6),
        formattedValue: '¥9,996.29',
      ),
      CustomPieChartData(
        label: '支付宝',
        value: 1.0,
        percentage: 5.3,
        color: const Color(0xFFF59E0B),
        formattedValue: '¥0.00',
      ),
      CustomPieChartData(
        label: 'test',
        value: 1.0,
        percentage: 5.3,
        color: const Color(0xFFEF4444),
        formattedValue: '¥0.00',
      ),
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题和图标
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF10B981).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.pie_chart,
                  color: Color(0xFF10B981),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                '资产分布分析',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // 迷你饼图
          SizedBox(
            height: 120,
            child: Row(
              children: [
                // 饼图
                Expanded(
                  flex: 2,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      SizedBox(
                        width: 80,
                        height: 80,
                        child: CustomPaint(
                          painter: _MiniPieChartPainter(mockData),
                        ),
                      ),
                      const Text(
                        '4',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF10B981),
                        ),
                      ),
                    ],
                  ),
                ),
                // 图例
                Expanded(
                  flex: 3,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: mockData.take(3).map((item) => _buildLegendItem(item)).toList(),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 总计
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF10B981).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '总资产',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF10B981),
                  ),
                ),
                Text(
                  '¥17,433.78',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.green[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建图例项
  static Widget _buildLegendItem(CustomPieChartData data) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: data.color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              data.label,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Text(
            '${data.percentage.toStringAsFixed(1)}%',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: data.color,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建模拟柱状图
  static Widget _buildMockBarChart(String question) {
    final mockData = [
      CustomBarChartData(
        label: 'OKX',
        value: 7437.49,
        color: const Color(0xFF10B981),
        formattedValue: '¥7,437.49',
      ),
      CustomBarChartData(
        label: 'Wise',
        value: 9996.29,
        color: const Color(0xFF3B82F6),
        formattedValue: '¥9,996.29',
      ),
      CustomBarChartData(
        label: '支付宝',
        value: 0.0,
        color: const Color(0xFFF59E0B),
        formattedValue: '¥0.00',
      ),
      CustomBarChartData(
        label: 'test',
        value: 0.0,
        color: const Color(0xFFEF4444),
        formattedValue: '¥0.00',
      ),
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题和图标
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF3B82F6).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.bar_chart,
                  color: Color(0xFF3B82F6),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                '平台对比分析',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // 迷你柱状图
          SizedBox(
            height: 120,
            child: Row(
              children: [
                // 柱状图
                Expanded(
                  flex: 3,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: mockData.map((item) => _buildMiniBar(item)).toList(),
                  ),
                ),
                // 图例
                Expanded(
                  flex: 2,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: mockData.take(3).map((item) => _buildBarLegendItem(item)).toList(),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 总计
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF3B82F6).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '总资产',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF3B82F6),
                  ),
                ),
                Text(
                  '¥17,433.78',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建迷你柱状图
  static Widget _buildMiniBar(CustomBarChartData data) {
    final maxValue = 10000.0; // 最大值
    final height = (data.value / maxValue) * 60; // 60是最大高度
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        Container(
          width: 20,
          height: height > 0 ? height : 4,
          decoration: BoxDecoration(
            color: data.value > 0 ? data.color : Colors.grey[300],
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          data.label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w500,
            color: data.value > 0 ? const Color(0xFF1F2937) : Colors.grey[500],
          ),
        ),
      ],
    );
  }

  /// 构建柱状图图例项
  static Widget _buildBarLegendItem(CustomBarChartData data) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: data.value > 0 ? data.color : Colors.grey[300],
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              data.label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: data.value > 0 ? const Color(0xFF1F2937) : Colors.grey[500],
              ),
            ),
          ),
          Text(
            data.value > 0 ? '¥${(data.value / 1000).toStringAsFixed(1)}k' : '¥0',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: data.value > 0 ? data.color : Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建模拟折线图
  static Widget _buildMockLineChart(String question) {
    final mockData = [
      CustomLineChartData(
        label: '1月',
        value: 15000.0,
        formattedValue: '¥15,000',
      ),
      CustomLineChartData(
        label: '2月',
        value: 16500.0,
        formattedValue: '¥16,500',
      ),
      CustomLineChartData(
        label: '3月',
        value: 17437.49,
        formattedValue: '¥17,437.49',
      ),
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题和图标
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF8B5CF6).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.trending_up,
                  color: Color(0xFF8B5CF6),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                '资产变化趋势',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // 迷你折线图
          SizedBox(
            height: 120,
            child: Row(
              children: [
                // 折线图
                Expanded(
                  flex: 3,
                  child: CustomPaint(
                    painter: _MiniLineChartPainter(mockData),
                    size: const Size(double.infinity, 80),
                  ),
                ),
                // 图例
                Expanded(
                  flex: 2,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: mockData.map((item) => _buildLineLegendItem(item)).toList(),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 趋势信息
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF8B5CF6).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '增长趋势',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF8B5CF6),
                  ),
                ),
                Row(
                  children: [
                    const Icon(
                      Icons.trending_up,
                      color: Colors.green,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '+16.3%',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[700],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建模拟数据表格
  static Widget _buildMockTable(String question) {
    final mockData = [
      {
        'platform': 'OKX',
        'total_value': 7437.49,
        'asset_count': 10,
      },
      {
        'platform': 'Wise',
        'total_value': 9996.29,
        'asset_count': 7,
      },
      {
        'platform': '支付宝',
        'total_value': 0.0,
        'asset_count': 1,
      },
      {
        'platform': 'test',
        'total_value': 0.0,
        'asset_count': 1,
      },
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题和图标
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF10B981).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.analytics,
                  color: Color(0xFF10B981),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                '数据分析结果',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // 数据概览卡片
          Row(
            children: [
              Expanded(
                child: _buildDataCard(
                  '总资产',
                  '¥17,433.78',
                  const Color(0xFF10B981),
                  Icons.account_balance_wallet,
                ),
              ),
              const SizedBox(width: 12),
              // 平台数量卡片
              Container(
                width: 120, // 固定宽度避免溢出
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFE0F2FE),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.business,
                          size: 16,
                          color: Colors.blue[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '平台数量',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.blue[700],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '4',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[800],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // 平台分布
          const Text(
            '平台分布',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 8),
          
          // 平台列表
          ...mockData.map((item) => _buildPlatformRow(
            item['platform'] as String,
            item['total_value'] as double,
            item['asset_count'] as int,
          )),
        ],
      ),
    );
  }

  /// 构建数据卡片
  static Widget _buildDataCard(String title, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  color: color.withOpacity(0.8),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建平台行
  static Widget _buildPlatformRow(String platform, double value, int count) {
    final isActive = value > 0;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isActive ? Colors.green.withOpacity(0.05) : Colors.grey.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isActive ? Colors.green.withOpacity(0.2) : Colors.grey.withOpacity(0.2),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: isActive ? Colors.green : Colors.grey,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              platform,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: isActive ? const Color(0xFF1F2937) : Colors.grey[600],
              ),
            ),
          ),
          Text(
            '¥${value.toStringAsFixed(0)}',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: isActive ? Colors.green[700] : Colors.grey[600],
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: isActive ? Colors.green.withOpacity(0.1) : Colors.grey.withOpacity(0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              '$count项',
              style: TextStyle(
                fontSize: 12,
                color: isActive ? Colors.green[700] : Colors.grey[600],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 推断图表标题
  static String _inferTitle(String question) {
    if (question.contains('分布')) {
      return '资产分布分析';
    } else if (question.contains('趋势')) {
      return '资产变化趋势';
    } else if (question.contains('对比')) {
      return '平台对比分析';
    } else if (question.contains('排行')) {
      return '资产排行分析';
    } else {
      return '数据分析结果';
    }
  }

  /// 获取随机颜色
  static Color _getRandomColor() {
    final colors = [
      const Color(0xFF10B981), // 绿色
      const Color(0xFF3B82F6), // 蓝色
      const Color(0xFF8B5CF6), // 紫色
      const Color(0xFFF59E0B), // 黄色
      const Color(0xFFEF4444), // 红色
      const Color(0xFF06B6D4), // 青色
    ];
    return colors[DateTime.now().millisecond % colors.length];
  }

  /// 判断趋势是否为正
  static bool _isPositiveTrend(List<CustomLineChartData> data) {
    if (data.length < 2) return false;
    
    final firstValue = data.first.value;
    final lastValue = data.last.value;
    
    return lastValue > firstValue;
  }

  /// 构建迷你饼图
  static Widget _buildMiniPieChart(List<CustomPieChartData> data) {
    return Container(
      width: 80,
      height: 80,
      child: CustomPaint(
        painter: _MiniPieChartPainter(data),
      ),
    );
  }



  /// 构建迷你折线图
  static Widget _buildMiniLine(List<CustomLineChartData> data) {
    return Container(
      width: 80,
      height: 60,
      child: CustomPaint(
        painter: _MiniLineChartPainter(data),
      ),
    );
  }

  /// 格式化数值
  static String _formatValue(dynamic value) {
    final numValue = value is num ? value : 0.0;
    if (numValue >= 10000) {
      return '¥${(numValue / 10000).toStringAsFixed(2)}万';
    } else if (numValue >= 1000) {
      return '¥${numValue.toStringAsFixed(0)}';
    } else {
      return '¥${numValue.toStringAsFixed(2)}';
    }
  }
}

/// 图表主题配置
class ChartThemeConfig {
  static const double borderRadius = 20;
  static const double cardElevation = 8;
  static const EdgeInsets chartPadding = EdgeInsets.all(16);
  static const EdgeInsets titlePadding = EdgeInsets.fromLTRB(24, 20, 20, 16);
  
  // 动画配置
  static const Duration animationDuration = Duration(milliseconds: 300);
  static const Curve animationCurve = Curves.easeInOut;
  
  // 响应式配置
  static double getChartHeight(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;
    return screenHeight * 0.35; // 35% of screen height
  }
  
  static bool isTablet(BuildContext context) {
    return MediaQuery.of(context).size.width > 600;
  }
}

/// 图表状态管理
class ChartState {
  final bool isLoading;
  final String? error;
  final Widget? chart;
  
  const ChartState({
    this.isLoading = false,
    this.error,
    this.chart,
  });
  
  ChartState copyWith({
    bool? isLoading,
    String? error,
    Widget? chart,
  }) {
    return ChartState(
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      chart: chart ?? this.chart,
    );
  }
}

/// 迷你饼图绘制器
class _MiniPieChartPainter extends CustomPainter {
  final List<CustomPieChartData> data;

  _MiniPieChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // 计算总和
    final totalValue = data.fold(0.0, (sum, item) => sum + item.value);

    // 绘制饼图
    var startAngle = -pi / 2; // 从顶部开始
    for (var i = 0; i < data.length; i++) {
      final item = data[i];
      final sweepAngle = (item.value / totalValue) * 2 * pi;

      final paint = Paint()
        ..color = item.color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 10
        ..strokeCap = StrokeCap.round;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        false,
        paint,
      );

      startAngle += sweepAngle;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}

/// 迷你折线图绘制器
class _MiniLineChartPainter extends CustomPainter {
  final List<CustomLineChartData> data;

  _MiniLineChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // 计算总和
    final totalValue = data.fold(0.0, (sum, item) => sum + item.value);

    // 绘制折线图
    final path = Path();
    final firstPoint = Offset(0, size.height - (data.first.value / totalValue) * radius * 2);
    path.moveTo(firstPoint.dx, firstPoint.dy);

    for (var i = 1; i < data.length; i++) {
      final item = data[i];
      final point = Offset(size.width * (i / (data.length - 1)), size.height - (item.value / totalValue) * radius * 2);
      path.lineTo(point.dx, point.dy);
    }

    final paint = Paint()
      ..color = const Color(0xFF8B5CF6)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}



/// 构建折线图图例项
Widget _buildLineLegendItem(CustomLineChartData data) {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 2),
    child: Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: const Color(0xFF8B5CF6),
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            data.label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: Color(0xFF1F2937),
            ),
          ),
        ),
        Text(
          data.formattedValue,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: Color(0xFF8B5CF6),
          ),
        ),
      ],
    ),
  );
}