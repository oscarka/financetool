import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'services/api_client.dart';
import 'models/asset_stats.dart';
import 'models/trend_data.dart';
// 导入新的图表系统
import 'pages/main_app_demo.dart';

void main() {
  runApp(const PersonalFinanceApp());
}

class PersonalFinanceApp extends StatelessWidget {
  const PersonalFinanceApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '个人金融仪表板',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF10B981),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF6F7FB),
      ),
      // 使用新的主应用演示作为首页
      home: const AppSelectionPage(),
    );
  }
}

/// 应用选择页面 - 可以选择原有应用或新的图表系统
class AppSelectionPage extends StatelessWidget {
  const AppSelectionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F7FB),
      appBar: AppBar(
        title: const Text(
          '个人金融应用',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            letterSpacing: -0.5,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF10B981),
        elevation: 0,
        centerTitle: true,
      ),
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 应用图标
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF10B981), Color(0xFF059669)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF10B981).withOpacity(0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.account_balance_wallet,
                  color: Colors.white,
                  size: 60,
                ),
              ),
              
              const SizedBox(height: 32),
              
              // 标题
              const Text(
                '个人金融管理系统',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 12),
              
              const Text(
                '选择您要使用的应用版本',
                style: TextStyle(
                  fontSize: 16,
                  color: Color(0xFF6B7280),
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 48),
              
              // 应用选项
              Column(
                children: [
                  _buildAppOption(
                    context,
                    title: '🚀 新版 AI智能图表系统',
                    subtitle: '体验双重确认的AI图表生成流程',
                    description: '• AI意图识别\n• 智能图表生成\n• 专业视觉设计\n• 双重确认机制',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const MainAppDemo(),
                        ),
                      );
                    },
                    isPrimary: true,
                  ),
                  
                  const SizedBox(height: 20),
                  
                  _buildAppOption(
                    context,
                    title: '📊 原版 资产管理仪表板',
                    subtitle: '查看传统的资产数据和统计信息',
                    description: '• 资产统计\n• 趋势图表\n• 数据展示\n• API集成',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const AssetHomePage(),
                        ),
                      );
                    },
                    isPrimary: false,
                  ),
                ],
              ),
              
              const SizedBox(height: 48),
              
              // 提示信息
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF10B981).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFF10B981).withOpacity(0.2),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      color: const Color(0xFF10B981),
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        '推荐使用新版AI智能图表系统，体验完整的图表生成和保存流程',
                        style: TextStyle(
                          fontSize: 14,
                          color: const Color(0xFF10B981).withAlpha(200),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppOption(
    BuildContext context, {
    required String title,
    required String subtitle,
    required String description,
    required VoidCallback onTap,
    required bool isPrimary,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isPrimary 
                ? const Color(0xFF10B981) 
                : Colors.grey[300]!,
            width: isPrimary ? 2 : 1,
          ),
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
            Row(
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: isPrimary 
                          ? const Color(0xFF10B981) 
                          : const Color(0xFF1F2937),
                    ),
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  color: isPrimary 
                      ? const Color(0xFF10B981) 
                      : Colors.grey[400],
                  size: 18,
                ),
              ],
            ),
            
            const SizedBox(height: 8),
            
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 14,
                color: Color(0xFF6B7280),
              ),
            ),
            
            const SizedBox(height: 16),
            
            Text(
              description,
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF9CA3AF),
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// 保留原有的AssetHomePage类
class AssetHomePage extends StatefulWidget {
  const AssetHomePage({super.key});

  @override
  State<AssetHomePage> createState() => _AssetHomePageState();
}

class _AssetHomePageState extends State<AssetHomePage> {
  String selectedCurrency = 'USD';
  bool showCurrencyDropdown = false;
  bool isDataVisible = true;
  
  // 数据状态
  AssetStats? assetStats;
  List<TrendData> trendData = [];
  List<Map<String, dynamic>> assetSnapshots = [];
  bool isLoading = true;
  String? errorMessage;
  String? largestHolding;
  String riskLevel = "中等";

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      // 并行加载聚合统计、趋势数据、最大持仓和资产快照
      final futures = await Future.wait([
        ApiClient.getAggregatedStats(selectedCurrency),
        ApiClient.getAssetTrend(2, selectedCurrency), // 获取2天数据用于计算24小时变化
        ApiClient.getLargestHolding(selectedCurrency),
        ApiClient.getAssetSnapshots(selectedCurrency),
      ]);

      final statsJson = futures[0] as Map<String, dynamic>;
      final trendJson = futures[1] as List<Map<String, dynamic>>;
      final largestHoldingResult = futures[2] as String?;
      final snapshotsResult = futures[3] as List<Map<String, dynamic>>;

      // 计算24小时变化
      final trendDataList = trendJson.map((json) => TrendData.fromJson(json)).toList();
      double? dailyChangePercentage = TrendData.calculateDailyChangePercentage(trendDataList);
      double? dailyProfit = TrendData.calculateDailyProfit(trendDataList);

      // 如果没有足够的历史数据，显示0
      if (dailyChangePercentage == null || trendDataList.length < 2) {
        dailyChangePercentage = 0.0;
        dailyProfit = 0.0;
        print('历史数据不足，24小时变化和今日收益显示为0');
      }

      // 使用快照数据计算总资产价值，确保数据一致性
      final totalValueFromSnapshots = snapshotsResult.fold<double>(0.0, (sum, snapshot) {
        final baseValue = snapshot['base_value'];
        if (baseValue == null) return sum;
        return sum + (baseValue is num ? baseValue.toDouble() : 0.0);
      });
      
      // 更新统计数据，使用快照数据的总价值
      statsJson['total_value'] = totalValueFromSnapshots;
      statsJson['daily_change_percentage'] = dailyChangePercentage;
      statsJson['daily_profit'] = dailyProfit;

      setState(() {
        assetStats = AssetStats.fromJson(statsJson);
        trendData = trendDataList;
        assetSnapshots = snapshotsResult;
        largestHolding = largestHoldingResult ?? "BTC";
        riskLevel = _calculateRiskLevelFromSnapshots(snapshotsResult);
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = '数据加载失败: $e';
        isLoading = false;
      });
      print('数据加载错误: $e');
    }
  }

  String _calculateRiskLevelFromSnapshots(List<Map<String, dynamic>> snapshots) {
    if (snapshots.isEmpty) {
      return "中等";
    }

    // 按资产类型分组并计算总值
    final Map<String, double> assetTypeTotals = {};
    for (final snapshot in snapshots) {
      final assetType = snapshot['asset_type'] as String;
      final baseValue = snapshot['base_value'];
      final double value = baseValue is num ? baseValue.toDouble() : 0.0;
      assetTypeTotals[assetType] = (assetTypeTotals[assetType] ?? 0.0) + value;
    }

    final totalValue = assetTypeTotals.values.fold(0.0, (sum, value) => sum + value);
    
    if (totalValue == 0) return "中等";

    // 计算各资产类型占比
    final digitalCurrencyRatio = (assetTypeTotals['数字货币'] ?? 0) / totalValue;
    final stockRatio = (assetTypeTotals['证券'] ?? 0) / totalValue;
    final fundRatio = (assetTypeTotals['基金'] ?? assetTypeTotals['fund'] ?? 0) / totalValue;
    final forexRatio = (assetTypeTotals['外汇'] ?? 0) / totalValue;
    
    // 风险评分算法
    double riskScore = 0;
    
    // 数字货币权重最高 (高风险)
    riskScore += digitalCurrencyRatio * 0.8;
    
    // 股票投资权重较高 (中高风险)
    riskScore += stockRatio * 0.6;
    
    // 基金投资权重中等 (中风险)
    riskScore += fundRatio * 0.4;
    
    // 外汇权重较低 (中低风险)
    riskScore += forexRatio * 0.3;
    
    // 根据风险评分返回等级
    if (riskScore >= 0.6) return "高风险";
    if (riskScore >= 0.4) return "中高风险";
    if (riskScore >= 0.2) return "中等";
    if (riskScore >= 0.1) return "中低风险";
    return "低风险";
  }

  void _toggleCurrencyDropdown() {
    setState(() {
      showCurrencyDropdown = !showCurrencyDropdown;
    });
  }

  void _selectCurrency(String currency) {
    setState(() {
      selectedCurrency = currency;
      showCurrencyDropdown = false;
    });
    _loadData(); // 重新加载数据
  }

  void _toggleDataVisibility() {
    setState(() {
      isDataVisible = !isDataVisible;
    });
  }

  Widget _buildCurrencyOption(String currency, {bool isMore = false}) {
    final isSelected = selectedCurrency == currency;
    return GestureDetector(
      onTap: () {
        if (!isMore) {
          _selectCurrency(currency);
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white.withOpacity(0.1) : Colors.transparent,
          borderRadius: BorderRadius.circular(4),
        ),
        child: Row(
          children: [
            Text(
              currency,
              style: TextStyle(
                color: isMore ? Colors.grey : Colors.white,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            if (isSelected && !isMore)
              const Padding(
                padding: EdgeInsets.only(left: 8),
                child: Icon(Icons.check, color: Colors.green, size: 16),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomNavigation() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              _buildNavItem(Icons.home, '首页', 0, true),
              _buildNavItem(Icons.show_chart, '行情', 1, false),
              _buildAICenterButton(),
              _buildNavItem(Icons.account_balance_wallet, '资产', 3, false),
              _buildNavItem(Icons.person, '我的', 4, false),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index, bool isSelected) {
    return Expanded(
      child: GestureDetector(
        onTap: () {
          // 这里可以添加页面切换逻辑
        },
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? const Color(0xFF10B981) : const Color(0xFF64748B),
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: isSelected ? const Color(0xFF10B981) : const Color(0xFF64748B),
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAICenterButton() {
    return Expanded(
      child: GestureDetector(
        onTap: () {
          // AI功能触发逻辑
        },
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF10B981),
                    Color(0xFF059669),
                  ],
                ),
                borderRadius: BorderRadius.circular(28),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF10B981).withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(
                Icons.psychology,
                color: Colors.white,
                size: 28,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'AI',
              style: TextStyle(
                fontSize: 12,
                color: Color(0xFF10B981),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAssetCard() {
    if (isLoading) {
      return Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          color: const Color(0xFF1E1F24),
        ),
        padding: const EdgeInsets.all(20),
        child: const Center(
          child: CircularProgressIndicator(
            color: Colors.white,
          ),
        ),
      );
    }

    if (errorMessage != null) {
      return Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          color: const Color(0xFF1E1F24),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 8),
            Text(
              errorMessage!,
              style: const TextStyle(color: Colors.white70),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadData,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (assetStats == null) {
      return Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          color: const Color(0xFF1E1F24),
        ),
        padding: const EdgeInsets.all(20),
        child: const Center(
          child: Text(
            '暂无数据',
            style: TextStyle(color: Colors.white70),
          ),
        ),
      );
    }

    return Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                color: const Color(0xFF1E1F24),
              ),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Text('总资产估值', style: TextStyle(color: Colors.white70)),
                      const SizedBox(width: 8),
                      GestureDetector(
                        onTap: _toggleCurrencyDropdown,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(selectedCurrency, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                            const SizedBox(width: 4),
                            Icon(
                              showCurrencyDropdown ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                              color: Colors.white54,
                              size: 16,
                            ),
                          ],
                        ),
                      ),
                      const Spacer(),
              GestureDetector(
                onTap: _toggleDataVisibility,
                child: Icon(
                  isDataVisible ? Icons.remove_red_eye_outlined : Icons.visibility_off_outlined,
                  color: Colors.white54,
                ),
              ),
                    ],
                  ),
                  if (showCurrencyDropdown)
                    Container(
                      margin: const EdgeInsets.only(top: 8),
                      decoration: BoxDecoration(
                        color: const Color(0xFF2A2A2A),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.white.withOpacity(0.1)),
                      ),
                      child: Column(
                        children: [
                          _buildCurrencyOption('CNY'),
                          _buildCurrencyOption('USD'),
                          _buildCurrencyOption('USDT'),
                          _buildCurrencyOption('BTC'),
                          _buildCurrencyOption('更多 >', isMore: true),
                        ],
                      ),
                    ),
                  const SizedBox(height: 10),
          Text(
            isDataVisible 
              ? assetStats!.formatCurrency(assetStats!.totalValue, selectedCurrency)
              : '*****',
            style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
            children: [
              Icon(
                assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
                  ? (assetStats!.dailyChangePercent! >= 0 ? Icons.arrow_upward : Icons.arrow_downward)
                  : Icons.remove,
                size: 14,
                color: assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
                  ? (assetStats!.dailyChangePercent! >= 0 ? Colors.green : Colors.red)
                  : Colors.grey,
              ),
              const SizedBox(width: 4),
                      Text(
                assetStats!.dailyChangePercent != null
                  ? '${assetStats!.dailyChangePercent! >= 0 ? '+' : ''}${assetStats!.dailyChangePercent!.toStringAsFixed(2)}%'
                  : '0.00%',
                style: TextStyle(
                  color: assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
                    ? (assetStats!.dailyChangePercent! >= 0 ? Colors.green : Colors.red)
                    : Colors.grey,
                ),
              ),
              const SizedBox(width: 6),
              const Text('24h', style: TextStyle(color: Colors.white38)),
                    ],
                  ),
                  const Divider(color: Colors.white24, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _AssetInfo(
                title: '可用余额',
                amount: isDataVisible 
                  ? assetStats!.formatCurrency(assetStats!.calculatedAvailableBalance, selectedCurrency)
                  : '*****',
              ),
              _AssetInfo(
                title: '冻结资产',
                amount: isDataVisible 
                  ? assetStats!.formatCurrency(assetStats!.calculatedFrozenAssets, selectedCurrency)
                  : '*****',
              ),
              _AssetInfo(
                title: '今日收益',
                amount: assetStats!.todayProfit != null && isDataVisible
                  ? '${assetStats!.todayProfit! >= 0 ? '+' : ''}${assetStats!.formatCurrency(assetStats!.todayProfit!.abs(), selectedCurrency)}'
                  : isDataVisible 
                    ? assetStats!.formatCurrency(0.0, selectedCurrency)
                    : '*****',
                highlight: true,
              ),
                    ],
                  )
                ],
              ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F7FB),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 顶部导航栏
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const CircleAvatar(
                        backgroundColor: Color(0xFF10B981),
                        child: Icon(Icons.person, color: Colors.white, size: 20),
                        radius: 20,
                      ),
                      const SizedBox(width: 10),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('欢迎回来', style: TextStyle(fontSize: 14, color: Colors.grey[600])),
                          Text('资产管理', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      )
                    ],
                  ),
                  Row(
                    children: const [
                      Icon(Icons.notifications_none),
                      SizedBox(width: 12),
                      Icon(Icons.more_vert),
                    ],
                  )
                ],
              ),
              const SizedBox(height: 24),

              // 总资产卡片
              _buildAssetCard(),
            const SizedBox(height: 20),
            
            // 功能按钮区
            _ActionButtons(),
            const SizedBox(height: 20),
            
            // 资产分布
              _AssetDistributionCard(
                assetStats: assetStats,
                selectedCurrency: selectedCurrency,
                largestHolding: largestHolding,
                riskLevel: riskLevel,
                assetSnapshots: assetSnapshots,
              ),
            const SizedBox(height: 20),
            
            // 资产排行
            _AssetRankingCard(assetSnapshots: assetSnapshots),
            const SizedBox(height: 20),
            
            // 市场行情
            _MarketTrendsCard(),
            const SizedBox(height: 80), // 为底部导航留空间
          ],
          ),
        ),
      ),
      bottomNavigationBar: _buildBottomNavigation(),
    );
  }
}

class _AssetInfo extends StatelessWidget {
  final String title;
  final String amount;
  final bool highlight;

  const _AssetInfo({
    required this.title,
    required this.amount,
    this.highlight = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(color: Colors.white70, fontSize: 12)),
        const SizedBox(height: 4),
        Text(
          amount,
          style: TextStyle(
            color: highlight ? Colors.greenAccent : Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

class _ActionButtons extends StatelessWidget {
  final List<_ActionItem> actions = const [
    _ActionItem(icon: Icons.add, label: '充值', bgColor: Color(0xFFF2FFFA)),
    _ActionItem(icon: Icons.remove, label: '提现', bgColor: Color(0xFFFFF6ED)),
    _ActionItem(icon: Icons.swap_horiz, label: '交易', bgColor: Color(0xFFF1FFFB)),
    _ActionItem(icon: Icons.savings_outlined, label: '理财', bgColor: Color(0xFFF5F5F5)),
  ];

  const _ActionButtons({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: actions.map((item) => item).toList(),
    );
  }
}

class _ActionItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color bgColor;

  const _ActionItem({required this.icon, required this.label, required this.bgColor});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Icon(icon, size: 28, color: Colors.black87),
        ),
        const SizedBox(height: 6),
        Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
      ],
    );
  }
}

class _AssetDistributionCard extends StatelessWidget {
  final AssetStats? assetStats;
  final String selectedCurrency;
  final String? largestHolding;
  final String riskLevel;
  final List<Map<String, dynamic>> assetSnapshots;

  const _AssetDistributionCard({
    this.assetStats,
    required this.selectedCurrency,
    this.largestHolding,
    required this.riskLevel,
    required this.assetSnapshots,
  });

  @override
  Widget build(BuildContext context) {
    // 计算资产类型分布数据
    final assetTypeData = _calculateAssetTypeDistribution();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text("资产分布", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFFE6FFF1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text("实时", style: TextStyle(fontSize: 12, color: Colors.green)),
              ),
              const SizedBox(width: 4),
              const Icon(Icons.more_horiz, color: Colors.black45),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              SizedBox(
                width: 120,
                height: 120,
                child: PieChart(
                  PieChartData(
                    centerSpaceRadius: 35,
                    sectionsSpace: 3,
                    startDegreeOffset: -90,
                    sections: assetTypeData.map((data) => PieChartSectionData(
                      value: data['percentage'] as double,
                      color: data['color'] as Color,
                      radius: 35,
                        title: '',
                      titleStyle: const TextStyle(fontSize: 0),
                    )).toList(),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: assetTypeData.map((data) => Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: _Legend(
                      title: data['title'] as String,
                      percent: "${data['percentage'].toStringAsFixed(1)}%",
                      value: data['formattedValue'] as String,
                      color: data['color'] as Color,
                    ),
                  )).toList(),
                ),
                      ),
                    ],
                  ),
          const Divider(height: 24),
          Row(
            children: [
              Expanded(
                child: _buildMetric("最大持仓", largestHolding ?? "BTC", Colors.black87),
                ),
              Expanded(
                child: _buildMetric("涨幅最大", "股票 +15.23%", Colors.green),
              ),
              Expanded(
                child: _buildMetric("风险等级", riskLevel, Colors.orange),
              ),
            ],
          ),
        ],
      ),
    );
  }

  List<Map<String, dynamic>> _calculateAssetTypeDistribution() {
    if (assetStats == null || assetSnapshots.isEmpty) {
      // 返回默认数据
      return [
        {
          'title': '数字货币',
          'percentage': 60.9,
          'value': 78234.0,
          'formattedValue': '\$78,234',
          'color': const Color(0xFF00C082),
        },
        {
          'title': '股票投资',
          'percentage': 25.1,
          'value': 32145.0,
          'formattedValue': '\$32,145',
          'color': const Color(0xFFFFAA00),
        },
        {
          'title': '基金理财',
          'percentage': 14.0,
          'value': 18076.0,
          'formattedValue': '\$18,076',
          'color': const Color(0xFF999999),
        },
      ];
    }

    // 使用快照数据计算资产分布
    final Map<String, double> assetTypeTotals = {};
    for (final snapshot in assetSnapshots) {
      final assetType = snapshot['asset_type'] as String;
      final baseValue = snapshot['base_value'];
      final double value = baseValue is num ? baseValue.toDouble() : 0.0;
      assetTypeTotals[assetType] = (assetTypeTotals[assetType] ?? 0.0) + value;
    }

    final totalValue = assetTypeTotals.values.fold(0.0, (sum, value) => sum + value);
    
    if (totalValue == 0) return [];

    // 映射资产类型名称和颜色
    final assetTypeMapping = {
      'fund': {'name': '基金理财', 'color': const Color(0xFF999999)},
      '基金': {'name': '基金理财', 'color': const Color(0xFF999999)},
      '数字货币': {'name': '数字货币', 'color': const Color(0xFF00C082)},
      '外汇': {'name': '外汇', 'color': const Color(0xFF1890FF)},
      '证券': {'name': '股票投资', 'color': const Color(0xFFFFAA00)},
    };

    final List<Map<String, dynamic>> result = [];
    
    assetTypeTotals.forEach((type, value) {
      final percentage = (value / totalValue) * 100;
      final mapping = assetTypeMapping[type] ?? {'name': type, 'color': const Color(0xFF666666)};
      
      result.add({
        'title': mapping['name'] as String,
        'percentage': percentage,
        'value': value,
        'formattedValue': assetStats!.formatCurrency(value, selectedCurrency),
        'color': mapping['color'] as Color,
      });
    });

    // 按百分比排序
    result.sort((a, b) => (b['percentage'] as double).compareTo(a['percentage'] as double));
    
    return result;
  }

  Widget _buildMetric(String label, String value, Color valueColor) {
    return Container(
      height: 50, // 固定高度确保对齐
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label, 
            style: const TextStyle(
              color: Colors.grey, 
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Flexible(
            child: Text(
              value,
              style: TextStyle(
                color: valueColor,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
              overflow: TextOverflow.ellipsis,
              maxLines: 1, // 限制为单行
            ),
          ),
        ],
      ),
    );
  }
}

class _Legend extends StatelessWidget {
  final String title;
  final String percent;
  final String value;
  final Color color;

  const _Legend({required this.title, required this.percent, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 12, 
          height: 12, 
          decoration: BoxDecoration(
            color: color, 
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.3),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          flex: 2,
          child: Text(
            title, 
            style: const TextStyle(
              fontSize: 12, 
              fontWeight: FontWeight.w500,
              color: Colors.black87,
            ),
          ),
        ),
        SizedBox(
          width: 45, // 固定宽度确保对齐
          child: Text(
            percent, 
            style: const TextStyle(
              fontSize: 11, 
              color: Colors.black54,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.right,
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 70, // 固定宽度确保对齐
          child: Text(
            value, 
            style: const TextStyle(
              fontSize: 11, 
              color: Colors.black54,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }
}

class _LabelPair extends StatelessWidget {
  final String label;
  final String value;

  const _LabelPair({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class _AssetRankingCard extends StatelessWidget {
  final List<Map<String, dynamic>> assetSnapshots;
  
  const _AssetRankingCard({required this.assetSnapshots});

  @override
  Widget build(BuildContext context) {
    // 基于真实数据生成资产排行
    final sortedSnapshots = List<Map<String, dynamic>>.from(assetSnapshots)
      ..sort((a, b) => (b['base_value'] ?? 0.0).compareTo(a['base_value'] ?? 0.0));
    
    // 计算总资产价值
    final totalValue = assetSnapshots.fold<double>(0.0, (sum, snapshot) {
      final baseValue = snapshot['base_value'];
      return sum + (baseValue is num ? baseValue.toDouble() : 0.0);
    });
    
    // 生成排行行
    final rankingRows = sortedSnapshots.take(5).map((snapshot) {
      final assetType = snapshot['asset_type'] as String? ?? '未知';
      final assetName = snapshot['asset_name'] as String? ?? '未知资产';
      final baseValue = snapshot['base_value'] as num? ?? 0.0;
      final ratio = totalValue > 0 ? (baseValue / totalValue * 100).toStringAsFixed(1) : '0.0';
      
      // 根据资产类型选择图标和颜色
      IconData? icon;
      Color indexColor;
      String subtitle;
      
      switch (assetType) {
        case '基金':
          icon = Icons.pie_chart;
          indexColor = const Color(0xFF944DFF);
          subtitle = '基金 • ${snapshot['balance']?.toStringAsFixed(2) ?? '0.00'}';
          break;
        case '外汇':
          icon = Icons.currency_exchange;
          indexColor = const Color(0xFF00C399);
          subtitle = '外汇 • ${snapshot['balance']?.toStringAsFixed(2) ?? '0.00'}';
          break;
        case '证券':
          icon = null;
          indexColor = const Color(0xFFFF9734);
          subtitle = '证券 • ${snapshot['balance']?.toStringAsFixed(2) ?? '0.00'}';
          break;
        default:
          icon = Icons.attach_money;
          indexColor = Colors.grey;
          subtitle = '$assetType • ${snapshot['balance']?.toStringAsFixed(2) ?? '0.00'}';
      }
      
      return _RankingRow(
        icon: icon,
        title: assetName.length > 10 ? '${assetName.substring(0, 10)}...' : assetName,
        subtitle: subtitle,
        value: "\$${baseValue.toStringAsFixed(0)}",
        ratio: "$ratio%",
        change: "+0.0%", // 暂时使用固定值，后续可以添加真实变化数据
        changeColor: const Color(0xFF34B27B),
        indexColor: indexColor,
        logoText: assetType == '证券' ? 'STK' : null,
        logoColor: indexColor,
      );
    }).toList();
    
    // 计算Top 5占比
    final top5Value = sortedSnapshots.take(5).fold<double>(0.0, (sum, snapshot) {
      final baseValue = snapshot['base_value'];
      return sum + (baseValue is num ? baseValue.toDouble() : 0.0);
    });
    final top5Ratio = totalValue > 0 ? (top5Value / totalValue * 100).toStringAsFixed(1) : '0.0';
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("资产排行", style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
          const SizedBox(height: 16),
          _RankingHeader(),
          const Divider(height: 24),
          ...rankingRows,
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE7E7E7), width: 1),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Top 5 占总资产", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                Text("$top5Ratio%", style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
              ],
            ),
          )
        ],
      ),
    );
  }
}

class _RankingHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: const [
        Expanded(child: Text("资产", style: TextStyle(fontSize: 13, color: Colors.black54))),
        Text("价值", style: TextStyle(fontSize: 13, color: Colors.black54)),
        SizedBox(width: 16),
        Text("涨跌", style: TextStyle(fontSize: 13, color: Colors.black54)),
      ],
    );
  }
}

class _RankingRow extends StatelessWidget {
  final IconData? icon;
  final String title;
  final String subtitle;
  final String value;
  final String ratio;
  final String change;
  final Color changeColor;
  final Color indexColor;
  final String? logoText;
  final Color? logoColor;

  const _RankingRow({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.value,
    required this.ratio,
    required this.change,
    required this.changeColor,
    required this.indexColor,
    this.logoText,
    this.logoColor,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          if (icon != null)
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.grey.shade100,
              child: Icon(icon, size: 16, color: indexColor),
            )
          else if (logoText != null)
            CircleAvatar(
              radius: 16,
              backgroundColor: logoColor ?? Colors.grey.shade200,
              child: Text(logoText!, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white)),
            ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.black45)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
              Text(ratio, style: const TextStyle(fontSize: 12, color: Colors.black45)),
            ],
          ),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: changeColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(change, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: changeColor)),
          ),
        ],
      ),
    );
  }
}

class _MarketTrendsCard extends StatelessWidget {
  const _MarketTrendsCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Text("市场行情", style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              Spacer(),
              Text("更多", style: TextStyle(fontSize: 13, color: Color(0xFF466AFF), fontWeight: FontWeight.w500)),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            height: 120,
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFFF2F3F5),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Center(
              child: Text(
                "图表占位",
                style: TextStyle(color: Colors.black38, fontSize: 14),
              ),
            ),
          )
        ],
      ),
    );
  }
}


