import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math';
import 'services/smart_api_client.dart';
import 'services/background_cache_service.dart';
import 'services/asset_precache_service.dart';
import 'services/smart_asset_service.dart';
import 'services/cache_service.dart';
import 'utils/debug_logger.dart';
import 'models/asset_stats.dart';
import 'models/trend_data.dart';
import 'pages/main_app_demo.dart';
import 'pages/analysis_page.dart'; // Added import for AnalysisPage
import 'pages/snapshot_page.dart'; // Added import for SnapshotPage
import 'pages/my_page.dart'; // Added import for MyPage
import 'widgets/ai_chat_widget.dart'; // Added import for AIChatWidget
import 'widgets/expandable_asset_chart.dart'; // Added import for ExpandableAssetChart and ExpandedChartSection
import 'design/design_tokens.dart';
import 'services/currency_manager.dart';

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
          seedColor: T.primary,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: T.background,
      ),
      // 暂时使用原版应用作为首页
      home: const AssetHomePage(),
    );
  }
}

/// 应用选择页面 - 可以选择原有应用或新的图表系统
class AppSelectionPage extends StatelessWidget {
  const AppSelectionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.background,
      appBar: AppBar(
        title: const Text(
          '个人金融应用',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            letterSpacing: -0.5,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: T.primary,
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
                    colors: [T.primary, T.primaryDark],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: T.primary.withValues(alpha: 0.3),
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
                  color: const Color(0xFF10B981).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFF10B981).withValues(alpha: 0.2),
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
              color: Colors.black.withValues(alpha: 0.05),
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
  bool isChartExpanded = false; // 新增：控制图表展开状态
  String selectedTimeRange = '1日'; // 新增：选中的时间范围
  bool isDataFromCache = false; // 新增：数据是否来自缓存
  
  // 页面状态 - 0: 首页, 1: 行情, 3: 资产
  int currentPageIndex = 0;
  
  // 数据状态
  AssetStats? assetStats;
  List<TrendData> trendData = [];
  List<Map<String, dynamic>> assetSnapshots = [];
  bool isLoading = true;
  String? errorMessage;
  String? largestHolding;
  String riskLevel = "中等";
  int? _hoveredDataIndex; // 悬停的数据点索引

  @override
  void initState() {
    super.initState();
    _loadData();
    _startBackgroundCaching();
  }

  // 根据时间范围获取对应的天数
  int _getDaysFromTimeRange(String timeRange) {
    switch (timeRange) {
      case '1日':
        return 1;
      case '1周':
        return 7;
      case '1月':
        return 30;
      case '半年':
        return 180;
      default:
        return 1;
    }
  }

  /// 启动后台缓存服务
  Future<void> _startBackgroundCaching() async {
    try {
      // 启动通用后台缓存服务
      await BackgroundCacheService.start();
      DebugLogger.logSuccess(' [AssetHomePage] 通用后台缓存服务已启动');
      
      // 启动专门的资产预缓存服务
      await AssetPrecacheService.start();
      DebugLogger.logSuccess(' [AssetHomePage] 资产预缓存服务已启动');
      
      // 立即预加载一次资产数据
      await SmartAssetService.preloadAllAssets();
      DebugLogger.logSuccess(' [AssetHomePage] 初始资产数据预加载完成');
      
    } catch (e) {
      DebugLogger.logError(' [AssetHomePage] 启动后台缓存服务失败: $e');
    }
  }

  Future<void> _loadData({bool forceRefresh = false}) async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
              // 开始加载 $selectedCurrency 的数据...
      
      // 获取当前选择的时间范围对应的天数
      final days = _getDaysFromTimeRange(selectedTimeRange);
      
      // 先加载聚合统计数据，获取当前总资产值
      final statsJson = await SmartApiClient.getAggregatedStats(selectedCurrency, forceRefresh: forceRefresh);
      final currentTotalValue = statsJson['total_value'] ?? 0.0;
      
      DebugLogger.logInfo('当前总资产值: $currentTotalValue ($selectedCurrency)');
      
      // 并行加载其他数据
      final futures = await Future.wait([
        SmartApiClient.getLargestHolding(selectedCurrency, forceRefresh: forceRefresh),
        SmartApiClient.getAssetSnapshots(selectedCurrency, forceRefresh: forceRefresh),
      ]);

      final largestHoldingResult = futures[0] as String?;
      final snapshotsResult = futures[1] as List<Map<String, dynamic>>;
      
      // 根据时间范围生成趋势数据
      List<Map<String, dynamic>> trendJson;
      
      // 先尝试从缓存获取趋势数据
      DebugLogger.logInfo('检查缓存: $selectedCurrency $selectedTimeRange, forceRefresh: $forceRefresh');
      final cachedTrendData = await CacheService.getTrendDataFromCache(selectedCurrency, selectedTimeRange);
      if (cachedTrendData != null && !forceRefresh) {
        DebugLogger.logInfo('${selectedTimeRange}范围：使用缓存数据');
        trendJson = cachedTrendData;
        isDataFromCache = true;
        DebugLogger.logInfo('缓存数据详情:');
        for (int i = 0; i < trendJson.length; i++) {
          DebugLogger.log('  - 数据${i+1}: ${trendJson[i]['total']} (${trendJson[i]['date']})');
        }
      } else {
        // 缓存无效或强制刷新，生成新数据
        if (selectedTimeRange == '1日' || selectedTimeRange == '1周') {
          DebugLogger.logInfo('${selectedTimeRange}范围：使用基于真实资产的小时数据');
          trendJson = _generateDefaultTrendData(currentTotalValue).map((data) => {
            'date': data.date,
            'total': data.total,
          }).toList();
          DebugLogger.logInfo(' ${selectedTimeRange}范围最终数据:');
          for (int i = 0; i < trendJson.length; i++) {
            DebugLogger.log('  - 数据${i+1}: ${trendJson[i]['total']} (${trendJson[i]['date']})');
          }
        } else {
          // 1月和半年范围：先尝试后端API，如果失败则使用模拟数据
          DebugLogger.logInfo(' ${selectedTimeRange}范围：尝试调用后端API，天数: $days');
          try {
            trendJson = await SmartApiClient.getAssetTrend(days, selectedCurrency, forceRefresh: forceRefresh);
            DebugLogger.logInfo(' 后端API返回数据:');
            for (int i = 0; i < trendJson.length; i++) {
              DebugLogger.log('  - 数据${i+1}: ${trendJson[i]['total']} (${trendJson[i]['date']})');
            }
            
            // 如果后端返回的数据为空或无效，使用模拟数据
            if (trendJson.isEmpty) {
              DebugLogger.logWarning(' 后端API返回空数据，使用模拟数据');
              trendJson = _generateDefaultTrendData(currentTotalValue).map((data) => {
                'date': data.date,
                'total': data.total,
              }).toList();
            }
          } catch (e) {
            DebugLogger.logWarning(' 后端API调用失败: $e，使用模拟数据');
            trendJson = _generateDefaultTrendData(currentTotalValue).map((data) => {
              'date': data.date,
              'total': data.total,
            }).toList();
          }
        }
        
        // 保存到缓存
        DebugLogger.logInfo('保存数据到缓存: $selectedCurrency $selectedTimeRange');
        await CacheService.saveTrendDataToCache(selectedCurrency, selectedTimeRange, trendJson);
        isDataFromCache = false;
      }

      // 计算24小时变化
      final trendDataList = trendJson.map((json) => TrendData.fromJson(json)).toList();
      double? dailyChangePercentage = TrendData.calculateDailyChangePercentage(trendDataList);
      double? dailyProfit = TrendData.calculateDailyProfit(trendDataList);

      // 如果没有足够的历史数据，显示0
      if (dailyChangePercentage == null || trendDataList.length < 2) {
        dailyChangePercentage = 0.0;
        dailyProfit = 0.0;
        // 历史数据不足，24小时变化和今日收益显示为0
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
      
              // $selectedCurrency 数据加载完成
      
      // 后台预加载其他货币数据
      SmartApiClient.preloadOtherCurrencies(selectedCurrency);
      
    } catch (e) {
      setState(() {
        errorMessage = '数据加载失败: $e';
        isLoading = false;
      });
              // 数据加载错误: $e
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

  void _selectCurrency(String currency) async {
    if (currency == selectedCurrency) return;
    
    setState(() {
      selectedCurrency = currency;
      showCurrencyDropdown = false;
    });
    
    // 通知全局货币管理器
    CurrencyManager().setCurrency(currency);
    
    // 检查是否有缓存数据
    final hasCache = await SmartApiClient.hasValidCache(currency, 'aggregated_stats');
    
    if (hasCache) {
              // 发现 $currency 的缓存数据，快速切换
      // 有缓存时快速加载
      _loadData(forceRefresh: false);
    } else {
              // $currency 无缓存，从网络加载
      // 无缓存时从网络加载
      _loadData(forceRefresh: true);
    }
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
          color: isSelected ? Colors.white.withValues(alpha: 0.1) : Colors.transparent,
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
          color: Colors.black.withValues(alpha: 0.05),
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
              _buildNavItem(Icons.home, '首页', 0, currentPageIndex == 0),
              _buildNavItem(Icons.show_chart, '行情', 1, currentPageIndex == 1),
              _buildAICenterButton(),
              _buildNavItem(Icons.account_balance_wallet, '资产', 3, currentPageIndex == 3),
              _buildNavItem(Icons.person, '我的', 4, currentPageIndex == 4),
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
          if (index == 1) { // 行情按钮
            setState(() {
              currentPageIndex = 1;
            });
          } else if (index == 3) { // 资产按钮
            setState(() {
              currentPageIndex = 3;
            });
          } else if (index == 0) { // 首页按钮
            setState(() {
              currentPageIndex = 0;
            });
          } else if (index == 4) { // 我的按钮
            setState(() {
              currentPageIndex = 4;
            });
          }
        },
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
                               Icon(
                     icon,
                     color: isSelected ? T.primary : T.textSecondary,
                     size: 24,
                   ),
            const SizedBox(height: 4),
                               Text(
                     label,
                     style: TextStyle(
                       fontSize: 12,
                       color: isSelected ? T.primary : T.textSecondary,
                       fontWeight: isSelected ? T.fontWeightSemiBold : T.fontWeightNormal,
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
          // 弹出AI聊天界面
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            backgroundColor: Colors.transparent,
            builder: (context) => DraggableScrollableSheet(
              initialChildSize: 0.9,
              minChildSize: 0.5,
              maxChildSize: 0.95,
              builder: (context, scrollController) => Container(
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                ),
                child: Column(
                  children: [
                    // 拖拽指示器
                    Container(
                      margin: const EdgeInsets.only(top: 8),
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.grey[300],
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    // 顶部关闭按钮
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'AI财务助手',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF10B981),
                            ),
                          ),
                          IconButton(
                            onPressed: () => Navigator.of(context).pop(),
                            icon: const Icon(Icons.close, color: Colors.grey),
                            style: IconButton.styleFrom(
                              backgroundColor: Colors.grey[100],
                              shape: const CircleBorder(),
                            ),
                          ),
                        ],
                      ),
                    ),
                    // AI聊天界面
                    Expanded(
                      child: AIChatWidget(
                        placeholder: '输入您想了解的财务问题...',
                        onChartGenerated: (chart, question) {
                          // 图表生成后的回调
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('图表已生成：$question'),
                              backgroundColor: const Color(0xFF10B981),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
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
                    color: const Color(0xFF10B981).withValues(alpha: 0.3),
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
                fontWeight: FontWeight.w600,
                color: Color(0xFF10B981),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAssetCard() {
    // 1. 加载状态
    if (isLoading) {
      return _buildLoadingCard();
    }

    // 2. 错误状态
    if (errorMessage != null) {
      return _buildErrorCard();
    }

    // 3. 无数据状态
    if (assetStats == null) {
      return _buildNoDataCard();
    }

    // 4. 正常状态 - 重构后的清晰布局
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: const Color(0xFF1E1F24),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 顶部标题行
          _buildCardHeader(),
          
          // 货币选择下拉菜单
          if (showCurrencyDropdown) _buildCurrencyDropdown(),
          
          // 总资产金额和24小时变化组合行 - 与折线图并排显示
          const SizedBox(height: 16),
          _buildTotalAssetWithChangeRow(),
          
          // 展开的折线图区域 - 在卡片内部
          if (isChartExpanded) ...[
            const SizedBox(height: 24),
            _buildExpandedChartInCard(),
          ],
          
          // 分隔线
          const Divider(color: Colors.white24, height: 8),
          
          // 底部资产信息
          _buildAssetDetails(),
        ],
      ),
    );
  }

  // 在卡片内部构建展开的折线图
  Widget _buildExpandedChartInCard() {
    DebugLogger.logInfo(' 构建展开图表卡片');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 时间范围选择器
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: ['1日', '1周', '1月', '半年'].map((range) {
            final isSelected = range == selectedTimeRange;
            return GestureDetector(
              onTap: () {
                setState(() {
                  selectedTimeRange = range;
                });
                DebugLogger.log('🎯 选择时间范围: $range');
                // 重新加载数据，优先使用缓存
                _loadData(forceRefresh: false);
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected ? const Color(0xFF10B981) : Colors.transparent,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isSelected ? const Color(0xFF10B981) : Colors.white.withValues(alpha: 0.3),
                    width: 1,
                  ),
                ),
                child: Text(
                  range,
                  style: TextStyle(
                    color: isSelected ? Colors.white : Colors.white.withValues(alpha: 0.7),
                    fontSize: 14,
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
          height: 200,
          child: LayoutBuilder(
            builder: (context, constraints) {
              return _buildExpandedLineChart(constraints.maxWidth);
            },
          ),
        ),
        
        // 底部向上箭头 - 作为关闭按钮
        Center(
          child: GestureDetector(
            onTap: () {
              setState(() {
                isChartExpanded = false;
              });
            },
            child: Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Icon(
                Icons.keyboard_arrow_up,
                color: Colors.white.withValues(alpha: 0.7),
                size: 24,
              ),
            ),
          ),
        ),
      ],
    );
  }

  // 展开的折线图
  Widget _buildExpandedLineChart(double width) {
    // 使用真实数据，如果没有数据则使用默认数据（全为0）
    final displayData = trendData.isNotEmpty ? trendData : _generateDefaultTrendData(assetStats?.totalValue ?? 0.0);
    
    DebugLogger.logInfo(' 绘制图表，数据点数量: ${displayData.length}');
    DebugLogger.logInfo(' 真实数据: ${trendData.isNotEmpty}, 使用默认数据: ${trendData.isEmpty}');
    DebugLogger.logInfo(' 时间范围: $selectedTimeRange');
    DebugLogger.logInfo(' 悬停索引: $_hoveredDataIndex');
    DebugLogger.logInfo(' 大图表显示数据详情:');
    for (int i = 0; i < displayData.length; i++) {
      DebugLogger.log('  - 数据${i+1}: ${displayData[i].total.toStringAsFixed(2)} (${displayData[i].date})');
    }
    
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      child: GestureDetector(
        onPanUpdate: (details) {
          // 处理鼠标悬停
          _handleChartHover(details.localPosition, displayData, width);
        },
        child: CustomPaint(
          size: Size(width, 200),
          painter: _ExpandedLineChartPainter(
            trendData: displayData,
            lineColor: const Color(0xFF10B981),
            maxValue: displayData.isNotEmpty ? displayData.map((d) => d.total).reduce((a, b) => a > b ? a : b) : 0.0,
            minValue: displayData.isNotEmpty ? displayData.map((d) => d.total).reduce((a, b) => a < b ? a : b) : 0.0,
            totalValue: assetStats?.totalValue ?? 0.0,
            hoveredIndex: _hoveredDataIndex,
            timeRange: selectedTimeRange,
          ),
        ),
      ),
    );
  }

  // 处理图表悬停
  void _handleChartHover(Offset position, List<TrendData> data, double width) {
    if (data.isEmpty) {
      DebugLogger.logInfo(' 悬停处理：数据为空');
      return;
    }
    
    DebugLogger.logInfo(' 悬停处理：图表宽度: $width');
    final padding = 20.0;
    final dataWidth = width - 2 * padding;
    
    // 计算悬停的数据点索引
    final relativeX = position.dx - padding;
    final dataIndex = (relativeX / dataWidth * (data.length - 1)).round();
    
    DebugLogger.logInfo(' 悬停位置: ${position.dx}, 相对位置: $relativeX, 数据索引: $dataIndex');
    
    if (dataIndex >= 0 && dataIndex < data.length) {
      DebugLogger.logInfo(' 悬停数据点: ${data[dataIndex].total}, 时间: ${data[dataIndex].date}');
      setState(() {
        _hoveredDataIndex = dataIndex;
      });
    }
  }

  // 格式化悬停时间显示
  String _formatHoverTime(String dateString, String timeRange) {
    try {
      final date = DateTime.parse(dateString);
      
      if (timeRange == '1日' || timeRange == '1周') {
        // 按小时维度：显示日期和时间
        return '${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
      } else {
        // 按天维度：只显示日期
        return '${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
      }
    } catch (e) {
      return dateString;
    }
  }

  // 生成默认趋势数据（1日范围使用模拟数据，其他范围全为0）
  List<TrendData> _generateDefaultTrendData(double baseValue) {
    final now = DateTime.now();
    final data = <TrendData>[];
    
    DebugLogger.logInfo(' 生成默认数据，时间范围: $selectedTimeRange，基准值: $baseValue');
    
    // 根据时间范围生成对应时间粒度的默认数据
    switch (selectedTimeRange) {
      case '1日':
        // 1日范围：生成24小时模拟数据
        DebugLogger.logInfo(' 生成24小时模拟数据，基于真实资产值: $baseValue');
        for (int i = 23; i >= 0; i--) {
          final time = now.subtract(Duration(hours: i));
          // 生成模拟的上升趋势数据
          final trendValue = baseValue + (i * (baseValue * 0.001)); // 轻微上升趋势
          final randomVariation = (Random().nextDouble() - 0.5) * (baseValue * 0.002); // 小幅随机波动
          final finalValue = trendValue + randomVariation;
          
          data.add(TrendData(
            date: time.toIso8601String(),
            total: finalValue,
          ));
        }
        DebugLogger.logInfo(' 生成了 ${data.length} 个数据点，起始值: ${data.first.total.toStringAsFixed(2)}');
        DebugLogger.logInfo(' 24小时数据详情:');
        for (int i = 0; i < data.length; i++) {
          final hour = 23 - i;
          DebugLogger.log('  - 第${hour}小时: ${data[i].total.toStringAsFixed(2)} (${data[i].date})');
        }
        break;
      case '1周':
        // 1周范围：生成168小时数据（7天 × 24小时）
        DebugLogger.logInfo(' 生成168小时数据（1周），基于真实资产值: $baseValue');
        for (int i = 167; i >= 0; i--) {
          final time = now.subtract(Duration(hours: i));
          // 生成模拟的上升趋势数据
          final trendValue = baseValue + (i * (baseValue * 0.0001)); // 轻微上升趋势
          final randomVariation = (Random().nextDouble() - 0.5) * (baseValue * 0.001); // 小幅随机波动
          final finalValue = trendValue + randomVariation;
          
          data.add(TrendData(
            date: time.toIso8601String(),
            total: finalValue,
          ));
        }
        DebugLogger.logInfo(' 生成了 ${data.length} 个数据点，起始值: ${data.first.total.toStringAsFixed(2)}');
        break;
      case '1月':
        // 1月范围：生成30天数据
        DebugLogger.logInfo(' 生成30天数据，基于真实资产值: $baseValue');
        for (int i = 29; i >= 0; i--) {
          final time = now.subtract(Duration(days: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
      case '半年':
        // 半年范围：生成180天数据
        DebugLogger.logInfo(' 生成180天数据，基于真实资产值: $baseValue');
        for (int i = 179; i >= 0; i--) {
          final time = now.subtract(Duration(days: i));
          data.add(TrendData(
            date: time.toIso8601String(),
            total: 0.0,
          ));
        }
        break;
    }
    
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

  // ==================== 重构后的辅助方法 ====================
  
  // 加载状态卡片
  Widget _buildLoadingCard() {
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

  // 错误状态卡片
  Widget _buildErrorCard() {
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

  // 无数据状态卡片
  Widget _buildNoDataCard() {
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

  // 卡片头部 - 标题、货币选择、刷新按钮、可见性切换
  Widget _buildCardHeader() {
    return Row(
      children: [
        // 标题
        const Text('总资产估值', style: TextStyle(color: Colors.white70)),
        const SizedBox(width: 8),
        
        // 货币选择
        GestureDetector(
          onTap: _toggleCurrencyDropdown,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                selectedCurrency, 
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)
              ),
              const SizedBox(width: 4),
              Icon(
                showCurrencyDropdown ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                color: Colors.white54,
                size: 16,
              ),
            ],
          ),
        ),
        const SizedBox(width: 12),
        
        // 刷新按钮
        GestureDetector(
          onTap: () => _loadData(forceRefresh: true),
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.refresh,
              color: Colors.white54,
              size: 16,
            ),
          ),
        ),
        
        const Spacer(),
        
        // 数据可见性切换
        GestureDetector(
          onTap: _toggleDataVisibility,
          child: Icon(
            isDataVisible ? Icons.remove_red_eye_outlined : Icons.visibility_off_outlined,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }

  // 货币选择下拉菜单
  Widget _buildCurrencyDropdown() {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A2A),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
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
    );
  }

  // 总资产金额和24小时变化组合行 - 与折线图并排显示，居中对齐
  Widget _buildTotalAssetWithChangeRow() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center, // 居中对齐，确保折线图与组合模块同高
      children: [
        // 左侧：总额和24小时变化组合模块
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 总资产金额
              Text(
                isDataVisible 
                  ? assetStats!.formatCurrency(assetStats!.totalValue, selectedCurrency)
                  : '*****',
                style: const TextStyle(
                  fontSize: 36, // 大字体突出显示
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  height: 1.1, // 减少行高，让文字更紧凑
                ),
              ),
              
              // 24小时变化信息
              const SizedBox(height: 4), // 小间距
              Row(
                children: [
                  // 变化箭头
                  Icon(
                    assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
                      ? (assetStats!.dailyChangePercent! >= 0 ? Icons.arrow_upward : Icons.arrow_downward)
                      : Icons.remove,
                    size: 16,
                    color: assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
                      ? (assetStats!.dailyChangePercent! >= 0 ? Colors.green : Colors.red)
                      : Colors.grey,
                  ),
                  const SizedBox(width: 6),
                  
                  // 变化百分比
                  Text(
                    assetStats!.dailyChangePercent != null
                      ? '${assetStats!.dailyChangePercent! >= 0 ? '+' : ''}${assetStats!.dailyChangePercent!.toStringAsFixed(2)}%'
                      : '0.00%',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
                        ? (assetStats!.dailyChangePercent! >= 0 ? Colors.green : Colors.red)
                        : Colors.grey,
                    ),
                  ),
                  const SizedBox(width: 8),
                  
                  // 24h标签
                  const Text(
                    '24h', 
                    style: TextStyle(
                      color: Colors.white38,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        
        // 右侧：折线图组件 - 与组合模块居中对齐
        const SizedBox(width: 16), // 保持间距
        ExpandableAssetChart(
          trendData: trendData,
          selectedCurrency: selectedCurrency,
          totalValue: assetStats!.totalValue,
          dailyChangePercent: assetStats!.dailyChangePercent,
          selectedTimeRange: selectedTimeRange,
          onTimeRangeChanged: (String timeRange) {
            setState(() {
              selectedTimeRange = timeRange;
            });
            _loadData(forceRefresh: false);
          },
          onTap: () {
            setState(() {
              isChartExpanded = !isChartExpanded;
            });
            DebugLogger.log('🎯 点击折线图，展开状态: $isChartExpanded');
            DebugLogger.log('🎯 如果展开，应该显示大图表');
          },
        ),
      ],
    );
  }

  // 24小时变化行 - 独立显示，不包含折线图
  Widget _buildDailyChangeRow() {
    return Row(
      children: [
        // 变化箭头
        Icon(
          assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
            ? (assetStats!.dailyChangePercent! >= 0 ? Icons.arrow_upward : Icons.arrow_downward)
            : Icons.remove,
          size: 16,
          color: assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
            ? (assetStats!.dailyChangePercent! >= 0 ? Colors.green : Colors.red)
            : Colors.grey,
        ),
        const SizedBox(width: 6),
        
        // 变化百分比
        Text(
          assetStats!.dailyChangePercent != null
            ? '${assetStats!.dailyChangePercent! >= 0 ? '+' : ''}${assetStats!.dailyChangePercent!.toStringAsFixed(2)}%'
            : '0.00%',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: assetStats!.dailyChangePercent != null && assetStats!.dailyChangePercent! != 0
              ? (assetStats!.dailyChangePercent! >= 0 ? Colors.green : Colors.red)
              : Colors.grey,
          ),
        ),
        const SizedBox(width: 8),
        
        // 24h标签
        const Text(
          '24h', 
          style: TextStyle(
            color: Colors.white38,
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  // 底部资产详情
  Widget _buildAssetDetails() {
    return Row(
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
    );
  }

  @override
  Widget build(BuildContext context) {
            return Scaffold(
          backgroundColor: T.background,
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 40),
          child: _buildPageContent(),
        ),
      ),
      bottomNavigationBar: _buildBottomNavigation(),
    );
  }

  Widget _buildPageContent() {
    switch (currentPageIndex) {
      case 0: // 首页
        return Column(
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
            _AssetRankingCard(
              assetSnapshots: assetSnapshots,
              selectedCurrency: selectedCurrency,
            ),
            const SizedBox(height: 20),
            
            // 市场行情
            _MarketTrendsCard(),
            const SizedBox(height: 80), // 为底部导航留空间
          ],
        );
      
      case 1: // 行情页面
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 顶部标题
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('市场行情', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                IconButton(
                  onPressed: () => setState(() => currentPageIndex = 0),
                  icon: Icon(Icons.arrow_back),
                ),
              ],
            ),
            const SizedBox(height: 20),
            
            // 行情内容 - 暂时显示简单内容，避免布局冲突
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  Icon(Icons.show_chart, size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 16),
                  Text('市场行情功能', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('点击行情按钮查看详细分析', style: TextStyle(color: Colors.grey[600])),
                ],
              ),
            ),
            const SizedBox(height: 80),
          ],
        );
      
      case 3: // 资产页面
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 顶部标题
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('资产快照', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                IconButton(
                  onPressed: () => setState(() => currentPageIndex = 0),
                  icon: Icon(Icons.arrow_back),
                ),
              ],
            ),
            const SizedBox(height: 20),
            
            // 资产快照内容 - 使用SnapshotPage的内容
            const SnapshotPage(),
            const SizedBox(height: 80),
          ],
        );
      
      case 4: // 我的页面
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 我的页面内容
            const MyPage(),
            const SizedBox(height: 80),
          ],
        );
      
      default:
        return Container(); // 默认返回空容器
    }
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
          color: Colors.black.withValues(alpha: 0.05),
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
                color: color.withValues(alpha: 0.3),
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
  final String selectedCurrency;
  
  const _AssetRankingCard({
    required this.assetSnapshots,
    required this.selectedCurrency,
  });

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
      
      // 根据选择的货币格式化显示
      final currencySymbol = _getCurrencySymbol(selectedCurrency);
      final formattedValue = _formatCurrencyValue(baseValue, selectedCurrency);
      
      return _RankingRow(
        icon: icon,
        title: assetName.length > 10 ? '${assetName.substring(0, 10)}...' : assetName,
        subtitle: subtitle,
        value: formattedValue,
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
          color: Colors.black.withValues(alpha: 0.05),
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
  
  /// 获取货币符号
  String _getCurrencySymbol(String currency) {
    switch (currency) {
      case 'CNY':
        return '¥';
      case 'USD':
        return '\$';
      case 'EUR':
        return '€';
      case 'USDT':
        return 'USDT ';
      case 'BTC':
        return '₿';
      default:
        return '\$';
    }
  }
  
  /// 格式化货币值
  String _formatCurrencyValue(num value, String currency) {
    final symbol = _getCurrencySymbol(currency);
    
    // 根据货币类型选择合适的小数位数
    int decimalPlaces;
    switch (currency) {
      case 'CNY':
      case 'USD':
      case 'EUR':
        decimalPlaces = 0; // 整数显示
        break;
      case 'USDT':
        decimalPlaces = 2; // 保留2位小数
        break;
      case 'BTC':
        decimalPlaces = 4; // 保留4位小数
        break;
      default:
        decimalPlaces = 0;
    }
    
    if (decimalPlaces == 0) {
      return "$symbol${value.toStringAsFixed(0)}";
    } else {
      return "$symbol${value.toStringAsFixed(decimalPlaces)}";
    }
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
              color: changeColor.withValues(alpha: 0.1),
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
            color: Colors.black.withValues(alpha: 0.05),
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




// 展开的折线图绘制器
class _ExpandedLineChartPainter extends CustomPainter {
  final List<TrendData> trendData;
  final Color lineColor;
  final double maxValue;
  final double minValue;
  final double totalValue;
  final int? hoveredIndex;
  final String timeRange;

  _ExpandedLineChartPainter({
    required this.trendData,
    required this.lineColor,
    required this.maxValue,
    required this.minValue,
    required this.totalValue,
    this.hoveredIndex,
    required this.timeRange,
  });

  @override
  void paint(Canvas canvas, Size size) {
    DebugLogger.log('🎨 [大图表] 开始绘制，尺寸: ${size.width} x ${size.height}');
    DebugLogger.log('📊 [大图表] 数据点数量: ${trendData.length}');
    
    if (trendData.isEmpty) {
      DebugLogger.logInfo(' 绘制器：数据为空，跳过绘制');
      return;
    }

    DebugLogger.logInfo(' 绘制器：绘制 ${trendData.length} 个数据点，悬停索引: $hoveredIndex');

    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final path = Path();
    final width = size.width;
    final height = size.height;
    final padding = 20.0;

    // 计算数据点位置
    final dataPoints = <Offset>[];
    for (int i = 0; i < trendData.length; i++) {
      final x = padding + (width - 2 * padding) * i / (trendData.length - 1);
      
      // 防止除零错误：当所有值都相同时，将y坐标设为中间位置
      double y;
      if (maxValue == minValue) {
        y = height / 2; // 所有点都在中间位置
      } else {
        y = height - padding - (trendData[i].total - minValue) / (maxValue - minValue) * (height - 2 * padding);
      }
      
      dataPoints.add(Offset(x, y));
    }

    // 绘制折线
    if (dataPoints.isNotEmpty) {
      path.moveTo(dataPoints.first.dx, dataPoints.first.dy);
      for (int i = 1; i < dataPoints.length; i++) {
        path.lineTo(dataPoints[i].dx, dataPoints[i].dy);
      }
      canvas.drawPath(path, paint);
    }

    // 绘制数据点
    final pointPaint = Paint()
      ..color = lineColor
      ..style = PaintingStyle.fill;

    for (int i = 0; i < dataPoints.length; i++) {
      final point = dataPoints[i];
      final isHovered = hoveredIndex == i;
      
      // 悬停的数据点更大更亮
      final radius = isHovered ? 5.0 : 3.0;
      final color = isHovered ? Colors.white : lineColor;
      
      final currentPointPaint = Paint()
        ..color = color
        ..style = PaintingStyle.fill;
      
      canvas.drawCircle(point, radius, currentPointPaint);
      
      // 悬停时显示数据标签
      if (isHovered) {
        _drawDataLabel(canvas, point, trendData[i]);
      }
    }
  }

  // 格式化悬停时间显示
  String _formatHoverTime(String dateString, String timeRange) {
    try {
      final date = DateTime.parse(dateString);
      
      if (timeRange == '1日' || timeRange == '1周') {
        // 按小时维度：显示日期和时间
        return '${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
      } else {
        // 按天维度：只显示日期
        return '${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
      }
    } catch (e) {
      return dateString;
    }
  }

  void _drawDataLabel(Canvas canvas, Offset point, TrendData data) {
    // 格式化时间显示
    final timeString = _formatHoverTime(data.date, timeRange);
    
    // 创建金额文本
    final amountTextPainter = TextPainter(
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
    
    // 创建时间文本
    final timeTextPainter = TextPainter(
      text: TextSpan(
        text: timeString,
        style: const TextStyle(
          color: Colors.white70,
          fontSize: 10,
          fontWeight: FontWeight.normal,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    
    amountTextPainter.layout();
    timeTextPainter.layout();
    
    // 计算标签总尺寸
    final totalWidth = amountTextPainter.width > timeTextPainter.width 
        ? amountTextPainter.width 
        : timeTextPainter.width;
    final totalHeight = amountTextPainter.height + timeTextPainter.height + 2;
    
    // 在数据点上方显示标签
    final labelOffset = Offset(
      point.dx - totalWidth / 2,
      point.dy - 30,
    );
    
    // 绘制背景
    final backgroundPaint = Paint()
      ..color = Colors.black.withValues(alpha: 0.7)
      ..style = PaintingStyle.fill;
    
    final backgroundRect = Rect.fromLTWH(
      labelOffset.dx - 4,
      labelOffset.dy - 2,
      totalWidth + 8,
      totalHeight + 4,
    );
    
    canvas.drawRRect(
      RRect.fromRectAndRadius(backgroundRect, const Radius.circular(4)),
      backgroundPaint,
    );
    
    // 绘制金额文字（上方）
    amountTextPainter.paint(canvas, Offset(
      labelOffset.dx + (totalWidth - amountTextPainter.width) / 2,
      labelOffset.dy,
    ));
    
    // 绘制时间文字（下方）
    timeTextPainter.paint(canvas, Offset(
      labelOffset.dx + (totalWidth - timeTextPainter.width) / 2,
      labelOffset.dy + amountTextPainter.height + 2,
    ));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
