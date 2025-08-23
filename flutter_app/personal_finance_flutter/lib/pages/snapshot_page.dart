import 'package:flutter/material.dart';
import '../design/design_tokens.dart';

class SnapshotPage extends StatelessWidget {
  const SnapshotPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
          // 顶部状态栏
          Container(
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
                  child: const Row(
                    children: [
                      Icon(Icons.check_circle, size: 16, color: T.success),
                      SizedBox(width: T.spacingXS),
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
                const Text(
                  "3分钟前更新",
                  style: TextStyle(fontSize: T.fontSizeS, color: T.textTertiary),
                )
              ],
            ),
          ),
          const SizedBox(height: T.spacingL),

          // 筛选按钮
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildFilterButton(Icons.calendar_today, "今日", true),
              _buildFilterButton(Icons.calendar_today, "本周", false),
              _buildFilterButton(Icons.calendar_today, "本月", false),
              _buildFilterButton(Icons.show_chart, "全部", false),
            ],
          ),
          const SizedBox(height: T.spacingL),

          // 资产卡片
          _buildAssetCard(
            title: "支付宝 · 基金投资",
            subtitle: "3分钟前更新 · \$22,110.04",
            status: "正常 · 2笔资产",
            items: const [
              {"name": "易方达沪深300ETF", "value": "\$16,821.18"},
              {"name": "华夏货币基金", "value": "\$5,288.86"},
            ],
            change: "+0.8%",
            changeColor: Color(0xFF18A058),
          ),
          _buildAssetCard(
            title: "Wise · 多币种账户",
            subtitle: "5分钟前更新 · \$8,750.32",
            status: "正常 · 3种货币",
            items: const [],
            tip: "汇率提醒: USD/CNY 今日上涨 0.2%",
          ),
          _buildAssetCard(
            title: "IBKR · 证券投资",
            subtitle: "2小时前更新 · \$45,890.15",
            status: "数据有点旧，建议刷新",
            items: const [],
            actions: true,
          ),
          _buildAssetCard(
            title: "Binance · 加密货币",
            subtitle: "1小时前更新 · \$12,450.78",
            status: "正常 · 5种代币",
            items: const [
              {"name": "Bitcoin", "value": "\$8,234.56"},
              {"name": "Ethereum", "value": "\$4,216.22"},
            ],
            change: "+2.4%",
            changeColor: Color(0xFF18A058),
          ),
          const SizedBox(height: T.spacingL),

          // 今日表现
          Container(
            padding: const EdgeInsets.all(T.spacingL),
            decoration: BoxDecoration(
              color: T.cardBackground,
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.emoji_events, color: T.warning, size: 20),
                    SizedBox(width: T.spacingM),
                    Text("今日表现",
                        style: TextStyle(
                            fontSize: T.fontSizeL, fontWeight: T.fontWeightBold)),
                  ],
                ),
                SizedBox(height: T.spacingM),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildFilterButton(Icons.trending_up, "全部", true),
                    _buildFilterButton(Icons.trending_up, "基金", false),
                    _buildFilterButton(Icons.trending_up, "股票", false),
                    _buildFilterButton(Icons.trending_up, "其他", false),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: T.spacingL),

          // 最近快照记录
          const Text(
            "最近快照记录",
            style: TextStyle(fontSize: T.fontSizeL, fontWeight: T.fontWeightBold),
          ),
          const SizedBox(height: T.spacingS),
          _buildLogRow("15:25 全量更新 (13条)", true),
          _buildLogRow("15:00 增量更新 (8条)", true),
          _buildLogRow("14:15 IBKR重试失败", false),
          _buildLogRow("14:00 Binance同步完成", true),
          _buildLogRow("13:45 Wise汇率更新", true),
          const SizedBox(height: T.spacingS),
          const Text(
            "查看完整历史",
            style: TextStyle(
                color: T.info, fontSize: T.fontSizeM, fontWeight: T.fontWeightMedium),
          ),
          const SizedBox(height: T.spacingL),

          // 今日统计
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("今日统计 · 成功率 96% · 延迟 2.3分钟",
                    style: TextStyle(fontSize: 13, color: Colors.grey)),
                Text("详细统计",
                    style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: Colors.blue)),
              ],
            ),
          ),
          const SizedBox(height: T.spacingXL),
        ],
      );
  }

  // 筛选按钮
  static Widget _buildFilterButton(IconData icon, String text, bool active) {
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

  // 资产卡片
  static Widget _buildAssetCard({
    required String title,
    required String subtitle,
    required String status,
    List<Map<String, String>> items = const [],
    String? change,
    Color? changeColor,
    String? tip,
    bool actions = false,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: T.spacingM),
      padding: const EdgeInsets.all(T.spacingL),
      decoration: BoxDecoration(
        color: T.cardBackground,
        borderRadius: BorderRadius.circular(T.radiusM),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Text(title,
              style:
                  const TextStyle(fontSize: T.fontSizeL, fontWeight: T.fontWeightBold)),
          const Icon(Icons.add_circle_outline, color: T.success),
        ]),
        const SizedBox(height: T.spacingXS),
        Text(subtitle,
            style: const TextStyle(fontSize: T.fontSizeS, color: T.textTertiary)),
        const SizedBox(height: T.spacingM),
        Text(status,
            style: TextStyle(
                fontSize: T.fontSizeS,
                color: status.contains("建议刷新")
                    ? T.error
                    : T.success)),
        const SizedBox(height: T.spacingS),
        for (var item in items)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(item["name"]!,
                    style: const TextStyle(fontSize: T.fontSizeM, color: T.textPrimary)),
                Text(item["value"]!,
                    style: const TextStyle(
                        fontSize: T.fontSizeM, fontWeight: T.fontWeightMedium)),
              ],
            ),
          ),
        if (tip != null)
          Padding(
            padding: const EdgeInsets.only(top: T.spacingM),
            child: Text(tip,
                style: const TextStyle(fontSize: T.fontSizeS, color: T.info)),
          ),
        if (change != null)
          Padding(
            padding: const EdgeInsets.only(top: T.spacingM),
            child: Text("最近变化: $change",
                style: TextStyle(fontSize: T.fontSizeS, color: changeColor)),
          ),
        if (actions)
          Padding(
            padding: const EdgeInsets.only(top: T.spacingS),
            child: Row(
              children: [
                ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                        backgroundColor: T.success,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(T.radiusM))),
                    child: const Text("立即重试",
                        style: TextStyle(color: T.textInverse, fontSize: T.fontSizeS))),
                const SizedBox(width: T.spacingM),
                OutlinedButton(
                    onPressed: () {},
                    style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: T.textTertiary),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(T.radiusM))),
                    child: const Text("查看详情",
                        style: TextStyle(color: T.textPrimary, fontSize: T.fontSizeS))),
              ],
            ),
          ),
      ]),
    );
  }

  // 快照记录
  static Widget _buildLogRow(String text, bool success) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text(text,
              style: const TextStyle(fontSize: T.fontSizeS, color: T.textPrimary)),
          const Spacer(),
          Icon(success ? Icons.check_circle : Icons.cancel,
              size: 16, color: success ? T.success : T.error),
        ],
      ),
    );
  }
}
