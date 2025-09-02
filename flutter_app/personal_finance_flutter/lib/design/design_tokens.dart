import 'package:flutter/material.dart';

/// 统一设计令牌 - 确保所有页面风格一致
class DesignTokens {
  // ===== 颜色系统 =====
  
  // 主色调 - 品牌绿
  static const primary = Color(0xFF24A27A);        // 主绿
  static const primaryLight = Color(0xFF2EB872);   // 浅绿
  static const primaryDark = Color(0xFF1B8E6A);    // 深绿
  static const success = Color(0xFF19A15C);        // 成功绿
  
  // 背景色
  static const background = Color(0xFFF4F6F8);     // 主背景（浅灰）
  static const cardBackground = Colors.white;      // 卡片背景
  static const card = Colors.white;                // 卡片背景（别名）
  static const surfaceBackground = Color(0xFFF6F7F9); // 表面背景
  
  // 文字颜色
  static const textPrimary = Color(0xFF111826);    // 主要文字
  static const textSecondary = Color(0xFF4B5563);  // 次要文字
  static const textTertiary = Color(0xFF9CA3AF);   // 第三级文字
  static const textInverse = Colors.white;         // 反色文字
  
  // 图标颜色
  static const iconPrimary = Color(0xFF24A27A);    // 主要图标
  static const iconSecondary = Color(0xFF9AA0A6);  // 次要图标
  static const iconAccent = Color(0xFFF59E0B);     // 强调图标（黄色）
  
  // 分割线和边框
  static const divider = Color(0xFFE5E7EB);        // 分割线
  static const border = Color(0xFFEAEDEF);         // 边框
  
  // 状态颜色
  static const error = Color(0xFFE74C3C);          // 错误红
  static const warning = Color(0xFFF59E0B);        // 警告黄
  static const info = Color(0xFF3B82F6);           // 信息蓝
  
  // ===== 尺寸系统 =====
  
  // 间距
  static const spacingXS = 4.0;    // 超小间距
  static const spacingS = 8.0;     // 小间距
  static const spacingM = 12.0;    // 中等间距
  static const spacingL = 16.0;    // 大间距
  static const spacingXL = 20.0;   // 超大间距
  static const spacingXXL = 24.0;  // 超超大间距
  
  // 圆角
  static const radiusS = 8.0;      // 小圆角
  static const radiusM = 12.0;     // 中等圆角
  static const radiusL = 16.0;     // 大圆角
  static const radiusXL = 18.0;    // 超大圆角
  
  // 阴影
  static const shadowLight = [
    BoxShadow(
      color: Color(0x14000000),    // 8% 黑
      blurRadius: 18,
      offset: Offset(0, 8),
    ),
  ];
  
  static const shadowMedium = [
    BoxShadow(
      color: Color(0x20000000),    // 12% 黑
      blurRadius: 24,
      offset: Offset(0, 12),
    ),
  ];
  
  // ===== 字体系统 =====
  
  // 字体大小
  static const fontSizeXS = 11.0;   // 超小字体
  static const fontSizeS = 12.5;    // 小字体
  static const fontSizeM = 14.5;    // 中等字体
  static const fontSizeL = 15.5;    // 大字体
  static const fontSizeXL = 16.5;   // 超大字体
  static const fontSizeXXL = 20.0;  // 超超大字体
  static const fontSizeTitle = 22.0; // 标题字体
  
  // 字体粗细
  static const fontWeightNormal = FontWeight.w400;
  static const fontWeightMedium = FontWeight.w500;
  static const fontWeightSemiBold = FontWeight.w600;
  static const fontWeightBold = FontWeight.w700;
  static const fontWeightExtraBold = FontWeight.w800;
  
  // ===== 组件样式 =====
  
  // 卡片样式
  static BoxDecoration cardDecoration = BoxDecoration(
    color: cardBackground,
    borderRadius: BorderRadius.circular(radiusL),
    boxShadow: shadowLight,
  );
  
  // 按钮样式
  static ButtonStyle primaryButtonStyle = ElevatedButton.styleFrom(
    backgroundColor: primary,
    foregroundColor: textInverse,
    elevation: 0,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radiusM),
    ),
    padding: const EdgeInsets.symmetric(
      horizontal: spacingL,
      vertical: spacingM,
    ),
  );
  
  // 输入框样式
  static InputDecoration inputDecoration = InputDecoration(
    filled: true,
    fillColor: surfaceBackground,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radiusM),
      borderSide: const BorderSide(color: border),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radiusM),
      borderSide: const BorderSide(color: border),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(radiusM),
      borderSide: const BorderSide(color: primary, width: 2),
    ),
  );
}

/// 便捷访问别名 - 直接使用静态属性
class T {
  // 颜色系统
  static const primary = DesignTokens.primary;
  static const primaryLight = DesignTokens.primaryLight;
  static const primaryDark = DesignTokens.primaryDark;
  static const success = DesignTokens.success;
  
  // 背景色
  static const background = DesignTokens.background;
  static const cardBackground = DesignTokens.cardBackground;
  static const card = DesignTokens.card;
  static const surfaceBackground = DesignTokens.surfaceBackground;
  
  // 文字颜色
  static const textPrimary = DesignTokens.textPrimary;
  static const textSecondary = DesignTokens.textSecondary;
  static const textTertiary = DesignTokens.textTertiary;
  static const textInverse = DesignTokens.textInverse;
  
  // 图标颜色
  static const iconPrimary = DesignTokens.iconPrimary;
  static const iconSecondary = DesignTokens.iconSecondary;
  static const iconAccent = DesignTokens.iconAccent;
  
  // 分割线和边框
  static const divider = DesignTokens.divider;
  static const border = DesignTokens.border;
  
  // 状态颜色
  static const error = DesignTokens.error;
  static const warning = DesignTokens.warning;
  static const info = DesignTokens.info;
  
  // 间距
  static const spacingXS = DesignTokens.spacingXS;
  static const spacingS = DesignTokens.spacingS;
  static const spacingM = DesignTokens.spacingM;
  static const spacingL = DesignTokens.spacingL;
  static const spacingXL = DesignTokens.spacingXL;
  static const spacingXXL = DesignTokens.spacingXXL;
  
  // 圆角
  static const radiusS = DesignTokens.radiusS;
  static const radiusM = DesignTokens.radiusM;
  static const radiusL = DesignTokens.radiusL;
  static const radiusXL = DesignTokens.radiusXL;
  
  // 阴影
  static const shadowLight = DesignTokens.shadowLight;
  static const shadowMedium = DesignTokens.shadowMedium;
  
  // 字体大小
  static const fontSizeXS = DesignTokens.fontSizeXS;
  static const fontSizeS = DesignTokens.fontSizeS;
  static const fontSizeM = DesignTokens.fontSizeM;
  static const fontSizeL = DesignTokens.fontSizeL;
  static const fontSizeXL = DesignTokens.fontSizeXL;
  static const fontSizeXXL = DesignTokens.fontSizeXXL;
  static const fontSizeTitle = DesignTokens.fontSizeTitle;
  
  // 字体粗细
  static const fontWeightNormal = DesignTokens.fontWeightNormal;
  static const fontWeightMedium = DesignTokens.fontWeightMedium;
  static const fontWeightSemiBold = DesignTokens.fontWeightSemiBold;
  static const fontWeightBold = DesignTokens.fontWeightBold;
  static const fontWeightExtraBold = DesignTokens.fontWeightExtraBold;
  
  // 组件样式
  static BoxDecoration get cardDecoration => DesignTokens.cardDecoration;
  static ButtonStyle get primaryButtonStyle => DesignTokens.primaryButtonStyle;
  static InputDecoration get inputDecoration => DesignTokens.inputDecoration;
}
