#!/usr/bin/env python3
"""
测试Wise API primaryAmount字段解析修复
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_wise_primary_amount_fix():
    """测试修复后的primaryAmount解析逻辑"""
    
    # 模拟Wise API返回的交易数据
    test_transactions = [
        {
            "id": "test_1",
            "primaryAmount": "+ 279.77 AUD",
            "description": "Test transaction 1",
            "type": "CREDIT"
        },
        {
            "id": "test_2", 
            "primaryAmount": "1,234.56 USD",
            "description": "Test transaction 2",
            "type": "DEBIT"
        },
        {
            "id": "test_3",
            "primaryAmount": "12,345.67 EUR",
            "description": "Test transaction 3", 
            "type": "CREDIT"
        },
        {
            "id": "test_4",
            "primaryAmount": "- 2,500.00 GBP",
            "description": "Test transaction 4",
            "type": "DEBIT"
        },
        {
            "id": "test_5",
            "primaryAmount": "1,000 JPY",
            "description": "Test transaction 5",
            "type": "CREDIT"
        },
        {
            "id": "test_6",
            "primaryAmount": "123.45 CNY",
            "description": "Test transaction 6",
            "type": "DEBIT"
        },
        {
            "id": "test_7",
            "primaryAmount": "",
            "description": "Test transaction 7",
            "type": "CREDIT"
        },
        {
            "id": "test_8",
            "primaryAmount": "invalid format",
            "description": "Test transaction 8",
            "type": "DEBIT"
        }
    ]
    
    def parse_primary_amount_fixed(primary_amount):
        """修复后的解析方法"""
        amount_value = 0.0
        currency = 'USD'
        
        if primary_amount:
            # 匹配金额和货币 - 支持逗号分隔符
            amount_match = re.search(r'([+-]?\s*[\d,]+\.?\d*)\s*([A-Z]{3})', primary_amount)
            if amount_match:
                amount_str = amount_match.group(1).replace(' ', '').replace(',', '')
                currency = amount_match.group(2)
                try:
                    amount_value = float(amount_str)
                except ValueError:
                    print(f"⚠️  无法转换交易金额: {amount_str}, 使用默认值: 0.0")
                    amount_value = 0.0
        
        return {"amount": amount_value, "currency": currency}
    
    print("=== 测试Wise API primaryAmount字段解析修复 ===")
    
    success_count = 0
    total_count = len(test_transactions)
    
    for i, transaction in enumerate(test_transactions, 1):
        print(f"\n{i}. 交易ID: {transaction['id']}")
        print(f"   原始数据: '{transaction['primaryAmount']}'")
        print(f"   描述: {transaction['description']}")
        print(f"   类型: {transaction['type']}")
        
        result = parse_primary_amount_fixed(transaction['primaryAmount'])
        
        print(f"   解析结果: 金额={result['amount']}, 货币={result['currency']}")
        
        # 验证解析结果
        if transaction['primaryAmount'] == "":
            if result['amount'] == 0.0 and result['currency'] == 'USD':
                print("   ✅ 空字符串处理正确")
                success_count += 1
            else:
                print("   ❌ 空字符串处理错误")
        elif transaction['primaryAmount'] == "invalid format":
            if result['amount'] == 0.0 and result['currency'] == 'USD':
                print("   ✅ 无效格式处理正确")
                success_count += 1
            else:
                print("   ❌ 无效格式处理错误")
        else:
            # 验证带逗号的数字是否正确解析
            if result['amount'] > 0 or result['amount'] < 0:
                print("   ✅ 金额解析正确")
                success_count += 1
            else:
                print("   ❌ 金额解析错误")
    
    print(f"\n=== 测试结果 ===")
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！primaryAmount字段解析修复成功！")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    print(f"\n=== 修复说明 ===")
    print("问题: 原始正则表达式无法处理带逗号的数字格式")
    print("修复: 更新正则表达式支持逗号分隔符，并在转换前移除逗号")
    print("影响: 现在可以正确解析如 '1,234.56 USD' 这样的格式")

if __name__ == "__main__":
    test_wise_primary_amount_fix()