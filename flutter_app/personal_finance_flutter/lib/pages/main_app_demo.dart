import 'package:flutter/material.dart';
import '../widgets/chart_design_system.dart';
import '../widgets/ai_chat_widget.dart';
import 'chart_showcase_page.dart';
import 'deep_analysis_page.dart';

/// 主应用演示页面 - 展示聊天和图表功能的完整集成
class MainAppDemo extends StatefulWidget {
  const MainAppDemo({super.key});

  @override
  State<MainAppDemo> createState() => _MainAppDemoState();
}

class _MainAppDemoState extends State<MainAppDemo> {
  int _currentIndex = 0;
  final List<Widget> _savedCharts = [];
  final List<String> _savedQuestions = [];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          _buildHomePage(),
          _buildDeepAnalysisPage(),
          _buildChatPage(),
          const ChartShowcasePage(),
        ],
      ),
      bottomNavigationBar: _buildBottomNavigationBar(),
      floatingActionButton: _buildFloatingActionButton(),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }

  /// 构建首页
  Widget _buildHomePage() {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          '个人金融仪表板',
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
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 欢迎区域
            _buildWelcomeCard(),
            
            const SizedBox(height: 20),
            
            // 快速操作
            _buildQuickActions(),
            
            const SizedBox(height: 20),
            
            // 最近生成的图表
            if (_savedCharts.isNotEmpty) _buildRecentCharts(),
            
            const SizedBox(height: 20),
            
            // 功能介绍
            _buildFeatureIntro(),
          ],
        ),
      ),
    );
  }

  /// 构建深度分析页面
  Widget _buildDeepAnalysisPage() {
    return DeepAnalysisPageWithCharts(
      savedCharts: _savedCharts,
      savedQuestions: _savedQuestions,
    );
  }

  /// 构建聊天页面
  Widget _buildChatPage() {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          'AI财务助手',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            letterSpacing: -0.5,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: ChartDesignSystem.primary,
        elevation: 0,
        centerTitle: true,
      ),
      body: AIChatWidget(
        onChartGenerated: _handleChartGenerated,
        placeholder: '问我任何财务问题，我会为您生成专业图表...',
      ),
    );
  }

  /// 处理图表生成
  void _handleChartGenerated(Widget chart, String question) {
    setState(() {
      _savedCharts.insert(0, chart);
      _savedQuestions.insert(0, question);
      
      // 限制保存的图表数量
      if (_savedCharts.length > 10) {
        _savedCharts.removeLast();
        _savedQuestions.removeLast();
      }
    });
  }

  /// 构建欢迎卡片
  Widget _buildWelcomeCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            ChartDesignSystem.primary,
            ChartDesignSystem.primary.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: ChartDesignSystem.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '欢迎使用AI图表分析',
                      style: ChartDesignSystem.titleStyle.copyWith(
                        color: Colors.white,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '智能数据分析，专业图表生成',
                      style: ChartDesignSystem.subtitleStyle.copyWith(
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            '与AI对话生成专业图表，深度分析您的财务数据',
            style: ChartDesignSystem.labelStyle.copyWith(
              color: Colors.white.withOpacity(0.8),
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建快速操作
  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '快速操作',
          style: ChartDesignSystem.titleStyle.copyWith(fontSize: 18),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                '开始对话',
                '与AI助手交流',
                Icons.chat_bubble_outline,
                ChartDesignSystem.primary,
                () => setState(() => _currentIndex = 2),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildActionCard(
                '图表展示',
                '查看所有图表类型',
                Icons.insert_chart,
                ChartDesignSystem.secondary,
                () => setState(() => _currentIndex = 3),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                '深度分析',
                '查看保存的分析',
                Icons.analytics,
                ChartDesignSystem.accent,
                () => setState(() => _currentIndex = 1),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildActionCard(
                '数据导入',
                '导入财务数据',
                Icons.upload_file,
                ChartDesignSystem.warning,
                () => _showDataImportDialog(),
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// 构建操作卡片
  Widget _buildActionCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontSize: 11,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  /// 构建最近图表
  Widget _buildRecentCharts() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '最近生成的图表',
              style: ChartDesignSystem.titleStyle.copyWith(fontSize: 18),
            ),
            const Spacer(),
            TextButton(
              onPressed: () => setState(() => _currentIndex = 1),
              child: Text(
                '查看全部',
                style: TextStyle(color: ChartDesignSystem.primary),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 120,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _savedCharts.length.clamp(0, 3),
            itemBuilder: (context, index) {
              return Container(
                width: 200,
                margin: const EdgeInsets.only(right: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: ChartDesignSystem.cardShadow,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Container(
                        decoration: const BoxDecoration(
                          color: Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.vertical(
                            top: Radius.circular(12),
                          ),
                        ),
                        child: const Center(
                          child: Icon(
                            Icons.insert_chart,
                            size: 40,
                            color: Colors.grey,
                          ),
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(
                        _savedQuestions[index],
                        style: ChartDesignSystem.labelStyle.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  /// 构建功能介绍
  Widget _buildFeatureIntro() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '功能亮点',
          style: ChartDesignSystem.titleStyle.copyWith(fontSize: 18),
        ),
        const SizedBox(height: 16),
        
        _buildFeatureItem(
          Icons.psychology,
          'AI智能分析',
          '自然语言理解，智能生成专业图表',
          ChartDesignSystem.primary,
        ),
        _buildFeatureItem(
          Icons.palette,
          '专业设计',
          '金融级视觉标准，统一设计语言',
          ChartDesignSystem.secondary,
        ),
        _buildFeatureItem(
          Icons.speed,
          '实时响应',
          '快速处理，流畅交互体验',
          ChartDesignSystem.accent,
        ),
        _buildFeatureItem(
          Icons.save,
          '保存分析',
          '一键保存图表，随时查看历史分析',
          ChartDesignSystem.warning,
        ),
      ],
    );
  }

  /// 构建功能项
  Widget _buildFeatureItem(IconData icon, String title, String description, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: ChartDesignSystem.labelStyle.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: ChartDesignSystem.labelStyle.copyWith(
                    fontSize: 12,
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

  /// 构建底部导航栏
  Widget _buildBottomNavigationBar() {
    return BottomAppBar(
      shape: const CircularNotchedRectangle(),
      notchMargin: 8,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildBottomNavItem(
            icon: Icons.home_outlined,
            activeIcon: Icons.home,
            label: '首页',
            index: 0,
          ),
          _buildBottomNavItem(
            icon: Icons.analytics_outlined,
            activeIcon: Icons.analytics,
            label: '深度分析',
            index: 1,
          ),
          const SizedBox(width: 40), // FAB空间
          _buildBottomNavItem(
            icon: Icons.chat_outlined,
            activeIcon: Icons.chat,
            label: 'AI助手',
            index: 2,
          ),
          _buildBottomNavItem(
            icon: Icons.insert_chart_outlined,
            activeIcon: Icons.insert_chart,
            label: '图表展示',
            index: 3,
          ),
        ],
      ),
    );
  }

  /// 构建底部导航项
  Widget _buildBottomNavItem({
    required IconData icon,
    required IconData activeIcon,
    required String label,
    required int index,
  }) {
    final isActive = _currentIndex == index;
    
    return InkWell(
      onTap: () => setState(() => _currentIndex = index),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isActive ? activeIcon : icon,
              color: isActive ? ChartDesignSystem.primary : Colors.grey[600],
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: isActive ? ChartDesignSystem.primary : Colors.grey[600],
                fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建悬浮按钮
  Widget _buildFloatingActionButton() {
    return FloatingActionButton(
      onPressed: _showAIChatModal,
      backgroundColor: ChartDesignSystem.primary,
      child: const Icon(Icons.auto_awesome, color: Colors.white),
    );
  }

  /// 显示AI聊天模态框
  void _showAIChatModal() {
    AIChatModal.show(
      context,
      onChartGenerated: _handleChartGenerated,
      placeholder: '问我任何财务问题，我会为您生成专业图表...',
    );
  }

  /// 显示数据导入对话框
  void _showDataImportDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Icon(Icons.upload_file, color: ChartDesignSystem.primary),
            const SizedBox(width: 8),
            const Text('数据导入'),
          ],
        ),
        content: const Text('数据导入功能正在开发中，敬请期待！\n\n即将支持：\n• Excel文件导入\n• CSV数据导入\n• API数据同步'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              '了解了',
              style: TextStyle(color: ChartDesignSystem.primary),
            ),
          ),
        ],
      ),
    );
  }
}

/// 带有保存图表功能的深度分析页面
class DeepAnalysisPageWithCharts extends StatelessWidget {
  final List<Widget> savedCharts;
  final List<String> savedQuestions;

  const DeepAnalysisPageWithCharts({
    super.key,
    required this.savedCharts,
    required this.savedQuestions,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
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
            onPressed: savedCharts.isNotEmpty ? () {} : null,
            tooltip: '刷新分析',
          ),
        ],
      ),
      body: savedCharts.isEmpty 
          ? _buildEmptyState(context)
          : _buildChartsGrid(),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.analytics_outlined,
              size: 80,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              '还没有保存的分析',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.grey,
              ),
            ),
            SizedBox(height: 8),
            Text(
              '与AI对话生成图表后，即可在这里查看保存的分析',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartsGrid() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: savedCharts.length,
      itemBuilder: (context, index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          child: savedCharts[index],
        );
      },
    );
  }
}