import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/chart_storage_service.dart';
import '../widgets/chart_design_system.dart';

/// 分析页面 - 显示保存的图表
class AnalysisPage extends StatefulWidget {
  const AnalysisPage({super.key});

  @override
  State<AnalysisPage> createState() => _AnalysisPageState();
}

class _AnalysisPageState extends State<AnalysisPage> {
  List<SavedChart> _savedCharts = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSavedCharts();
  }

  /// 加载保存的图表
  Future<void> _loadSavedCharts() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final charts = await ChartStorageService.getSavedCharts();
      setState(() {
        _savedCharts = charts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('加载图表失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// 删除图表
  Future<void> _deleteChart(String chartId) async {
    try {
      final success = await ChartStorageService.deleteChart(chartId);
      if (success) {
        await _loadSavedCharts(); // 重新加载
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('图表删除成功'),
              backgroundColor: Colors.green,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('删除失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// 构建饼图
  Widget _buildPieChart(SavedChart chart) {
    final data = (chart.chartConfig['data'] as List<dynamic>).map((item) {
      return CustomPieChartData(
        label: item['label'],
        value: (item['value'] ?? 0.0).toDouble(),
        percentage: (item['percentage'] ?? 0.0).toDouble(),
        color: Color(item['color'] ?? 0xFF000000),
        formattedValue: item['formattedValue'] ?? '',
      );
    }).toList();

    return PieChart(
      PieChartData(
        centerSpaceRadius: 25,
        sectionsSpace: 1.0,
        startDegreeOffset: -90,
        sections: data.asMap().entries.map((entry) {
          final item = entry.value;
          return PieChartSectionData(
            color: item.color,
            value: item.value,
            title: '${item.percentage.toStringAsFixed(1)}%',
            radius: 60.0,
            titleStyle: const TextStyle(
              fontSize: 12,
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          '分析',
          style: TextStyle(
            color: Colors.black87,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.black87),
            onPressed: _loadSavedCharts,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _savedCharts.isEmpty
              ? _buildEmptyState()
              : _buildChartsList(),
    );
  }

  /// 构建空状态
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.pie_chart_outline,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '暂无保存的图表',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '在AI聊天中生成图表后，点击保存即可在此查看',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  /// 构建图表列表
  Widget _buildChartsList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _savedCharts.length,
      itemBuilder: (context, index) {
        final chart = _savedCharts[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: [
              // 标题栏
              Container(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            chart.title,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.black87,
                            ),
                          ),
                          if (chart.subtitle.isNotEmpty) ...[
                            const SizedBox(height: 4),
                            Text(
                              chart.subtitle,
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    Text(
                      _formatDate(chart.savedAt),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.delete_outline, size: 20),
                      onPressed: () => _showDeleteDialog(chart.id),
                      color: Colors.red[400],
                    ),
                  ],
                ),
              ),
              
              // 图表内容
              Container(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Row(
                  children: [
                    // 左侧：饼图
                    Expanded(
                      flex: 2,
                      child: SizedBox(
                        height: 200,
                        child: _buildPieChart(chart),
                      ),
                    ),
                    
                    // 右侧：图例
                    const SizedBox(width: 16),
                    Expanded(
                      flex: 1,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          ...(chart.chartConfig['data'] as List<dynamic>).map((item) {
                            final color = Color(item['color'] ?? 0xFF000000);
                            return Container(
                              margin: const EdgeInsets.only(bottom: 8),
                              child: Row(
                                children: [
                                  Container(
                                    width: 10,
                                    height: 10,
                                    decoration: BoxDecoration(
                                      color: color,
                                      borderRadius: BorderRadius.circular(5),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      item['label'],
                                      style: const TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w500,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  Text(
                                    '${item['percentage'].toStringAsFixed(1)}%',
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      color: color,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  /// 显示删除确认对话框
  void _showDeleteDialog(String chartId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('确定要删除这个图表吗？删除后无法恢复。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _deleteChart(chartId);
            },
            child: Text(
              '删除',
              style: TextStyle(color: Colors.red[600]),
            ),
          ),
        ],
      ),
    );
  }

  /// 格式化日期
  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}天前';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
}
