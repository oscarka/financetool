import 'package:flutter/material.dart';
import 'chart_design_system.dart';

/// 图表保存确认对话框 - 在用户要保存图表时弹出确认
class ChartSaveDialog extends StatefulWidget {
  final Widget chartWidget;
  final String question;
  final String chartType;
  final Function(bool confirmed, String? customName) onConfirm;

  const ChartSaveDialog({
    super.key,
    required this.chartWidget,
    required this.question,
    required this.chartType,
    required this.onConfirm,
  });

  @override
  State<ChartSaveDialog> createState() => _ChartSaveDialogState();
}

class _ChartSaveDialogState extends State<ChartSaveDialog>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  
  final TextEditingController _nameController = TextEditingController();
  bool _isCustomNaming = false;
  String _selectedCategory = '投资分析';
  
  final List<String> _categories = [
    '投资分析',
    '资产分布',
    '收益统计',
    '风险评估',
    '市场趋势',
    '自定义'
  ];

  @override
  void initState() {
    super.initState();
    _nameController.text = _generateDefaultName();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 350),
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
    _nameController.dispose();
    super.dispose();
  }

  /// 显示图表保存确认对话框
  static void show(
    BuildContext context, {
    required Widget chartWidget,
    required String question,
    required String chartType,
    required Function(bool confirmed, String? customName) onConfirm,
  }) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: '保存图表',
      barrierColor: Colors.black.withOpacity(0.5),
      transitionDuration: const Duration(milliseconds: 350),
      pageBuilder: (context, animation, secondaryAnimation) {
        return ChartSaveDialog(
          chartWidget: chartWidget,
          question: question,
          chartType: chartType,
          onConfirm: onConfirm,
        );
      },
    );
  }

  /// 生成默认名称
  String _generateDefaultName() {
    final now = DateTime.now();
    final timeStr = '${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
    
    switch (widget.chartType.toLowerCase()) {
      case 'pie':
        return '资产占比分析 $timeStr';
      case 'bar':
        return '数值对比分析 $timeStr';
      case 'line':
        return '趋势变化分析 $timeStr';
      case 'table':
        return '数据明细表 $timeStr';
      default:
        return '智能图表分析 $timeStr';
    }
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
              maxHeight: MediaQuery.of(context).size.height * 0.8,
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
                Flexible(child: _buildContent()),
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
            ChartDesignSystem.secondary,
            ChartDesignSystem.secondary.withOpacity(0.8),
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
            child: const Icon(
              Icons.bookmark_add,
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
                  '💾 保存图表到深度分析',
                  style: ChartDesignSystem.titleStyle.copyWith(
                    color: Colors.white,
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '为您的图表添加备注，方便日后查找',
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
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 图表预览
            _buildChartPreview(),
            
            const SizedBox(height: 24),
            
            // 图表信息
            _buildChartInfo(),
            
            const SizedBox(height: 24),
            
            // 命名设置
            _buildNamingSection(),
            
            const SizedBox(height: 20),
            
            // 分类设置
            _buildCategorySection(),
          ],
        ),
      ),
    );
  }

  /// 构建图表预览
  Widget _buildChartPreview() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  Icons.preview,
                  color: ChartDesignSystem.primary,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Text(
                  '图表预览',
                  style: ChartDesignSystem.labelStyle.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(12),
              ),
            ),
            child: ClipRRect(
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(12),
              ),
              child: widget.chartWidget,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建图表信息
  Widget _buildChartInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ChartDesignSystem.secondary.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: ChartDesignSystem.secondary.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.info_outline,
                color: ChartDesignSystem.secondary,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                '图表详情',
                style: ChartDesignSystem.labelStyle.copyWith(
                  fontWeight: FontWeight.w600,
                  color: ChartDesignSystem.secondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildInfoRow('原始问题', widget.question),
          _buildInfoRow('图表类型', _getChartTypeDescription()),
          _buildInfoRow('生成时间', _formatCurrentTime()),
          _buildInfoRow('数据来源', 'MCP智能分析'),
        ],
      ),
    );
  }

  /// 构建信息行
  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
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
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建命名设置
  Widget _buildNamingSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '图表名称',
              style: ChartDesignSystem.labelStyle.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: () {
                setState(() {
                  _isCustomNaming = !_isCustomNaming;
                });
              },
              icon: Icon(
                _isCustomNaming ? Icons.auto_awesome : Icons.edit,
                size: 16,
              ),
              label: Text(_isCustomNaming ? '使用默认' : '自定义'),
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
              color: _isCustomNaming 
                  ? ChartDesignSystem.primary 
                  : Colors.grey[300]!,
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: TextField(
            controller: _nameController,
            enabled: _isCustomNaming,
            decoration: InputDecoration(
              border: InputBorder.none,
              contentPadding: const EdgeInsets.all(12),
              hintText: '为您的图表起个名字...',
              hintStyle: TextStyle(color: Colors.grey[500]),
              prefixIcon: Icon(
                Icons.title,
                color: _isCustomNaming 
                    ? ChartDesignSystem.primary 
                    : Colors.grey[400],
                size: 20,
              ),
            ),
            style: ChartDesignSystem.labelStyle.copyWith(
              color: _isCustomNaming ? Colors.black : Colors.grey[700],
            ),
          ),
        ),
      ],
    );
  }

  /// 构建分类设置
  Widget _buildCategorySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '图表分类',
          style: ChartDesignSystem.labelStyle.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _categories.map((category) {
            final isSelected = _selectedCategory == category;
            return GestureDetector(
              onTap: () {
                setState(() {
                  _selectedCategory = category;
                });
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected 
                      ? ChartDesignSystem.primary 
                      : Colors.grey[100],
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isSelected 
                        ? ChartDesignSystem.primary 
                        : Colors.grey[300]!,
                  ),
                ),
                child: Text(
                  category,
                  style: ChartDesignSystem.labelStyle.copyWith(
                    fontSize: 12,
                    color: isSelected ? Colors.white : Colors.grey[700],
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  /// 构建操作按钮
  Widget _buildActions() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(20)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
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
                      _isCustomNaming ? _nameController.text.trim() : null,
                    );
                  },
                  icon: const Icon(Icons.bookmark_add, size: 18),
                  label: const Text('保存图表'),
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
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.folder,
                size: 16,
                color: Colors.grey[600],
              ),
              const SizedBox(width: 6),
              Text(
                '保存到：深度分析 > $_selectedCategory',
                style: ChartDesignSystem.labelStyle.copyWith(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 获取图表类型描述
  String _getChartTypeDescription() {
    switch (widget.chartType.toLowerCase()) {
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

  /// 格式化当前时间
  String _formatCurrentTime() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
  }
}