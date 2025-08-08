class TrendData {
  final String date;
  final double total;

  TrendData({
    required this.date,
    required this.total,
  });

  factory TrendData.fromJson(Map<String, dynamic> json) {
    return TrendData(
      date: json['date'] ?? '',
      total: (json['total'] ?? 0.0).toDouble(),
    );
  }

  // 计算24小时变化百分比
  static double? calculateDailyChangePercentage(List<TrendData> trendData) {
    if (trendData.length < 2) return null;
    
    final today = trendData.last.total;
    final yesterday = trendData[trendData.length - 2].total;
    
    if (yesterday == 0) return null;
    
    return ((today - yesterday) / yesterday) * 100;
  }

  // 计算今日收益
  static double? calculateDailyProfit(List<TrendData> trendData) {
    if (trendData.length < 2) return null;
    
    final today = trendData.last.total;
    final yesterday = trendData[trendData.length - 2].total;
    
    return today - yesterday;
  }
}
