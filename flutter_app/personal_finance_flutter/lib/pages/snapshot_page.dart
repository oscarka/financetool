import 'package:flutter/material.dart';
import '../design/design_tokens.dart';
import '../services/alipay_fund_service.dart';
import '../services/wise_service.dart';
import '../services/ibkr_service.dart';
import '../services/okx_service.dart';
import '../services/currency_manager.dart';
import '../models/fund_position.dart';
import '../models/wise_balance.dart';
import '../models/ibkr_position.dart';
import '../models/okx_balance.dart';
import '../pages/fund_operation_page.dart';

class SnapshotPage extends StatefulWidget {
  const SnapshotPage({super.key});

  @override
  State<SnapshotPage> createState() => _SnapshotPageState();
}

class _SnapshotPageState extends State<SnapshotPage> {
  List<FundPosition> _fundPositions = [];
  Map<String, dynamic> _positionSummary = {};
  List<WiseBalance> _wiseBalances = [];
  Map<String, dynamic> _wiseSummary = {};
  Map<String, Map<String, dynamic>> _exchangeRates = {};
  
  // IBKR数据
  List<IBKRPosition> _ibkrPositions = [];
  List<Map<String, dynamic>> _ibkrBalances = [];
  Map<String, dynamic> _ibkrSummary = {};
  
  // OKX数据
  List<OKXBalance> _okxBalances = [];
  List<Map<String, dynamic>> _okxPositions = [];
  Map<String, dynamic> _okxSummary = {};
  
  bool _isLoading = true;
  String? _errorMessage;
  
  // 货币管理器
  late CurrencyManager _currencyManager;
  String _currentBaseCurrency = 'CNY';

  @override
  void initState() {
    super.initState();
    _currencyManager = CurrencyManager();
    _currentBaseCurrency = _currencyManager.selectedCurrency;
    _currencyManager.addListener(_onCurrencyChanged);
    _loadAllData();
  }

  @override
  void dispose() {
    _currencyManager.removeListener(_onCurrencyChanged);
    super.dispose();
  }

  /// 货币变化时的回调
  void _onCurrencyChanged() {
    setState(() {
      _currentBaseCurrency = _currencyManager.selectedCurrency;
    });
  }

  Future<void> _loadAllData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 并行加载所有数据
      final futures = await Future.wait([
        AlipayFundService.getFundPositions(),
        AlipayFundService.getPositionSummary(),
        WiseService.getAllBalances(),
        WiseService.getWiseSummary(),
        WiseService.getExchangeRates(source: 'USD', target: 'CNY'),
        IBKRService.getPositions(),
        IBKRService.getBalances(),
        IBKRService.getIBKRSummary(),
        OKXService.getAccountBalance(),
        OKXService.getOKXSummary(),
      ]);

      // 获取其他货币对的汇率
      final otherRates = await Future.wait([
        WiseService.getExchangeRates(source: 'EUR', target: 'CNY'),
        WiseService.getExchangeRates(source: 'GBP', target: 'CNY'),
        WiseService.getExchangeRates(source: 'JPY', target: 'CNY'),
        WiseService.getExchangeRates(source: 'AUD', target: 'CNY'),
        WiseService.getExchangeRates(source: 'HKD', target: 'CNY'),
        WiseService.getExchangeRates(source: 'SGD', target: 'CNY'),
        WiseService.getExchangeRates(source: 'CHF', target: 'CNY'),
        WiseService.getExchangeRates(source: 'CAD', target: 'CNY'),
      ]);

      setState(() {
        _fundPositions = futures[0] as List<FundPosition>;
        _positionSummary = futures[1] as Map<String, dynamic>;
        _wiseBalances = futures[2] as List<WiseBalance>;
        _wiseSummary = futures[3] as Map<String, dynamic>;
        _exchangeRates = {
          'USD_CNY': futures[4] as Map<String, dynamic>,
          'EUR_CNY': otherRates[0] as Map<String, dynamic>,
          'GBP_CNY': otherRates[1] as Map<String, dynamic>,
          'JPY_CNY': otherRates[2] as Map<String, dynamic>,
          'AUD_CNY': otherRates[3] as Map<String, dynamic>,
          'HKD_CNY': otherRates[4] as Map<String, dynamic>,
          'SGD_CNY': otherRates[5] as Map<String, dynamic>,
          'CHF_CNY': otherRates[6] as Map<String, dynamic>,
          'CAD_CNY': otherRates[7] as Map<String, dynamic>,
        };
        _ibkrPositions = futures[5] as List<IBKRPosition>;
        _ibkrBalances = futures[6] as List<Map<String, dynamic>>;
        _ibkrSummary = futures[7] as Map<String, dynamic>;
        _okxBalances = futures[8] as List<OKXBalance>;
        _okxSummary = futures[9] as Map<String, dynamic>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return _buildLoadingState();
    }

    if (_errorMessage != null) {
      return _buildErrorState();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
          // 顶部状态栏
        _buildStatusBar(),
        const SizedBox(height: T.spacingL),

        // 筛选按钮
        _buildFilterButtons(),
        const SizedBox(height: T.spacingL),

        // 支付宝基金持仓卡片
        _buildAlipayFundCard(),
        const SizedBox(height: T.spacingL),

        // 其他平台卡片（暂时使用模拟数据）
        _buildWiseCard(),
        const SizedBox(height: T.spacingM),
        _buildIBKRCard(),
        const SizedBox(height: T.spacingM),
        _buildOKXCard(),
        const SizedBox(height: T.spacingL),

        // 今日表现
        // 暂时注释掉这些功能，后续实现
        // _buildTodayPerformance(),
        // const SizedBox(height: T.spacingL),

        // // 最近快照记录
        // _buildSnapshotLogs(),
        // const SizedBox(height: T.spacingL),

        // // 今日统计
        // _buildTodayStats(),
        const SizedBox(height: T.spacingXL),
      ],
    );
  }

  Widget _buildLoadingState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('加载中...'),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 16),
          Text('加载失败: $_errorMessage'),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadAllData,
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }

  // 顶部状态栏
  Widget _buildStatusBar() {
    final totalValue = _positionSummary['total_value'] ?? 0.0;
    final lastUpdateTime = _fundPositions.isNotEmpty 
        ? _fundPositions.first.lastUpdatedText 
        : '未知';

    return Container(
            padding: const EdgeInsets.symmetric(horizontal: T.spacingL, vertical: T.spacingM),
            decoration: BoxDecoration(
              color: T.cardBackground,
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: T.spacingS, vertical: T.spacingXS),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE6F7EE),
                    borderRadius: BorderRadius.circular(T.radiusXL),
                  ),
            child: Row(
                    children: [
                const Icon(Icons.check_circle, size: 16, color: T.success),
                const SizedBox(width: T.spacingXS),
                      Text(
                        "数据正常",
                        style: TextStyle(
                          fontSize: T.fontSizeS,
                          fontWeight: T.fontWeightMedium,
                          color: T.success,
                        ),
                      ),
                    ],
                  ),
                ),
          Text(
            lastUpdateTime,
            style: TextStyle(
              fontSize: T.fontSizeS, 
              color: T.textTertiary,
              fontWeight: T.fontWeightNormal,
            )
                )
              ],
            ),
    );
  }

          // 筛选按钮
  Widget _buildFilterButtons() {
    return Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildFilterButton(Icons.calendar_today, "今日", true),
              _buildFilterButton(Icons.calendar_today, "本周", false),
              _buildFilterButton(Icons.calendar_today, "本月", false),
              _buildFilterButton(Icons.show_chart, "全部", false),
            ],
      );
  }

  // 筛选按钮组件
  Widget _buildFilterButton(IconData icon, String text, bool active) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(T.spacingM),
          decoration: BoxDecoration(
            color: active ? const Color(0xFFE6F7EE) : T.cardBackground,
            borderRadius: BorderRadius.circular(T.radiusM),
          ),
          child: Icon(icon,
              color: active ? T.success : T.textTertiary, size: 20),
        ),
        const SizedBox(height: T.spacingXS),
        Text(
          text,
          style: TextStyle(
              fontSize: T.fontSizeS,
              color: active ? T.success : T.textTertiary,
              fontWeight: active ? T.fontWeightSemiBold : T.fontWeightNormal),
        )
      ],
    );
  }

  // 支付宝基金持仓卡片
  Widget _buildAlipayFundCard() {
    final totalValue = _positionSummary['total_value'] ?? 0.0;
    final assetCount = _fundPositions.length;
    final totalProfit = _positionSummary['total_profit'] ?? 0.0;
    final profitRate = _positionSummary['total_profit_rate'] ?? 0.0;

    // 按市值从高到低排序基金列表
    final sortedPositions = List<FundPosition>.from(_fundPositions)
      ..sort((a, b) => b.currentValue.compareTo(a.currentValue));

    return Container(
      margin: const EdgeInsets.only(bottom: T.spacingM),
      padding: const EdgeInsets.all(T.spacingL),
      decoration: BoxDecoration(
        color: T.cardBackground,
        borderRadius: BorderRadius.circular(T.radiusM),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "支付宝 · 基金投资",
                style: TextStyle(
                  fontSize: T.fontSizeL, 
                  fontWeight: T.fontWeightBold,
                  color: T.textPrimary,
                )
              ),
              IconButton(
                onPressed: () async {
                  final result = await Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const FundOperationPage(),
                    ),
                  );
                  
                  // 如果操作成功，刷新数据
                  if (result == true) {
                    _loadAllData();
                  }
                },
                icon: const Icon(Icons.add_circle_outline, color: T.success),
                tooltip: '新增操作',
              ),
            ],
          ),
        const SizedBox(height: T.spacingXS),
          Text(
            "${_fundPositions.isNotEmpty ? _fundPositions.first.lastUpdatedText : '未知'} · ¥${totalValue.toStringAsFixed(2)}",
            style: TextStyle(
              fontSize: T.fontSizeS, 
              color: T.textTertiary,
              fontWeight: T.fontWeightNormal,
            )
          ),
        const SizedBox(height: T.spacingM),
          Text(
            "正常 · ${assetCount}笔资产",
            style: TextStyle(
                fontSize: T.fontSizeS,
              color: T.success,
              fontWeight: T.fontWeightMedium,
            )
          ),
        const SizedBox(height: T.spacingS),
          
          // 基金持仓明细（按市值排序）
          for (var position in sortedPositions)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                  Text(
                    position.assetName,
                    style: TextStyle(
                      fontSize: T.fontSizeM, 
                      color: T.textPrimary,
                      fontWeight: T.fontWeightMedium,
                    )
                  ),
                  Text(
                    position.currentValueText,
                    style: TextStyle(
                      fontSize: T.fontSizeM,
                      fontWeight: T.fontWeightSemiBold,
                      color: T.textPrimary,
                    )
                  ),
              ],
            ),
          ),
          
          // 显示真实的收益变化数据（如果有的话）
          if (totalProfit != 0)
          Padding(
            padding: const EdgeInsets.only(top: T.spacingM),
              child: Text(
                "总收益: ${totalProfit >= 0 ? '+' : ''}¥${totalProfit.toStringAsFixed(2)} (${profitRate >= 0 ? '+' : ''}${(profitRate * 100).toStringAsFixed(2)}%)",
                style: TextStyle(
                  fontSize: T.fontSizeS,
                  color: totalProfit >= 0 ? T.success : T.error,
                  fontWeight: T.fontWeightMedium,
                )
              ),
            ),
        ],
      ),
    );
  }

  // Wise多币种账户卡片
  Widget _buildWiseCard() {
    final totalAccounts = _wiseSummary['total_accounts'] ?? 0;
    final totalCurrencies = _wiseSummary['total_currencies'] ?? 0;
    final recentTransactionsCount = _wiseSummary['recent_transactions_count'] ?? 0;
    
    // 过滤掉余额为0的账户，并按余额从高到低排序
    final nonZeroBalances = _wiseBalances.where((b) => b.availableBalance > 0).toList()
      ..sort((a, b) => b.availableBalance.compareTo(a.availableBalance));
    
    // 根据基准货币计算总价值
    double totalValue = 0.0;
    final usdCnyRate = _exchangeRates['USD_CNY']?['rate'] ?? 7.2; // 默认汇率
    
    for (var balance in nonZeroBalances) {
      totalValue += _getBalanceInBaseCurrency(balance, _currentBaseCurrency, usdCnyRate);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: T.spacingM),
            padding: const EdgeInsets.all(T.spacingL),
            decoration: BoxDecoration(
              color: T.cardBackground,
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
              Text(
                "Wise · 多币种账户",
                        style: TextStyle(
                  fontSize: T.fontSizeL, 
                  fontWeight: T.fontWeightBold,
                  color: T.textPrimary,
                )
              ),
              Row(
                children: [
                  // 数据同步按钮
                  IconButton(
                    onPressed: () {
                      // TODO: 触发Wise数据同步
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('正在同步Wise数据...')),
                      );
                      _loadAllData(); // 重新加载数据
                    },
                    icon: const Icon(Icons.sync, color: T.info),
                    tooltip: '同步数据',
                  ),
                  // 新增操作按钮
                  IconButton(
                    onPressed: () {
                      // TODO: 跳转到Wise操作选择页面
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Wise操作功能开发中...')),
                      );
                    },
                    icon: const Icon(Icons.add_circle_outline, color: T.success),
                    tooltip: '新增操作',
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: T.spacingXS),
          Text(
            "${_wiseBalances.isNotEmpty ? _wiseBalances.first.lastUpdatedText : '未知'} · ${_currencyManager.baseCurrencySymbol}${totalValue.toStringAsFixed(2)}",
            style: TextStyle(
              fontSize: T.fontSizeS, 
              color: T.textTertiary,
              fontWeight: T.fontWeightNormal,
            )
          ),
          const SizedBox(height: T.spacingM),
          Text(
            "正常 · ${nonZeroBalances.length}种货币",
            style: TextStyle(
              fontSize: T.fontSizeS,
              color: T.success,
              fontWeight: T.fontWeightMedium,
            )
          ),
          const SizedBox(height: T.spacingS),
          
          // Wise余额明细（按余额排序，只显示非零余额）
          for (var balance in nonZeroBalances)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // 左侧：中文货币名称
                  Text(
                    _getCurrencyDisplayName(balance.currency),
                    style: TextStyle(
                      fontSize: T.fontSizeM, 
                      color: T.textPrimary,
                      fontWeight: T.fontWeightMedium,
                    )
                  ),
                  // 右侧：余额和基准货币转换
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: T.spacingS, vertical: T.spacingXS),
                    decoration: BoxDecoration(
                      color: T.surfaceBackground,
                      borderRadius: BorderRadius.circular(T.radiusS),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 原始余额
                        Text(
                          balance.formattedAvailableBalance,
                          style: TextStyle(
                            fontSize: T.fontSizeM,
                            fontWeight: T.fontWeightSemiBold,
                            color: T.textPrimary,
                          )
                        ),
                        const SizedBox(width: T.spacingXS),
                        // 分隔符
                        Text(
                          "·",
                          style: TextStyle(
                            fontSize: T.fontSizeS,
                            color: T.textTertiary,
                            fontWeight: T.fontWeightNormal,
                          )
                        ),
                        const SizedBox(width: T.spacingXS),
                        // 基准货币转换金额
                        Text(
                          "${_currencyManager.baseCurrencySymbol}${_getBalanceInBaseCurrency(balance, _currentBaseCurrency, usdCnyRate).toStringAsFixed(2)}",
                          style: TextStyle(
                            fontSize: T.fontSizeS,
                            color: T.textSecondary,
                            fontWeight: T.fontWeightMedium,
                          )
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          
          // 显示汇率变化信息
          if (_exchangeRates.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: T.spacingM),
              child: Container(
                padding: const EdgeInsets.all(T.spacingS),
                decoration: BoxDecoration(
                  color: T.surfaceBackground,
                  borderRadius: BorderRadius.circular(T.radiusS),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                  children: [
                        Icon(
                          _getExchangeRateIcon(_exchangeRates['USD_CNY']?['change_percent'] ?? 0.0),
                          size: 16,
                          color: _getExchangeRateColor(_exchangeRates['USD_CNY']?['change_percent'] ?? 0.0),
                        ),
                        const SizedBox(width: T.spacingXS),
                        Text(
                          "USD/CNY: ${(_exchangeRates['USD_CNY']?['rate'] ?? 0.0).toStringAsFixed(2)} ",
                          style: TextStyle(
                            fontSize: T.fontSizeS,
                            color: T.textSecondary,
                            fontWeight: T.fontWeightMedium,
                          )
                        ),
                        Text(
                          "${_exchangeRates['USD_CNY']?['change_percent'] != null ? (_exchangeRates['USD_CNY']?['change_percent'] >= 0 ? '+' : '') : ''}${(_exchangeRates['USD_CNY']?['change_percent'] ?? 0.0).toStringAsFixed(2)}%",
                          style: TextStyle(
                            fontSize: T.fontSizeS,
                            color: _getExchangeRateColor(_exchangeRates['USD_CNY']?['change_percent'] ?? 0.0),
                            fontWeight: T.fontWeightMedium,
                          )
                        ),
                      ],
                    ),
                    // 显示汇率来源信息
                    if (_exchangeRates['USD_CNY']?['is_default'] == true)
                      Padding(
                        padding: const EdgeInsets.only(top: T.spacingXS),
                        child: Text(
                          "使用默认汇率 (API获取失败)",
                          style: TextStyle(
                            fontSize: T.fontSizeXS,
                            color: T.warning,
                            fontWeight: T.fontWeightNormal,
                          )
                        ),
                ),
              ],
            ),
          ),
            ),
          
          // 显示最近交易数量
          if (recentTransactionsCount > 0)
          Padding(
            padding: const EdgeInsets.only(top: T.spacingM),
              child: Text(
                "最近交易: ${recentTransactionsCount}笔",
                style: TextStyle(
                  fontSize: T.fontSizeS,
                  color: T.textSecondary,
                  fontWeight: T.fontWeightMedium,
                )
              ),
            ),
        ],
      ),
    );
  }
  
  /// 获取货币的中文显示名称
  String _getCurrencyDisplayName(String currency) {
    switch (currency.toUpperCase()) {
      case 'USD':
        return '美元 (USD)';
      case 'EUR':
        return '欧元 (EUR)';
      case 'GBP':
        return '英镑 (GBP)';
      case 'JPY':
        return '日元 (JPY)';
      case 'AUD':
        return '澳元 (AUD)';
      case 'CNY':
        return '人民币 (CNY)';
      case 'HKD':
        return '港币 (HKD)';
      case 'SGD':
        return '新加坡元 (SGD)';
      case 'CHF':
        return '瑞士法郎 (CHF)';
      case 'CAD':
        return '加拿大元 (CAD)';
      default:
        return '$currency ($currency)';
    }
  }
  
  /// 计算余额对应的基准货币金额
  double _getBalanceInBaseCurrency(WiseBalance balance, String baseCurrency, double usdCnyRate) {
    final currency = balance.currency.toUpperCase();
    final baseCurr = baseCurrency.toUpperCase();
    
    // 如果货币和基准货币相同，直接返回
    if (currency == baseCurr) {
      return balance.availableBalance;
    }
    
    // 如果基准货币是CNY，使用直接汇率转换（与后台保持一致）
    if (baseCurr == 'CNY') {
      return _getBalanceInCNYDirect(balance);
    }
    
    // 如果基准货币是USD，转换为USD
    if (baseCurr == 'USD') {
      return _getBalanceInUSDDirect(balance);
    }
    
    // 如果基准货币是EUR，转换为EUR
    if (baseCurr == 'EUR') {
      return _getBalanceInEURDirect(balance);
    }
    
    // 其他基准货币，先转换为USD再转换为目标货币
    final usdValue = _getBalanceInUSDDirect(balance);
    return _convertUSDToCurrency(usdValue, baseCurr, usdCnyRate);
  }
  
  /// 使用直接汇率转换为CNY（与后台计算保持一致）
  double _getBalanceInCNYDirect(WiseBalance balance) {
    // 使用前端获取的直接汇率，如果没有则使用后台的已知汇率
    final directRate = _exchangeRates['${balance.currency}_CNY']?['rate'];
    if (directRate != null && directRate > 0) {
      return balance.availableBalance * directRate;
    }
    
    // 如果没有直接汇率，使用后台已知的汇率
    switch (balance.currency.toUpperCase()) {
      case 'JPY':
        return balance.availableBalance * 0.0485; // 后台汇率: 6,782.47 ÷ 139,833
      case 'AUD':
        return balance.availableBalance * 4.66;   // 后台汇率: 1,308.46 ÷ 280.74
      case 'USD':
        return balance.availableBalance * 7.13;   // 当前USD/CNY汇率
      case 'EUR':
        return balance.availableBalance * 8.325;  // 后台汇率: 6.66 ÷ 0.80
      case 'CNY':
        return balance.availableBalance;
      case 'HKD':
        return balance.availableBalance * 0.915;  // 后台汇率
      default:
        return balance.availableBalance * 7.13;   // 默认按USD汇率
    }
  }
  
  /// 使用直接汇率转换为USD
  double _getBalanceInUSDDirect(WiseBalance balance) {
    final directRate = _exchangeRates['${balance.currency}_USD']?['rate'];
    if (directRate != null && directRate > 0) {
      return balance.availableBalance * directRate;
    }
    
    // 使用后台已知的汇率除以USD/CNY汇率
    final usdCnyRate = _exchangeRates['USD_CNY']?['rate'] ?? 7.13;
    return _getBalanceInCNYDirect(balance) / usdCnyRate;
  }
  
  /// 使用直接汇率转换为EUR
  double _getBalanceInEURDirect(WiseBalance balance) {
    final directRate = _exchangeRates['${balance.currency}_EUR']?['rate'];
    if (directRate != null && directRate > 0) {
      return balance.availableBalance * directRate;
    }
    
    // 通过CNY中转转换
    final cnyValue = _getBalanceInCNYDirect(balance);
    final eurCnyRate = _exchangeRates['EUR_CNY']?['rate'] ?? 8.325;
    return cnyValue / eurCnyRate;
  }
  
  /// 将USD转换为指定货币
  double _convertUSDToCurrency(double usdValue, String targetCurrency, double usdCnyRate) {
    switch (targetCurrency.toUpperCase()) {
      case 'USD':
        return usdValue;
      case 'CNY':
        return usdValue * usdCnyRate;
      case 'EUR':
        return usdValue * 0.92; // USD/EUR汇率
      case 'GBP':
        return usdValue * 1.26; // USD/GBP汇率
      case 'JPY':
        return usdValue * 150; // USD/JPY汇率
      case 'AUD':
        return usdValue * 0.66; // USD/AUD汇率
      case 'HKD':
        return usdValue * 7.8; // USD/HKD汇率
      case 'SGD':
        return usdValue * 1.35; // USD/SGD汇率
      case 'CHF':
        return usdValue * 0.88; // USD/CHF汇率
      case 'CAD':
        return usdValue * 1.35; // USD/CAD汇率
      default:
        return usdValue; // 默认按USD处理
    }
  }
  
  /// 获取汇率变化图标
  IconData _getExchangeRateIcon(double changePercent) {
    if (changePercent > 0) {
      return Icons.trending_up;
    } else if (changePercent < 0) {
      return Icons.trending_down;
    } else {
      return Icons.trending_flat;
    }
  }
  
  /// 获取汇率变化颜色
  Color _getExchangeRateColor(double changePercent) {
    if (changePercent > 0) {
      return T.success;
    } else if (changePercent < 0) {
      return T.error;
    } else {
      return T.textSecondary;
    }
  }

  /// 构建IBKR证券投资卡片
  Widget _buildIBKRCard() {
    if (_ibkrPositions.isEmpty && _ibkrBalances.isEmpty) {
      return Container();
    }

    // 计算总市值
    final totalMarketValue = _ibkrPositions.fold<double>(
      0.0, (sum, position) => sum + position.marketValue);
    
    // 计算总现金
    final totalCash = _ibkrBalances.fold<double>(
      0.0, (sum, balance) => sum + (balance['total_cash'] ?? 0.0));
    
    // 计算总资产
    final totalAssets = totalMarketValue + totalCash;
    
    // 计算总盈亏
    final totalUnrealizedPnl = _ibkrPositions.fold<double>(
      0.0, (sum, position) => sum + position.unrealizedPnl);
    
    final totalRealizedPnl = _ibkrPositions.fold<double>(
      0.0, (sum, position) => sum + position.realizedPnl);
    
    final totalPnl = totalUnrealizedPnl + totalRealizedPnl;
    
    // 按市值排序持仓
    final sortedPositions = List<IBKRPosition>.from(_ibkrPositions)
      ..sort((a, b) => b.marketValue.compareTo(a.marketValue));

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(T.spacingL),
      decoration: BoxDecoration(
        color: T.cardBackground,
        borderRadius: BorderRadius.circular(T.radiusL),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题行
          Row(
            children: [
              Icon(
                Icons.account_balance,
                color: T.primary,
                size: 24,
              ),
              const SizedBox(width: T.spacingS),
              Expanded(
                child: Text(
                  'IBKR·证券投资',
            style: TextStyle(
                    fontSize: T.fontSizeL,
                    fontWeight: FontWeight.bold,
                    color: T.textPrimary,
                  ),
                ),
              ),
              IconButton(
                onPressed: () {
                  // TODO: 实现数据同步
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('IBKR数据同步功能开发中...')),
                  );
                },
                icon: Icon(
                  Icons.sync,
                  color: T.iconSecondary,
                  size: 20,
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingM),

          // 更新状态和总资产
          Row(
            children: [
              Text(
                '8小时前更新·${_currencyManager.getCurrencySymbol(_currentBaseCurrency)}${_getTotalAssetsInBaseCurrency(totalAssets, 'USD')}',
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  color: T.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingS),

          // 账户状态
          Row(
            children: [
          Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: T.spacingS,
                  vertical: 2,
                ),
            decoration: BoxDecoration(
                  color: T.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(T.radiusS),
                ),
                child: Text(
                  '正常·${_ibkrSummary['total_accounts'] ?? 0}个账户',
                  style: TextStyle(
                    fontSize: T.fontSizeS,
                    color: T.success,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingM),

          // 持仓列表
          if (sortedPositions.isNotEmpty) ...[
            ...sortedPositions.map((position) => Padding(
              padding: const EdgeInsets.only(bottom: T.spacingS),
            child: Row(
              children: [
                  Expanded(
                    flex: 2,
                    child: Text(
                      position.symbol,
                    style: TextStyle(
                        fontSize: T.fontSizeM,
                        fontWeight: FontWeight.w500,
                        color: T.textPrimary,
                      ),
                    ),
                  ),
                  Expanded(
                    flex: 1,
                    child: Text(
                      position.formattedQuantity,
                      style: TextStyle(
                        fontSize: T.fontSizeM,
                        color: T.textSecondary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Text(
                      position.formattedMarketValue,
                      style: TextStyle(
                        fontSize: T.fontSizeM,
                        fontWeight: FontWeight.w500,
                        color: T.textPrimary,
                      ),
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            )),
            const SizedBox(height: T.spacingS),
          ],

          // 现金余额
          if (totalCash > 0) ...[
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: Text(
                    '现金余额',
                    style: TextStyle(
                      fontSize: T.fontSizeM,
                      color: T.textSecondary,
                    ),
                  ),
                ),
                Expanded(
                  flex: 1,
                  child: Container(),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    '\$${totalCash.toStringAsFixed(2)}',
                    style: TextStyle(
                      fontSize: T.fontSizeM,
                      fontWeight: FontWeight.w500,
                      color: T.textPrimary,
                    ),
                    textAlign: TextAlign.right,
                  ),
                ),
              ],
            ),
            const SizedBox(height: T.spacingS),
          ],

          // 分割线
          Divider(color: T.divider, height: 1),
          const SizedBox(height: T.spacingS),

          // 总收益
          Row(
            children: [
              Text(
                '总收益:',
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  color: T.textSecondary,
                ),
              ),
              const Spacer(),
              Text(
                '${totalPnl >= 0 ? '+' : ''}${_currencyManager.getCurrencySymbol(_currentBaseCurrency)}${_getTotalAssetsInBaseCurrency(totalPnl, 'USD')}',
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  fontWeight: FontWeight.w500,
                  color: totalPnl >= 0 ? T.success : T.error,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 构建OKX数字货币卡片
  Widget _buildOKXCard() {
    if (_okxBalances.isEmpty) {
      return Container();
    }

    // 按账户类型分组余额
    final tradingBalances = _okxBalances.where((balance) => 
      balance.accountType == 'trading' && balance.totalBalance > 0).toList();
    final fundingBalances = _okxBalances.where((balance) => 
      balance.accountType == 'funding' && balance.totalBalance > 0).toList();
    final savingsBalances = _okxBalances.where((balance) => 
      balance.accountType == 'savings' && balance.totalBalance > 0).toList();
    
    // 添加调试信息
    print('🔍 [OKX Debug] 原始余额数据: ${_okxBalances.length}条');
    print('🔍 [OKX Debug] Trading账户: ${tradingBalances.length}条');
    print('🔍 [OKX Debug] Funding账户: ${fundingBalances.length}条');
    print('🔍 [OKX Debug] Savings账户: ${savingsBalances.length}条');
    
    // 过滤掉小于1美元的资产
    final filteredTrading = _filterBalancesByUSDValue(tradingBalances);
    final filteredFunding = _filterBalancesByUSDValue(fundingBalances);
    final filteredSavings = _filterBalancesByUSDValue(savingsBalances);
    
    // 添加过滤后的调试信息
    print('🔍 [OKX Debug] 过滤后Trading: ${filteredTrading.length}条');
    print('🔍 [OKX Debug] 过滤后Funding: ${filteredFunding.length}条');
    print('🔍 [OKX Debug] 过滤后Savings: ${filteredSavings.length}条');
    
    // 计算总资产（转换为当前基准货币）
    double totalAssets = 0.0;
    totalAssets += _calculateTotalValueInBaseCurrency(filteredTrading);
    totalAssets += _calculateTotalValueInBaseCurrency(filteredFunding);
    totalAssets += _calculateTotalValueInBaseCurrency(filteredSavings);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(T.spacingL),
      decoration: BoxDecoration(
        color: T.cardBackground,
        borderRadius: BorderRadius.circular(T.radiusL),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题行
          Row(
            children: [
              Icon(
                Icons.currency_bitcoin,
                color: T.primary,
                size: 24,
              ),
              const SizedBox(width: T.spacingS),
              Expanded(
                child: Text(
                  'OKX·数字货币',
                  style: TextStyle(
                    fontSize: T.fontSizeL,
                    fontWeight: FontWeight.bold,
                    color: T.textPrimary,
                  ),
                ),
              ),
              IconButton(
                onPressed: () {
                  // TODO: 实现数据同步
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('OKX数据同步功能开发中...')),
                  );
                },
                icon: Icon(
                  Icons.sync,
                  color: T.iconSecondary,
                  size: 20,
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingM),

          // 更新状态和总资产
          Row(
            children: [
              Text(
                '1小时前更新·${_currencyManager.getCurrencySymbol(_currentBaseCurrency)}${totalAssets.toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  color: T.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingS),

          // 账户状态
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: T.spacingS,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: T.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(T.radiusS),
                ),
                child: Text(
                  '正常·${filteredTrading.length + filteredFunding.length + filteredSavings.length}种货币',
                  style: TextStyle(
                    fontSize: T.fontSizeS,
                    color: T.success,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingM),

          // 交易账户余额
          if (filteredTrading.isNotEmpty) ...[
            _buildAccountSection('Trading', filteredTrading),
            const SizedBox(height: T.spacingM),
          ],

          // 资金账户余额
          if (filteredFunding.isNotEmpty) ...[
            _buildAccountSection('Funding', filteredFunding),
            const SizedBox(height: T.spacingM),
          ],

          // 储蓄账户余额
          if (filteredSavings.isNotEmpty) ...[
            _buildAccountSection('Savings', filteredSavings),
            const SizedBox(height: T.spacingM),
          ],

          // 分割线
          Divider(color: T.divider, height: 1),
          const SizedBox(height: T.spacingS),

          // 持仓信息
          if (_okxPositions.isNotEmpty) ...[
            Row(
              children: [
                Text(
                  '持仓数量:',
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    color: T.textSecondary,
                  ),
                ),
                const Spacer(),
                Text(
                  '${_okxSummary['position_count'] ?? 0}个',
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    fontWeight: FontWeight.w500,
                    color: T.textPrimary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: T.spacingS),
          ],
        ],
      ),
    );
  }

  /// 构建账户区块
  Widget _buildAccountSection(String accountType, List<OKXBalance> balances) {
    // 按余额排序
    balances.sort((a, b) => b.totalBalance.compareTo(a.totalBalance));
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 账户类型标签
        Container(
          padding: const EdgeInsets.symmetric(horizontal: T.spacingS, vertical: T.spacingXS),
          decoration: BoxDecoration(
            color: T.surfaceBackground,
            borderRadius: BorderRadius.circular(T.radiusS),
            border: Border.all(color: T.divider, width: 1),
          ),
          child: Text(
            accountType,
            style: TextStyle(
              fontSize: T.fontSizeS,
              color: T.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        const SizedBox(height: T.spacingS),
        
        // 货币余额列表
        ...balances.map((balance) => Padding(
          padding: const EdgeInsets.only(bottom: T.spacingS),
          child: Row(
            children: [
              // 左侧：货币代码（不显示中文名称）
              Expanded(
                flex: 2,
                child: Text(
                  balance.currency,
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    fontWeight: FontWeight.w500,
                    color: T.textPrimary,
                  ),
                ),
              ),
              // 中间：数量（不显示单位）
              Expanded(
                flex: 2,
                child: Text(
                  balance.totalBalance.toStringAsFixed(6),
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    fontWeight: FontWeight.w500,
                    color: T.textPrimary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              // 右侧：价值（按当前计价标准，四舍五入）
              Expanded(
                flex: 2,
                child: Text(
                  '≈ ${_currencyManager.getCurrencySymbol(_currentBaseCurrency)}${_getOKXBalanceInBaseCurrency(balance).toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    color: T.textSecondary,
                  ),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          ),
        )),
      ],
    );
  }

  /// 过滤掉小于1美元的余额
  List<OKXBalance> _filterBalancesByUSDValue(List<OKXBalance> balances) {
    return balances.where((balance) {
      final usdValue = _getOKXBalanceInUSD(balance);
      return usdValue >= 1.0; // 只显示大于等于1美元的资产
    }).toList();
  }

  /// 计算余额对应的USD价值
  double _getOKXBalanceInUSD(OKXBalance balance) {
    // 这里需要根据实际汇率计算，暂时使用模拟值
    switch (balance.currency.toUpperCase()) {
      case 'BTC':
        return balance.totalBalance * 45000; // 模拟BTC价格
      case 'ETH':
        return balance.totalBalance * 3000;  // 模拟ETH价格
      case 'USDT':
      case 'USDC':
        return balance.totalBalance;
      case 'USD':
        return balance.totalBalance;
      case 'SOL':
        return balance.totalBalance * 100;   // 模拟SOL价格
      case 'ADA':
        return balance.totalBalance * 0.5;   // 模拟ADA价格
      case 'DOT':
        return balance.totalBalance * 7;     // 模拟DOT价格
      case 'LINK':
        return balance.totalBalance * 15;    // 模拟LINK价格
      default:
        return balance.totalBalance; // 其他货币暂时按1:1计算
    }
  }

  /// 计算总价值（转换为当前基准货币）
  double _calculateTotalValueInBaseCurrency(List<OKXBalance> balances) {
    double total = 0.0;
    for (final balance in balances) {
      total += _getOKXBalanceInBaseCurrency(balance);
    }
    return total;
  }



  /// 计算OKX余额对应的基准货币金额
  double _getOKXBalanceInBaseCurrency(OKXBalance balance) {
    // 这里需要根据实际汇率计算，暂时使用模拟值
    double usdValue = 0.0;
    switch (balance.currency.toUpperCase()) {
      case 'BTC':
        usdValue = balance.totalBalance * 45000; // 模拟BTC价格
        break;
      case 'ETH':
        usdValue = balance.totalBalance * 3000;  // 模拟ETH价格
        break;
      case 'USDT':
      case 'USDC':
        usdValue = balance.totalBalance;
        break;
      default:
        usdValue = balance.totalBalance;
    }
    
    return _getTotalAssetsInBaseCurrency(usdValue, 'USD');
  }
  
  /// 计算余额对应的CNY金额（修复汇率计算）
  double _getBalanceInCNY(WiseBalance balance, double usdCnyRate) {
    switch (balance.currency.toUpperCase()) {
      case 'USD':
        return balance.availableBalance * usdCnyRate;
      case 'EUR':
        // EUR → USD → CNY: EUR × (1/USD/EUR) × USD/CNY
        return balance.availableBalance * (1 / 0.92) * usdCnyRate;
      case 'GBP':
        // GBP → USD → CNY: GBP × (1/USD/GBP) × USD/CNY
        return balance.availableBalance * (1 / 1.26) * usdCnyRate;
      case 'JPY':
        // JPY → USD → CNY: JPY × (1/USD/JPY) × USD/CNY
        return balance.availableBalance * (1 / 150) * usdCnyRate;
      case 'AUD':
        // AUD → USD → CNY: AUD × (1/USD/AUD) × USD/CNY
        return balance.availableBalance * (1 / 0.66) * usdCnyRate;
      case 'CNY':
        return balance.availableBalance;
      case 'HKD':
        // HKD → USD → CNY: HKD × (1/USD/HKD) × USD/CNY
        return balance.availableBalance * (1 / 7.8) * usdCnyRate;
      case 'SGD':
        // SGD → USD → CNY: SGD × (1/USD/SGD) × USD/CNY
        return balance.availableBalance * (1 / 1.35) * usdCnyRate;
      case 'CHF':
        // CHF → USD → CNY: CHF × (1/USD/CHF) × USD/CNY
        return balance.availableBalance * (1 / 0.88) * usdCnyRate;
      case 'CAD':
        // CAD → USD → CNY: CAD × (1/USD/CAD) × USD/CNY
        return balance.availableBalance * (1 / 1.35) * usdCnyRate;
      default:
        return balance.availableBalance * usdCnyRate; // 默认按USD汇率
    }
  }

  /// 计算总资产对应的基准货币金额
  double _getTotalAssetsInBaseCurrency(double totalAssets, String baseCurrency) {
    final baseCurr = baseCurrency.toUpperCase();
    final usdCnyRate = _exchangeRates['USD_CNY']?['rate'] ?? 7.13; // 默认USD/CNY汇率

    if (baseCurr == 'CNY') {
      return totalAssets;
    }

    if (baseCurr == 'USD') {
      return totalAssets;
    }

    if (baseCurr == 'EUR') {
      return totalAssets * 0.92; // USD/EUR汇率
    }

    if (baseCurr == 'GBP') {
      return totalAssets * 1.26; // USD/GBP汇率
    }

    if (baseCurr == 'JPY') {
      return totalAssets * 150; // USD/JPY汇率
    }

    if (baseCurr == 'AUD') {
      return totalAssets * 0.66; // USD/AUD汇率
    }

    if (baseCurr == 'HKD') {
      return totalAssets * 7.8; // USD/HKD汇率
    }

    if (baseCurr == 'SGD') {
      return totalAssets * 1.35; // USD/SGD汇率
    }

    if (baseCurr == 'CHF') {
      return totalAssets * 0.88; // USD/CHF汇率
    }

    if (baseCurr == 'CAD') {
      return totalAssets * 1.35; // USD/CAD汇率
    }

    return totalAssets; // 默认按USD处理
  }
}
