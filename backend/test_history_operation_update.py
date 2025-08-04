#!/usr/bin/env python3
"""
测试历史操作修改时的净值匹配逻辑
"""
import sys
import os
from datetime import datetime, date, time, timedelta
from decimal import Decimal

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import get_db
from app.services.fund_service import FundOperationService, FundNavService
from app.models.database import UserOperation, FundNav
from app.models.schemas import FundOperationUpdate


def test_history_operation_update():
    """测试历史操作修改时的净值匹配逻辑"""
    print("=== 测试历史操作修改时的净值匹配逻辑 ===")
    
    db = next(get_db())
    
    try:
        # 测试基金代码
        fund_code = "000001"  # 平安银行
        
        # 创建历史净值数据（一周前）
        historical_date = date.today() - timedelta(days=7)
        historical_nav = Decimal("1.2000")
        
        try:
            FundNavService.create_nav(db, fund_code, historical_date, historical_nav)
            print(f"插入历史净值: {historical_date} = {historical_nav}")
        except Exception as e:
            print(f"插入历史净值失败: {e}")
        
        # 创建历史操作（一周前15:00之前）
        historical_operation_time = datetime.combine(historical_date, time(14, 30, 0))
        
        from app.models.schemas import FundOperationCreate
        
        operation_data = FundOperationCreate(
            operation_date=historical_operation_time.isoformat(),
            operation_type="buy",
            asset_code=fund_code,
            asset_name="测试基金",
            amount=Decimal("1000"),
            currency="CNY"
        )
        
        # 创建历史操作
        operation = FundOperationService.create_operation(db, operation_data)
        print(f"创建历史操作: ID={operation.id}, 时间={operation.operation_date}")
        print(f"初始状态: {operation.status}, 净值: {operation.nav}, 份额: {operation.quantity}")
        
        # 测试修改历史操作
        print("\n--- 测试修改历史操作 ---")
        
        # 修改操作时间（改为15:00之后）
        new_operation_time = datetime.combine(historical_date, time(16, 30, 0))
        
        update_data = FundOperationUpdate(
            operation_date=new_operation_time.isoformat()
        )
        
        print(f"修改操作时间: {new_operation_time}")
        
        # 执行修改
        updated_operation = FundOperationService.update_operation(db, operation.id, update_data)
        
        print(f"修改后状态: {updated_operation.status}")
        print(f"修改后净值: {updated_operation.nav}")
        print(f"修改后份额: {updated_operation.quantity}")
        print(f"修改后时间: {updated_operation.operation_date}")
        
        # 验证结果
        if updated_operation.status == "confirmed":
            print("✅ 历史操作修改成功，状态为已确认")
        else:
            print("❌ 历史操作修改失败，状态仍为待确认")
        
        # 测试未来操作修改
        print("\n--- 测试修改未来操作 ---")
        
        # 创建未来操作（明天15:00之后）
        future_date = date.today() + timedelta(days=1)
        future_operation_time = datetime.combine(future_date, time(16, 30, 0))
        
        future_operation_data = FundOperationCreate(
            operation_date=future_operation_time.isoformat(),
            operation_type="buy",
            asset_code=fund_code,
            asset_name="测试基金",
            amount=Decimal("1000"),
            currency="CNY"
        )
        
        future_operation = FundOperationService.create_operation(db, future_operation_data)
        print(f"创建未来操作: ID={future_operation.id}, 时间={future_operation.operation_date}")
        print(f"初始状态: {future_operation.status}")
        
        # 修改未来操作时间
        new_future_time = datetime.combine(future_date, time(14, 30, 0))
        
        future_update_data = FundOperationUpdate(
            operation_date=new_future_time.isoformat()
        )
        
        print(f"修改未来操作时间: {new_future_time}")
        
        # 执行修改
        updated_future_operation = FundOperationService.update_operation(db, future_operation.id, future_update_data)
        
        print(f"修改后状态: {updated_future_operation.status}")
        print(f"修改后净值: {updated_future_operation.nav}")
        print(f"修改后份额: {updated_future_operation.quantity}")
        
        # 验证结果
        if updated_future_operation.status == "pending":
            print("✅ 未来操作修改正确，状态为待确认（因为对应净值还未同步）")
        else:
            print("❌ 未来操作修改状态异常")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_history_operation_update() 