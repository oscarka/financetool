import 'package:flutter/material.dart';
import '../widgets/chart_design_system.dart';

/// 图表展示页面 - 展示各种类型的专业图表
class ChartShowcasePage extends StatefulWidget {
  const ChartShowcasePage({super.key});

  @override
  State<ChartShowcasePage> createState() => _ChartShowcasePageState();
}

class _ChartShowcasePageState extends State<ChartShowcasePage>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          '图表展示',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            letterSpacing: -0.5,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: ChartDesignSystem.primary,
        elevation: 0,
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          labelColor: ChartDesignSystem.primary,
          unselectedLabelColor: Colors.grey[600],
          indicatorColor: ChartDesignSystem.primary,
          tabs: const [
            Tab(text: '饼图'),
            Tab(text: '柱状图'),
            Tab(text: '折线图'),
            Tab(text: '综合展示'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildPieChartsTab(),
          _buildBarChartsTab(),
          _buildLineChartsTab(),
          _buildComprehensiveTab(),
        ],
      ),
    );
  }

  /// 饼图展示页
  Widget _buildPieChartsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        children: [
          // 资产分布饼图
          ProfessionalPieChart(
            data: [
              PieChartData(
                label: '基金投资',
                value: 158460.30,
                percentage: 68.5,
                color: ChartDesignSystem.primary,
                formattedValue: '15.85万',
              ),
              PieChartData(
                label: '外汇资产',
                value: 45230.50,
                percentage: 19.6,
                color: ChartDesignSystem.secondary,
                formattedValue: '4.52万',
              ),
              PieChartData(
                label: '数字货币',
                value: 18960.20,
                percentage: 8.2,
                color: ChartDesignSystem.accent,
                formattedValue: '1.90万',
              ),
              PieChartData(
                label: '股票投资',
                value: 8580.75,
                percentage: 3.7,
                color: ChartDesignSystem.warning,
                formattedValue: '8581',
              ),
            ],
            title: '资产类型分布',
            subtitle: '各类投资资产占比分析',
            showLegend: true,
            showValues: true,
          ),

          const SizedBox(height: 16),

          // 平台分布饼图
          ProfessionalPieChart(
            data: [
              PieChartData(
                label: '支付宝',
                value: 125680.40,
                percentage: 54.3,
                color: const Color(0xFF1677FF),
                formattedValue: '12.57万',
              ),
              PieChartData(
                label: 'Wise',
                value: 67890.20,
                percentage: 29.3,
                color: const Color(0xFF00D4AA),
                formattedValue: '6.79万',
              ),
              PieChartData(
                label: 'IBKR',
                value: 25430.15,
                percentage: 11.0,
                color: const Color(0xFF722ED1),
                formattedValue: '2.54万',
              ),
              PieChartData(
                label: 'OKX',
                value: 12580.90,
                percentage: 5.4,
                color: const Color(0xFFFA8C16),
                formattedValue: '1.26万',
              ),
            ],
            title: '平台资产分布',
            subtitle: '各投资平台资产分配情况',
            showLegend: true,
            showValues: true,
          ),

          const SizedBox(height: 16),

          // 小尺寸饼图示例
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Expanded(
                  child: _buildMiniPieChart(
                    '基金类型',
                    [
                      PieChartData(label: '股票型', value: 60, percentage: 60, color: ChartDesignSystem.primary, formattedValue: '60%'),
                      PieChartData(label: '债券型', value: 25, percentage: 25, color: ChartDesignSystem.secondary, formattedValue: '25%'),
                      PieChartData(label: '混合型', value: 15, percentage: 15, color: ChartDesignSystem.accent, formattedValue: '15%'),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildMiniPieChart(
                    '风险分布',
                    [
                      PieChartData(label: '低风险', value: 35, percentage: 35, color: ChartDesignSystem.secondary, formattedValue: '35%'),
                      PieChartData(label: '中风险', value: 45, percentage: 45, color: ChartDesignSystem.warning, formattedValue: '45%'),
                      PieChartData(label: '高风险', value: 20, percentage: 20, color: ChartDesignSystem.danger, formattedValue: '20%'),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 柱状图展示页
  Widget _buildBarChartsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        children: [
          // 平台对比柱状图
          ProfessionalBarChart(
            data: [
              BarChartData(
                label: '支付宝',
                value: 125680.40,
                color: ChartDesignSystem.primary,
                formattedValue: '12.57万',
              ),
              BarChartData(
                label: 'Wise',
                value: 67890.20,
                color: ChartDesignSystem.secondary,
                formattedValue: '6.79万',
              ),
              BarChartData(
                label: 'IBKR',
                value: 25430.15,
                color: ChartDesignSystem.accent,
                formattedValue: '2.54万',
              ),
              BarChartData(
                label: 'OKX',
                value: 12580.90,
                color: ChartDesignSystem.warning,
                formattedValue: '1.26万',
              ),
            ],
            title: '平台资产对比',
            subtitle: '各投资平台的资产价值比较',
            showGrid: true,
          ),

          const SizedBox(height: 16),

          // 月度收益柱状图
          ProfessionalBarChart(
            data: [
              BarChartData(
                label: '1月',
                value: 8250.30,
                color: ChartDesignSystem.secondary,
                formattedValue: '8250',
              ),
              BarChartData(
                label: '2月',
                value: -2150.80,
                color: ChartDesignSystem.danger,
                formattedValue: '-2151',
              ),
              BarChartData(
                label: '3月',
                value: 12680.40,
                color: ChartDesignSystem.secondary,
                formattedValue: '1.27万',
              ),
              BarChartData(
                label: '4月',
                value: 5420.90,
                color: ChartDesignSystem.secondary,
                formattedValue: '5421',
              ),
              BarChartData(
                label: '5月',
                value: -890.20,
                color: ChartDesignSystem.danger,
                formattedValue: '-890',
              ),
              BarChartData(
                label: '6月',
                value: 15240.60,
                color: ChartDesignSystem.secondary,
                formattedValue: '1.52万',
              ),
            ],
            title: '月度收益分析',
            subtitle: '近6个月的投资收益情况',
            showGrid: true,
          ),

          const SizedBox(height: 16),

          // 资产类型对比
          ProfessionalBarChart(
            data: [
              BarChartData(
                label: '基金',
                value: 158460.30,
                color: const Color(0xFF1890FF),
                formattedValue: '15.85万',
              ),
              BarChartData(
                label: '外汇',
                value: 45230.50,
                color: const Color(0xFF52C41A),
                formattedValue: '4.52万',
              ),
              BarChartData(
                label: '股票',
                value: 28960.20,
                color: const Color(0xFF722ED1),
                formattedValue: '2.90万',
              ),
              BarChartData(
                label: '数字货币',
                value: 18580.75,
                color: const Color(0xFFFA8C16),
                formattedValue: '1.86万',
              ),
              BarChartData(
                label: '债券',
                value: 12340.10,
                color: const Color(0xFFEB2F96),
                formattedValue: '1.23万',
              ),
            ],
            title: '资产类型价值对比',
            subtitle: '不同投资类型的价值分布',
            showGrid: true,
          ),
        ],
      ),
    );
  }

  /// 折线图展示页
  Widget _buildLineChartsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        children: [
          // 资产趋势图
          ProfessionalLineChart(
            data: [
              LineChartData(label: '1月', value: 180000, formattedValue: '18万'),
              LineChartData(label: '2月', value: 185000, formattedValue: '18.5万'),
              LineChartData(label: '3月', value: 178000, formattedValue: '17.8万'),
              LineChartData(label: '4月', value: 192000, formattedValue: '19.2万'),
              LineChartData(label: '5月', value: 205000, formattedValue: '20.5万'),
              LineChartData(label: '6月', value: 231581, formattedValue: '23.16万'),
            ],
            title: '资产价值趋势',
            subtitle: '近6个月总资产价值变化',
            showDots: true,
            showArea: true,
            lineColor: ChartDesignSystem.secondary,
          ),

          const SizedBox(height: 16),

          // 基金净值走势
          ProfessionalLineChart(
            data: [
              LineChartData(label: '1/1', value: 2.1580, formattedValue: '2.158'),
              LineChartData(label: '1/2', value: 2.1624, formattedValue: '2.162'),
              LineChartData(label: '1/3', value: 2.1456, formattedValue: '2.146'),
              LineChartData(label: '1/4', value: 2.1789, formattedValue: '2.179'),
              LineChartData(label: '1/5', value: 2.1923, formattedValue: '2.192'),
              LineChartData(label: '1/6', value: 2.2045, formattedValue: '2.205'),
              LineChartData(label: '1/7', value: 2.1987, formattedValue: '2.199'),
              LineChartData(label: '1/8', value: 2.2156, formattedValue: '2.216'),
            ],
            title: '基金净值走势',
            subtitle: '易方达蓝筹精选混合基金净值变化',
            showDots: true,
            showArea: true,
            lineColor: ChartDesignSystem.primary,
          ),

          const SizedBox(height: 16),

          // 收益率对比
          ProfessionalLineChart(
            data: [
              LineChartData(label: 'Q1', value: 8.5, formattedValue: '8.5%'),
              LineChartData(label: 'Q2', value: -2.3, formattedValue: '-2.3%'),
              LineChartData(label: 'Q3', value: 12.8, formattedValue: '12.8%'),
              LineChartData(label: 'Q4', value: 6.7, formattedValue: '6.7%'),
            ],
            title: '季度收益率',
            subtitle: '各季度投资收益率表现',
            showDots: true,
            showArea: false,
            lineColor: ChartDesignSystem.accent,
          ),
        ],
      ),
    );
  }

  /// 综合展示页
  Widget _buildComprehensiveTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        children: [
          // 概览卡片
          _buildOverviewCards(),

          const SizedBox(height: 16),

          // 组合图表
          ProfessionalPieChart(
            data: [
              PieChartData(
                label: '稳健型',
                value: 45.2,
                percentage: 45.2,
                color: ChartDesignSystem.secondary,
                formattedValue: '45.2%',
              ),
              PieChartData(
                label: '平衡型',
                value: 35.8,
                percentage: 35.8,
                color: ChartDesignSystem.primary,
                formattedValue: '35.8%',
              ),
              PieChartData(
                label: '进取型',
                value: 19.0,
                percentage: 19.0,
                color: ChartDesignSystem.warning,
                formattedValue: '19.0%',
              ),
            ],
            title: '投资风格分布',
            subtitle: '基于风险偏好的资产配置',
            showLegend: true,
            showValues: true,
          ),

          const SizedBox(height: 16),

          // 表格数据展示
          _buildDataTable(),
        ],
      ),
    );
  }

  /// 构建概览卡片
  Widget _buildOverviewCards() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: _buildStatsCard(
              '总资产',
              '¥231,581',
              '+12.5%',
              ChartDesignSystem.secondary,
              Icons.account_balance_wallet,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatsCard(
              '今日收益',
              '¥+1,245',
              '+0.54%',
              ChartDesignSystem.secondary,
              Icons.trending_up,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatsCard(
              '持仓数量',
              '12',
              '+2',
              ChartDesignSystem.primary,
              Icons.pie_chart,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建统计卡片
  Widget _buildStatsCard(String title, String value, String change, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: ChartDesignSystem.labelStyle.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: ChartDesignSystem.valueStyle.copyWith(
              fontSize: 18,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            change,
            style: ChartDesignSystem.labelStyle.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建迷你饼图
  Widget _buildMiniPieChart(String title, List<PieChartData> data) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Column(
        children: [
          Text(
            title,
            style: ChartDesignSystem.titleStyle.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 120,
            child: PieChart(
              PieChartData(
                sectionsSpace: 2,
                centerSpaceRadius: 25,
                sections: data.map((item) {
                  return PieChartSectionData(
                    color: item.color,
                    value: item.value,
                    title: '${item.percentage.toInt()}%',
                    radius: 35,
                    titleStyle: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
          const SizedBox(height: 12),
          ...data.map((item) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: item.color,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    item.label,
                    style: ChartDesignSystem.labelStyle.copyWith(fontSize: 10),
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  /// 构建数据表格
  Widget _buildDataTable() {
    return StandardChartContainer(
      title: '持仓明细',
      subtitle: '当前投资组合详细信息',
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(Colors.grey[50]),
          columns: const [
            DataColumn(label: Text('资产名称')),
            DataColumn(label: Text('平台')),
            DataColumn(label: Text('当前价值')),
            DataColumn(label: Text('收益率')),
            DataColumn(label: Text('状态')),
          ],
          rows: [
            _buildDataRow('易方达蓝筹精选', '支付宝', '¥85,230', '+6.54%', true),
            _buildDataRow('美元现金', 'Wise', '¥6,458', '-0.64%', false),
            _buildDataRow('苹果股票', 'IBKR', '¥420', '+10.61%', true),
            _buildDataRow('比特币', 'OKX', '¥1,206', '+20.57%', true),
            _buildDataRow('欧元现金', 'Wise', '¥1,700', '+2.15%', true),
          ],
        ),
      ),
    );
  }

  /// 构建数据行
  DataRow _buildDataRow(String name, String platform, String value, String rate, bool isPositive) {
    return DataRow(
      cells: [
        DataCell(Text(name, style: ChartDesignSystem.labelStyle)),
        DataCell(Text(platform, style: ChartDesignSystem.labelStyle)),
        DataCell(Text(value, style: ChartDesignSystem.valueStyle.copyWith(fontSize: 14))),
        DataCell(
          Text(
            rate,
            style: ChartDesignSystem.labelStyle.copyWith(
              color: isPositive ? ChartDesignSystem.secondary : ChartDesignSystem.danger,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        DataCell(
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: isPositive ? ChartDesignSystem.secondary.withOpacity(0.1) : ChartDesignSystem.danger.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              isPositive ? '盈利' : '亏损',
              style: ChartDesignSystem.labelStyle.copyWith(
                fontSize: 10,
                color: isPositive ? ChartDesignSystem.secondary : ChartDesignSystem.danger,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ],
    );
  }
}