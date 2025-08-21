import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// 图表数据模型
class SavedChart {
  final String id;
  final String title;
  final String subtitle;
  final String question;
  final Map<String, dynamic> chartConfig;
  final DateTime savedAt;
  final String chartType;

  SavedChart({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.question,
    required this.chartConfig,
    required this.savedAt,
    required this.chartType,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'subtitle': subtitle,
      'question': question,
      'chartConfig': chartConfig,
      'savedAt': savedAt.toIso8601String(),
      'chartType': chartType,
    };
  }

  factory SavedChart.fromJson(Map<String, dynamic> json) {
    return SavedChart(
      id: json['id'],
      title: json['title'],
      subtitle: json['subtitle'],
      question: json['question'],
      chartConfig: json['chartConfig'],
      savedAt: DateTime.parse(json['savedAt']),
      chartType: json['chartType'],
    );
  }
}

/// 图表存储服务
class ChartStorageService {
  static const String _storageKey = 'saved_charts';
  
  /// 保存图表
  static Future<bool> saveChart(SavedChart chart) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedChartsJson = prefs.getStringList(_storageKey) ?? [];
      
      // 检查是否已存在相同ID的图表
      final existingIndex = savedChartsJson.indexWhere((json) {
        final existingChart = SavedChart.fromJson(jsonDecode(json));
        return existingChart.id == chart.id;
      });
      
      if (existingIndex != -1) {
        // 更新现有图表
        savedChartsJson[existingIndex] = jsonEncode(chart.toJson());
      } else {
        // 添加新图表
        savedChartsJson.add(jsonEncode(chart.toJson()));
      }
      
      await prefs.setStringList(_storageKey, savedChartsJson);
      return true;
    } catch (e) {
      print('保存图表失败: $e');
      return false;
    }
  }
  
  /// 获取所有保存的图表
  static Future<List<SavedChart>> getSavedCharts() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedChartsJson = prefs.getStringList(_storageKey) ?? [];
      
      return savedChartsJson.map((json) {
        return SavedChart.fromJson(jsonDecode(json));
      }).toList();
    } catch (e) {
      print('获取保存的图表失败: $e');
      return [];
    }
  }
  
  /// 删除图表
  static Future<bool> deleteChart(String chartId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedChartsJson = prefs.getStringList(_storageKey) ?? [];
      
      final filteredCharts = savedChartsJson.where((json) {
        final chart = SavedChart.fromJson(jsonDecode(json));
        return chart.id != chartId;
      }).toList();
      
      await prefs.setStringList(_storageKey, filteredCharts);
      return true;
    } catch (e) {
      print('删除图表失败: $e');
      return false;
    }
  }
  
  /// 生成唯一ID
  static String generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString();
  }
}
