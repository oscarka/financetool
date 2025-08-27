import 'package:flutter/material.dart';
import 'design_tokens.dart';

/// 通用组件库 - 确保所有页面使用一致的组件样式

/// 页面标题组件
class PageTitle extends StatelessWidget {
  final String title;
  final IconData? icon;
  final Color? iconColor;
  final VoidCallback? onBackPressed;
  final Widget? trailing;

  const PageTitle({
    super.key,
    required this.title,
    this.icon,
    this.iconColor,
    this.onBackPressed,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(T.spacingL, T.spacingS, T.spacingL, T.spacingM),
      child: Row(
        children: [
          if (onBackPressed != null)
            IconButton(
              onPressed: onBackPressed,
              icon: const Icon(Icons.arrow_back),
              iconSize: 24,
              color: T.iconSecondary,
            ),
          if (icon != null) ...[
            Icon(
              icon,
              color: iconColor ?? T.iconPrimary,
              size: 20,
            ),
            const SizedBox(width: T.spacingS),
          ],
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: T.fontSizeTitle,
                fontWeight: T.fontWeightExtraBold,
                color: T.textPrimary,
                height: 1.2,
              ),
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

/// 标准卡片容器
class StandardCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final VoidCallback? onTap;
  final bool showShadow;

  const StandardCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.showShadow = true,
  });

  @override
  Widget build(BuildContext context) {
    Widget card = Container(
      margin: margin ?? const EdgeInsets.symmetric(horizontal: T.spacingL, vertical: T.spacingS),
      decoration: BoxDecoration(
        color: T.cardBackground,
        borderRadius: BorderRadius.circular(T.radiusL),
        boxShadow: showShadow ? T.shadowLight : null,
      ),
      child: child,
    );

    if (onTap != null) {
      card = Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(T.radiusL),
          onTap: onTap,
          child: card,
        ),
      );
    }

    return card;
  }
}

/// 信息卡片
class InfoCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;
  final Color? backgroundColor;
  final Color? textColor;

  const InfoCard({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
    this.backgroundColor,
    this.textColor,
  });

  @override
  Widget build(BuildContext context) {
    return StandardCard(
      onTap: onTap,
      padding: const EdgeInsets.all(T.spacingL),
      child: Row(
        children: [
          if (leading != null) ...[
            leading!,
            const SizedBox(width: T.spacingM),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: T.fontSizeM,
                    fontWeight: T.fontWeightSemiBold,
                    color: textColor ?? T.textPrimary,
                  ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: T.spacingXS),
                  Text(
                    subtitle!,
                    style: TextStyle(
                      fontSize: T.fontSizeS,
                      color: textColor?.withOpacity(0.7) ?? T.textSecondary,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

/// 统计卡片
class StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData? icon;
  final Color? color;
  final bool isPositive;

  const StatCard({
    super.key,
    required this.label,
    required this.value,
    this.icon,
    this.color,
    this.isPositive = true,
  });

  @override
  Widget build(BuildContext context) {
    return StandardCard(
      padding: const EdgeInsets.all(T.spacingL),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(
                  icon,
                  color: color ?? T.iconPrimary,
                  size: 20,
                ),
                const SizedBox(width: T.spacingS),
              ],
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    fontSize: T.fontSizeS,
                    color: T.textSecondary,
                    fontWeight: T.fontWeightMedium,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: T.spacingS),
          Text(
            value,
            style: TextStyle(
              fontSize: T.fontSizeXL,
              fontWeight: T.fontWeightExtraBold,
              color: color ?? T.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}

/// 操作按钮
class ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? textColor;
  final bool isOutlined;

  const ActionButton({
    super.key,
    required this.label,
    required this.icon,
    this.onPressed,
    this.backgroundColor,
    this.textColor,
    this.isOutlined = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isOutlined) {
      return OutlinedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 20),
        label: Text(label),
        style: OutlinedButton.styleFrom(
          foregroundColor: textColor ?? T.primary,
          side: BorderSide(color: textColor ?? T.primary),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(T.radiusM),
          ),
          padding: const EdgeInsets.symmetric(
            horizontal: T.spacingL,
            vertical: T.spacingM,
          ),
        ),
      );
    }

    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 20),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor ?? T.primary,
        foregroundColor: textColor ?? T.textInverse,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(T.radiusM),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: T.spacingL,
          vertical: T.spacingM,
        ),
      ),
    );
  }
}

/// 分段选择器
class SegmentedSelector extends StatelessWidget {
  final List<String> items;
  final String value;
  final ValueChanged<String> onChanged;
  final Color? activeColor;

  const SegmentedSelector({
    super.key,
    required this.items,
    required this.value,
    required this.onChanged,
    this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 34,
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F2F4),
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: items.map((item) {
          final selected = item == value;
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2),
            child: GestureDetector(
              onTap: () => onChanged(item),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 160),
                padding: const EdgeInsets.symmetric(horizontal: 14),
                alignment: Alignment.center,
                height: 28,
                decoration: BoxDecoration(
                  color: selected ? (activeColor ?? T.primary) : Colors.transparent,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  item,
                  style: TextStyle(
                    fontSize: T.fontSizeS,
                    fontWeight: T.fontWeightExtraBold,
                    color: selected ? T.textInverse : T.textSecondary,
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

/// 设置项
class SettingItem extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData? icon;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool showDivider;

  const SettingItem({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.trailing,
    this.onTap,
    this.showDivider = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        StandardCard(
          onTap: onTap,
          padding: const EdgeInsets.fromLTRB(T.spacingL, T.spacingM, T.spacingS, T.spacingM),
          child: Row(
            children: [
              if (icon != null) ...[
                Icon(icon, color: T.iconSecondary, size: 20),
                const SizedBox(width: T.spacingM),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: T.fontSizeM,
                        fontWeight: T.fontWeightSemiBold,
                        color: T.textPrimary,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: T.spacingXS),
                      Text(
                        subtitle!,
                        style: const TextStyle(
                          fontSize: T.fontSizeS,
                          color: T.textSecondary,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (trailing != null) trailing!,
              if (onTap != null) ...[
                const SizedBox(width: T.spacingS),
                const Icon(Icons.chevron_right, color: T.iconSecondary, size: 20),
              ],
            ],
          ),
        ),
        if (showDivider)
          const Divider(
            height: 1,
            color: T.divider,
            indent: T.spacingL,
            endIndent: T.spacingL,
          ),
      ],
    );
  }
}
