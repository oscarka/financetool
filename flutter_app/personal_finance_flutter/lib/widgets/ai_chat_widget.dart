import 'package:flutter/material.dart';
import 'chart_design_system.dart';
import 'mcp_chart_adapter.dart';
import 'chart_preview_modal.dart';
import 'chart_intent_dialog.dart';
import 'chart_save_dialog.dart';
import 'dart:convert';

/// AI聊天交互组件 - 支持生成图表并保存
class AIChatWidget extends StatefulWidget {
  final Function(Widget chart, String question)? onChartGenerated;
  final bool showSaveButton;
  final String? placeholder;

  const AIChatWidget({
    super.key,
    this.onChartGenerated,
    this.showSaveButton = true,
    this.placeholder,
  });

  @override
  State<AIChatWidget> createState() => _AIChatWidgetState();
}

class _AIChatWidgetState extends State<AIChatWidget>
    with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  
  bool _isLoading = false;
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    );
    
    // 添加欢迎消息
    _addWelcomeMessage();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  /// 添加欢迎消息
  void _addWelcomeMessage() {
    setState(() {
      _messages.add(ChatMessage(
        text: '您好！我是您的AI财务分析助手。我可以帮您分析资产数据并生成专业图表。\n\n试试问我：\n• "显示各平台的资产分布"\n• "最近的资产变化趋势"\n• "收益率最高的投资"',
        isUser: false,
        timestamp: DateTime.now(),
        messageType: ChatMessageType.welcome,
      ));
    });
  }

  /// 发送消息
  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // 添加用户消息
    setState(() {
      _messages.add(ChatMessage(
        text: text,
        isUser: true,
        timestamp: DateTime.now(),
        messageType: ChatMessageType.text,
      ));
      _isLoading = true;
    });

    _messageController.clear();
    _scrollToBottom();

    try {
      // 判断是否是图表请求
      if (_isChartRequest(text)) {
        // 显示意图确认对话框
        _showChartIntentDialog(text);
      } else {
        await _generateTextResponse(text);
      }
    } catch (e) {
      _addErrorMessage('抱歉，处理您的请求时出现了问题。请稍后再试。');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  /// 判断是否是图表请求
  bool _isChartRequest(String text) {
    final chartKeywords = [
      '分布', '占比', '趋势', '变化', '对比', '比较', '统计', '分析',
      '图表', '饼图', '柱状图', '折线图', '走势', '排行', '明细'
    ];
    
    return chartKeywords.any((keyword) => text.contains(keyword));
  }

  /// 判断图表类型
  String _determineChartType(String question) {
    final q = question.toLowerCase();
    
    if (q.contains('占比') || q.contains('分布') || q.contains('比例')) {
      return 'pie';
    } else if (q.contains('趋势') || q.contains('变化') || q.contains('走势')) {
      return 'line';
    } else if (q.contains('对比') || q.contains('排行') || q.contains('比较')) {
      return 'bar';
    } else if (q.contains('明细') || q.contains('列表') || q.contains('详细')) {
      return 'table';
    } else {
      return 'chart'; // 默认类型
    }
  }

  /// 显示图表意图确认对话框
  void _showChartIntentDialog(String originalQuestion) {
    setState(() {
      _isLoading = false; // 停止加载状态
    });

    final chartType = _determineChartType(originalQuestion);
    
    ChartIntentDialog.show(
      context,
      userQuestion: originalQuestion,
      detectedChartType: chartType,
      onConfirm: (confirmed, modifiedQuestion) {
        if (confirmed) {
          final finalQuestion = modifiedQuestion ?? originalQuestion;
          _generateChartResponse(finalQuestion);
        }
      },
    );
  }

  /// 生成图表响应
  Future<void> _generateChartResponse(String question) async {
    try {
      // 生成图表
      final chart = await MCPChartAdapter.generateProfessionalChart(question);
      
      // 添加AI回复
      setState(() {
        _messages.add(ChatMessage(
          text: '我为您生成了专业的数据分析图表：',
          isUser: false,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        
        _messages.add(ChatMessage(
          text: question,
          isUser: false,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.chart,
          chartWidget: chart,
          originalQuestion: question,
          chartType: _determineChartType(question), // 自动判断图表类型
        ));
      });
      
      _scrollToBottom();
      _fadeController.forward();
      
    } catch (e) {
      _addErrorMessage('生成图表时出现问题，请稍后再试。');
    }
  }

  /// 生成文本响应
  Future<void> _generateTextResponse(String question) async {
    await Future.delayed(const Duration(milliseconds: 800)); // 模拟处理时间
    
    String response = _generateSmartResponse(question);
    
    setState(() {
      _messages.add(ChatMessage(
        text: response,
        isUser: false,
        timestamp: DateTime.now(),
        messageType: ChatMessageType.text,
      ));
    });
    
    _scrollToBottom();
  }

  /// 生成智能回复
  String _generateSmartResponse(String question) {
    final q = question.toLowerCase();
    
    if (q.contains('资产') || q.contains('投资')) {
      return '基于您的投资组合，我建议关注以下几个方面：\n\n• 资产配置是否均衡\n• 风险分散情况\n• 收益率表现\n\n如需详细分析，请告诉我您想了解哪个具体方面的数据图表。';
    } else if (q.contains('收益') || q.contains('利润')) {
      return '关于收益分析，我可以为您提供：\n\n• 各平台收益对比\n• 时间段收益趋势\n• 资产类型收益排行\n\n请告诉我您想查看哪种收益分析图表。';
    } else if (q.contains('风险')) {
      return '风险管理很重要！我可以帮您分析：\n\n• 投资风险分布\n• 资产波动情况\n• 风险调整后收益\n\n需要我生成相关的风险分析图表吗？';
    } else {
      return '我理解您的问题。作为您的AI财务助手，我可以：\n\n• 分析您的资产配置\n• 生成各类专业图表\n• 提供投资建议\n\n请描述您想了解的具体财务数据，我会为您生成相应的分析图表。';
    }
  }

  /// 添加错误消息
  void _addErrorMessage(String error) {
    setState(() {
      _messages.add(ChatMessage(
        text: error,
        isUser: false,
        timestamp: DateTime.now(),
        messageType: ChatMessageType.error,
      ));
    });
    _scrollToBottom();
  }

  /// 滚动到底部
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  /// 保存图表到页面
  void _saveChart(Widget chart, String question) {
    // 从对话消息中获取图表类型
    String chartType = 'chart';
    for (final message in _messages.reversed) {
      if (message.chartWidget == chart && message.chartType != null) {
        chartType = message.chartType!;
        break;
      }
    }

    ChartSaveDialog.show(
      context,
      chartWidget: chart,
      question: question,
      chartType: chartType,
      onConfirm: (confirmed, customName) {
        if (confirmed) {
          widget.onChartGenerated?.call(chart, question);
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(customName != null 
                  ? '"$customName" 已保存到深度分析页面'
                  : '图表已保存到深度分析页面'),
              backgroundColor: ChartDesignSystem.secondary,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              action: SnackBarAction(
                label: '查看',
                textColor: Colors.white,
                onPressed: () {
                  // 这里可以导航到深度分析页面
                  Navigator.pushNamed(context, '/deep-analysis');
                },
              ),
            ),
          );
        }
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        children: [
          // 聊天头部
          _buildChatHeader(),
          
          // 聊天内容
          Expanded(
            child: _buildChatContent(),
          ),
          
          // 输入区域
          _buildInputArea(),
        ],
      ),
    );
  }

  /// 构建聊天头部
  Widget _buildChatHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ChartDesignSystem.primary.withOpacity(0.05),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              gradient: ChartDesignSystem.primaryGradient,
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.auto_awesome,
              color: Colors.white,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI财务助手',
                  style: ChartDesignSystem.titleStyle.copyWith(fontSize: 16),
                ),
                Text(
                  '专业数据分析 · 智能图表生成',
                  style: ChartDesignSystem.subtitleStyle.copyWith(fontSize: 12),
                ),
              ],
            ),
          ),
          if (_isLoading)
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: ChartDesignSystem.primary,
              ),
            ),
        ],
      ),
    );
  }

  /// 构建聊天内容
  Widget _buildChatContent() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        return _buildMessageBubble(message);
      },
    );
  }

  /// 构建消息气泡
  Widget _buildMessageBubble(ChatMessage message) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) _buildAvatar(false),
          
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.75,
              ),
              child: message.messageType == ChatMessageType.chart
                  ? _buildChartMessage(message)
                  : _buildTextMessage(message),
            ),
          ),
          
          if (message.isUser) _buildAvatar(true),
        ],
      ),
    );
  }

  /// 构建头像
  Widget _buildAvatar(bool isUser) {
    return Container(
      margin: EdgeInsets.only(
        left: isUser ? 8 : 0,
        right: isUser ? 0 : 8,
        top: 4,
      ),
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: isUser ? ChartDesignSystem.primary : ChartDesignSystem.secondary,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Icon(
        isUser ? Icons.person : Icons.auto_awesome,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  /// 构建文本消息
  Widget _buildTextMessage(ChatMessage message) {
    Color backgroundColor;
    Color textColor;
    
    if (message.isUser) {
      backgroundColor = ChartDesignSystem.primary;
      textColor = Colors.white;
    } else if (message.messageType == ChatMessageType.error) {
      backgroundColor = ChartDesignSystem.danger.withOpacity(0.1);
      textColor = ChartDesignSystem.danger;
    } else if (message.messageType == ChatMessageType.welcome) {
      backgroundColor = ChartDesignSystem.secondary.withOpacity(0.1);
      textColor = Colors.grey[700]!;
    } else {
      backgroundColor = Colors.grey[100]!;
      textColor = Colors.grey[800]!;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            message.text,
            style: ChartDesignSystem.labelStyle.copyWith(
              color: textColor,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            _formatTime(message.timestamp),
            style: ChartDesignSystem.labelStyle.copyWith(
              fontSize: 10,
              color: textColor.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建图表消息
  Widget _buildChartMessage(ChatMessage message) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 图表容器 - 添加点击打开预览功能
        GestureDetector(
          onTap: () => _openChartPreview(message),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[200]!),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Stack(
                children: [
                  message.chartWidget!,
                  // 添加点击提示覆盖层
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.zoom_in,
                            color: Colors.white,
                            size: 12,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '点击查看详情',
                            style: ChartDesignSystem.labelStyle.copyWith(
                              fontSize: 10,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        
        const SizedBox(height: 8),
        
        // 操作按钮
        if (widget.showSaveButton)
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildActionButton(
                '打开详情',
                Icons.open_in_full,
                ChartDesignSystem.primary,
                () => _openChartPreview(message),
              ),
              const SizedBox(width: 8),
              _buildActionButton(
                '快速保存',
                Icons.bookmark_add,
                ChartDesignSystem.secondary,
                () => _saveChart(message.chartWidget!, message.originalQuestion ?? ''),
              ),
              const SizedBox(width: 8),
              _buildActionButton(
                '重新生成',
                Icons.refresh,
                ChartDesignSystem.accent,
                () => _regenerateChart(message.originalQuestion ?? ''),
              ),
            ],
          ),
        
        const SizedBox(height: 4),
        
        // 时间戳
        Text(
          _formatTime(message.timestamp),
          style: ChartDesignSystem.labelStyle.copyWith(
            fontSize: 10,
            color: Colors.grey[500],
          ),
        ),
      ],
    );
  }

  /// 构建操作按钮
  Widget _buildActionButton(String label, IconData icon, Color color, VoidCallback onPressed) {
    return InkWell(
      onTap: onPressed,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(
              label,
              style: ChartDesignSystem.labelStyle.copyWith(
                fontSize: 11,
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 打开图表预览
  void _openChartPreview(ChatMessage message) {
    if (message.chartWidget == null) return;
    
    ChartPreviewModal.show(
      context,
      chartWidget: message.chartWidget!,
      question: message.originalQuestion ?? message.text,
      chartType: message.chartType ?? 'chart',
      onSaveChart: widget.onChartGenerated,
    );
  }

  /// 重新生成图表
  void _regenerateChart(String question) {
    _sendMessage(question);
  }

  /// 构建输入区域
  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        border: Border(top: BorderSide(color: Colors.grey[200]!)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: TextField(
                controller: _messageController,
                decoration: InputDecoration(
                  hintText: widget.placeholder ?? '输入您想了解的财务问题...',
                  hintStyle: TextStyle(color: Colors.grey[500]),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: _sendMessage,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              gradient: ChartDesignSystem.primaryGradient,
              borderRadius: BorderRadius.circular(24),
            ),
            child: IconButton(
              icon: const Icon(Icons.send, color: Colors.white),
              onPressed: _isLoading ? null : () => _sendMessage(_messageController.text),
            ),
          ),
        ],
      ),
    );
  }

  /// 格式化时间
  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

/// 聊天消息数据类
class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final ChatMessageType messageType;
  final Widget? chartWidget;
  final String? originalQuestion;
  final String? chartType; // 添加图表类型字段

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    required this.messageType,
    this.chartWidget,
    this.originalQuestion,
    this.chartType,
  });
}

/// 消息类型枚举
enum ChatMessageType {
  text,
  chart,
  welcome,
  error,
}

/// AI聊天模态框
class AIChatModal {
  static void show(
    BuildContext context, {
    Function(Widget chart, String question)? onChartGenerated,
    String? placeholder,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.3,
        maxChildSize: 0.95,
        builder: (context, scrollController) => AIChatWidget(
          onChartGenerated: onChartGenerated,
          placeholder: placeholder,
        ),
      ),
    );
  }
}