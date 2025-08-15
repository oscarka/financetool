import 'package:flutter/material.dart';
import '../widgets/chart_design_system.dart';
import '../widgets/mcp_chart_adapter.dart';

/// 深度分析页面 - 专业的MCP智能图表
class DeepAnalysisPage extends StatefulWidget {
  const DeepAnalysisPage({super.key});

  @override
  State<DeepAnalysisPage> createState() => _DeepAnalysisPageState();
}

class _DeepAnalysisPageState extends State<DeepAnalysisPage>
    with TickerProviderStateMixin {
  final TextEditingController _questionController = TextEditingController();
  final List<Widget> _charts = [];
  final List<String> _exampleQuestions = [
    '显示各平台的资产分布',
    '各资产类型的占比情况',
    '最近6个月的资产变化趋势',
    '收益率最高的投资项目',
    '各平台交易手续费对比',
    '定投计划执行情况统计',
  ];

  bool _isLoading = false;
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    );
    
    // 预加载一些示例图表
    _loadExampleCharts();
  }

  @override
  void dispose() {
    _questionController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  /// 预加载示例图表
  void _loadExampleCharts() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _generateChart('各资产类型的占比情况');
    });
  }

  /// 生成图表
  Future<void> _generateChart(String question) async {
    if (question.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final chart = await MCPChartAdapter.generateProfessionalChart(question);
      
      setState(() {
        _charts.insert(0, chart); // 最新图表显示在顶部
      });
      
      _questionController.clear();
      _fadeController.forward();
      
    } catch (e) {
      if (mounted) {
        _showErrorSnackBar('生成图表失败: $e');
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  /// 显示错误提示
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: ChartDesignSystem.danger,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: _buildAppBar(),
      body: Column(
        children: [
          _buildInputSection(),
          Expanded(
            child: _charts.isEmpty ? _buildEmptyState() : _buildChartsGrid(),
          ),
        ],
      ),
    );
  }

  /// 构建应用栏
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text(
        '深度分析',
        style: TextStyle(
          fontWeight: FontWeight.w700,
          letterSpacing: -0.5,
        ),
      ),
      backgroundColor: Colors.white,
      foregroundColor: ChartDesignSystem.primary,
      elevation: 0,
      centerTitle: true,
      actions: [
        IconButton(
          icon: const Icon(Icons.refresh),
          onPressed: _charts.isNotEmpty ? _clearCharts : null,
          tooltip: '清空图表',
        ),
        IconButton(
          icon: const Icon(Icons.help_outline),
          onPressed: _showHelpDialog,
          tooltip: '使用帮助',
        ),
      ],
    );
  }

  /// 构建输入区域
  Widget _buildInputSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 主输入框
            _buildMainInput(),
            const SizedBox(height: 16),
            
            // 示例问题
            _buildExampleQuestions(),
          ],
        ),
      ),
    );
  }

  /// 构建主输入框
  Widget _buildMainInput() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.grey[200]!,
          width: 1,
        ),
      ),
      child: TextField(
        controller: _questionController,
        decoration: InputDecoration(
          hintText: '请描述您想要分析的内容...',
          hintStyle: TextStyle(
            color: Colors.grey[500],
            fontSize: 16,
          ),
          prefixIcon: Icon(
            Icons.search,
            color: ChartDesignSystem.primary,
            size: 24,
          ),
          suffixIcon: _isLoading
              ? Container(
                  width: 24,
                  height: 24,
                  margin: const EdgeInsets.all(12),
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: ChartDesignSystem.primary,
                  ),
                )
              : IconButton(
                  icon: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      gradient: ChartDesignSystem.primaryGradient,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.auto_awesome,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                  onPressed: () => _generateChart(_questionController.text),
                ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 16,
          ),
        ),
        style: const TextStyle(fontSize: 16),
        textInputAction: TextInputAction.search,
        onSubmitted: _generateChart,
      ),
    );
  }

  /// 构建示例问题
  Widget _buildExampleQuestions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '试试这些分析:',
          style: ChartDesignSystem.labelStyle.copyWith(
            color: Colors.grey[600],
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 6,
          children: _exampleQuestions.take(4).map((question) {
            return _buildExampleChip(question);
          }).toList(),
        ),
      ],
    );
  }

  /// 构建示例芯片
  Widget _buildExampleChip(String question) {
    return InkWell(
      onTap: () => _generateChart(question),
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: ChartDesignSystem.primary.withOpacity(0.08),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: ChartDesignSystem.primary.withOpacity(0.2),
            width: 1,
          ),
        ),
        child: Text(
          question,
          style: ChartDesignSystem.labelStyle.copyWith(
            color: ChartDesignSystem.primary,
            fontWeight: FontWeight.w500,
            fontSize: 11,
          ),
        ),
      ),
    );
  }

  /// 构建图表网格
  Widget _buildChartsGrid() {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: _charts.length,
        itemBuilder: (context, index) {
          return AnimatedContainer(
            duration: ChartThemeConfig.animationDuration,
            curve: ChartThemeConfig.animationCurve,
            margin: const EdgeInsets.only(bottom: 8),
            child: _charts[index],
          );
        },
      ),
    );
  }

  /// 构建空状态
  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 插图
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    ChartDesignSystem.primary.withOpacity(0.1),
                    ChartDesignSystem.secondary.withOpacity(0.1),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(60),
              ),
              child: Icon(
                Icons.analytics_outlined,
                size: 60,
                color: ChartDesignSystem.primary,
              ),
            ),
            
            const SizedBox(height: 24),
            
            // 主标题
            Text(
              'AI 深度分析',
              style: ChartDesignSystem.titleStyle.copyWith(
                fontSize: 24,
                color: Colors.grey[800],
              ),
            ),
            
            const SizedBox(height: 8),
            
            // 副标题
            Text(
              '输入您的问题，AI 将为您生成专业的数据分析图表',
              style: ChartDesignSystem.subtitleStyle,
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 32),
            
            // 功能亮点
            _buildFeatureHighlights(),
          ],
        ),
      ),
    );
  }

  /// 构建功能亮点
  Widget _buildFeatureHighlights() {
    final features = [
      {
        'icon': Icons.auto_awesome,
        'title': '智能分析',
        'description': '自然语言理解',
      },
      {
        'icon': Icons.insert_chart,
        'title': '多种图表',
        'description': '饼图、柱图、折线图',
      },
      {
        'icon': Icons.speed,
        'title': '实时响应',
        'description': '快速生成结果',
      },
    ];

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: features.map((feature) {
        return Column(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: ChartDesignSystem.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(
                feature['icon'] as IconData,
                color: ChartDesignSystem.primary,
                size: 24,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              feature['title'] as String,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              feature['description'] as String,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontSize: 10,
                color: Colors.grey[500],
              ),
            ),
          ],
        );
      }).toList(),
    );
  }

  /// 清空图表
  void _clearCharts() {
    setState(() {
      _charts.clear();
    });
    _fadeController.reset();
  }

  /// 显示帮助对话框
  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Icon(
              Icons.help_outline,
              color: ChartDesignSystem.primary,
            ),
            const SizedBox(width: 8),
            const Text('使用帮助'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHelpItem('📊 资产分布', '查看各平台、类型的资产占比'),
            _buildHelpItem('📈 趋势分析', '了解资产价值的变化趋势'),
            _buildHelpItem('💰 收益统计', '分析投资收益和盈亏情况'),
            _buildHelpItem('📋 明细查询', '获取详细的数据列表'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              '知道了',
              style: TextStyle(color: ChartDesignSystem.primary),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建帮助项
  Widget _buildHelpItem(String title, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: ChartDesignSystem.labelStyle.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          Text(
            description,
            style: ChartDesignSystem.labelStyle.copyWith(
              color: Colors.grey[600],
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}