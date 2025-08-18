import 'package:flutter/material.dart';
import 'chart_design_system.dart';
import 'dart:convert';
import 'dart:math';
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
    // 转换数据格式
    final chartData = rawData.map((item) {
      final name = item['name']?.toString() ?? '未知';
      final value = (item['value'] ?? 0.0).toDouble();
      final totalValue = (item['total_value'] ?? 0.0).toDouble();
      
      return CustomPieChartData(
        label: name,
        value: value,
        percentage: value,
        color: _getRandomColor(name),
        formattedValue: totalValue > 0 ? '¥${totalValue.toStringAsFixed(2)}' : '¥0.00',
      );
    }).toList();

    return ProfessionalPieChart(
      data: chartData,
      title: title,
      subtitle: subtitle,
      showValues: true,
      showLegend: true,
    );
  }

  /// 构建专业柱状图
  static Widget _buildProfessionalBarChart(List<dynamic> rawData, String title, String? subtitle) {
    // 转换数据格式
    final chartData = rawData.map((item) {
      final name = item['name']?.toString() ?? '未知';
      final value = (item['value'] ?? 0.0).toDouble();
      final totalValue = (item['total_value'] ?? 0.0).toDouble();
      
      return CustomBarChartData(
        label: name,
        value: value,
        color: _getRandomColor(name),
        formattedValue: totalValue > 0 ? '¥${totalValue.toStringAsFixed(2)}' : '¥0.00',
      );
    }).toList();

    return ProfessionalBarChart(
      data: chartData,
      title: title,
      subtitle: subtitle,
      showValues: true,
      showGrid: true,
    );
  }

  /// 构建专业折线图
  static Widget _buildProfessionalLineChart(List<dynamic> rawData, String title, String? subtitle) {
    // 转换数据格式
    final chartData = rawData.asMap().entries.map((entry) {
      final index = entry.key;
      final item = entry.value;
      final name = item['name']?.toString() ?? '未知';
      final value = (item['value'] ?? 0.0).toDouble();
      final totalValue = (item['total_value'] ?? 0.0).toDouble();
      
      return CustomLineChartData(
        label: name,
        value: value,
        formattedValue: totalValue > 0 ? '¥${totalValue.toStringAsFixed(2)}' : '¥0.00',
      );
    }).toList();

    return ProfessionalLineChart(
      data: chartData,
      title: title,
      subtitle: subtitle,
      showValues: true,
      showGrid: true,
      showArea: true,
    );
  }

  /// 构建专业数据表格
  static Widget _buildProfessionalTable(List<dynamic> rawData, String title, String? subtitle) {
    return StandardChartContainer(
      title: title,
      subtitle: subtitle,
      child: _buildDataTable(rawData),
    );
  }

  /// 构建数据表格
  static Widget _buildDataTable(List<dynamic> rawData) {
    if (rawData.isEmpty) {
      return const Center(
        child: Text('暂无数据'),
      );
    }

    // 推断列结构
    final columns = _inferTableColumns(rawData);
    
    return DataTable(
      headingRowColor: MaterialStateProperty.all(Colors.grey[50]),
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
          color: MaterialStateProperty.all(
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
  static Color _getRandomColor(String seed) {
    final colors = [
      const Color(0xFF10B981),
      const Color(0xFF3B82F6),
      const Color(0xFFF59E0B),
      const Color(0xFFEF4444),
      const Color(0xFF8B5CF6),
      const Color(0xFF14B8A6),
      const Color(0xFFEC4899),
    ];
    
    final index = seed.hashCode.abs() % colors.length;
    return colors[index];
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