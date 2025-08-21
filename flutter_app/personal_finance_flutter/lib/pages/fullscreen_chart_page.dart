import 'package:flutter/material.dart';
import '../widgets/chart_design_system.dart';
import '../services/chart_storage_service.dart';

/// 全屏图表展示页面
class FullscreenChartPage extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget chartContent;
  final List<CustomPieChartData>? legendData;
  final bool showLegend;

  const FullscreenChartPage({
    super.key,
    required this.title,
    this.subtitle,
    required this.chartContent,
    this.legendData,
    this.showLegend = true,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black87),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          title,
          style: const TextStyle(
            color: Colors.black87,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share, color: Colors.black87),
            onPressed: () {
              // TODO: 实现分享功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('分享功能开发中...')),
              );
            },
          ),
                                IconButton(
                        icon: const Icon(Icons.save, color: Colors.black87),
                        onPressed: () async {
                          try {
                            // 保存图表数据
                            final chart = SavedChart(
                              id: ChartStorageService.generateId(),
                              title: title,
                              subtitle: subtitle ?? '',
                              question: title, // 使用标题作为问题
                              chartConfig: {
                                'chartType': 'pie',
                                'data': legendData?.map((item) => {
                                  'label': item.label,
                                  'value': item.value,
                                  'percentage': item.percentage,
                                  'color': item.color.value,
                                  'formattedValue': item.formattedValue,
                                }).toList() ?? [],
                              },
                              savedAt: DateTime.now(),
                              chartType: 'pie',
                            );
                            
                            final success = await ChartStorageService.saveChart(chart);
                            
                            if (success) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('图表保存成功！'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            } else {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('保存失败，请重试'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('保存出错: $e'),
                                backgroundColor: Colors.red,
                              ),
                            );
                          }
                        },
                      ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // 标题区域
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              color: Colors.white,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  if (subtitle != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      subtitle!,
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            
            // 专业金融仪表板风格
            Container(
              margin: const EdgeInsets.all(16),
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
                  // 顶部标题栏
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                    ),
                    child: Row(
                      children: [
                        Text(
                          '资产分布',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            color: Colors.grey[900],
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.green[50],
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: Colors.green[200]!),
                          ),
                          child: Text(
                            '实时',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Colors.green[700],
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Icon(
                          Icons.more_vert,
                          color: Colors.grey[600],
                          size: 20,
                        ),
                      ],
                    ),
                  ),
                  
                  // 主要内容区域
                  Container(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // 左侧：饼图区域
                        Expanded(
                          flex: 3,
                          child: SizedBox(
                            height: 200, // 减少高度，让卡片更扁
                            child: chartContent,
                          ),
                        ),
                        
                        // 右侧：图例和数值
                        if (showLegend && legendData != null) ...[
                          const SizedBox(width: 24),
                          Expanded(
                            flex: 2,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                ...legendData!.map((item) => Container(
                                  margin: const EdgeInsets.only(bottom: 12), // 减少间距
                                  child: Row(
                                    children: [
                                      Container(
                                        width: 10, // 减小圆点
                                        height: 10,
                                        decoration: BoxDecoration(
                                          color: item.color,
                                          borderRadius: BorderRadius.circular(5),
                                        ),
                                      ),
                                      const SizedBox(width: 10), // 减少间距
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              item.label,
                                              style: TextStyle(
                                                fontSize: 13, // 减小字体
                                                fontWeight: FontWeight.w600,
                                                color: Colors.grey[900],
                                              ),
                                            ),
                                            Text(
                                              item.formattedValue,
                                              style: TextStyle(
                                                fontSize: 12, // 减小字体
                                                fontWeight: FontWeight.w500,
                                                color: Colors.grey[700],
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      Text(
                                        '${item.percentage.toStringAsFixed(1)}%',
                                        style: TextStyle(
                                          fontSize: 14, // 减小字体
                                          fontWeight: FontWeight.w700,
                                          color: item.color,
                                        ),
                                      ),
                                    ],
                                  ),
                                )).toList(),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  
                  // 底部指标区域
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: const BorderRadius.vertical(bottom: Radius.circular(16)),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '最大持仓',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'OKX',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.grey[900],
                                ),
                              ),
                            ],
                          ),
                        ),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '占比最大',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '52.6%',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.green[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '平台数量',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${legendData?.length ?? 0}个',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.orange[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // 底部留白，确保滚动到底部时内容不被遮挡
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
