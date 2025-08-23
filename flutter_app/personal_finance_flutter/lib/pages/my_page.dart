import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import '../design/design_tokens.dart';

class MyPage extends StatelessWidget {
  const MyPage({super.key});

    @override
  Widget build(BuildContext context) {
    return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 顶部栏：左标题 + 右通知（带红点）
          Padding(
            padding: const EdgeInsets.fromLTRB(0, T.spacingS, 0, T.spacingM),
            child: Row(
              children: [
                const Text(
                  '我的',
                  style: TextStyle(
                    fontSize: T.fontSizeTitle,
                    height: 1.2,
                    fontWeight: T.fontWeightExtraBold,
                    color: T.textPrimary,
                  ),
                ),
                const Spacer(),
                Stack(
                  clipBehavior: Clip.none,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.notifications_none, color: T.iconSecondary),
                      onPressed: () {},
                      padding: const EdgeInsets.all(T.spacingM),
                      constraints: const BoxConstraints(),
                    ),
                    Positioned(
                      right: 4,
                      top: 4,
                      child: Container(
                        width: 9,
                        height: 9,
                        decoration: BoxDecoration(
                          color: T.error,
                          borderRadius: BorderRadius.circular(99),
                          border: Border.all(color: Colors.white, width: 1.5),
                        ),
                      ),
                    )
                  ],
                ),
              ],
            ),
          ),

          // 用户卡片（渐变 + 徽章 + 年化收益率）
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 0, vertical: T.spacingM),
            child: _ProfileCard(),
          ),

          // 显示偏好
          Padding(
            padding: const EdgeInsets.fromLTRB(0, T.spacingS, 0, T.spacingM),
            child: _PreferenceCard(),
          ),

          // 快捷操作
          Padding(
            padding: const EdgeInsets.fromLTRB(0, T.spacingS, 0, T.spacingM),
            child: _QuickActionsCard(),
          ),

          // 更多设置
          Padding(
            padding: const EdgeInsets.fromLTRB(0, T.spacingS, 0, T.spacingXXL),
            child: _MoreSettingsTile(),
          ),
          const SizedBox(height: T.spacingXXL),
        ],
      );
  }
}

// ========== 组件们 ==========

class _ProfileCard extends StatelessWidget {
  const _ProfileCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(T.spacingL, T.spacingL, T.spacingL, T.spacingM),
              decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(T.radiusXL),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              T.primaryLight, // 更亮
              T.primary,      // 主绿
            ],
          ),
          boxShadow: T.shadowLight,
        ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 头像 + 文案
          Row(
            children: [
              const CircleAvatar(
                radius: 22,
                backgroundColor: Colors.white,
                child: Icon(Icons.person, color: T.primary, size: 24),
              ),
              const SizedBox(width: T.spacingM),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    '投资分析师',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: T.fontSizeXL,
                      fontWeight: T.fontWeightExtraBold,
                      height: 1.1,
                    ),
                  ),
                  SizedBox(height: T.spacingXS),
                  Text(
                    '使用51天 • 记录307笔资产',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: T.fontSizeS,
                      height: 1.1,
                      fontWeight: T.fontWeightMedium,
                    ),
                  ),
                ],
              )
            ],
          ),
          const SizedBox(height: T.spacingM),

          // 四个徽章（两列网格，等宽）
          LayoutBuilder(
            builder: (context, c) {
              final w = (c.maxWidth - T.spacingS) / 2; // 间距8
              return Wrap(
                spacing: T.spacingS,
                runSpacing: T.spacingS,
                children: [
                  _BadgeBox(width: w, title: '连续使用30天', sub: '坚持记录'),
                  _BadgeBox(width: w, title: '资产超过10万', sub: '投资达人'),
                  _BadgeBox(width: w, title: '平台连接达人', sub: '多平台管理'),
                  _BadgeBox(width: w, title: '投资高手', sub: '收益稳定'),
                ],
              );
            },
          ),
          const SizedBox(height: T.spacingM),

          // 年化收益率条
          Container(
            padding: const EdgeInsets.symmetric(horizontal: T.spacingM, vertical: T.spacingM),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.16),
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.gps_fixed, size: 18, color: Colors.white),
                SizedBox(width: T.spacingS),
                Text(
                  '年化收益率  +8.5%',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: T.fontSizeM,
                    fontWeight: T.fontWeightBold,
                  ),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}

class _BadgeBox extends StatelessWidget {
  final double width;
  final String title;
  final String sub;
  const _BadgeBox({required this.width, required this.title, required this.sub});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(T.radiusM),
        border: Border.all(color: Colors.white.withOpacity(0.18), width: 0.6),
      ),
      child: Row(
        children: [
          Container(
            width: 20, height: 20,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.22),
              borderRadius: BorderRadius.circular(T.radiusM),
            ),
            child: const Icon(Icons.check, size: 14, color: Colors.white),
          ),
          const SizedBox(width: T.spacingS),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: T.fontSizeS,
                      fontWeight: T.fontWeightBold,
                      height: 1.05,
                    )),
                const SizedBox(height: 2),
                Text(sub,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: T.fontSizeXS,
                      height: 1.05,
                      fontWeight: T.fontWeightMedium,
                    )),
              ],
            ),
          )
        ],
      ),
    );
  }
}

class _PreferenceCard extends StatefulWidget {
  const _PreferenceCard();

  @override
  State<_PreferenceCard> createState() => _PreferenceCardState();
}

class _PreferenceCardState extends State<_PreferenceCard> {
  String cur = 'USD';
  bool showMode = true;
  bool lightTheme = true;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: T.card,
        borderRadius: BorderRadius.circular(T.radiusL),
        boxShadow: T.shadowLight,
      ),
      padding: const EdgeInsets.fromLTRB(T.spacingL, T.spacingM, T.spacingL, T.spacingM),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题行：图标 + 文案
          const _SectionTitle(
            icon: Icons.payments_outlined,
            iconColor: T.primary,
            title: '显示偏好',
          ),
          const SizedBox(height: T.spacingM),

          // 币种分段选择
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('币种',
                  style: TextStyle(
                      color: T.textPrimary,
                      fontSize: T.fontSizeM,
                      fontWeight: T.fontWeightSemiBold)),
              _Segmented(
                items: const ['CNY', 'USD', 'EUR'],
                value: cur,
                onChanged: (v) => setState(() => cur = v),
              )
            ],
          ),
          const SizedBox(height: T.spacingM),

          // 显示模式
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('显示模式',
                  style: TextStyle(
                      color: T.textPrimary,
                      fontSize: T.fontSizeM,
                      fontWeight: T.fontWeightSemiBold)),
              CupertinoSwitch(
                value: showMode,
                onChanged: (v) => setState(() => showMode = v),
                activeColor: T.primary,
              )
            ],
          ),
          const SizedBox(height: T.spacingM),
          const Divider(height: 20, color: T.divider),

          // 浅色主题
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('浅色主题',
                  style: TextStyle(
                      color: T.textPrimary,
                      fontSize: T.fontSizeM,
                      fontWeight: T.fontWeightSemiBold)),
              CupertinoSwitch(
                value: lightTheme,
                onChanged: (v) => setState(() => lightTheme = v),
                activeColor: T.primary,
              )
            ],
          ),
        ],
      ),
    );
  }
}

class _QuickActionsCard extends StatelessWidget {
  const _QuickActionsCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: T.card,
        borderRadius: BorderRadius.circular(T.radiusL),
        boxShadow: T.shadowLight,
      ),
      padding: const EdgeInsets.fromLTRB(T.spacingL, T.spacingM, T.spacingL, T.spacingM),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _SectionTitle(
            icon: Icons.bolt_rounded,
            iconColor: Color(0xFFF59E0B), // 闪电黄
            title: '快捷操作',
          ),
          const SizedBox(height: T.spacingM),
          Row(
            children: const [
              _ActionButton(
                icon: Icons.insert_chart_outlined_rounded,
                label: '导出报告',
              ),
              SizedBox(width: T.spacingM),
              _ActionButton(
                icon: Icons.cloud_sync_outlined,
                label: '同步数据',
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MoreSettingsTile extends StatelessWidget {
  const _MoreSettingsTile();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: T.card,
        borderRadius: BorderRadius.circular(T.radiusL),
        boxShadow: T.shadowLight,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(T.radiusL),
          onTap: () {},
          child: Padding(
            padding: const EdgeInsets.fromLTRB(T.spacingL, T.spacingM, T.spacingS, T.spacingM),
            child: Row(
              children: const [
                Icon(Icons.settings_outlined, color: T.iconSecondary),
                SizedBox(width: T.spacingM),
                Expanded(
                  child: Text(
                    '更多设置',
                    style: TextStyle(
                      color: T.textPrimary,
                      fontSize: 15,
                      fontWeight: T.fontWeightSemiBold,
                    ),
                  ),
                ),
                Icon(Icons.chevron_right, color: T.iconSecondary),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ===== 小组件：标题行/分段/快捷按钮 =====

class _SectionTitle extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  const _SectionTitle({
    required this.icon,
    required this.iconColor,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: iconColor),
        const SizedBox(width: T.spacingS),
        Text(
          title,
          style: const TextStyle(
            fontSize: T.fontSizeL,
            fontWeight: T.fontWeightExtraBold,
            color: T.textPrimary,
          ),
        ),
      ],
    );
  }
}

class _Segmented extends StatelessWidget {
  final List<String> items;
  final String value;
  final ValueChanged<String> onChanged;

  const _Segmented({
    required this.items,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 34,
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F2F4),
        borderRadius: BorderRadius.circular(T.radiusXL),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: items.map((e) {
          final selected = e == value;
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2),
            child: GestureDetector(
              onTap: () => onChanged(e),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 160),
                padding: const EdgeInsets.symmetric(horizontal: 14),
                alignment: Alignment.center,
                height: 28,
                decoration: BoxDecoration(
                  color: selected ? T.primary : Colors.transparent,
                  borderRadius: BorderRadius.circular(T.radiusXL),
                ),
                child: Text(
                  e,
                  style: TextStyle(
                    fontSize: T.fontSizeS,
                    fontWeight: T.fontWeightExtraBold,
                    color: selected ? Colors.white : T.textSecondary,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  const _ActionButton({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        height: 64,
        decoration: BoxDecoration(
          color: const Color(0xFFF6F7F9),
          borderRadius: BorderRadius.circular(T.radiusM),
          border: Border.all(color: const Color(0xFFEAEDEF)),
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(T.radiusM),
            onTap: () {},
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 22, color: T.textSecondary),
                const SizedBox(height: T.spacingM),
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: T.fontSizeS,
                    color: T.textPrimary,
                    fontWeight: T.fontWeightSemiBold,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
