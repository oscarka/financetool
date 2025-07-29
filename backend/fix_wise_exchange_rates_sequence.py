#!/usr/bin/env python3
"""
修复wise_exchange_rates表的序列问题
解决主键冲突问题
"""

import os
import sys
from sqlalchemy import text
from app.utils.database import SessionLocal

def fix_sequence():
    """修复wise_exchange_rates表的序列"""
    print("🔧 开始修复wise_exchange_rates序列...")
    
    db = SessionLocal()
    try:
        # 1. 检查当前序列值
        result = db.execute(text("SELECT last_value, is_called FROM wise_exchange_rates_id_seq"))
        current_seq = result.fetchone()
        print(f"📊 当前序列状态: last_value={current_seq[0]}, is_called={current_seq[1]}")
        
        # 2. 获取表中最大ID
        result = db.execute(text("SELECT MAX(id) FROM wise_exchange_rates"))
        max_id = result.fetchone()[0]
        print(f"📊 表中最大ID: {max_id}")
        
        if max_id is None:
            print("❌ 表中没有数据，无法修复序列")
            return False
        
        # 3. 重置序列到最大ID
        db.execute(text(f"SELECT setval('wise_exchange_rates_id_seq', {max_id})"))
        db.commit()
        
        # 4. 验证修复结果
        result = db.execute(text("SELECT last_value, is_called FROM wise_exchange_rates_id_seq"))
        new_seq = result.fetchone()
        print(f"✅ 序列修复完成: last_value={new_seq[0]}, is_called={new_seq[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复序列失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def check_duplicates():
    """检查是否有重复记录"""
    print("🔍 检查重复记录...")
    
    db = SessionLocal()
    try:
        # 检查重复的币种对和时间
        result = db.execute(text("""
            SELECT source_currency, target_currency, time, COUNT(*) as count
            FROM wise_exchange_rates
            GROUP BY source_currency, target_currency, time
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """))
        
        duplicates = result.fetchall()
        if duplicates:
            print(f"⚠️  发现 {len(duplicates)} 组重复记录:")
            for dup in duplicates:
                print(f"   {dup[0]}->{dup[1]} {dup[2]}: {dup[3]} 条")
        else:
            print("✅ 没有发现重复记录")
            
        return len(duplicates) == 0
        
    except Exception as e:
        print(f"❌ 检查重复记录失败: {e}")
        return False
    finally:
        db.close()

def clean_duplicates():
    """清理重复记录"""
    print("🧹 清理重复记录...")
    
    db = SessionLocal()
    try:
        # 删除重复记录，保留ID最小的
        result = db.execute(text("""
            DELETE FROM wise_exchange_rates
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM wise_exchange_rates
                GROUP BY source_currency, target_currency, time
            )
        """))
        
        deleted_count = result.rowcount
        db.commit()
        print(f"✅ 清理完成，删除了 {deleted_count} 条重复记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理重复记录失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("🚀 Wise汇率表序列修复工具")
    print("=" * 50)
    
    # 设置环境变量
    os.environ.setdefault('DATABASE_URL', 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test')
    os.environ.setdefault('DATABASE_PERSISTENT_PATH', './data')
    os.environ.setdefault('APP_ENV', 'prod')
    
    # 1. 检查重复记录
    if not check_duplicates():
        print("❌ 发现重复记录，需要清理")
        if not clean_duplicates():
            print("❌ 清理重复记录失败")
            return
    
    # 2. 修复序列
    if fix_sequence():
        print("✅ 序列修复成功")
    else:
        print("❌ 序列修复失败")
        return
    
    # 3. 最终验证
    print("\n🔍 最终验证...")
    if check_duplicates():
        print("✅ 验证通过，没有重复记录")
    else:
        print("❌ 验证失败，仍有重复记录")
    
    print("\n🎉 修复完成！")

if __name__ == "__main__":
    main()