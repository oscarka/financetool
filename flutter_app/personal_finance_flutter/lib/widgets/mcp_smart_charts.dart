import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

/// MCP智能图表数据模型
class ChartConfig {
  final String chartType;
  final String title;
  final String description;
  final List<dynamic> data;
  final Map<String, dynamic> style;
  final String? xAxis;
  final String? yAxis;

  ChartConfig({
    required this.chartType,
    required this.title,
    required this.description,
    required this.data,
    required this.style,
    this.xAxis,
    this.yAxis,
  });

  factory ChartConfig.fromJson(Map<String, dynamic> json) {
    return ChartConfig(
      chartType: json['chart_type'] ?? 'bar',
      title: json['title'] ?? '未知图表',
      description: json['description'] ?? '',
      data: json['data'] ?? [],
      style: json['style'] ?? {},
      xAxis: json['x_axis'],
      yAxis: json['y_axis'],
    );
  }
}

/// MCP智能图表服务
class MCPChartService {
  static const String baseUrl = 'https://your-railway-backend.railway.app';
  
  /// 调用MCP智能图表API生成图表
  static Future<ChartConfig> generateChart(String userQuestion) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/mcp-smart-chart/generate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'question': userQuestion}),
      );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        return ChartConfig.fromJson(jsonData);
      } else {
        throw Exception('API调用失败: ${response.statusCode}');
      }
    } catch (e) {
      // 返回模拟数据用于演示
      return _getMockChartConfig(userQuestion);
    }
  }

  /// 获取示例问题列表
  static Future<List<String>> getExampleQuestions() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/mcp-smart-chart/examples'),
      );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        return List<String>.from(jsonData['examples'] ?? []);
      }
    } catch (e) {
      // 返回默认示例
    }
    
    return [
      '显示各平台的资产分布',
      '各资产类型的占比',
      '最近30天的资产变化趋势',
      '最近的交易统计',
      '收益率最高的投资',
      '手续费支出统计',
      '定投计划执行情况',
    ];
  }

  /// 模拟数据生成器（用于演示）
  static ChartConfig _getMockChartConfig(String question) {
    if (question.contains('占比') || question.contains('分布')) {
      return ChartConfig(
        chartType: 'pie',
        title: '资产类型分布',
        description: '各类资产占比分析',
        data: [
          {'name': '基金', 'value': 158460.30, 'label': '基金'},
          {'name': '外汇', 'value': 8158.23, 'label': '外汇'},
          {'name': '数字货币', 'value': 1205.67, 'label': '数字货币'},
          {'name': '股票', 'value': 420.30, 'label': '股票'},
        ],
        style: {
          'colors': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
          'animation': true,
        },
      );
    } else if (question.contains('趋势') || question.contains('变化')) {
      return ChartConfig(
        chartType: 'line',
        title: '资产变化趋势',
        description: '最近30天资产价值变化',
        data: [
          {'name': '1月1日', 'value': 160000.0, 'label': '1月1日'},
          {'name': '1月2日', 'value': 165000.0, 'label': '1月2日'},
          {'name': '1月3日', 'value': 158000.0, 'label': '1月3日'},
          {'name': '1月4日', 'value': 162000.0, 'label': '1月4日'},
          {'name': '1月5日', 'value': 167866.26, 'label': '1月5日'},
        ],
        style: {
          'colors': ['#10B981'],
          'animation': true,
        },
      );
    } else {
      return ChartConfig(
        chartType: 'bar',
        title: '平台资产对比',
        description: '各平台资产价值对比',
        data: [
          {'name': '支付宝', 'value': 158460.30, 'label': '支付宝'},
          {'name': 'Wise', 'value': 8158.23, 'label': 'Wise'},
          {'name': 'IBKR', 'value': 420.30, 'label': 'IBKR'},
          {'name': 'OKX', 'value': 1205.67, 'label': 'OKX'},
        ],
        style: {
          'colors': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
          'animation': true,
        },
      );
    }
  }
}

/// MCP智能图表Widget
class MCPSmartChart extends StatelessWidget {
  final ChartConfig config;
  final double height;

  const MCPSmartChart({
    super.key,
    required this.config,
    this.height = 300,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 图表标题
            Text(
              config.title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            if (config.description.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                config.description,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
            const SizedBox(height: 16),
            
            // 图表内容
            SizedBox(
              height: height,
              child: _buildChart(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChart() {
    switch (config.chartType.toLowerCase()) {
      case 'pie':
        return _buildPieChart();
      case 'line':
        return _buildLineChart();
      case 'bar':
        return _buildBarChart();
      case 'table':
        return _buildTableChart();
      default:
        return _buildBarChart();
    }
  }

  /// 构建饼图
  Widget _buildPieChart() {
    if (config.data.isEmpty) return _buildNoDataWidget();

    final colors = _getColors();
    
    return PieChart(
      PieChartData(
        sectionsSpace: 2,
        centerSpaceRadius: 40,
        sections: config.data.asMap().entries.map((entry) {
          final index = entry.key;
          final item = entry.value;
          final value = (item['value'] ?? 0).toDouble();
          final total = config.data.fold<double>(0, (sum, data) => sum + (data['value'] ?? 0).toDouble());
          final percentage = total > 0 ? (value / total * 100) : 0;
          
          return PieChartSectionData(
            color: colors[index % colors.length],
            value: value,
            title: '${percentage.toStringAsFixed(1)}%',
            radius: 80,
            titleStyle: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          );
        }).toList(),
      ),
    );
  }

  /// 构建折线图
  Widget _buildLineChart() {
    if (config.data.isEmpty) return _buildNoDataWidget();

    final spots = config.data.asMap().entries.map((entry) {
      return FlSpot(
        entry.key.toDouble(),
        (entry.value['value'] ?? 0).toDouble(),
      );
    }).toList();

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 60,
              getTitlesWidget: (value, meta) {
                return Text(
                  _formatCurrency(value),
                  style: const TextStyle(fontSize: 10),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < config.data.length) {
                  final label = config.data[index]['label'] ?? '';
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      label,
                      style: const TextStyle(fontSize: 10),
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          rightTitles: const AxisTitles(),
          topTitles: const AxisTitles(),
        ),
        borderData: FlBorderData(show: true),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: _getColors().first,
            barWidth: 3,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(
              show: true,
              color: _getColors().first.withOpacity(0.1),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建柱状图
  Widget _buildBarChart() {
    if (config.data.isEmpty) return _buildNoDataWidget();

    final colors = _getColors();

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: config.data.map((item) => (item['value'] ?? 0).toDouble()).reduce((a, b) => a > b ? a : b) * 1.2,
        barTouchData: BarTouchData(
          touchTooltipData: BarTouchTooltipData(
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              final item = config.data[group.x.toInt()];
              return BarTooltipItem(
                '${item['label']}\n${_formatCurrency(rod.toY)}',
                const TextStyle(color: Colors.white),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 60,
              getTitlesWidget: (value, meta) {
                return Text(
                  _formatCurrency(value),
                  style: const TextStyle(fontSize: 10),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < config.data.length) {
                  final label = config.data[index]['label'] ?? '';
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      label,
                      style: const TextStyle(fontSize: 10),
                      textAlign: TextAlign.center,
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          rightTitles: const AxisTitles(),
          topTitles: const AxisTitles(),
        ),
        borderData: FlBorderData(show: false),
        barGroups: config.data.asMap().entries.map((entry) {
          return BarChartGroupData(
            x: entry.key,
            barRods: [
              BarChartRodData(
                toY: (entry.value['value'] ?? 0).toDouble(),
                color: colors[entry.key % colors.length],
                width: 20,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  /// 构建表格
  Widget _buildTableChart() {
    if (config.data.isEmpty) return _buildNoDataWidget();

    return SingleChildScrollView(
      child: DataTable(
        columns: [
          const DataColumn(label: Text('项目')),
          const DataColumn(label: Text('数值')),
        ],
        rows: config.data.map((item) {
          return DataRow(
            cells: [
              DataCell(Text(item['label'] ?? item['name'] ?? '未知')),
              DataCell(Text(_formatCurrency((item['value'] ?? 0).toDouble()))),
            ],
          );
        }).toList(),
      ),
    );
  }

  /// 无数据Widget
  Widget _buildNoDataWidget() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.insert_chart, size: 48, color: Colors.grey),
          SizedBox(height: 8),
          Text('暂无数据', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  /// 获取颜色列表
  List<Color> _getColors() {
    final styleColors = config.style['colors'] as List<dynamic>?;
    if (styleColors != null) {
      return styleColors.map((colorHex) => Color(int.parse(colorHex.toString().replaceFirst('#', '0xFF')))).toList();
    }
    return [
      const Color(0xFF10B981),
      const Color(0xFF3B82F6),
      const Color(0xFFF59E0B),
      const Color(0xFFEF4444),
      const Color(0xFF8B5CF6),
    ];
  }

  /// 格式化货币
  String _formatCurrency(double value) {
    if (value >= 10000) {
      return '${(value / 10000).toStringAsFixed(1)}万';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}k';
    } else {
      return value.toStringAsFixed(0);
    }
  }
}

/// MCP智能图表页面
class MCPSmartChartPage extends StatefulWidget {
  const MCPSmartChartPage({super.key});

  @override
  State<MCPSmartChartPage> createState() => _MCPSmartChartPageState();
}

class _MCPSmartChartPageState extends State<MCPSmartChartPage> {
  final TextEditingController _questionController = TextEditingController();
  final List<ChartConfig> _charts = [];
  final List<String> _exampleQuestions = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadExampleQuestions();
  }

  Future<void> _loadExampleQuestions() async {
    final examples = await MCPChartService.getExampleQuestions();
    setState(() {
      _exampleQuestions.addAll(examples);
    });
  }

  Future<void> _generateChart(String question) async {
    if (question.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final chartConfig = await MCPChartService.generateChart(question);
      setState(() {
        _charts.insert(0, chartConfig); // 最新的图表显示在顶部
      });
      _questionController.clear();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('生成图表失败: $e')),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('深度分析'),
        backgroundColor: const Color(0xFF10B981),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          // 输入区域
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Column(
              children: [
                // 问题输入框
                TextField(
                  controller: _questionController,
                  decoration: InputDecoration(
                    hintText: '请输入您想要分析的问题...',
                    prefixIcon: const Icon(Icons.chat),
                    suffixIcon: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : IconButton(
                            icon: const Icon(Icons.send),
                            onPressed: () => _generateChart(_questionController.text),
                          ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onSubmitted: _generateChart,
                ),
                
                const SizedBox(height: 12),
                
                // 示例问题
                if (_exampleQuestions.isNotEmpty) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      '试试这些问题:',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 4,
                    children: _exampleQuestions.take(3).map((question) {
                      return ActionChip(
                        label: Text(
                          question,
                          style: const TextStyle(fontSize: 12),
                        ),
                        onPressed: () => _generateChart(question),
                        backgroundColor: const Color(0xFF10B981).withOpacity(0.1),
                      );
                    }).toList(),
                  ),
                ],
              ],
            ),
          ),
          
          // 图表列表
          Expanded(
            child: _charts.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _charts.length,
                    itemBuilder: (context, index) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: MCPSmartChart(
                          config: _charts[index],
                          height: 300,
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.analytics_outlined,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '开始您的深度分析',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '输入问题，AI将为您生成专业的图表分析',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey[500],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _questionController.dispose();
    super.dispose();
  }
}