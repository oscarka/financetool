import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

/// 图表设计系统 - 专业的视觉规范
class ChartDesignSystem {
  // 主色调系列 - 基于现代金融应用的设计趋势
  static const Color primary = Color(0xFF2563EB);      // 深蓝 - 主色
  static const Color secondary = Color(0xFF10B981);    // 翠绿 - 成功/收益
  static const Color accent = Color(0xFF8B5CF6);       // 紫色 - 强调色
  static const Color warning = Color(0xFFF59E0B);      // 琥珀 - 警告
  static const Color danger = Color(0xFFEF4444);       // 红色 - 风险/损失
  
  // 渐变色系
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF3B82F6), Color(0xFF1D4ED8)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient successGradient = LinearGradient(
    colors: [Color(0xFF10B981), Color(0xFF059669)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient warningGradient = LinearGradient(
    colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // 专业配色方案
  static List<Color> get professionalColors => [
    primary,
    secondary, 
    accent,
    warning,
    danger,
    const Color(0xFF6366F1), // 靛青
    const Color(0xFF14B8A6), // 青绿
    const Color(0xFFEC4899), // 粉红
  ];

  // 数据可视化专用配色（色盲友好）
  static List<Color> get accessibleColors => [
    const Color(0xFF0066CC), // 蓝色
    const Color(0xFFFF6B00), // 橙色  
    const Color(0xFF00AA44), // 绿色
    const Color(0xFFDD0000), // 红色
    const Color(0xFF8800DD), // 紫色
    const Color(0xFF004D99), // 深蓝
    const Color(0xFF997700), // 棕色
    const Color(0xFF333333), // 深灰
  ];

  // 阴影效果
  static List<BoxShadow> get cardShadow => [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 16,
      offset: const Offset(0, 4),
    ),
    BoxShadow(
      color: Colors.black.withOpacity(0.04),
      blurRadius: 8,
      offset: const Offset(0, 2),
    ),
  ];

  // 文字样式
  static TextStyle get titleStyle => const TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w700,
    letterSpacing: -0.5,
    height: 1.2,
  );

  static TextStyle get subtitleStyle => TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    color: Colors.grey[600],
    height: 1.3,
  );

  static TextStyle get labelStyle => const TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
  );

  static TextStyle get valueStyle => const TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.2,
  );
}

/// 标准化图表容器
class StandardChartContainer extends StatelessWidget {
  final Widget child;
  final String title;
  final String? subtitle;
  final Widget? headerAction;
  final EdgeInsets? padding;
  final double? height;

  const StandardChartContainer({
    super.key,
    required this.child,
    required this.title,
    this.subtitle,
    this.headerAction,
    this.padding,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 图表头部
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 20, 20, 16),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: ChartDesignSystem.titleStyle),
                      if (subtitle != null) ...[
                        const SizedBox(height: 4),
                        Text(subtitle!, style: ChartDesignSystem.subtitleStyle),
                      ],
                    ],
                  ),
                ),
                if (headerAction != null) headerAction!,
              ],
            ),
          ),
          
          // 图表内容
          Container(
            height: height ?? 320, // 增加默认高度，给图表更多空间
            padding: padding ?? const EdgeInsets.fromLTRB(16, 0, 16, 20),
            child: child,
          ),
        ],
      ),
    );
  }
}

/// 专业饼图组件
class ProfessionalPieChart extends StatefulWidget {
  final List<CustomPieChartData> data;
  final String title;
  final String? subtitle;
  final bool showValues;
  final bool showLegend;

  const ProfessionalPieChart({
    super.key,
    required this.data,
    required this.title,
    this.subtitle,
    this.showValues = true,
    this.showLegend = true,
  });

  @override
  State<ProfessionalPieChart> createState() => _ProfessionalPieChartState();
}

class _ProfessionalPieChartState extends State<ProfessionalPieChart> {
  int touchedIndex = -1;

  @override
  Widget build(BuildContext context) {
    print('🥧 ProfessionalPieChart build 开始');
    print('📊 数据条数: ${widget.data.length}');
    print('📝 数据内容: ${widget.data.map((e) => '${e.label}:${e.value}(${e.percentage.toStringAsFixed(1)}%)').join(', ')}');
    print('🎨 显示设置: showValues=${widget.showValues}, showLegend=${widget.showLegend}');
    
    return StandardChartContainer(
      title: widget.title,
      subtitle: widget.subtitle,
      child: Row(
        children: [
          // 饼图
          Expanded(
            flex: 5, // 增加饼图的比例，给图例留更多空间
            child: PieChart(
              PieChartData(
                centerSpaceRadius: 25, // 进一步减小中心空间
                sectionsSpace: 0.5, // 进一步减小切片间距
                startDegreeOffset: -90,
                sections: widget.data.asMap().entries.map((entry) {
                  final index = entry.key;
                  final data = entry.value;
                  final isTouched = index == touchedIndex;
                  final radius = isTouched ? 55.0 : 45.0; // 进一步减小半径，避免溢出
                  
                  print('  🎯 构建饼图切片 $index: ${data.label} = ${data.value} (${data.percentage.toStringAsFixed(1)}%)');
                  
                  return PieChartSectionData(
                    color: data.color,
                    value: data.value,
                    title: widget.showValues ? '${data.percentage.toStringAsFixed(1)}%' : '',
                    radius: radius,
                    titleStyle: TextStyle(
                      fontSize: isTouched ? 14 : 12,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                      shadows: [
                        Shadow(
                          color: Colors.black.withOpacity(0.3),
                          blurRadius: 2,
                        ),
                      ],
                    ),
                    badgeWidget: isTouched ? _buildBadge(data) : null,
                    badgePositionPercentageOffset: 1.3,
                  );
                }).toList(),
                pieTouchData: PieTouchData(
                  touchCallback: (FlTouchEvent event, pieTouchResponse) {
                    setState(() {
                      if (!event.isInterestedForInteractions ||
                          pieTouchResponse == null ||
                          pieTouchResponse.touchedSection == null) {
                        touchedIndex = -1;
                        return;
                      }
                      touchedIndex = pieTouchResponse.touchedSection!.touchedSectionIndex;
                    });
                  },
                ),
              ),
            ),
          ),
          
          // 图例
          if (widget.showLegend) ...[
            const SizedBox(width: 8), // 进一步减小图例与饼图的间距
            Expanded(
              flex: 2, // 增加图例的比例，确保有足够空间
              child: Container(
                constraints: const BoxConstraints(maxWidth: 120), // 限制图例最大宽度
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start, // 改为顶部对齐，避免居中导致的溢出
                    mainAxisSize: MainAxisSize.min, // 确保Column不会超出可用空间
                    crossAxisAlignment: CrossAxisAlignment.start, // 确保图例项左对齐
                    children: widget.data.asMap().entries.map((entry) {
                      final index = entry.key;
                      final data = entry.value;
                      final isSelected = index == touchedIndex;
                      
                      return Container(
                        margin: const EdgeInsets.symmetric(vertical: 1), // 进一步减小图例项间距
                        child: _buildLegendItem(data, isSelected),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBadge(CustomPieChartData data) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Text(
        data.formattedValue,
        style: ChartDesignSystem.labelStyle.copyWith(
          color: data.color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildLegendItem(CustomPieChartData data, bool isSelected) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isSelected ? data.color.withOpacity(0.1) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        border: isSelected ? Border.all(color: data.color.withOpacity(0.3)) : null,
      ),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: data.color,
              borderRadius: BorderRadius.circular(6),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  data.label,
                  style: ChartDesignSystem.labelStyle.copyWith(
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                  ),
                ),
                Text(
                  data.formattedValue,
                  style: ChartDesignSystem.labelStyle.copyWith(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// 专业柱状图组件
class ProfessionalBarChart extends StatelessWidget {
  final List<CustomBarChartData> data;
  final String title;
  final String? subtitle;
  final bool showValues;
  final bool showGrid;

  const ProfessionalBarChart({
    super.key,
    required this.data,
    required this.title,
    this.subtitle,
    this.showValues = true,
    this.showGrid = true,
  });

  @override
  Widget build(BuildContext context) {
    final maxValue = data.map((e) => e.value).reduce((a, b) => a > b ? a : b);
    
    return StandardChartContainer(
      title: title,
      subtitle: subtitle,
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: maxValue * 1.2,
          backgroundColor: Colors.transparent,
          barTouchData: BarTouchData(
            enabled: true,
            touchTooltipData: BarTouchTooltipData(
              getTooltipItem: (group, groupIndex, rod, rodIndex) {
                final data = this.data[group.x];
                return BarTooltipItem(
                  '${data.label}\n${data.formattedValue}',
                  const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                );
              },
              tooltipRoundedRadius: 8,
              tooltipPadding: const EdgeInsets.all(8),
            ),
          ),
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  if (value.toInt() >= 0 && value.toInt() < data.length) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        data[value.toInt()].label,
                        style: ChartDesignSystem.labelStyle.copyWith(
                          color: Colors.grey[600],
                        ),
                        textAlign: TextAlign.center,
                      ),
                    );
                  }
                  return const Text('');
                },
                reservedSize: 32,
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 60,
                getTitlesWidget: (value, meta) {
                  return Text(
                    _formatValue(value),
                    style: ChartDesignSystem.labelStyle.copyWith(
                      color: Colors.grey[600],
                      fontSize: 10,
                    ),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          gridData: FlGridData(
            show: showGrid,
            drawVerticalLine: false,
            horizontalInterval: _getMaxY() / 5,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: Colors.grey[200]!,
                strokeWidth: 1,
              );
            },
          ),
          borderData: FlBorderData(
            show: false,
          ),
          barGroups: data.asMap().entries.map((entry) {
            final index = entry.key;
            final item = entry.value;
            
            return BarChartGroupData(
              x: index,
              barRods: [
                BarChartRodData(
                  toY: item.value,
                  gradient: _getBarGradient(item.color),
                  width: 24,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(6),
                  ),
                  backDrawRodData: BackgroundBarChartRodData(
                    show: true,
                    toY: _getMaxY() * 1.1,
                    color: Colors.grey[100],
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  double _getMaxY() {
    return data.map((e) => e.value).reduce((a, b) => a > b ? a : b);
  }

  LinearGradient _getBarGradient(Color color) {
    return LinearGradient(
      colors: [
        color,
        color.withOpacity(0.7),
      ],
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
    );
  }

  String _formatValue(double value) {
    if (value >= 10000) {
      return '${(value / 10000).toStringAsFixed(1)}万';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}k';
    } else {
      return value.toStringAsFixed(0);
    }
  }
}

/// 专业折线图组件
class ProfessionalLineChart extends StatelessWidget {
  final List<CustomLineChartData> data;
  final String title;
  final String? subtitle;
  final bool showValues;
  final bool showGrid;
  final bool showArea;

  const ProfessionalLineChart({
    super.key,
    required this.data,
    required this.title,
    this.subtitle,
    this.showValues = true,
    this.showGrid = true,
    this.showArea = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = ChartDesignSystem.primary; // Default line color
    
    return StandardChartContainer(
      title: title,
      subtitle: subtitle,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            horizontalInterval: 1,
            verticalInterval: 1,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: Colors.grey[300]!,
                strokeWidth: 1,
              );
            },
            getDrawingVerticalLine: (value) {
              return FlLine(
                color: Colors.grey[300]!,
                strokeWidth: 1,
              );
            },
          ),
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 32,
                interval: _getXInterval(),
                getTitlesWidget: (value, meta) {
                  final index = value.toInt();
                  if (index >= 0 && index < data.length) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        data[index].label,
                        style: ChartDesignSystem.labelStyle.copyWith(
                          color: Colors.grey[600],
                          fontSize: 10,
                        ),
                      ),
                    );
                  }
                  return const Text('');
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 60,
                getTitlesWidget: (value, meta) {
                  return Text(
                    _formatValue(value),
                    style: ChartDesignSystem.labelStyle.copyWith(
                      color: Colors.grey[600],
                      fontSize: 10,
                    ),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: data.asMap().entries.map((entry) {
                return FlSpot(entry.key.toDouble(), entry.value.value);
              }).toList(),
              isCurved: true,
              curveSmoothness: 0.3,
              color: color,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true, // showDots is removed, so always show dots
                getDotPainter: (spot, percent, barData, index) {
                  return FlDotCirclePainter(
                    radius: 4,
                    color: Colors.white,
                    strokeWidth: 3,
                    strokeColor: color,
                  );
                },
              ),
              belowBarData: BarAreaData(
                show: showArea,
                gradient: LinearGradient(
                  colors: [
                    color.withOpacity(0.2),
                    color.withOpacity(0.05),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            enabled: true,
            touchTooltipData: LineTouchTooltipData(
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  final dataPoint = data[spot.x.toInt()];
                  return LineTooltipItem(
                    '${dataPoint.label}\n${dataPoint.formattedValue}',
                    const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  );
                }).toList();
              },
              tooltipRoundedRadius: 8,
              tooltipPadding: const EdgeInsets.all(8),
            ),
          ),
        ),
      ),
    );
  }

  double _getYInterval() {
    final maxY = data.map((e) => e.value).reduce((a, b) => a > b ? a : b);
    return maxY / 5;
  }

  double _getXInterval() {
    return data.length > 10 ? (data.length / 5).ceilToDouble() : 1;
  }

  String _formatValue(double value) {
    if (value >= 10000) {
      return '${(value / 10000).toStringAsFixed(1)}万';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}k';
    } else {
      return value.toStringAsFixed(0);
    }
  }
}

/// 数据模型类
class CustomPieChartData {
  final String label;
  final double value;
  final double percentage;
  final Color color;
  final String formattedValue;

  CustomPieChartData({
    required this.label,
    required this.value,
    required this.percentage,
    required this.color,
    required this.formattedValue,
  });
}

class CustomBarChartData {
  final String label;
  final double value;
  final Color color;
  final String formattedValue;

  CustomBarChartData({
    required this.label,
    required this.value,
    required this.color,
    required this.formattedValue,
  });
}

class CustomLineChartData {
  final String label;
  final double value;
  final String formattedValue;

  CustomLineChartData({
    required this.label,
    required this.value,
    required this.formattedValue,
  });
}

/// 新的组合式图表组件 - 方案B
/// 组件职责单一，结构清晰，易于维护

/// 图表头部组件
class ChartHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? action;

  const ChartHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 20, 20, 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: ChartDesignSystem.titleStyle),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(subtitle!, style: ChartDesignSystem.subtitleStyle),
                ],
              ],
            ),
          ),
          if (action != null) action!,
        ],
      ),
    );
  }
}

/// 图表内容区域组件
class ChartBody extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final double? height;

  const ChartBody({
    super.key,
    required this.child,
    this.padding,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height ?? 280,
      padding: padding ?? const EdgeInsets.fromLTRB(16, 0, 16, 20),
      decoration: const BoxDecoration(
        color: Colors.white,
      ),
      child: child,
    );
  }
}

/// 图表图例组件
class ChartLegend extends StatelessWidget {
  final List<CustomPieChartData> data;
  final int? selectedIndex;
  final Function(int)? onItemTap;

  const ChartLegend({
    super.key,
    required this.data,
    this.selectedIndex,
    this.onItemTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: data.asMap().entries.map((entry) {
          final index = entry.key;
          final item = entry.value;
          final isSelected = index == selectedIndex;
          
          return GestureDetector(
            onTap: () => onItemTap?.call(index),
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 2),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected ? item.color.withOpacity(0.1) : Colors.transparent,
                borderRadius: BorderRadius.circular(8),
                border: isSelected ? Border.all(color: item.color.withOpacity(0.3)) : null,
              ),
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
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.label,
                          style: ChartDesignSystem.labelStyle.copyWith(
                            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                          ),
                        ),
                        Text(
                          item.formattedValue,
                          style: ChartDesignSystem.labelStyle.copyWith(
                            fontSize: 11,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

/// 主要的组合式图表组件
class ChartWidget extends StatefulWidget {
  final String title;
  final String? subtitle;
  final Widget chartContent;
  final List<CustomPieChartData>? legendData;
  final bool showLegend;
  final Widget? headerAction;

  const ChartWidget({
    super.key,
    required this.title,
    this.subtitle,
    required this.chartContent,
    this.legendData,
    this.showLegend = true,
    this.headerAction,
  });

  @override
  State<ChartWidget> createState() => _ChartWidgetState();
}

class _ChartWidgetState extends State<ChartWidget> {
  int selectedIndex = -1;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 头部
          ChartHeader(
            title: widget.title,
            subtitle: widget.subtitle,
            action: widget.headerAction,
          ),
          
          // 图表内容
          ChartBody(
            height: 280,
            child: widget.chartContent,
          ),
          
          // 图例（如果启用）
          if (widget.showLegend && widget.legendData != null)
            ChartLegend(
              data: widget.legendData!,
              selectedIndex: selectedIndex,
              onItemTap: (index) {
                setState(() {
                  selectedIndex = selectedIndex == index ? -1 : index;
                });
              },
            ),
        ],
      ),
    );
  }
}