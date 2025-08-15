import 'package:flutter/material.dart';
import 'chart_design_system.dart';
import 'chart_save_dialog.dart';

/// 图表预览模态框 - 在聊天中点击图表时打开
class ChartPreviewModal extends StatefulWidget {
  final Widget chartWidget;
  final String question;
  final String chartType;
  final Function(Widget chart, String question)? onSaveChart;

  const ChartPreviewModal({
    super.key,
    required this.chartWidget,
    required this.question,
    required this.chartType,
    this.onSaveChart,
  });

  @override
  State<ChartPreviewModal> createState() => _ChartPreviewModalState();
}

class _ChartPreviewModalState extends State<ChartPreviewModal>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
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
    super.dispose();
  }

  /// 显示图表预览模态框
  static void show(
    BuildContext context, {
    required Widget chartWidget,
    required String question,
    required String chartType,
    Function(Widget chart, String question)? onSaveChart,
  }) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: '图表预览',
      barrierColor: Colors.black.withOpacity(0.5),
      transitionDuration: const Duration(milliseconds: 300),
      pageBuilder: (context, animation, secondaryAnimation) {
        return ChartPreviewModal(
          chartWidget: chartWidget,
          question: question,
          chartType: chartType,
          onSaveChart: onSaveChart,
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
              maxHeight: MediaQuery.of(context).size.height * 0.8,
              maxWidth: MediaQuery.of(context).size.width * 0.9,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // 头部区域
                _buildHeader(),
                
                // 图表内容区域
                Flexible(
                  child: _buildChartContent(),
                ),
                
                // 操作按钮区域
                _buildActionButtons(),
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
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: ChartDesignSystem.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getChartIcon(),
                  color: ChartDesignSystem.primary,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '图表预览',
                      style: ChartDesignSystem.titleStyle.copyWith(fontSize: 18),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _getChartTypeDescription(),
                      style: ChartDesignSystem.subtitleStyle.copyWith(fontSize: 12),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.close),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.grey[100],
                  foregroundColor: Colors.grey[600],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: ChartDesignSystem.primary.withOpacity(0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: ChartDesignSystem.primary.withOpacity(0.2),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.psychology,
                  color: ChartDesignSystem.primary,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.question,
                    style: ChartDesignSystem.labelStyle.copyWith(
                      color: ChartDesignSystem.primary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建图表内容
  Widget _buildChartContent() {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 0),
      decoration: const BoxDecoration(
        color: Colors.white,
      ),
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              // 图表区域
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey[200]!),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: widget.chartWidget,
                ),
              ),
              
              const SizedBox(height: 16),
              
              // 图表信息
              _buildChartInfo(),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建图表信息
  Widget _buildChartInfo() {
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
                Icons.info_outline,
                color: ChartDesignSystem.primary,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                '图表信息',
                style: ChartDesignSystem.labelStyle.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildInfoRow('图表类型', _getChartTypeDescription()),
          _buildInfoRow('生成时间', _formatCurrentTime()),
          _buildInfoRow('数据来源', 'MCP智能分析'),
          _buildInfoRow('适用场景', _getChartUsage()),
        ],
      ),
    );
  }

  /// 构建信息行
  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 70,
            child: Text(
              label,
              style: ChartDesignSystem.labelStyle.copyWith(
                color: Colors.grey[600],
                fontSize: 12,
              ),
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

  /// 构建操作按钮
  Widget _buildActionButtons() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
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
          // 主要操作按钮
          Row(
            children: [
              Expanded(
                child: _buildActionButton(
                  '保存到深度分析',
                  Icons.bookmark_add,
                  ChartDesignSystem.secondary,
                  true,
                  _saveToAnalysis,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildActionButton(
                  '查看深度分析',
                  Icons.analytics,
                  ChartDesignSystem.primary,
                  false,
                  _goToAnalysis,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // 次要操作按钮
          Row(
            children: [
              Expanded(
                child: _buildSecondaryButton(
                  '分享图表',
                  Icons.share,
                  _shareChart,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSecondaryButton(
                  '重新生成',
                  Icons.refresh,
                  _regenerateChart,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSecondaryButton(
                  '导出图片',
                  Icons.download,
                  _exportChart,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 构建主要操作按钮
  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    bool isPrimary,
    VoidCallback onPressed,
  ) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 18),
      label: Text(
        label,
        style: TextStyle(
          fontWeight: FontWeight.w600,
          fontSize: 14,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: isPrimary ? color : Colors.white,
        foregroundColor: isPrimary ? Colors.white : color,
        elevation: isPrimary ? 2 : 0,
        side: isPrimary ? null : BorderSide(color: color),
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  /// 构建次要操作按钮
  Widget _buildSecondaryButton(
    String label,
    IconData icon,
    VoidCallback onPressed,
  ) {
    return OutlinedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 16),
      label: Text(
        label,
        style: const TextStyle(fontSize: 12),
      ),
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.grey[700],
        side: BorderSide(color: Colors.grey[300]!),
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  /// 保存到深度分析
  void _saveToAnalysis() {
    ChartSaveDialog.show(
      context,
      chartWidget: widget.chartWidget,
      question: widget.question,
      chartType: widget.chartType,
      onConfirm: (confirmed, customName) {
        if (confirmed) {
          widget.onSaveChart?.call(widget.chartWidget, widget.question);
          
          // 显示成功提示
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.white, size: 20),
                  const SizedBox(width: 8),
                  Text(customName != null 
                      ? '"$customName" 已保存到深度分析页面'
                      : '图表已保存到深度分析页面'),
                ],
              ),
              backgroundColor: ChartDesignSystem.secondary,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              action: SnackBarAction(
                label: '查看',
                textColor: Colors.white,
                onPressed: _goToAnalysis,
              ),
            ),
          );
          
          Navigator.of(context).pop(); // 关闭预览模态框
        }
      },
    );
  }

  /// 前往深度分析页面
  void _goToAnalysis() {
    Navigator.of(context).pop(); // 关闭预览模态框
    // 这里可以导航到深度分析页面
    // Navigator.pushNamed(context, '/deep-analysis');
  }

  /// 分享图表
  void _shareChart() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Icon(Icons.share, color: ChartDesignSystem.primary),
            const SizedBox(width: 8),
            const Text('分享图表'),
          ],
        ),
        content: const Text('分享功能正在开发中，敬请期待！'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('确定', style: TextStyle(color: ChartDesignSystem.primary)),
          ),
        ],
      ),
    );
  }

  /// 重新生成图表
  void _regenerateChart() {
    Navigator.of(context).pop();
    // 这里可以触发重新生成
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('正在重新生成图表...'),
        backgroundColor: ChartDesignSystem.primary,
      ),
    );
  }

  /// 导出图表
  void _exportChart() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Icon(Icons.download, color: ChartDesignSystem.primary),
            const SizedBox(width: 8),
            const Text('导出图表'),
          ],
        ),
        content: const Text('图表导出功能正在开发中！\n\n即将支持：\n• PNG 图片导出\n• PDF 报告导出\n• Excel 数据导出'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('了解了', style: TextStyle(color: ChartDesignSystem.primary)),
          ),
        ],
      ),
    );
  }

  /// 获取图表图标
  IconData _getChartIcon() {
    switch (widget.chartType.toLowerCase()) {
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

  /// 获取图表用途
  String _getChartUsage() {
    switch (widget.chartType.toLowerCase()) {
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

  /// 格式化当前时间
  String _formatCurrentTime() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
  }
}