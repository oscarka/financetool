import 'package:flutter/material.dart';
import 'chart_design_system.dart';
import 'mcp_chart_adapter.dart';
import 'chart_preview_modal.dart';
import 'chart_intent_dialog.dart';
import 'chart_save_dialog.dart';
import '../pages/fullscreen_chart_page.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

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
      
      // 添加测试按钮
      _messages.add(ChatMessage(
        text: '',
        isUser: false,
        timestamp: DateTime.now(),
        messageType: ChatMessageType.test,
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
    
    showDialog(
      context: context,
      builder: (context) => ChartIntentDialog(
      userQuestion: originalQuestion,
      detectedChartType: chartType,
      onConfirm: (confirmed, modifiedQuestion) {
        if (confirmed) {
          final finalQuestion = modifiedQuestion ?? originalQuestion;
          _generateChartResponse(finalQuestion);
        }
      },
      ),
    );
  }

  /// 生成图表响应
  void _generateChartResponse(String question) async {
    setState(() {
      _isLoading = true; // Changed from _isGenerating to _isLoading
    });

    try {
      // 使用真实的图表生成方法
      final chartWidget = await MCPChartAdapter.generateChartResponse(question);
      
      setState(() {
        _messages.add(ChatMessage(
          text: question,
          isUser: true,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        
        // 从MCPChartAdapter中获取最新的图表数据
        List<dynamic>? chartData;
        Map<String, dynamic>? aiAnalysis;
        
        try {
          print('🔍 尝试从MCPChartAdapter获取最新图表数据...');
          chartData = MCPChartAdapter.lastChartData;
          if (chartData != null) {
            print('✅ 获取到图表数据: ${chartData.length} 项');
            print('📊 数据预览: ${chartData.take(3).map((e) => '${e['label']}:${e['value']}').join(', ')}');
          } else {
            print('⚠️  未获取到图表数据');
          }
        } catch (e) {
          print('❌ 获取图表数据失败: $e');
        }
        
        _messages.add(ChatMessage(
          text: '',
          isUser: false,
          timestamp: DateTime.now(),
          chartWidget: chartWidget,
          messageType: ChatMessageType.chart,
          originalQuestion: question,
          chartData: chartData,
          aiAnalysis: aiAnalysis,
        ));
        
        _isLoading = false; // Changed from _isGenerating to _isLoading
      });
      
      // 滚动到底部
      _scrollToBottom();
      
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: '生成图表时发生错误: $e',
          isUser: false,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        _isLoading = false; // Changed from _isGenerating to _isLoading
      });
      
      _scrollToBottom();
    }
  }

  /// 生成文本响应
  Future<void> _generateTextResponse(String question) async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      // 调用AI生成回复
      final aiResponse = await _callAITextAPI(question);
      
      setState(() {
        _messages.add(ChatMessage(
          text: aiResponse,
          isUser: false,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
      
    } catch (e) {
      print('❌ AI文本回复失败: $e');
      // 回退到智能模板回复
      String fallbackResponse = _generateSmartResponse(question);
      
      setState(() {
        _messages.add(ChatMessage(
          text: fallbackResponse,
          isUser: false,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
    }
  }
  
  /// 调用AI文本API
  Future<String> _callAITextAPI(String question) async {
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/ai-chat/text'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'question': question}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'] ?? '抱歉，AI回复生成失败';
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      throw Exception('AI API调用失败: $e');
    }
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

    showDialog(
      context: context,
      builder: (context) => ChartSaveDialog(
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
      ),
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
                  : message.messageType == ChatMessageType.test
                      ? _buildTestMessage()
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
    
    // 根据图表类型生成全屏图表内容
    Widget fullscreenChartContent;
    List<CustomPieChartData>? legendData;
    
    if (message.chartWidget is Container) {
      // 如果是缩略图容器，尝试从消息中提取真实数据
      legendData = _extractRealLegendData(message);
      
      if (legendData != null && legendData.isNotEmpty) {
        // 使用真实数据生成全屏饼图
        fullscreenChartContent = MCPChartAdapter.buildFullscreenPieChart(
          legendData,
          message.originalQuestion ?? message.text,
        );
      } else {
        // 如果没有真实数据，使用模拟数据
        print('⚠️  未找到真实图例数据，使用模拟数据');
        legendData = _createMockLegendData();
        fullscreenChartContent = MCPChartAdapter.buildFullscreenPieChart(
          legendData,
          message.originalQuestion ?? message.text,
        );
      }
    } else {
      // 其他情况直接使用原组件
      fullscreenChartContent = message.chartWidget!;
      legendData = _createMockLegendData(); // 临时使用模拟数据
    }
    
    // 跳转到全屏页面而不是弹窗
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => FullscreenChartPage(
          title: message.originalQuestion ?? message.text,
          subtitle: '基于真实数据生成',
          chartContent: fullscreenChartContent,
          legendData: legendData,
          showLegend: true,
        ),
      ),
    );
  }
  
  /// 从消息中提取真实的图例数据
  List<CustomPieChartData>? _extractRealLegendData(ChatMessage message) {
    try {
      print('🔍 尝试从消息中提取真实图例数据...');
      
      // 检查消息是否包含图表数据
      if (message.chartData != null) {
        print('✅ 找到图表数据: ${message.chartData}');
        return _convertToLegendData(message.chartData!);
      }
      
      // 检查消息是否包含AI分析结果
      if (message.aiAnalysis != null) {
        print('✅ 找到AI分析结果: ${message.aiAnalysis}');
        final data = message.aiAnalysis!['data'] as List<dynamic>?;
        if (data != null) {
          return _convertToLegendData(data);
        }
      }
      
      print('⚠️  未找到真实图例数据');
      return null;
    } catch (e) {
      print('❌ 提取真实图例数据失败: $e');
      return null;
    }
  }
  
  /// 转换数据为图例格式
  List<CustomPieChartData> _convertToLegendData(List<dynamic> data) {
    try {
      print('🔄 转换数据为图例格式...');
      print('📊 原始数据: $data');
      
      final legendData = <CustomPieChartData>[];
      
      // 计算总值用于百分比计算
      final total = data.fold(0.0, (sum, item) {
        final value = (item['value'] ?? item['total_value'] ?? 0.0).toDouble();
        return sum + value;
      });
      
      print('💰 数据总值: $total');
      
      for (int i = 0; i < data.length; i++) {
        final item = data[i];
        final label = item['label'] ?? item['name'] ?? '未知${i + 1}';
        final value = (item['value'] ?? item['total_value'] ?? 0.0).toDouble();
        
        // 计算百分比
        final percentage = total > 0 ? (value / total * 100) : 0.0;
        
        // 格式化数值显示
        String formattedValue;
        if (item['total_value'] != null) {
          final totalValue = item['total_value'];
          if (totalValue is num) {
            formattedValue = '¥${totalValue.toStringAsFixed(2)}';
          } else {
            formattedValue = '¥${value.toStringAsFixed(2)}';
          }
        } else {
          formattedValue = '¥${value.toStringAsFixed(2)}';
        }
        
        // 使用预定义的颜色或生成随机颜色
        final color = _getColorForIndex(i, label);
        
        legendData.add(CustomPieChartData(
          label: label,
          value: value,
          percentage: percentage,
          color: color,
          formattedValue: formattedValue,
        ));
        
        print('  📊 转换项目: $label = $value (${percentage.toStringAsFixed(1)}%) - $formattedValue');
      }
      
      print('✅ 图例数据转换完成: ${legendData.length} 项');
      return legendData;
    } catch (e) {
      print('❌ 数据转换失败: $e');
      print('💥 异常堆栈: ${StackTrace.current}');
      return [];
    }
  }
  
  /// 根据索引和标签获取颜色
  Color _getColorForIndex(int index, String label) {
    // 预定义的颜色映射
    const colorMap = {
      'OKX': Color(0xFF8B5CF6),
      'Wise': Color(0xFF10B981),
      '支付宝': Color(0xFFF59E0B),
      'IBKR': Color(0xFF3B82F6),
      'PayPal': Color(0xFFEF4444),
      'test': Color(0xFF8B5CF6),
    };
    
    // 如果标签有预定义颜色，使用预定义颜色
    if (colorMap.containsKey(label)) {
      return colorMap[label]!;
    }
    
    // 否则使用索引生成颜色
    final colors = [
      const Color(0xFF8B5CF6), // 紫色
      const Color(0xFF10B981), // 绿色
      const Color(0xFFF59E0B), // 橙色
      const Color(0xFF3B82F6), // 蓝色
      const Color(0xFFEF4444), // 红色
      const Color(0xFF06B6D4), // 青色
      const Color(0xFF8B5CF6), // 紫色
      const Color(0xFF10B981), // 绿色
    ];
    
    return colors[index % colors.length];
  }

  /// 创建模拟的图例数据用于测试（保留作为备用）
  List<CustomPieChartData> _createMockLegendData() {
    print('🎭 使用模拟图例数据');
    return [
      CustomPieChartData(
        label: 'OKX',
        value: 10.0,
        percentage: 52.6,
        color: const Color(0xFF8B5CF6),
        formattedValue: '¥10.00',
      ),
      CustomPieChartData(
        label: 'Wise',
        value: 7.0,
        percentage: 36.8,
        color: const Color(0xFF10B981),
        formattedValue: '¥7.00',
      ),
      CustomPieChartData(
        label: '支付宝',
        value: 1.0,
        percentage: 5.3,
        color: const Color(0xFFF59E0B),
        formattedValue: '¥1.00',
      ),
      CustomPieChartData(
        label: 'test',
        value: 1.0,
        percentage: 5.3,
        color: const Color(0xFFEF4444),
        formattedValue: '¥1.00',
      ),
    ];
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

  /// 构建测试消息
  Widget _buildTestMessage() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🧪 AI API 连接测试',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.blue[700],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '点击下方按钮测试AI API是否正常工作：',
            style: TextStyle(
              fontSize: 14,
              color: Colors.blue[600],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _testAIAPI('显示各平台的资产分布'),
                  icon: const Icon(Icons.pie_chart, size: 18),
                  label: const Text('测试饼图生成'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[600],
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _testAIAPI('各平台资产对比分析'),
                  icon: const Icon(Icons.bar_chart, size: 18),
                  label: const Text('测试柱状图'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green[600],
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 测试AI API
  void _testAIAPI(String question) async {
    print('🧪 开始测试AI API: $question');
    
    setState(() {
      _isLoading = true;
    });

    try {
      // 直接调用AI API
      final chartWidget = await MCPChartAdapter.generateChartResponse(question);
      
      setState(() {
        _messages.add(ChatMessage(
          text: '🧪 测试问题: $question',
          isUser: true,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        
        _messages.add(ChatMessage(
          text: '',
          isUser: false,
          timestamp: DateTime.now(),
          chartWidget: chartWidget,
          messageType: ChatMessageType.chart,
        ));
        
        _isLoading = false;
      });
      
      _scrollToBottom();
      
    } catch (e) {
      print('💥 AI API测试失败: $e');
      setState(() {
        _messages.add(ChatMessage(
          text: '🧪 测试问题: $question',
          isUser: true,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.text,
        ));
        
        _messages.add(ChatMessage(
          text: '❌ AI API测试失败: $e',
          isUser: false,
          timestamp: DateTime.now(),
          messageType: ChatMessageType.error,
        ));
        
        _isLoading = false;
      });
      
      _scrollToBottom();
    }
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
  final List<dynamic>? chartData; // 添加图表数据字段
  final Map<String, dynamic>? aiAnalysis; // 添加AI分析结果字段

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    required this.messageType,
    this.chartWidget,
    this.originalQuestion,
    this.chartType,
    this.chartData,
    this.aiAnalysis,
  });
}

/// 消息类型枚举
enum ChatMessageType {
  text,
  chart,
  welcome,
  error,
  test, // 新增测试消息类型
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