# Wise API primaryAmount字段解析问题修复

## 🐛 问题描述

在解析Wise API回传的交易记录时，发现`primaryAmount`字段的解析存在问题。该字段包含货币名称和带逗号的数字格式（如`"1,234.56 USD"`），但原始的正则表达式无法正确处理带逗号的数字，导致解析失败。

## 🔍 问题分析

### 1. 原始代码问题
在 `backend/app/services/wise_api_service.py` 的两个位置：

**位置1（第280行附近）**：
```python
# 解析金额字符串，如 "+ 279.77 AUD" 或 "3.27 USD"
if primary_amount:
    import re
    # 匹配金额和货币
    amount_match = re.search(r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})', primary_amount)
    if amount_match:
        amount_str = amount_match.group(1).replace(' ', '')
        currency = amount_match.group(2)
        try:
            amount_value = float(amount_str)
        except ValueError:
            amount_value = 0.0
```

**位置2（第535行附近）**：
```python
if primary_amount:
    amount_match = re.search(r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})', primary_amount)
    if amount_match:
        amount_str = amount_match.group(1).replace(' ', '')
        currency = amount_match.group(2)
        try:
            amount_value = float(amount_str)
        except ValueError:
            amount_value = 0.0
```

### 2. 问题场景
原始正则表达式 `r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})'` 无法处理以下格式：
- `"1,234.56 USD"` → 只能匹配到 `"234.56 USD"`，丢失了千位数字
- `"12,345.67 EUR"` → 只能匹配到 `"345.67 EUR"`，丢失了万位数字
- `"1,000 JPY"` → 只能匹配到 `"000 JPY"`，导致解析为0

### 3. 影响范围
- 交易金额解析错误，导致财务数据不准确
- 带逗号的大额交易金额被截断
- 影响交易记录的完整性和准确性

## ✅ 修复方案

### 1. 更新正则表达式
将正则表达式从：
```python
r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})'
```
更新为：
```python
r'([+-]?\s*[\d,]+\.?\d*)\s*([A-Z]{3})'
```

### 2. 添加逗号处理
在转换为float之前移除所有逗号：
```python
amount_str = amount_match.group(1).replace(' ', '').replace(',', '')
```

### 3. 改进错误处理
添加警告日志便于问题追踪：
```python
except ValueError:
    logger.warning(f"[Wise] 无法转换交易金额: {amount_str}, 使用默认值: 0.0")
    amount_value = 0.0
```

## 🧪 测试验证

### 测试用例覆盖
创建了8个测试用例，覆盖以下场景：
1. ✅ 标准格式：`"+ 279.77 AUD"`
2. ✅ 带逗号的数字：`"1,234.56 USD"`
3. ✅ 大数字带逗号：`"12,345.67 EUR"`
4. ✅ 负数带逗号：`"- 2,500.00 GBP"`
5. ✅ 整数带逗号：`"1,000 JPY"`
6. ✅ 小数不带逗号：`"123.45 CNY"`
7. ✅ 空字符串：`""`
8. ✅ 无效格式：`"invalid format"`

### 测试结果
- **原始方法成功率**：4/8 (50.0%)
- **修复方法成功率**：8/8 (100.0%)
- **改进效果**：成功率提升50%

## 📋 修复效果

### 1. 数据准确性
- 现在可以正确解析带逗号的数字格式
- 大额交易金额不再被截断
- 支持各种货币格式的完整解析

### 2. 系统稳定性
- 添加了更好的错误处理机制
- 异常情况下使用默认值保证数据完整性
- 增加了警告日志便于问题追踪

### 3. 用户体验
- 交易记录显示正确的金额
- 财务数据更加准确可靠
- 支持国际化数字格式

## 🔧 技术细节

### 正则表达式说明
- `[+-]?`：匹配可选的正负号
- `\s*`：匹配可选的空白字符
- `[\d,]+`：匹配一个或多个数字或逗号
- `\.?\d*`：匹配可选的小数点和后续数字
- `\s*`：匹配可选的空白字符
- `[A-Z]{3}`：匹配三个大写字母的货币代码

### 处理流程
1. 使用正则表达式提取金额和货币
2. 移除空白字符和逗号
3. 转换为float类型
4. 异常情况下使用默认值

## 📝 相关文件

- **主要修复文件**：`backend/app/services/wise_api_service.py`
- **测试文件**：`backend/test_primary_amount_parsing.py`
- **验证文件**：`backend/test_wise_primary_amount_fix.py`

## 🎯 总结

这次修复解决了Wise API交易记录中`primaryAmount`字段解析的核心问题，特别是带逗号数字格式的处理。修复后，系统能够：

1. **正确解析**各种数字格式，包括带逗号的千位分隔符
2. **保持兼容性**，不影响现有功能的正常运行
3. **提升准确性**，确保财务数据的正确性
4. **增强稳定性**，添加了完善的错误处理机制

这个修复对于处理国际化财务数据具有重要意义，特别是在处理不同地区货币格式时。