import 'package:flutter/material.dart';
import '../design/design_tokens.dart';
import '../models/fund_operation.dart';
import '../models/fund_position.dart';
import '../services/fund_operation_service.dart';
import '../services/alipay_fund_service.dart';

class FundOperationPage extends StatefulWidget {
  final FundPosition? fundPosition; // 如果从持仓页面进入，传入基金信息
  
  const FundOperationPage({
    super.key,
    this.fundPosition,
  });

  @override
  State<FundOperationPage> createState() => _FundOperationPageState();
}

class _FundOperationPageState extends State<FundOperationPage> {
  String _selectedOperationType = 'buy';
  String _selectedFundCode = '';
  String _selectedFundName = '';
  final TextEditingController _amountController = TextEditingController();
  final TextEditingController _navController = TextEditingController();
  final TextEditingController _feeController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();
  
  int _emotionScore = 5;
  String _strategy = '';
  bool _isLoading = false;
  String? _errorMessage;
  
  List<FundPosition> _fundPositions = [];
  double? _currentNav;
  double? _avgCost;
  
  @override
  void initState() {
    super.initState();
    _loadFundData();
    _initializeForm();
  }
  
  @override
  void dispose() {
    _amountController.dispose();
    _navController.dispose();
    _feeController.dispose();
    _notesController.dispose();
    super.dispose();
  }
  
  /// 加载基金数据
  Future<void> _loadFundData() async {
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
      
      // 获取基金持仓列表
      final positions = await AlipayFundService.getFundPositions();
      
      // 如果从持仓页面进入，预填充基金信息
      if (widget.fundPosition != null) {
        _selectedFundCode = widget.fundPosition!.assetCode;
        _selectedFundName = widget.fundPosition!.assetName;
        _avgCost = widget.fundPosition!.avgCost;
        
        // 获取最新净值
        _currentNav = await FundOperationService.getLatestNav(_selectedFundCode);
        if (_currentNav != null) {
          _navController.text = _currentNav!.toStringAsFixed(4);
        }
      }
      
      setState(() {
        _fundPositions = positions;
        _isLoading = false;
      });
      
      // 智能建议
      _updateSmartSuggestions();
      
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }
  
  /// 初始化表单
  void _initializeForm() {
    _feeController.text = '0.00';
    _updateSmartSuggestions();
  }
  
  /// 更新智能建议
  void _updateSmartSuggestions() {
    if (_selectedOperationType.isNotEmpty && _amountController.text.isNotEmpty) {
      final amount = double.tryParse(_amountController.text) ?? 0;
      final nav = double.tryParse(_navController.text);
      
      // 智能策略建议
      _strategy = FundOperationService.getSmartStrategy(
        operationType: _selectedOperationType,
        amount: amount,
        currentNav: nav,
        avgCost: _avgCost,
        marketTrend: _getMarketTrend(),
      );
      
      // 智能情绪评分
      _emotionScore = FundOperationService.getSmartEmotionScore(
        operationType: _selectedOperationType,
        amount: amount,
        currentNav: nav,
        avgCost: _avgCost,
        marketTrend: _getMarketTrend(),
      );
      
      setState(() {});
    }
  }
  
  /// 获取市场趋势（简化版本，实际可以从API获取）
  String _getMarketTrend() {
    // 这里可以根据实际数据计算市场趋势
    // 暂时返回中性
    return 'neutral';
  }
  
  /// 提交操作
  Future<void> _submitOperation() async {
    if (_selectedFundCode.isEmpty || _amountController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请填写完整的操作信息')),
      );
      return;
    }
    
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
      
      final operation = FundOperation(
        operationDate: DateTime.now().toIso8601String(),
        operationType: _selectedOperationType,
        assetCode: _selectedFundCode,
        assetName: _selectedFundName,
        amount: double.parse(_amountController.text),
        nav: double.tryParse(_navController.text),
        fee: double.tryParse(_feeController.text),
        quantity: _calculateQuantity(),
        strategy: _strategy,
        emotionScore: _emotionScore,
        notes: _notesController.text.isEmpty ? null : _notesController.text,
      );
      
      final result = await FundOperationService.createOperation(operation);
      
      if (result['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'] ?? '操作记录创建成功')),
        );
        Navigator.pop(context, true); // 返回并刷新
      } else {
        throw Exception(result['message'] ?? '创建失败');
      }
      
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('创建失败: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  /// 计算数量
  double? _calculateQuantity() {
    final amount = double.tryParse(_amountController.text);
    final nav = double.tryParse(_navController.text);
    
    if (amount != null && nav != null && nav > 0) {
      return amount / nav;
    }
    return null;
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('基金操作'),
        backgroundColor: T.primary,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(T.spacingL),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 操作类型选择
                  _buildOperationTypeSelector(),
                  const SizedBox(height: T.spacingL),
                  
                  // 基金选择
                  _buildFundSelector(),
                  const SizedBox(height: T.spacingL),
                  
                  // 操作金额
                  _buildAmountInput(),
                  const SizedBox(height: T.spacingL),
                  
                  // 净值输入
                  _buildNavInput(),
                  const SizedBox(height: T.spacingL),
                  
                  // 手续费
                  _buildFeeInput(),
                  const SizedBox(height: T.spacingL),
                  
                  // 智能建议
                  _buildSmartSuggestions(),
                  const SizedBox(height: T.spacingL),
                  
                  // 备注
                  _buildNotesInput(),
                  const SizedBox(height: T.spacingL),
                  
                  // 提交按钮
                  _buildSubmitButton(),
                  
                  if (_errorMessage != null) ...[
                    const SizedBox(height: T.spacingM),
                    Container(
                      padding: const EdgeInsets.all(T.spacingM),
                      decoration: BoxDecoration(
                        color: T.error.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(T.radiusM),
                      ),
                      child: Text(
                        _errorMessage!,
                        style: TextStyle(color: T.error),
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }
  
  /// 操作类型选择器
  Widget _buildOperationTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '操作类型',
          style: TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: FontWeight.bold,
            color: T.textPrimary,
          ),
        ),
        const SizedBox(height: T.spacingM),
        Row(
          children: [
            Expanded(
              child: _buildOperationTypeButton('buy', '买入', '📈', Colors.green),
            ),
            const SizedBox(width: T.spacingS),
            Expanded(
              child: _buildOperationTypeButton('sell', '卖出', '📉', Colors.red),
            ),
            const SizedBox(width: T.spacingS),
            Expanded(
              child: _buildOperationTypeButton('dividend', '分红', '💰', Colors.blue),
            ),
          ],
        ),
      ],
    );
  }
  
  /// 操作类型按钮
  Widget _buildOperationTypeButton(String type, String label, String icon, Color color) {
    final isSelected = _selectedOperationType == type;
    
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedOperationType = type;
        });
        _updateSmartSuggestions();
      },
      child: Container(
        padding: const EdgeInsets.all(T.spacingM),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.1) : T.cardBackground,
          border: Border.all(
            color: isSelected ? color : T.border,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(T.radiusM),
        ),
        child: Column(
          children: [
            Text(
              icon,
              style: const TextStyle(fontSize: 24),
            ),
            const SizedBox(height: T.spacingS),
            Text(
              label,
              style: TextStyle(
                fontSize: T.fontSizeM,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? color : T.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 基金选择器
  Widget _buildFundSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '选择基金',
          style: TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: FontWeight.bold,
            color: T.textPrimary,
          ),
        ),
        const SizedBox(height: T.spacingM),
        DropdownButtonFormField<String>(
          value: _selectedFundCode.isEmpty ? null : _selectedFundCode,
          decoration: InputDecoration(
            labelText: '基金代码',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
          ),
          items: _fundPositions.map((position) {
            return DropdownMenuItem(
              value: position.assetCode,
              child: Text('${position.assetCode} - ${position.assetName}'),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null) {
              final position = _fundPositions.firstWhere((p) => p.assetCode == value);
              setState(() {
                _selectedFundCode = value;
                _selectedFundName = position.assetName;
                _avgCost = position.avgCost;
              });
              _updateSmartSuggestions();
            }
          },
        ),
      ],
    );
  }
  
  /// 金额输入
  Widget _buildAmountInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '操作金额 (¥)',
          style: TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: FontWeight.bold,
            color: T.textPrimary,
          ),
        ),
        const SizedBox(height: T.spacingM),
        TextField(
          controller: _amountController,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: '请输入金额',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            suffixText: '元',
          ),
          onChanged: (value) => _updateSmartSuggestions(),
        ),
      ],
    );
  }
  
  /// 净值输入
  Widget _buildNavInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '基金净值',
          style: TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: FontWeight.bold,
            color: T.textPrimary,
          ),
        ),
        const SizedBox(height: T.spacingM),
        TextField(
          controller: _navController,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: '请输入净值',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            suffixText: '元/份',
          ),
          onChanged: (value) => _updateSmartSuggestions(),
        ),
        if (_currentNav != null) ...[
          const SizedBox(height: T.spacingS),
          Text(
            '最新净值: ¥${_currentNav!.toStringAsFixed(4)}',
            style: TextStyle(
              fontSize: T.fontSizeS,
              color: T.textSecondary,
            ),
          ),
        ],
      ],
    );
  }
  
  /// 手续费输入
  Widget _buildFeeInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '手续费 (¥)',
          style: TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: FontWeight.bold,
            color: T.textPrimary,
          ),
        ),
        const SizedBox(height: T.spacingM),
        TextField(
          controller: _feeController,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: '请输入手续费',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            suffixText: '元',
          ),
        ),
      ],
    );
  }
  
  /// 智能建议
  Widget _buildSmartSuggestions() {
    return Container(
      padding: const EdgeInsets.all(T.spacingM),
      decoration: BoxDecoration(
        color: T.primary.withOpacity(0.05),
        borderRadius: BorderRadius.circular(T.radiusM),
        border: Border.all(color: T.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb, color: T.primary, size: 20),
              const SizedBox(width: T.spacingS),
              Text(
                '智能建议',
                style: TextStyle(
                  fontSize: T.fontSizeL,
                  fontWeight: FontWeight.bold,
                  color: T.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingM),
          
          // 策略建议
          Row(
            children: [
              Text(
                '策略: ',
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  fontWeight: FontWeight.w500,
                  color: T.textPrimary,
                ),
              ),
              Expanded(
                child: Text(
                  _strategy,
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    color: T.textSecondary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingS),
          
          // 情绪评分
          Row(
            children: [
              Text(
                '情绪评分: ',
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  fontWeight: FontWeight.w500,
                  color: T.textPrimary,
                ),
              ),
              Text(
                _emotionScore.toString(),
                style: TextStyle(
                  fontSize: T.fontSizeM,
                  fontWeight: FontWeight.bold,
                  color: T.primary,
                ),
              ),
              const SizedBox(width: T.spacingS),
              Text(
                _getEmotionScoreDisplay(_emotionScore),
                style: TextStyle(
                  fontSize: T.fontSizeS,
                  color: T.textSecondary,
                ),
              ),
            ],
          ),
          
          // 数量计算
          if (_calculateQuantity() != null) ...[
            const SizedBox(height: T.spacingS),
            Row(
              children: [
                Text(
                  '预计数量: ',
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    fontWeight: FontWeight.w500,
                    color: T.textPrimary,
                  ),
                ),
                Text(
                  '${_calculateQuantity()!.toStringAsFixed(2)} 份',
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    fontWeight: FontWeight.bold,
                    color: T.success,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
  
  /// 获取情绪评分显示
  String _getEmotionScoreDisplay(int score) {
    switch (score) {
      case 1:
        return '😰 极度恐慌';
      case 2:
        return '😨 恐慌';
      case 3:
        return '😟 担忧';
      case 4:
        return '😐 中性';
      case 5:
        return '😊 乐观';
      case 6:
        return '😄 积极';
      case 7:
        return '😃 兴奋';
      case 8:
        return '🤩 狂热';
      case 9:
        return '🚀 极度乐观';
      case 10:
        return '💎 钻石手';
      default:
        return '未评分';
    }
  }
  
  /// 备注输入
  Widget _buildNotesInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '备注',
          style: TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: FontWeight.bold,
            color: T.textPrimary,
          ),
        ),
        const SizedBox(height: T.spacingM),
        TextField(
          controller: _notesController,
          maxLines: 3,
          decoration: InputDecoration(
            labelText: '请输入备注信息（可选）',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            hintText: '例如：市场调整，低位补仓',
          ),
        ),
      ],
    );
  }
  
  /// 提交按钮
  Widget _buildSubmitButton() {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _submitOperation,
        style: ElevatedButton.styleFrom(
          backgroundColor: T.primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(T.radiusM),
          ),
        ),
        child: _isLoading
            ? const CircularProgressIndicator(color: Colors.white)
            : Text(
                '确认${_selectedOperationType == 'buy' ? '买入' : _selectedOperationType == 'sell' ? '卖出' : '分红'}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }
}
