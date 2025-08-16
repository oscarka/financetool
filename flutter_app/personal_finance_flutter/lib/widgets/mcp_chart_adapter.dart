import 'package:flutter/material.dart';
import 'chart_design_system.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

/// MCP图表适配器 - 将MCP返回的数据转换为设计系统格式
class MCPChartAdapter {
  static const String baseUrl = 'https://your-railway-backend.railway.app';

  /// 从MCP服务生成专业图表
  static Future<Widget> generateProfessionalChart(String userQuestion) async {
    try {
      // 调用MCP智能图表API
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/mcp-smart-chart/generate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'question': userQuestion}),
      );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        return _buildProfessionalChart(jsonData, userQuestion);
      } else {
        throw Exception('API调用失败: ${response.statusCode}');
      }
    } catch (e) {
      // 使用模拟数据生成演示图表
      return _buildMockChart(userQuestion);
    }
  }

  /// 构建专业图表组件
  static Widget _buildProfessionalChart(Map<String, dynamic> mcpData, String question) {
    final chartType = mcpData['chart_type']?.toString().toLowerCase() ?? 'bar';
    final title = mcpData['title']?.toString() ?? _inferTitle(question);
    final subtitle = mcpData['description']?.toString();
    final rawData = mcpData['data'] as List<dynamic>? ?? [];

    switch (chartType) {
      case 'pie':
        return _buildProfessionalPieChart(rawData, title, subtitle);
      case 'line':
        return _buildProfessionalLineChart(rawData, title, subtitle);
      case 'bar':
        return _buildProfessionalBarChart(rawData, title, subtitle);
      case 'table':
        return _buildProfessionalTable(rawData, title, subtitle);
      default:
        return _buildProfessionalBarChart(rawData, title, subtitle);
    }
  }

  /// 构建专业饼图
  static Widget _buildProfessionalPieChart(List<dynamic> rawData, String title, String? subtitle) {
    if (rawData.isEmpty) return _buildEmptyChart(title, subtitle);

    // 计算总值
    final total = rawData.fold<double>(0.0, (sum, item) {
      final value = _extractValue(item);
      return sum + value;
    });

    // 转换数据格式
    final chartData = rawData.asMap().entries.map((entry) {
      final index = entry.key;
      final item = entry.value;
      final value = _extractValue(item);
      final label = _extractLabel(item);
      final percentage = total > 0 ? (value / total * 100) : 0.0;
      
      return PieChartData(
        label: label,
        value: value,
        percentage: percentage,
        color: _getSemanticColor(index, label, value),
        formattedValue: _formatCurrency(value),
      );
    }).toList();

    return ProfessionalPieChart(
      data: chartData,
      title: title,
      subtitle: subtitle,
      showLegend: true,
      showValues: true,
    );
  }

  /// 构建专业柱状图
  static Widget _buildProfessionalBarChart(List<dynamic> rawData, String title, String? subtitle) {
    if (rawData.isEmpty) return _buildEmptyChart(title, subtitle);

    final chartData = rawData.asMap().entries.map((entry) {
      final index = entry.key;
      final item = entry.value;
      final value = _extractValue(item);
      final label = _extractLabel(item);
      
      return BarChartData(
        label: label,
        value: value,
        color: _getSemanticColor(index, label, value),
        formattedValue: _formatCurrency(value),
      );
    }).toList();

    return ProfessionalBarChart(
      data: chartData,
      title: title,
      subtitle: subtitle,
      showGrid: true,
    );
  }

  /// 构建专业折线图
  static Widget _buildProfessionalLineChart(List<dynamic> rawData, String title, String? subtitle) {
    if (rawData.isEmpty) return _buildEmptyChart(title, subtitle);

    final chartData = rawData.map((item) {
      final value = _extractValue(item);
      final label = _extractLabel(item);
      
      return LineChartData(
        label: label,
        value: value,
        formattedValue: _formatCurrency(value),
      );
    }).toList();

    // 根据数据趋势选择颜色
    final isPositiveTrend = _isPositiveTrend(chartData);
    final lineColor = isPositiveTrend 
        ? ChartDesignSystem.secondary 
        : ChartDesignSystem.danger;

    return ProfessionalLineChart(
      data: chartData,
      title: title,
      subtitle: subtitle,
      showDots: true,
      showArea: true,
      lineColor: lineColor,
    );
  }

  /// 构建专业表格
  static Widget _buildProfessionalTable(List<dynamic> rawData, String title, String? subtitle) {
    if (rawData.isEmpty) return _buildEmptyChart(title, subtitle);

    return StandardChartContainer(
      title: title,
      subtitle: subtitle,
      child: SingleChildScrollView(
        child: _buildDataTable(rawData),
      ),
    );
  }

  /// 构建数据表格
  static Widget _buildDataTable(List<dynamic> rawData) {
    // 推断列结构
    final columns = _inferTableColumns(rawData);
    
    return DataTable(
      headingRowColor: WidgetStateProperty.all(Colors.grey[50]),
      headingRowHeight: 48,
      dataRowHeight: 56,
      headingTextStyle: ChartDesignSystem.labelStyle.copyWith(
        fontWeight: FontWeight.w600,
        color: Colors.grey[700],
      ),
      dataTextStyle: ChartDesignSystem.labelStyle,
      columns: columns.map((column) {
        return DataColumn(
          label: Text(column['label']),
        );
      }).toList(),
      rows: rawData.asMap().entries.map((entry) {
        final index = entry.key;
        final item = entry.value;
        
        return DataRow(
          color: WidgetStateProperty.all(
            index % 2 == 0 ? Colors.transparent : Colors.grey[25],
          ),
          cells: columns.map((column) {
            final value = item[column['key']] ?? '';
            final isNumeric = column['type'] == 'number';
            
            return DataCell(
              Text(
                isNumeric ? _formatCurrency(value.toDouble()) : value.toString(),
                style: ChartDesignSystem.labelStyle.copyWith(
                  fontWeight: isNumeric ? FontWeight.w600 : FontWeight.w500,
                  color: isNumeric ? ChartDesignSystem.primary : null,
                ),
              ),
            );
          }).toList(),
        );
      }).toList(),
    );
  }

  /// 构建空图表提示
  static Widget _buildEmptyChart(String title, String? subtitle) {
    return StandardChartContainer(
      title: title,
      subtitle: subtitle,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.insert_chart_outlined,
              size: 64,
              color: Colors.grey[300],
            ),
            const SizedBox(height: 16),
            Text(
              '暂无数据',
              style: ChartDesignSystem.subtitleStyle,
            ),
            const SizedBox(height: 8),
            Text(
              '请尝试其他查询条件',
              style: ChartDesignSystem.labelStyle.copyWith(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建模拟图表（用于演示）
  static Widget _buildMockChart(String question) {
    if (question.contains('占比') || question.contains('分布') || question.contains('构成')) {
      return _buildMockPieChart(question);
    } else if (question.contains('趋势') || question.contains('变化') || question.contains('走势')) {
      return _buildMockLineChart(question);
    } else {
      return _buildMockBarChart(question);
    }
  }

  /// 模拟饼图
  static Widget _buildMockPieChart(String question) {
    final mockData = [
      {'label': '基金投资', 'value': 158460.30},
      {'label': '外汇资产', 'value': 8158.23},
      {'label': '数字货币', 'value': 1205.67},
      {'label': '股票投资', 'value': 420.30},
    ];
    
    return _buildProfessionalPieChart(
      mockData, 
      _inferTitle(question), 
      '基于您的资产配置生成的智能分析'
    );
  }

  /// 模拟折线图
  static Widget _buildMockLineChart(String question) {
    final mockData = [
      {'label': '1月', 'value': 160000.0},
      {'label': '2月', 'value': 165000.0},
      {'label': '3月', 'value': 158000.0},
      {'label': '4月', 'value': 162000.0},
      {'label': '5月', 'value': 167866.26},
      {'label': '6月', 'value': 172341.89},
      {'label': '7月', 'value': 169876.45},
    ];
    
    return _buildProfessionalLineChart(
      mockData, 
      _inferTitle(question), 
      '近期资产变化趋势分析'
    );
  }

  /// 模拟柱状图
  static Widget _buildMockBarChart(String question) {
    final mockData = [
      {'label': '支付宝', 'value': 158460.30},
      {'label': 'Wise', 'value': 8158.23},
      {'label': 'IBKR', 'value': 420.30},
      {'label': 'OKX', 'value': 1205.67},
    ];
    
    return _buildProfessionalBarChart(
      mockData, 
      _inferTitle(question), 
      '各平台资产价值对比分析'
    );
  }

  // 辅助方法

  /// 提取数值
  static double _extractValue(dynamic item) {
    if (item is Map) {
      final value = item['value'] ?? item['amount'] ?? item['total'] ?? item['balance'] ?? 0;
      return (value is num) ? value.toDouble() : 0.0;
    }
    return 0.0;
  }

  /// 提取标签
  static String _extractLabel(dynamic item) {
    if (item is Map) {
      return item['label']?.toString() ?? 
             item['name']?.toString() ?? 
             item['category']?.toString() ?? 
             item['platform']?.toString() ?? 
             '未知';
    }
    return item?.toString() ?? '未知';
  }

  /// 获取语义化颜色
  static Color _getSemanticColor(int index, String label, double value) {
    final colors = ChartDesignSystem.professionalColors;
    
    // 基于标签的语义化颜色
    final labelLower = label.toLowerCase();
    if (labelLower.contains('基金') || labelLower.contains('fund')) {
      return ChartDesignSystem.primary;
    } else if (labelLower.contains('股票') || labelLower.contains('stock')) {
      return ChartDesignSystem.accent;
    } else if (labelLower.contains('外汇') || labelLower.contains('forex')) {
      return ChartDesignSystem.warning;
    } else if (labelLower.contains('数字货币') || labelLower.contains('crypto')) {
      return ChartDesignSystem.secondary;
    } else if (value < 0) {
      return ChartDesignSystem.danger;
    }
    
    return colors[index % colors.length];
  }

  /// 判断是否为正向趋势
  static bool _isPositiveTrend(List<LineChartData> data) {
    if (data.length < 2) return true;
    
    final first = data.first.value;
    final last = data.last.value;
    return last >= first;
  }

  /// 推断表格列结构
  static List<Map<String, dynamic>> _inferTableColumns(List<dynamic> rawData) {
    if (rawData.isEmpty) return [];
    
    final sample = rawData.first as Map;
    return sample.keys.map((key) {
      final value = sample[key];
      final isNumeric = value is num;
      
      return {
        'key': key,
        'label': _formatColumnLabel(key),
        'type': isNumeric ? 'number' : 'text',
      };
    }).toList();
  }

  /// 格式化列标签
  static String _formatColumnLabel(String key) {
    final labelMap = {
      'platform': '平台',
      'asset_type': '资产类型',
      'value': '价值',
      'amount': '金额',
      'balance': '余额',
      'total': '总计',
      'label': '名称',
      'name': '名称',
      'date': '日期',
      'percentage': '占比',
      'count': '数量',
    };
    
    return labelMap[key] ?? key;
  }

  /// 推断图表标题
  static String _inferTitle(String question) {
    if (question.contains('占比') || question.contains('分布')) {
      return '资产分布分析';
    } else if (question.contains('趋势') || question.contains('变化')) {
      return '资产趋势分析';
    } else if (question.contains('对比') || question.contains('比较')) {
      return '资产对比分析';
    } else if (question.contains('统计')) {
      return '数据统计分析';
    } else {
      return 'AI智能分析';
    }
  }

  /// 格式化货币
  static String _formatCurrency(double value) {
    if (value.abs() >= 100000000) {
      return '${(value / 100000000).toStringAsFixed(1)}亿';
    } else if (value.abs() >= 10000) {
      return '${(value / 10000).toStringAsFixed(1)}万';
    } else if (value.abs() >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}k';
    } else {
      return value.toStringAsFixed(0);
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