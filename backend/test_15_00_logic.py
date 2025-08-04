#!/usr/bin/env python3
"""
测试15:00时间点净值匹配逻辑
"""
import sys
import os
from datetime import datetime, date, time
from decimal import Decimal

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import get_db
from app.services.fund_service import FundOperationService, FundNavService
from app.models.database import UserOperation, FundNav


def test_15_00_logic():
    """测试15:00时间点净值匹配逻辑"""
    print("=== 测试15:00时间点净值匹配逻辑 ===")
    
    db = next(get_db())
    
    try:
        # 测试基金代码
        fund_code = "000001"  # 平安银行
        
        # 创建测试净值数据
        test_navs = [
            {"date": date(2024, 1, 15), "nav": Decimal("1.2345")},  # 周一
            {"date": date(2024, 1, 16), "nav": Decimal("1.2456")},  # 周二
            {"date": date(2024, 1, 17), "nav": Decimal("1.2567")},  # 周三
            {"date": date(2024, 1, 18), "nav": Decimal("1.2678")},  # 周四
            {"date": date(2024, 1, 19), "nav": Decimal("1.2789")},  # 周五
            {"date": date(2024, 1, 22), "nav": Decimal("1.2890")},  # 下周一
        ]
        
        # 插入测试净值数据
        for nav_data in test_navs:
            try:
                FundNavService.create_nav(db, fund_code, nav_data["date"], nav_data["nav"])
                print(f"插入净值: {nav_data['date']} = {nav_data['nav']}")
            except Exception as e:
                print(f"插入净值失败: {e}")
        
        # 测试场景1: 15:00之前的操作
        print("\n--- 测试场景1: 15:00之前的操作 ---")
        operation_time_1 = datetime(2024, 1, 15, 14, 30, 0)  # 周一14:30
        nav_date_1 = FundOperationService._get_nav_date_by_operation_time(db, fund_code, operation_time_1)
        print(f"操作时间: {operation_time_1}")
        print(f"匹配的净值日期: {nav_date_1}")
        print(f"预期结果: {date(2024, 1, 15)} (当天)")
        print(f"测试结果: {'✓' if nav_date_1 == date(2024, 1, 15) else '✗'}")
        
        # 测试场景2: 15:00之后的操作
        print("\n--- 测试场景2: 15:00之后的操作 ---")
        operation_time_2 = datetime(2024, 1, 15, 16, 30, 0)  # 周一16:30
        nav_date_2 = FundOperationService._get_nav_date_by_operation_time(db, fund_code, operation_time_2)
        print(f"操作时间: {operation_time_2}")
        print(f"匹配的净值日期: {nav_date_2}")
        print(f"预期结果: {date(2024, 1, 16)} (下一个交易日)")
        print(f"测试结果: {'✓' if nav_date_2 == date(2024, 1, 16) else '✗'}")
        
        # 测试场景3: 周五15:00之后的操作
        print("\n--- 测试场景3: 周五15:00之后的操作 ---")
        operation_time_3 = datetime(2024, 1, 19, 16, 30, 0)  # 周五16:30
        nav_date_3 = FundOperationService._get_nav_date_by_operation_time(db, fund_code, operation_time_3)
        print(f"操作时间: {operation_time_3}")
        print(f"匹配的净值日期: {nav_date_3}")
        print(f"预期结果: {date(2024, 1, 22)} (下周一)")
        print(f"测试结果: {'✓' if nav_date_3 == date(2024, 1, 22) else '✗'}")
        
        # 测试场景4: 获取对应的净值
        print("\n--- 测试场景4: 获取对应的净值 ---")
        nav_record_1 = FundOperationService._get_nav_by_operation_time(db, fund_code, operation_time_1)
        nav_record_2 = FundOperationService._get_nav_by_operation_time(db, fund_code, operation_time_2)
        
        print(f"15:00前操作净值: {nav_record_1.nav if nav_record_1 else 'None'}")
        print(f"15:00后操作净值: {nav_record_2.nav if nav_record_2 else 'None'}")
        
        # 测试场景5: 创建待确认操作
        print("\n--- 测试场景5: 创建待确认操作 ---")
        from app.models.schemas import FundOperationCreate
        
        # 创建15:00前的操作
        operation_data_1 = FundOperationCreate(
            operation_date=operation_time_1.isoformat(),
            operation_type="buy",
            asset_code=fund_code,
            asset_name="测试基金",
            amount=Decimal("1000"),
            currency="CNY"
        )
        
        operation_1 = FundOperationService.create_operation(db, operation_data_1)
        print(f"15:00前操作状态: {operation_1.status}")
        print(f"15:00前操作净值: {operation_1.nav}")
        print(f"15:00前操作份额: {operation_1.quantity}")
        
        # 创建15:00后的操作
        operation_data_2 = FundOperationCreate(
            operation_date=operation_time_2.isoformat(),
            operation_type="buy",
            asset_code=fund_code,
            asset_name="测试基金",
            amount=Decimal("1000"),
            currency="CNY"
        )
        
        operation_2 = FundOperationService.create_operation(db, operation_data_2)
        print(f"15:00后操作状态: {operation_2.status}")
        print(f"15:00后操作净值: {operation_2.nav}")
        print(f"15:00后操作份额: {operation_2.quantity}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_15_00_logic() 