#!/usr/bin/env python3
"""
测试Wise API primaryAmount字段解析问题
"""

import re

def test_primary_amount_parsing():
    """测试primaryAmount字段解析"""
    
    # 测试用例
    test_cases = [
        {
            "name": "标准格式",
            "input": "+ 279.77 AUD",
            "expected": {"amount": 279.77, "currency": "AUD"}
        },
        {
            "name": "带逗号的数字",
            "input": "1,234.56 USD",
            "expected": {"amount": 1234.56, "currency": "USD"}
        },
        {
            "name": "大数字带逗号",
            "input": "12,345.67 EUR",
            "expected": {"amount": 12345.67, "currency": "EUR"}
        },
        {
            "name": "负数带逗号",
            "input": "- 2,500.00 GBP",
            "expected": {"amount": -2500.00, "currency": "GBP"}
        },
        {
            "name": "整数带逗号",
            "input": "1,000 JPY",
            "expected": {"amount": 1000.0, "currency": "JPY"}
        },
        {
            "name": "小数不带逗号",
            "input": "123.45 CNY",
            "expected": {"amount": 123.45, "currency": "CNY"}
        },
        {
            "name": "空字符串",
            "input": "",
            "expected": {"amount": 0.0, "currency": "USD"}
        },
        {
            "name": "无效格式",
            "input": "invalid format",
            "expected": {"amount": 0.0, "currency": "USD"}
        }
    ]
    
    def parse_primary_amount_old(primary_amount):
        """原始解析方法"""
        amount_value = 0.0
        currency = 'USD'
        
        if primary_amount:
            # 原始正则表达式 - 无法处理逗号
            amount_match = re.search(r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})', primary_amount)
            if amount_match:
                amount_str = amount_match.group(1).replace(' ', '')
                currency = amount_match.group(2)
                try:
                    amount_value = float(amount_str)
                except ValueError:
                    amount_value = 0.0
        
        return {"amount": amount_value, "currency": currency}
    
    def parse_primary_amount_fixed(primary_amount):
        """修复后的解析方法"""
        amount_value = 0.0
        currency = 'USD'
        
        if primary_amount:
            # 修复后的正则表达式 - 支持逗号分隔符
            amount_match = re.search(r'([+-]?\s*[\d,]+\.?\d*)\s*([A-Z]{3})', primary_amount)
            if amount_match:
                amount_str = amount_match.group(1).replace(' ', '').replace(',', '')
                currency = amount_match.group(2)
                try:
                    amount_value = float(amount_str)
                except ValueError:
                    amount_value = 0.0
        
        return {"amount": amount_value, "currency": currency}
    
    print("=== 测试Wise API primaryAmount字段解析 ===")
    
    print("\n1. 测试原始解析方法:")
    old_success = 0
    old_total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   {i}. {test_case['name']}")
        print(f"      输入: '{test_case['input']}'")
        
        result = parse_primary_amount_old(test_case['input'])
        expected = test_case['expected']
        
        if result == expected:
            print(f"      ✅ 正确: {result}")
            old_success += 1
        else:
            print(f"      ❌ 错误: 期望 {expected}, 实际 {result}")
    
    print(f"\n   原始方法成功率: {old_success}/{old_total} ({old_success/old_total*100:.1f}%)")
    
    print("\n2. 测试修复后的解析方法:")
    fixed_success = 0
    fixed_total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   {i}. {test_case['name']}")
        print(f"      输入: '{test_case['input']}'")
        
        result = parse_primary_amount_fixed(test_case['input'])
        expected = test_case['expected']
        
        if result == expected:
            print(f"      ✅ 正确: {result}")
            fixed_success += 1
        else:
            print(f"      ❌ 错误: 期望 {expected}, 实际 {result}")
    
    print(f"\n   修复方法成功率: {fixed_success}/{fixed_total} ({fixed_success/fixed_total*100:.1f}%)")
    
    print("\n=== 修复说明 ===")
    print("原始正则表达式: r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})'")
    print("修复后正则表达式: r'([+-]?\s*[\d,]+\.?\d*)\s*([A-Z]{3})'")
    print("主要改进: 在数字部分添加了逗号支持 [\\d,]+")
    print("处理逻辑: 在转换为float之前移除所有逗号 .replace(',', '')")
    
    if fixed_success > old_success:
        print(f"\n🎉 修复成功！成功率从 {old_success/old_total*100:.1f}% 提升到 {fixed_success/fixed_total*100:.1f}%")
    else:
        print(f"\n⚠️  修复效果不明显，需要进一步分析")

if __name__ == "__main__":
    test_primary_amount_parsing()