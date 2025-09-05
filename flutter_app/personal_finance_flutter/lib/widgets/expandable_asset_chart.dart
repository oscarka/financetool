import 'package:flutter/material.dart';
import 'dart:math';
import '../models/trend_data.dart';

class ExpandableAssetChart extends StatelessWidget {
  final List<TrendData> trendData;
  final String selectedCurrency;
  final double totalValue;
  final double? dailyChangePercent;
  final VoidCallback? onTap;
  final String selectedTimeRange;
  final Function(String) onTimeRangeChanged;

  const ExpandableAssetChart({
    super.key,
    required this.trendData,
    required this.selectedCurrency,
    required this.totalValue,
    this.dailyChangePercent,
    this.onTap,
    this.selectedTimeRange = '1日',
    required this.onTimeRangeChanged,
  });

  @override
  Widget build(BuildContext context) {
    // 检查真实数据是否有效，如果无效则使用默认数据（全为0）
    final displayData = _shouldUseDefaultData() ? _generateDefaultData() : trendData;
    
    print('🔍 [ExpandableAssetChart] 构建组件');
    print('  - 数据条数: ${displayData.length}');
    print('  - 总资产: $totalValue');
    print('  - 货币: $selectedCurrency');
    print('  - 时间范围: $selectedTimeRange');
    if (displayData.isNotEmpty) {
      print('  - 第一条数据: ${displayData.first.total}');
      print('  - 最后一条数据: ${displayData.last.total}');
    }
    print('🔍 [ExpandableAssetChart] 小图表显示数据详情:');
    for (int i = 0; i < displayData.length; i++) {
      print('  - 数据${i+1}: ${displayData[i].total.toStringAsFixed(2)} (${displayData[i].date})');
    }

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 90,
        height: 80,
        child: _buildMiniLineChart(displayData),
      ),
    );
  }

  // 判断是否应该使用默认数据（全为0）
  bool _shouldUseDefaultData() {
    // 如果没有数据，使用默认数据（全为0）
    if (trendData.isEmpty) return true;
    
    // 如果数据点少于2个，使用默认数据
    if (trendData.length < 2) return true;
    
    // 对于1日和1周范围，即使所有数据都是0也显示（小时数据）
    if (selectedTimeRange == '1日' || selectedTimeRange == '1周') return false;
    
    // 如果所有数据都是0，使用默认数据
    final allZero = trendData.every((d) => d.total == 0.0);
    if (allZero) return true;
    
    print('🔍 数据有效性检查:');
    print('  - 数据点数量: ${trendData.length}');
    print('  - 数据范围: ${trendData.map((d) => d.total).reduce((a, b) => a > b ? a : b) - trendData.map((d) => d.total).reduce((a, b) => a < b ? a : b)}');
    
    print('✅ 真实数据有效，使用真实数据');
    return false;
  }

  // 生成默认数据（全为0）
  List<TrendData> _generateDefaultData() {
    final now = DateTime.now();
    final data = <TrendData>[];
    
    print('🔍 [ExpandableAssetChart] 生成默认数据，时间范围: $selectedTimeRange');
    
    // 根据时间范围生成对应天数的默认数据
    switch (selectedTimeRange) {
      case '1日':
        // 1日范围：生成24小时数据
        for (int i = 23; i >= 0; i--) {
          final time = now.subtract(Duration(hours: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '1周':
        // 1周范围：生成168小时数据（7天 × 24小时）
        for (int i = 167; i >= 0; i--) {
          final time = now.subtract(Duration(hours: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '1月':
        for (int i = 29; i >= 0; i--) {
          final time = now.subtract(Duration(days: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '半年':
        for (int i = 179; i >= 0; i--) {
          final time = now.subtract(Duration(days: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
    }
    
    print('🎲 [ExpandableAssetChart] 生成了 ${data.length} 条默认数据（全为0）');
    return data;
  }

  // 生成模拟数据 - 24小时上升趋势
  List<TrendData> _generateMockData() {
    final now = DateTime.now();
    final data = <TrendData>[];
    
    // 生成24个数据点，模拟24小时的变化
    for (int i = 0; i < 24; i++) {
      final time = now.subtract(Duration(hours: 23 - i));
      // 模拟一个上升趋势：从10000开始，逐渐上升到10500
      final baseValue = 10000.0;
      final trendValue = baseValue + (i * 20.83); // 500/24 ≈ 20.83
      final randomVariation = (Random().nextDouble() - 0.5) * 100; // ±50的随机波动
      final finalValue = trendValue + randomVariation;
      
      data.add(TrendData(
        date: time.toIso8601String(), // 转换为ISO字符串格式
        total: finalValue,
      ));
    }
    
    print('🎲 生成了 ${data.length} 条模拟数据');
    print('  - 起始值: ${data.first.total.toStringAsFixed(2)}');
    print('  - 结束值: ${data.last.total.toStringAsFixed(2)}');
    
    return data;
  }

  Widget _buildMiniLineChart(List<TrendData> displayData) {
    if (displayData.isEmpty || displayData.length < 2) {
      print('⚠️ 数据不足，显示占位符');
      return _buildPlaceholder();
    }

    final currentValue = totalValue;
    final maxValue = displayData.map((d) => d.total).reduce((a, b) => a > b ? a : b);
    final minValue = displayData.map((d) => d.total).reduce((a, b) => a < b ? a : b);

    print('📊 数据范围: ${minValue.toStringAsFixed(2)} - ${maxValue.toStringAsFixed(2)}, 当前值: ${currentValue.toStringAsFixed(2)}');

    // 使用模拟数据时，强制显示绿色上升趋势
    final isRising = displayData.last.total > displayData.first.total;
    final hasHigherPoints = maxValue > (currentValue + 0.001);

    Color lineColor;
    if (_shouldUseDefaultData()) {
      // 模拟数据时使用绿色
      lineColor = const Color(0xFF10B981);
      print('🎨 使用模拟数据，显示绿色上升趋势');
    } else if (isRising && !hasHigherPoints) {
      lineColor = const Color(0xFF10B981); // 绿色
    } else if (hasHigherPoints) {
      lineColor = const Color(0xFFEF4444); // 红色
    } else {
      lineColor = const Color(0xFF6B7280); // 灰色
    }

    print('🎨 选择颜色: $lineColor');

    return CustomPaint(
      size: const Size(90, 80),
      painter: _MiniLineChartPainter(
        trendData: displayData,
        lineColor: lineColor,
        maxValue: maxValue,
        minValue: minValue,
        totalValue: totalValue,
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.show_chart, color: Colors.white.withValues(alpha: 0.4), size: 18),
            const SizedBox(height: 4),
            Text(
              '暂无数据',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.4),
                fontSize: 10,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MiniLineChartPainter extends CustomPainter {
  final List<TrendData> trendData;
  final Color lineColor;
  final double maxValue;
  final double minValue;
  final double totalValue;

  _MiniLineChartPainter({
    required this.trendData,
    required this.lineColor,
    required this.maxValue,
    required this.minValue,
    required this.totalValue,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (trendData.length < 2) {
      print('⚠️ 绘制器：数据不足2条，跳过绘制');
      return;
    }

    print('🎨 开始绘制折线图，尺寸: ${size.width} x ${size.height}');
    print('📊 数据点数量: ${trendData.length}');

    // 使用传入的颜色，确保美观
    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final path = Path();
    double valueRange = maxValue - minValue;

    if (valueRange < 0.01) {
      valueRange = totalValue * 0.01;
      if (valueRange < 0.01) {
        valueRange = 0.01;
      }
    }

    print('📊 调整后的数值范围: ${valueRange.toStringAsFixed(2)}');

    for (int i = 0; i < trendData.length; i++) {
      final data = trendData[i];
      final x = (i / (trendData.length - 1)) * size.width;

      double normalizedValue;
      if (valueRange < 0.01) {
        normalizedValue = 0.5;
      } else {
        normalizedValue = (data.total - minValue) / valueRange;
        normalizedValue = normalizedValue.clamp(0.15, 0.85);
      }

      final y = size.height - (normalizedValue * size.height);

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    canvas.drawPath(path, paint);
    print('✅ 折线图绘制完成');

    // 绘制起点和终点的小圆点，增加美观性
    if (trendData.length >= 2) {
      final startNormalizedValue = (valueRange < 0.01) ? 0.5 : ((trendData.first.total - minValue) / valueRange).clamp(0.15, 0.85);
      final endNormalizedValue = (valueRange < 0.01) ? 0.5 : ((trendData.last.total - minValue) / valueRange).clamp(0.15, 0.85);

      final startPoint = Offset(0, size.height - (startNormalizedValue * size.height));
      final endPoint = Offset(size.width, size.height - (endNormalizedValue * size.height));

      final pointPaint = Paint()
        ..color = lineColor
        ..style = PaintingStyle.fill;

      // 绘制起点和终点的圆点
      canvas.drawCircle(startPoint, 2.0, pointPaint);
      canvas.drawCircle(endPoint, 2.0, pointPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ExpandedLineChartPainter extends CustomPainter {
  final List<TrendData> trendData;
  final Color lineColor;
  final double maxValue;
  final double minValue;
  final double totalValue;
  final int? hoveredIndex;

  _ExpandedLineChartPainter({
    required this.trendData,
    required this.lineColor,
    required this.maxValue,
    required this.minValue,
    required this.totalValue,
    this.hoveredIndex,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (trendData.length < 2) {
      print('⚠️ 绘制器：数据不足2条，跳过绘制');
      return;
    }

    print('🎨 开始绘制折线图，尺寸: ${size.width} x ${size.height}');
    print('📊 数据点数量: ${trendData.length}');

    // 使用传入的颜色，确保美观
    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final path = Path();
    double valueRange = maxValue - minValue;

    if (valueRange < 0.01) {
      valueRange = totalValue * 0.01;
      if (valueRange < 0.01) {
        valueRange = 0.01;
      }
    }

    print('📊 调整后的数值范围: ${valueRange.toStringAsFixed(2)}');

    for (int i = 0; i < trendData.length; i++) {
      final data = trendData[i];
      final x = (i / (trendData.length - 1)) * size.width;

      double normalizedValue;
      if (valueRange < 0.01) {
        normalizedValue = 0.5;
      } else {
        normalizedValue = (data.total - minValue) / valueRange;
        normalizedValue = normalizedValue.clamp(0.15, 0.85);
      }

      final y = size.height - (normalizedValue * size.height);

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    canvas.drawPath(path, paint);
    print('✅ 折线图绘制完成');

    // 绘制起点和终点的小圆点，增加美观性
    if (trendData.length >= 2) {
      final startNormalizedValue = (valueRange < 0.01) ? 0.5 : ((trendData.first.total - minValue) / valueRange).clamp(0.15, 0.85);
      final endNormalizedValue = (valueRange < 0.01) ? 0.5 : ((trendData.last.total - minValue) / valueRange).clamp(0.15, 0.85);

      final startPoint = Offset(0, size.height - (startNormalizedValue * size.height));
      final endPoint = Offset(size.width, size.height - (endNormalizedValue * size.height));

      final pointPaint = Paint()
        ..color = lineColor
        ..style = PaintingStyle.fill;

      // 绘制起点和终点的圆点
      canvas.drawCircle(startPoint, 2.0, pointPaint);
      canvas.drawCircle(endPoint, 2.0, pointPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// 展开区域组件
class ExpandedChartSection extends StatefulWidget {
  final List<TrendData> trendData;
  final String selectedCurrency;
  final double totalValue;
  final VoidCallback? onClose;
  final String selectedTimeRange;
  final Function(String) onTimeRangeChanged;

  const ExpandedChartSection({
    super.key,
    required this.trendData,
    required this.selectedCurrency,
    required this.totalValue,
    this.onClose,
    this.selectedTimeRange = '1日',
    required this.onTimeRangeChanged,
  });

  @override
  State<ExpandedChartSection> createState() => _ExpandedChartSectionState();
}

class _ExpandedChartSectionState extends State<ExpandedChartSection> {
  int? _hoveredDataIndex; // 悬停的数据点索引

  @override
  Widget build(BuildContext context) {
    print('🔍 [ExpandedChartSection] 构建展开图表组件');
    print('  - 数据条数: ${widget.trendData.length}');
    print('  - 时间范围: ${widget.selectedTimeRange}');
    print('  - 总资产: ${widget.totalValue}');
    
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 0), // 移除上边距，紧贴上面的卡片
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1F24),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(0), // 左上角不圆角，与上面的卡片连接
          topRight: Radius.circular(0), // 右上角不圆角，与上面的卡片连接
          bottomLeft: Radius.circular(20), // 保持左下角圆角
          bottomRight: Radius.circular(20), // 保持右下角圆角
        ),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1), width: 1),
      ),
      child: Column(
        children: [
          // 头部：标题和关闭按钮
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '资产趋势',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              GestureDetector(
                onTap: widget.onClose,
                child: Icon(
                  Icons.close,
                  color: Colors.white.withValues(alpha: 0.7),
                  size: 24,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // 时间范围选择器
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: ['1日', '1周', '1月', '半年'].map((range) {
              final isSelected = widget.selectedTimeRange == range;
              return GestureDetector(
                onTap: () {
                  print('🎯 [ExpandedChartSection] 选择时间范围: $range');
                  print('🎯 [ExpandedChartSection] 当前时间范围: ${widget.selectedTimeRange}');
                  widget.onTimeRangeChanged(range);
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: isSelected ? const Color(0xFF10B981) : Colors.transparent,
                    borderRadius: BorderRadius.circular(25),
                    border: Border.all(
                      color: isSelected ? const Color(0xFF10B981) : Colors.white.withValues(alpha: 0.3),
                      width: 1,
                    ),
                  ),
                  child: Text(
                    range,
                    style: TextStyle(
                      color: isSelected ? Colors.white : Colors.white.withValues(alpha: 0.7),
                      fontSize: 16,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          
          const SizedBox(height: 20),
          
          // 大折线图
          SizedBox(
            height: 300,
            child: _buildExpandedLineChart(),
          ),
          
          // 底部箭头提示
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Icon(
              Icons.keyboard_arrow_up,
              color: Colors.white.withValues(alpha: 0.5),
              size: 24,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpandedLineChart() {
    // 使用真实数据，如果没有数据则使用默认数据（全为0）
    final displayData = widget.trendData.isNotEmpty ? widget.trendData : _generateDefaultData();
    
    print('🔍 [DEBUG] 展开图表绘制，数据点数量: ${displayData.length}');
    print('🔍 [DEBUG] 真实数据: ${widget.trendData.isNotEmpty}, 使用默认数据: ${widget.trendData.isEmpty}');
    
    return GestureDetector(
      onPanUpdate: (details) {
        // 处理鼠标悬停
        _handleChartHover(details.localPosition, displayData);
      },
      child: CustomPaint(
        size: const Size(double.infinity, 300),
        painter: _NewExpandedLineChartPainter(
          trendData: displayData,
          lineColor: const Color(0xFF10B981),
          maxValue: displayData.map((d) => d.total).reduce((a, b) => a > b ? a : b),
          minValue: displayData.map((d) => d.total).reduce((a, b) => a < b ? a : b),
          totalValue: widget.totalValue,
          hoveredIndex: _hoveredDataIndex,
        ),
      ),
    );
  }

  // 处理图表悬停
  void _handleChartHover(Offset position, List<TrendData> data) {
    if (data.isEmpty) {
      print('🔍 [DEBUG] 悬停处理：数据为空');
      return;
    }
    
    final width = 300.0; // 图表宽度
    final padding = 20.0;
    final dataWidth = width - 2 * padding;
    
    // 计算悬停的数据点索引
    final relativeX = position.dx - padding;
    final dataIndex = (relativeX / dataWidth * (data.length - 1)).round();
    
    print('🔍 [DEBUG] 悬停位置: ${position.dx}, 相对位置: $relativeX, 数据索引: $dataIndex');
    
    if (dataIndex >= 0 && dataIndex < data.length) {
      print('🔍 [DEBUG] 悬停数据点: ${data[dataIndex].total}, 时间: ${data[dataIndex].date}');
      setState(() {
        _hoveredDataIndex = dataIndex;
      });
    }
  }

  // 生成默认数据（全为0）
  List<TrendData> _generateDefaultData() {
    final now = DateTime.now();
    final data = <TrendData>[];
    
    print('🔍 [ExpandedChartSection] 生成默认数据，时间范围: ${widget.selectedTimeRange}');
    
    // 根据时间范围生成对应天数的默认数据
    switch (widget.selectedTimeRange) {
      case '1日':
        // 1日范围：生成24小时数据
        for (int i = 23; i >= 0; i--) {
          final time = now.subtract(Duration(hours: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '1周':
        // 1周范围：生成168小时数据（7天 × 24小时）
        for (int i = 167; i >= 0; i--) {
          final time = now.subtract(Duration(hours: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '1月':
        for (int i = 29; i >= 0; i--) {
          final time = now.subtract(Duration(days: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '半年':
        for (int i = 179; i >= 0; i--) {
          final time = now.subtract(Duration(days: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
    }
    
    print('🎲 [ExpandedChartSection] 生成了 ${data.length} 条默认数据（全为0）');
    return data;
  }

  // 生成模拟数据
  List<TrendData> _generateMockData() {
    final now = DateTime.now();
    final data = <TrendData>[];
    
    for (int i = 0; i < 24; i++) {
      final time = now.subtract(Duration(hours: 23 - i));
      final baseValue = 10000.0;
      final trendValue = baseValue + (i * 20.83);
      final randomVariation = (Random().nextDouble() - 0.5) * 100;
      final finalValue = trendValue + randomVariation;
      
      data.add(TrendData(
        date: time.toIso8601String(),
        total: finalValue,
      ));
    }
    
    return data;
  }
}

// 新的展开折线图绘制器（支持悬停）
class _NewExpandedLineChartPainter extends CustomPainter {
  final List<TrendData> trendData;
  final Color lineColor;
  final double maxValue;
  final double minValue;
  final double totalValue;
  final int? hoveredIndex;

  _NewExpandedLineChartPainter({
    required this.trendData,
    required this.lineColor,
    required this.maxValue,
    required this.minValue,
    required this.totalValue,
    this.hoveredIndex,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (trendData.length < 2) {
      print('⚠️ 绘制器：数据不足2条，跳过绘制');
      return;
    }

    print('🎨 开始绘制折线图，尺寸: ${size.width} x ${size.height}');
    print('📊 数据点数量: ${trendData.length}');
    print('🔍 [DEBUG] 绘制器：绘制 ${trendData.length} 个数据点，悬停索引: $hoveredIndex');

    // 使用传入的颜色，确保美观
    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final path = Path();
    double valueRange = maxValue - minValue;

    if (valueRange < 0.01) {
      valueRange = totalValue * 0.01;
      if (valueRange < 0.01) {
        valueRange = 0.01;
      }
    }

    print('📊 调整后的数值范围: ${valueRange.toStringAsFixed(2)}');

    // 计算所有数据点位置
    final dataPoints = <Offset>[];
    for (int i = 0; i < trendData.length; i++) {
      final data = trendData[i];
      final x = (i / (trendData.length - 1)) * size.width;

      double normalizedValue;
      if (valueRange < 0.01) {
        normalizedValue = 0.5;
      } else {
        normalizedValue = (data.total - minValue) / valueRange;
        normalizedValue = normalizedValue.clamp(0.15, 0.85);
      }

      final y = size.height - (normalizedValue * size.height);
      dataPoints.add(Offset(x, y));

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    canvas.drawPath(path, paint);
    print('✅ 折线图绘制完成');

    // 绘制所有数据点，悬停的点高亮显示
    for (int i = 0; i < dataPoints.length; i++) {
      final point = dataPoints[i];
      final isHovered = hoveredIndex == i;
      
      // 悬停的数据点更大更亮
      final radius = isHovered ? 5.0 : 3.0;
      final color = isHovered ? Colors.white : lineColor;
      
      final pointPaint = Paint()
        ..color = color
        ..style = PaintingStyle.fill;
      
      canvas.drawCircle(point, radius, pointPaint);
      
      // 悬停时显示数据标签
      if (isHovered) {
        _drawDataLabel(canvas, point, trendData[i]);
      }
    }
  }

  void _drawDataLabel(Canvas canvas, Offset point, TrendData data) {
    final textPainter = TextPainter(
      text: TextSpan(
        text: '${data.total.toStringAsFixed(2)}',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    
    textPainter.layout();
    
    // 在数据点上方显示标签
    final labelOffset = Offset(
      point.dx - textPainter.width / 2,
      point.dy - 20,
    );
    
    // 绘制背景
    final backgroundPaint = Paint()
      ..color = Colors.black.withValues(alpha: 0.7)
      ..style = PaintingStyle.fill;
    
    final backgroundRect = Rect.fromLTWH(
      labelOffset.dx - 4,
      labelOffset.dy - 2,
      textPainter.width + 8,
      textPainter.height + 4,
    );
    
    canvas.drawRRect(
      RRect.fromRectAndRadius(backgroundRect, const Radius.circular(4)),
      backgroundPaint,
    );
    
    // 绘制文字
    textPainter.paint(canvas, labelOffset);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
