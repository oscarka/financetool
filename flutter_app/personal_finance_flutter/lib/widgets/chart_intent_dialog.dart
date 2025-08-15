import 'package:flutter/material.dart';
import 'chart_design_system.dart';

/// 图表意图确认对话框 - 在识别到图表意图后弹出确认
class ChartIntentDialog extends StatefulWidget {
  final String userQuestion;
  final String detectedChartType;
  final Function(bool confirmed, String? modifiedQuestion) onConfirm;

  const ChartIntentDialog({
    super.key,
    required this.userQuestion,
    required this.detectedChartType,
    required this.onConfirm,
  });

  @override
  State<ChartIntentDialog> createState() => _ChartIntentDialogState();
}

class _ChartIntentDialogState extends State<ChartIntentDialog>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  
  final TextEditingController _questionController = TextEditingController();
  bool _isModifying = false;

  @override
  void initState() {
    super.initState();
    _questionController.text = widget.userQuestion;
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );
    
    _scaleAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    );
    
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _questionController.dispose();
    super.dispose();
  }

  /// 显示图表意图确认对话框
  static void show(
    BuildContext context, {
    required String userQuestion,
    required String detectedChartType,
    required Function(bool confirmed, String? modifiedQuestion) onConfirm,
  }) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: '图表确认',
      barrierColor: Colors.black.withOpacity(0.5),
      transitionDuration: const Duration(milliseconds: 400),
      pageBuilder: (context, animation, secondaryAnimation) {
        return ChartIntentDialog(
          userQuestion: userQuestion,
          detectedChartType: detectedChartType,
          onConfirm: onConfirm,
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: Dialog(
          backgroundColor: Colors.transparent,
          child: Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.9,
            ),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildHeader(),
                _buildContent(),
                _buildActions(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// 构建头部
  Widget _buildHeader() {
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
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(25),
            ),
            child: Icon(
              _getChartIcon(),
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
                  '🤖 AI检测到图表需求',
                  style: ChartDesignSystem.titleStyle.copyWith(
                    color: Colors.white,
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '是否为您生成${_getChartTypeDescription()}？',
                  style: ChartDesignSystem.subtitleStyle.copyWith(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建内容
  Widget _buildContent() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI分析结果
          _buildAnalysisResult(),
          
          const SizedBox(height: 20),
          
          // 用户问题编辑
          _buildQuestionEditor(),
          
          const SizedBox(height: 16),
          
          // 图表预览信息
          _buildChartPreview(),
        ],
      ),
    );
  }

  /// 构建AI分析结果
  Widget _buildAnalysisResult() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ChartDesignSystem.primary.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: ChartDesignSystem.primary.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.psychology,
                color: ChartDesignSystem.primary,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                'AI智能分析',
                style: ChartDesignSystem.labelStyle.copyWith(
                  fontWeight: FontWeight.w600,
                  color: ChartDesignSystem.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildAnalysisItem('识别意图', '图表生成请求'),
          _buildAnalysisItem('推荐图表', _getChartTypeDescription()),
          _buildAnalysisItem('数据来源', 'MCP智能分析'),
          _buildAnalysisItem('预计时间', '2-3秒'),
        ],
      ),
    );
  }

  /// 构建分析项
  Widget _buildAnalysisItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          SizedBox(
            width: 70,
            child: Text(
              label,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ),
          Text(
            ': ',
            style: ChartDesignSystem.labelStyle.copyWith(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: ChartDesignSystem.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建问题编辑器
  Widget _buildQuestionEditor() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '您的问题',
              style: ChartDesignSystem.labelStyle.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: () {
                setState(() {
                  _isModifying = !_isModifying;
                });
              },
              icon: Icon(
                _isModifying ? Icons.check : Icons.edit,
                size: 16,
              ),
              label: Text(_isModifying ? '确认' : '修改'),
              style: TextButton.styleFrom(
                foregroundColor: ChartDesignSystem.primary,
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            border: Border.all(
              color: _isModifying 
                  ? ChartDesignSystem.primary 
                  : Colors.grey[300]!,
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: TextField(
            controller: _questionController,
            enabled: _isModifying,
            maxLines: 2,
            decoration: InputDecoration(
              border: InputBorder.none,
              contentPadding: const EdgeInsets.all(12),
              hintText: '请描述您想要的图表...',
              hintStyle: TextStyle(color: Colors.grey[500]),
            ),
            style: ChartDesignSystem.labelStyle.copyWith(
              color: _isModifying ? Colors.black : Colors.grey[700],
            ),
          ),
        ),
      ],
    );
  }

  /// 构建图表预览信息
  Widget _buildChartPreview() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                _getChartIcon(),
                color: ChartDesignSystem.secondary,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                '将要生成的图表',
                style: ChartDesignSystem.labelStyle.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: ChartDesignSystem.secondary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getChartIcon(),
                  color: ChartDesignSystem.secondary,
                  size: 30,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getChartTypeDescription(),
                      style: ChartDesignSystem.labelStyle.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _getChartUsage(),
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
        ],
      ),
    );
  }

  /// 构建操作按钮
  Widget _buildActions() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(20)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pop();
                    widget.onConfirm(false, null);
                  },
                  icon: const Icon(Icons.close, size: 18),
                  label: const Text('取消'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.grey[700],
                    side: BorderSide(color: Colors.grey[300]!),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                flex: 2,
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pop();
                    widget.onConfirm(
                      true, 
                      _questionController.text.trim() != widget.userQuestion
                          ? _questionController.text.trim()
                          : null,
                    );
                  },
                  icon: const Icon(Icons.auto_awesome, size: 18),
                  label: const Text('生成图表'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: ChartDesignSystem.secondary,
                    foregroundColor: Colors.white,
                    elevation: 2,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '💡 提示：生成后您可以在聊天中预览，点击查看详情并选择是否保存',
            style: ChartDesignSystem.labelStyle.copyWith(
              fontSize: 11,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  /// 获取图表图标
  IconData _getChartIcon() {
    switch (widget.detectedChartType.toLowerCase()) {
      case 'pie':
        return Icons.pie_chart;
      case 'bar':
        return Icons.bar_chart;
      case 'line':
        return Icons.show_chart;
      case 'table':
        return Icons.table_chart;
      default:
        return Icons.insert_chart;
    }
  }

  /// 获取图表类型描述
  String _getChartTypeDescription() {
    switch (widget.detectedChartType.toLowerCase()) {
      case 'pie':
        return '饼图 - 占比分析';
      case 'bar':
        return '柱状图 - 数值对比';
      case 'line':
        return '折线图 - 趋势分析';
      case 'table':
        return '数据表格 - 详细信息';
      default:
        return '智能图表';
    }
  }

  /// 获取图表用途
  String _getChartUsage() {
    switch (widget.detectedChartType.toLowerCase()) {
      case 'pie':
        return '适用于展示各部分占总体的比例关系';
      case 'bar':
        return '适用于比较不同类别的数值大小';
      case 'line':
        return '适用于展示数据随时间的变化趋势';
      case 'table':
        return '适用于展示详细的数据明细信息';
      default:
        return '智能选择最适合的图表类型';
    }
  }
}