#!/usr/bin/env python3
"""
测试Wise API余额解析中的数值转换问题
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_balance_parsing():
    """测试余额解析逻辑"""
    
    # 模拟Wise API返回的余额数据
    mock_balance_data = {
        "id": "124639690",
        "currency": "JPY",
        "amount": {
            "value": "139833.0",  # 字符串格式
            "currency": "JPY"
        },
        "reservedAmount": {
            "value": "0.0",  # 字符串格式
            "currency": "JPY"
        },
        "cashAmount": {
            "value": "139833.0",  # 字符串格式
            "currency": "JPY"
        },
        "totalWorth": {
            "value": "139833.0",  # 字符串格式
            "currency": "JPY"
        },
        "type": "STANDARD",
        "name": None,
        "icon": None,
        "investmentState": "NOT_INVESTED",
        "creationTime": "2025-06-16T10:03:30.348309Z",
        "modificationTime": "2025-07-11T09:41:12.966253Z",
        "visible": True,
        "primary": True
    }
    
    # 模拟另一个余额数据（包含小数）
    mock_balance_data_2 = {
        "id": "124405547",
        "currency": "AUD",
        "amount": {
            "value": "4.52",  # 字符串格式的小数
            "currency": "AUD"
        },
        "reservedAmount": {
            "value": "0.0",
            "currency": "AUD"
        },
        "cashAmount": {
            "value": "4.52",
            "currency": "AUD"
        },
        "totalWorth": {
            "value": "4.52",
            "currency": "AUD"
        },
        "type": "STANDARD",
        "name": None,
        "icon": None,
        "investmentState": "NOT_INVESTED",
        "creationTime": "2025-06-13T09:05:19.265240Z",
        "modificationTime": "2025-07-11T09:38:28.715357Z",
        "visible": True,
        "primary": True
    }
    
    # 模拟可能的问题数据
    mock_problematic_data = {
        "id": "test_account",
        "currency": "USD",
        "amount": {
            "value": None,  # 空值
            "currency": "USD"
        },
        "reservedAmount": {
            "value": "",  # 空字符串
            "currency": "USD"
        },
        "cashAmount": {
            "value": "invalid",  # 无效字符串
            "currency": "USD"
        },
        "totalWorth": {
            "value": "123.456.789",  # 格式错误的数字
            "currency": "USD"
        },
        "type": "STANDARD",
        "name": None,
        "icon": None,
        "investmentState": "NOT_INVESTED",
        "creationTime": "2025-06-16T10:03:30.348309Z",
        "modificationTime": "2025-07-11T09:41:12.966253Z",
        "visible": True,
        "primary": True
    }
    
    def parse_balance(balance_data):
        """解析余额数据，模拟WiseAPIService中的逻辑"""
        try:
            balance_id = balance_data.get('id')
            if not balance_id:
                print(f"❌ balance缺少id: {balance_data}")
                return None
                
            # 解析各种余额字段
            available_balance = 0.0
            reserved_balance = 0.0
            cash_amount = 0.0
            total_worth = 0.0
            
            # 解析可用余额
            amount_value = balance_data.get('amount', {}).get('value', 0)
            if amount_value is not None and amount_value != "":
                try:
                    available_balance = float(amount_value)
                except (ValueError, TypeError) as e:
                    print(f"❌ 解析available_balance失败: {amount_value}, 错误: {e}")
                    available_balance = 0.0
            
            # 解析冻结余额
            reserved_value = balance_data.get('reservedAmount', {}).get('value', 0)
            if reserved_value is not None and reserved_value != "":
                try:
                    reserved_balance = float(reserved_value)
                except (ValueError, TypeError) as e:
                    print(f"❌ 解析reserved_balance失败: {reserved_value}, 错误: {e}")
                    reserved_balance = 0.0
            
            # 解析现金金额
            cash_value = balance_data.get('cashAmount', {}).get('value', 0)
            if cash_value is not None and cash_value != "":
                try:
                    cash_amount = float(cash_value)
                except (ValueError, TypeError) as e:
                    print(f"❌ 解析cash_amount失败: {cash_value}, 错误: {e}")
                    cash_amount = 0.0
            
            # 解析总价值
            total_value = balance_data.get('totalWorth', {}).get('value', 0)
            if total_value is not None and total_value != "":
                try:
                    total_worth = float(total_value)
                except (ValueError, TypeError) as e:
                    print(f"❌ 解析total_worth失败: {total_value}, 错误: {e}")
                    total_worth = 0.0
            
            return {
                "account_id": balance_id,
                "currency": balance_data.get('currency'),
                "available_balance": available_balance,
                "reserved_balance": reserved_balance,
                "cash_amount": cash_amount,
                "total_worth": total_worth,
                "type": balance_data.get('type'),
                "name": balance_data.get('name'),
                "icon": balance_data.get('icon'),
                "investment_state": balance_data.get('investmentState'),
                "creation_time": balance_data.get('creationTime'),
                "modification_time": balance_data.get('modificationTime'),
                "visible": balance_data.get('visible'),
                "primary": balance_data.get('primary'),
                "update_time": "2025-07-13T23:36:16.819049"
            }
            
        except Exception as e:
            print(f"❌ 解析余额数据时发生异常: {e}")
            return None
    
    print("=== 测试Wise API余额解析 ===")
    
    # 测试正常数据
    print("\n1. 测试正常数据 (JPY):")
    result1 = parse_balance(mock_balance_data)
    if result1:
        print(f"✅ 解析成功: {json.dumps(result1, indent=2, ensure_ascii=False)}")
    else:
        print("❌ 解析失败")
    
    print("\n2. 测试正常数据 (AUD):")
    result2 = parse_balance(mock_balance_data_2)
    if result2:
        print(f"✅ 解析成功: {json.dumps(result2, indent=2, ensure_ascii=False)}")
    else:
        print("❌ 解析失败")
    
    print("\n3. 测试问题数据:")
    result3 = parse_balance(mock_problematic_data)
    if result3:
        print(f"✅ 解析成功 (应该处理了错误): {json.dumps(result3, indent=2, ensure_ascii=False)}")
    else:
        print("❌ 解析失败")
    
    # 测试边界情况
    print("\n4. 测试边界情况:")
    
    # 测试空数据
    empty_data = {}
    result4 = parse_balance(empty_data)
    if result4 is None:
        print("✅ 空数据处理正确")
    else:
        print("❌ 空数据处理错误")
    
    # 测试None数据
    result5 = parse_balance(None)
    if result5 is None:
        print("✅ None数据处理正确")
    else:
        print("❌ None数据处理错误")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_balance_parsing()