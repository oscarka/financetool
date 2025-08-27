# 设计指南 - 统一页面风格

## 概述
本文档定义了个人金融应用的设计标准，确保所有页面保持一致的视觉风格和用户体验。

## 设计原则

### 1. 一致性 (Consistency)
- 所有页面使用相同的颜色、字体、间距和组件
- 保持统一的交互模式和视觉层次

### 2. 清晰性 (Clarity)
- 信息层次分明，重要内容突出
- 使用适当的对比度和字体大小

### 3. 易用性 (Usability)
- 符合用户习惯的交互设计
- 清晰的视觉反馈和状态指示

## 颜色系统

### 主色调
- **主绿**: `#24A27A` - 品牌主色，用于主要按钮、链接等
- **浅绿**: `#2EB872` - 用于渐变、强调等
- **深绿**: `#1B8E6A` - 用于悬停状态、深色背景等

### 背景色
- **主背景**: `#F4F6F8` - 页面背景色
- **卡片背景**: `#FFFFFF` - 卡片、面板背景
- **表面背景**: `#F6F7F9` - 输入框、次要表面

### 文字颜色
- **主要文字**: `#111826` - 标题、重要文字
- **次要文字**: `#4B5563` - 正文、描述文字
- **第三级文字**: `#9CA3AF` - 辅助信息、标签

### 状态颜色
- **成功**: `#19A15C` - 成功状态、正面信息
- **警告**: `#F59E0B` - 警告状态、注意信息
- **错误**: `#E74C3C` - 错误状态、负面信息

## 字体系统

### 字体大小
- **超小**: 11.0px - 标签、辅助信息
- **小**: 12.5px - 说明文字、次要信息
- **中等**: 14.5px - 正文、按钮文字
- **大**: 15.5px - 标题、重要信息
- **超大**: 16.5px - 主要标题
- **标题**: 22.0px - 页面标题

### 字体粗细
- **正常**: 400 - 正文
- **中等**: 500 - 强调文字
- **半粗**: 600 - 标题、重要信息
- **粗体**: 700 - 主要标题
- **特粗**: 800 - 页面标题

## 间距系统

### 基础间距
- **XS**: 4px - 最小间距
- **S**: 8px - 小间距
- **M**: 12px - 中等间距
- **L**: 16px - 大间距
- **XL**: 20px - 超大间距
- **XXL**: 24px - 超超大间距

### 使用规则
- 组件内部使用 XS 到 M 间距
- 组件之间使用 L 到 XXL 间距
- 页面边缘使用 L 间距

## 圆角系统

### 圆角大小
- **S**: 8px - 小按钮、标签
- **M**: 12px - 中等按钮、输入框
- **L**: 16px - 卡片、面板
- **XL**: 18px - 大卡片、特殊组件

## 阴影系统

### 阴影类型
- **轻阴影**: 8% 黑色，18px 模糊，8px 偏移
- **中阴影**: 12% 黑色，24px 模糊，12px 偏移

### 使用场景
- 轻阴影用于普通卡片
- 中阴影用于浮动元素、模态框

## 组件使用指南

### 1. 页面标题
```dart
PageTitle(
  title: '页面名称',
  icon: Icons.home,
  onBackPressed: () => Navigator.pop(context),
)
```

### 2. 标准卡片
```dart
StandardCard(
  padding: EdgeInsets.all(T.spacingL),
  child: YourContent(),
)
```

### 3. 信息卡片
```dart
InfoCard(
  title: '标题',
  subtitle: '副标题',
  leading: Icon(Icons.info),
  onTap: () {},
)
```

### 4. 统计卡片
```dart
StatCard(
  label: '总资产',
  value: '\$100,000',
  icon: Icons.account_balance_wallet,
)
```

### 5. 操作按钮
```dart
ActionButton(
  label: '确认',
  icon: Icons.check,
  onPressed: () {},
)
```

### 6. 分段选择器
```dart
SegmentedSelector(
  items: ['今日', '本周', '本月'],
  value: selectedPeriod,
  onChanged: (value) => setState(() => selectedPeriod = value),
)
```

### 7. 设置项
```dart
SettingItem(
  title: '设置名称',
  subtitle: '设置描述',
  icon: Icons.settings,
  onTap: () {},
)
```

## 页面布局规范

### 标准页面结构
```dart
@override
Widget build(BuildContext context) {
  return Scaffold(
    backgroundColor: T.background,
    body: SafeArea(
      child: SingleChildScrollView(
        child: Column(
          children: [
            // 1. 页面标题
            PageTitle(title: '页面名称'),
            
            // 2. 主要内容区域
            Padding(
              padding: EdgeInsets.symmetric(horizontal: T.spacingL),
              child: Column(
                children: [
                  // 使用标准组件
                  StandardCard(child: YourContent()),
                  SizedBox(height: T.spacingL),
                  // 更多内容...
                ],
              ),
            ),
            
            // 3. 底部间距
            SizedBox(height: T.spacingXXL),
          ],
        ),
      ),
    ),
  );
}
```

### 卡片布局
- 卡片之间使用 L 间距
- 卡片内部使用 M 间距
- 卡片与页面边缘使用 L 间距

### 列表布局
- 列表项之间使用 S 间距
- 列表与页面边缘使用 L 间距
- 长列表考虑使用分割线

## 响应式设计

### 断点
- **小屏幕**: < 600px - 单列布局
- **中等屏幕**: 600px - 1200px - 双列布局
- **大屏幕**: > 1200px - 多列布局

### 适配原则
- 使用 `LayoutBuilder` 检测可用空间
- 根据屏幕大小调整间距和布局
- 保持组件的最小可用尺寸

## 最佳实践

### 1. 颜色使用
- 优先使用设计令牌中定义的颜色
- 避免硬编码颜色值
- 确保足够的对比度

### 2. 间距使用
- 使用设计令牌中的间距值
- 保持一致的间距节奏
- 避免随意使用数字

### 3. 组件复用
- 优先使用通用组件库
- 避免重复创建相似组件
- 保持组件的单一职责

### 4. 性能优化
- 合理使用 `const` 构造函数
- 避免不必要的重建
- 使用适当的动画时长

## 更新日志

### v1.0.0 (2025-08-22)
- 初始设计令牌定义
- 基础组件库创建
- 设计指南文档编写

## 联系方式
如有设计相关问题，请联系设计团队或查看最新设计规范。
