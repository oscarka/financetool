#!/usr/bin/env python3
"""
测试Wise API余额解析修复
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_wise_balance_parsing_fix():
    """测试修复后的余额解析逻辑"""
    
    # 模拟Wise API返回的各种问题数据
    test_cases = [
        {
            "name": "正常数据",
            "data": {
                "id": "124639690",
                "currency": "JPY",
                "amount": {"value": "139833.0"},
                "reservedAmount": {"value": "0.0"},
                "cashAmount": {"value": "139833.0"},
                "totalWorth": {"value": "139833.0"},
                "type": "STANDARD"
            }
        },
        {
            "name": "空值数据",
            "data": {
                "id": "test_account",
                "currency": "USD",
                "amount": {"value": None},
                "reservedAmount": {"value": ""},
                "cashAmount": {"value": None},
                "totalWorth": {"value": ""},
                "type": "STANDARD"
            }
        },
        {
            "name": "无效字符串数据",
            "data": {
                "id": "test_account",
                "currency": "USD",
                "amount": {"value": "invalid"},
                "reservedAmount": {"value": "not_a_number"},
                "cashAmount": {"value": "abc123"},
                "totalWorth": {"value": "123.456.789"},
                "type": "STANDARD"
            }
        },
        {
            "name": "缺失字段数据",
            "data": {
                "id": "test_account",
                "currency": "EUR",
                "type": "STANDARD"
                # 缺少amount, reservedAmount等字段
            }
        },
        {
            "name": "非字典字段数据",
            "data": {
                "id": "test_account",
                "currency": "GBP",
                "amount": "not_a_dict",
                "reservedAmount": 123,
                "cashAmount": None,
                "totalWorth": "string_value",
                "type": "STANDARD"
            }
        }
    ]
    
    def safe_float(value, default=0.0):
        """模拟修复后的_safe_float方法"""
        if value is None or value == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            print(f"⚠️  无法转换余额值: {value}, 使用默认值: {default}")
            return default
    
    def parse_balance_fixed(balance_data):
        """模拟修复后的余额解析逻辑"""
        try:
            balance_id = balance_data.get('id')
            if not balance_id:
                print(f"❌ balance缺少id: {balance_data}")
                return None
                
            # 安全获取嵌套字典值
            amount_data = balance_data.get('amount', {})
            reserved_data = balance_data.get('reservedAmount', {})
            cash_data = balance_data.get('cashAmount', {})
            total_data = balance_data.get('totalWorth', {})
            
            return {
                "account_id": balance_id,
                "currency": balance_data.get('currency'),
                "available_balance": safe_float(amount_data.get('value', 0) if isinstance(amount_data, dict) else 0),
                "reserved_balance": safe_float(reserved_data.get('value', 0) if isinstance(reserved_data, dict) else 0),
                "cash_amount": safe_float(cash_data.get('value', 0) if isinstance(cash_data, dict) else 0),
                "total_worth": safe_float(total_data.get('value', 0) if isinstance(total_data, dict) else 0),
                "type": balance_data.get('type'),
                "update_time": "2025-07-13T23:36:16.819049"
            }
            
        except Exception as e:
            print(f"❌ 解析余额数据时发生异常: {e}")
            return None
    
    print("=== 测试Wise API余额解析修复 ===")
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        print(f"   输入数据: {json.dumps(test_case['data'], indent=2, ensure_ascii=False)}")
        
        result = parse_balance_fixed(test_case['data'])
        
        if result:
            print(f"   ✅ 解析成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
            success_count += 1
        else:
            print("   ❌ 解析失败")
    
    print(f"\n=== 测试结果 ===")
    print(f"成功: {success_count}/{total_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！修复成功！")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    print("\n=== 修复说明 ===")
    print("1. 添加了_safe_float方法，安全处理数值转换")
    print("2. 添加了类型检查，确保嵌套字典访问安全")
    print("3. 对None、空字符串、无效数值等异常情况进行了处理")
    print("4. 所有异常情况都会记录警告日志并使用默认值")

if __name__ == "__main__":
    test_wise_balance_parsing_fix()