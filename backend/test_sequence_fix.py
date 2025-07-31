#!/usr/bin/env python3
"""
测试PostgreSQL序列修复
"""
import sys
import os

# 强制设置PostgreSQL数据库连接
os.environ['DATABASE_URL'] = 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test'
os.environ['DATABASE_PERSISTENT_PATH'] = './data'
os.environ['APP_ENV'] = 'test'

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text
from app.utils.database import get_db
from app.services.fund_service import FundOperationService
from app.models.database import UserOperation, AssetPosition
from datetime import datetime, date
from decimal import Decimal

def test_sequence_fix():
    """测试序列修复功能"""
    print(f"🔍 数据库URL: {os.environ.get('DATABASE_URL')}")
    
    db = next(get_db())
    
    try:
        print("🔍 开始测试PostgreSQL序列修复...")
        
        # 检测数据库类型
        try:
            db_type_result = db.execute(text("SELECT version()"))
            db_version = db_type_result.scalar()
            print(f"数据库版本: {db_version}")
            
            if 'PostgreSQL' not in db_version:
                print("⚠️ 当前不是PostgreSQL数据库，跳过序列测试")
                return
        except Exception as e:
            print(f"❌ 无法检测数据库类型: {e}")
            return
        
        # 1. 检查当前序列状态
        print("\n📊 检查当前序列状态:")
        
        # 检查asset_positions表
        try:
            max_id_result = db.execute(text("SELECT MAX(id) FROM asset_positions"))
            max_id = max_id_result.scalar()
            print(f"asset_positions 最大ID: {max_id}")
            
            seq_result = db.execute(text("SELECT last_value FROM asset_positions_id_seq"))
            current_seq = seq_result.scalar()
            print(f"asset_positions 当前序列值: {current_seq}")
        except Exception as e:
            print(f"❌ 检查asset_positions序列失败: {e}")
            max_id = None
            current_seq = 0
        
        # 检查user_operations表
        try:
            max_op_id_result = db.execute(text("SELECT MAX(id) FROM user_operations"))
            max_op_id = max_op_id_result.scalar()
            print(f"user_operations 最大ID: {max_op_id}")
            
            seq_op_result = db.execute(text("SELECT last_value FROM user_operations_id_seq"))
            current_op_seq = seq_op_result.scalar()
            print(f"user_operations 当前序列值: {current_op_seq}")
        except Exception as e:
            print(f"❌ 检查user_operations序列失败: {e}")
            max_op_id = None
            current_op_seq = 0
        
        # 检查fund_nav表
        try:
            max_nav_id_result = db.execute(text("SELECT MAX(id) FROM fund_nav"))
            max_nav_id = max_nav_id_result.scalar()
            print(f"fund_nav 最大ID: {max_nav_id}")
            
            seq_nav_result = db.execute(text("SELECT last_value FROM fund_nav_id_seq"))
            current_nav_seq = seq_nav_result.scalar()
            print(f"fund_nav 当前序列值: {current_nav_seq}")
        except Exception as e:
            print(f"❌ 检查fund_nav序列失败: {e}")
            max_nav_id = None
            current_nav_seq = 0
        
        # 2. 测试序列修复
        print("\n🔧 测试序列修复:")
        
        # 测试asset_positions序列修复
        if max_id is not None and current_seq < max_id:
            print(f"修复asset_positions序列: 当前={current_seq}, 最大ID={max_id}")
            db.execute(text(f"SELECT setval('asset_positions_id_seq', {max_id})"))
            db.commit()
            print("✅ asset_positions序列修复完成")
        else:
            print("✅ asset_positions序列正常")
        
        # 测试user_operations序列修复
        if max_op_id is not None and current_op_seq < max_op_id:
            print(f"修复user_operations序列: 当前={current_op_seq}, 最大ID={max_op_id}")
            db.execute(text(f"SELECT setval('user_operations_id_seq', {max_op_id})"))
            db.commit()
            print("✅ user_operations序列修复完成")
        else:
            print("✅ user_operations序列正常")
        
        # 测试fund_nav序列修复
        if max_nav_id is not None and current_nav_seq < max_nav_id:
            print(f"修复fund_nav序列: 当前={current_nav_seq}, 最大ID={max_nav_id}")
            db.execute(text(f"SELECT setval('fund_nav_id_seq', {max_nav_id})"))
            db.commit()
            print("✅ fund_nav序列修复完成")
        else:
            print("✅ fund_nav序列正常")
        
        # 3. 验证修复结果
        print("\n📋 验证修复结果:")
        
        # 重新检查序列状态
        try:
            seq_result_after = db.execute(text("SELECT last_value FROM asset_positions_id_seq"))
            current_seq_after = seq_result_after.scalar()
            print(f"asset_positions 修复后序列值: {current_seq_after}")
        except Exception as e:
            print(f"❌ 无法获取asset_positions修复后序列值: {e}")
        
        try:
            seq_op_result_after = db.execute(text("SELECT last_value FROM user_operations_id_seq"))
            current_op_seq_after = seq_op_result_after.scalar()
            print(f"user_operations 修复后序列值: {current_op_seq_after}")
        except Exception as e:
            print(f"❌ 无法获取user_operations修复后序列值: {e}")
        
        try:
            seq_nav_result_after = db.execute(text("SELECT last_value FROM fund_nav_id_seq"))
            current_nav_seq_after = seq_nav_result_after.scalar()
            print(f"fund_nav 修复后序列值: {current_nav_seq_after}")
        except Exception as e:
            print(f"❌ 无法获取fund_nav修复后序列值: {e}")
        
        print("\n✅ 序列修复测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
    finally:
        db.close()

if __name__ == "__main__":
    test_sequence_fix() 