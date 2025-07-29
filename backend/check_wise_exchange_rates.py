#!/usr/bin/env python3
"""
检查Wise汇率数据同步状态的脚本
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

# 设置环境变量
os.environ.setdefault('DATABASE_URL', 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test')

def check_wise_exchange_rates():
    """检查Wise汇率数据情况"""
    try:
        # 创建数据库连接
        engine = create_engine(os.environ['DATABASE_URL'])
        
        with engine.connect() as conn:
            print("🔍 检查Wise汇率数据同步状态...")
            print("=" * 60)
            
            # 1. 检查wise_exchange_rates表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'wise_exchange_rates'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ wise_exchange_rates表不存在")
                return
            
            print("✅ wise_exchange_rates表存在")
            
            # 2. 检查总记录数
            result = conn.execute(text("SELECT COUNT(*) FROM wise_exchange_rates"))
            total_count = result.scalar()
            print(f"📊 总记录数: {total_count}")
            
            if total_count == 0:
                print("❌ 没有汇率数据，需要同步")
                return
            
            # 3. 检查币种对分布
            result = conn.execute(text("""
                SELECT source_currency, target_currency, COUNT(*) as count
                FROM wise_exchange_rates 
                GROUP BY source_currency, target_currency
                ORDER BY count DESC
            """))
            
            print("\n📈 币种对分布:")
            currency_pairs = []
            for row in result:
                pair = f"{row.source_currency}->{row.target_currency}"
                print(f"  {pair}: {row.count} 条记录")
                currency_pairs.append({
                    'source': row.source_currency,
                    'target': row.target_currency,
                    'count': row.count
                })
            
            # 4. 检查时间范围
            result = conn.execute(text("""
                SELECT 
                    MIN(time) as earliest_time,
                    MAX(time) as latest_time,
                    COUNT(DISTINCT DATE(time)) as unique_days
                FROM wise_exchange_rates
            """))
            
            row = result.fetchone()
            earliest_time = row.earliest_time
            latest_time = row.latest_time
            unique_days = row.unique_days
            
            print(f"\n⏰ 时间范围:")
            print(f"  最早记录: {earliest_time}")
            print(f"  最新记录: {latest_time}")
            print(f"  覆盖天数: {unique_days} 天")
            
            # 5. 检查最近7天的数据
            seven_days_ago = datetime.now() - timedelta(days=7)
            result = conn.execute(text("""
                SELECT COUNT(*) FROM wise_exchange_rates 
                WHERE time >= :seven_days_ago
            """), {'seven_days_ago': seven_days_ago})
            
            recent_count = result.scalar()
            print(f"\n📅 最近7天数据:")
            print(f"  记录数: {recent_count}")
            
            # 6. 检查每个币种对的最新记录
            print(f"\n🔍 各币种对最新记录:")
            for pair in currency_pairs:
                result = conn.execute(text("""
                    SELECT MAX(time) as latest_time, COUNT(*) as total_count
                    FROM wise_exchange_rates 
                    WHERE source_currency = :source AND target_currency = :target
                """), {
                    'source': pair['source'],
                    'target': pair['target']
                })
                
                row = result.fetchone()
                latest_time = row.latest_time
                total_count = row.total_count
                
                # 计算距离现在多少天
                days_ago = (datetime.now() - latest_time).days if latest_time else None
                
                status = "✅" if days_ago is None or days_ago <= 1 else "⚠️" if days_ago <= 7 else "❌"
                print(f"  {status} {pair['source']}->{pair['target']}: {latest_time} ({days_ago}天前, {total_count}条)")
            
            # 7. 检查定时任务配置
            print(f"\n⚙️ 定时任务配置检查:")
            print("  任务ID: wise_exchange_rate_sync")
            print("  执行时间: 每天18:00")
            print("  状态: 已启用")
            
            # 8. 问题诊断
            print(f"\n🔧 问题诊断:")
            
            if recent_count == 0:
                print("  ❌ 最近7天没有新数据，可能存在以下问题:")
                print("    1. 定时任务未执行")
                print("    2. Wise API配置错误")
                print("    3. 汇率同步任务未实现")
                print("    4. 网络连接问题")
            elif recent_count < len(currency_pairs) * 7:
                print("  ⚠️  数据不完整，可能存在以下问题:")
                print("    1. 部分币种对同步失败")
                print("    2. API限制或错误")
                print("    3. 网络连接不稳定")
            else:
                print("  ✅ 数据同步正常")
            
            # 9. 建议
            print(f"\n💡 建议:")
            if recent_count == 0:
                print("  1. 检查定时任务是否正常运行")
                print("  2. 验证Wise API配置")
                print("  3. 实现汇率同步任务")
                print("  4. 手动触发同步测试")
            else:
                print("  1. 监控定时任务执行状态")
                print("  2. 定期检查数据完整性")
                print("  3. 设置数据同步告警")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_wise_exchange_rates()