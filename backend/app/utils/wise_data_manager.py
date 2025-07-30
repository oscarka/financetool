#!/usr/bin/env python3
"""
Wise数据管理模块
统一管理Wise相关的数据库维护、检查和诊断功能
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from loguru import logger

class WiseDataManager:
    """Wise数据管理器"""
    
    def __init__(self, database_url=None):
        """初始化数据管理器"""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url or not self.database_url.startswith("postgresql://"):
            raise ValueError("需要PostgreSQL数据库连接")
        
        self.engine = create_engine(self.database_url, echo=False)
    
    def fix_exchange_rates_sequence(self):
        """修复wise_exchange_rates表的序列问题"""
        logger.info("🔧 开始修复wise_exchange_rates序列...")
        
        try:
            with self.engine.connect() as conn:
                # 1. 检查当前序列值
                result = conn.execute(text("SELECT last_value, is_called FROM wise_exchange_rates_id_seq"))
                current_seq = result.fetchone()
                logger.info(f"📊 当前序列状态: last_value={current_seq[0]}, is_called={current_seq[1]}")
                
                # 2. 获取表中最大ID
                result = conn.execute(text("SELECT MAX(id) FROM wise_exchange_rates"))
                max_id = result.scalar()
                logger.info(f"📊 表中最大ID: {max_id}")
                
                if max_id is None:
                    logger.info("ℹ️  表中没有数据，无需修复序列")
                    return True
                
                # 3. 重置序列到最大ID
                conn.execute(text(f"SELECT setval('wise_exchange_rates_id_seq', {max_id})"))
                conn.commit()
                
                # 4. 验证修复结果
                result = conn.execute(text("SELECT last_value, is_called FROM wise_exchange_rates_id_seq"))
                new_seq = result.fetchone()
                logger.info(f"✅ 序列修复完成: last_value={new_seq[0]}, is_called={new_seq[1]}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ 修复序列失败: {e}")
            return False
    
    def clean_duplicate_records(self):
        """清理重复记录"""
        logger.info("🔍 检查重复记录...")
        
        try:
            with self.engine.connect() as conn:
                # 检查重复的币种对和时间
                result = conn.execute(text("""
                    SELECT source_currency, target_currency, time, COUNT(*) as count
                    FROM wise_exchange_rates
                    GROUP BY source_currency, target_currency, time
                    HAVING COUNT(*) > 1
                    ORDER BY count DESC
                    LIMIT 10
                """))
                
                duplicates = result.fetchall()
                if duplicates:
                    logger.warning(f"⚠️  发现 {len(duplicates)} 组重复记录:")
                    for dup in duplicates:
                        logger.warning(f"   {dup[0]}->{dup[1]} {dup[2]}: {dup[3]} 条")
                    
                    # 清理重复记录，保留ID最小的
                    logger.info("🧹 清理重复记录...")
                    result = conn.execute(text("""
                        DELETE FROM wise_exchange_rates
                        WHERE id NOT IN (
                            SELECT MIN(id)
                            FROM wise_exchange_rates
                            GROUP BY source_currency, target_currency, time
                        )
                    """))
                    
                    deleted_count = result.rowcount
                    conn.commit()
                    logger.info(f"✅ 清理完成，删除了 {deleted_count} 条重复记录")
                else:
                    logger.info("✅ 没有发现重复记录")
                    
                return True
                
        except Exception as e:
            logger.error(f"❌ 检查重复记录失败: {e}")
            return False
    
    def check_data_status(self):
        """检查Wise汇率数据状态"""
        logger.info("🔍 检查Wise汇率数据同步状态...")
        
        try:
            with self.engine.connect() as conn:
                # 1. 检查wise_exchange_rates表是否存在
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'wise_exchange_rates'
                    )
                """))
                table_exists = result.scalar()
                
                if not table_exists:
                    logger.error("❌ wise_exchange_rates表不存在")
                    return False
                
                logger.info("✅ wise_exchange_rates表存在")
                
                # 2. 检查总记录数
                result = conn.execute(text("SELECT COUNT(*) FROM wise_exchange_rates"))
                total_count = result.scalar()
                logger.info(f"📊 总记录数: {total_count}")
                
                if total_count == 0:
                    logger.warning("❌ 没有汇率数据，需要同步")
                    return False
                
                # 3. 检查币种对分布
                result = conn.execute(text("""
                    SELECT source_currency, target_currency, COUNT(*) as count
                    FROM wise_exchange_rates 
                    GROUP BY source_currency, target_currency
                    ORDER BY count DESC
                """))
                
                logger.info("📈 币种对分布:")
                currency_pairs = []
                for row in result:
                    pair = f"{row.source_currency}->{row.target_currency}"
                    logger.info(f"  {pair}: {row.count} 条记录")
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
                
                logger.info(f"⏰ 时间范围:")
                logger.info(f"  最早记录: {earliest_time}")
                logger.info(f"  最新记录: {latest_time}")
                logger.info(f"  覆盖天数: {unique_days} 天")
                
                # 5. 检查最近7天的数据
                seven_days_ago = datetime.now() - timedelta(days=7)
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM wise_exchange_rates 
                    WHERE time >= :seven_days_ago
                """), {'seven_days_ago': seven_days_ago})
                
                recent_count = result.scalar()
                logger.info(f"📅 最近7天数据:")
                logger.info(f"  记录数: {recent_count}")
                
                # 6. 检查每个币种对的最新记录
                logger.info("🔍 各币种对最新记录:")
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
                    logger.info(f"  {status} {pair['source']}->{pair['target']}: {latest_time} ({days_ago}天前, {total_count}条)")
                
                # 7. 问题诊断
                logger.info("🔧 问题诊断:")
                
                if recent_count == 0:
                    logger.error("❌ 最近7天没有新数据，可能存在以下问题:")
                    logger.error("    1. 定时任务未执行")
                    logger.error("    2. Wise API配置错误")
                    logger.error("    3. 汇率同步任务未实现")
                    logger.error("    4. 网络连接问题")
                    return False
                elif recent_count < len(currency_pairs) * 7:
                    logger.warning("⚠️  数据不完整，可能存在以下问题:")
                    logger.warning("    1. 部分币种对同步失败")
                    logger.warning("    2. API限制或错误")
                    logger.warning("    3. 网络连接不稳定")
                    return False
                else:
                    logger.info("✅ 数据同步正常")
                    return True
                
        except Exception as e:
            logger.error(f"❌ 检查失败: {e}")
            return False
    
    def get_data_summary(self):
        """获取数据摘要"""
        try:
            with self.engine.connect() as conn:
                # 获取基本统计信息
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(DISTINCT source_currency || '->' || target_currency) as currency_pairs,
                        MIN(time) as earliest_time,
                        MAX(time) as latest_time,
                        COUNT(DISTINCT DATE(time)) as unique_days
                    FROM wise_exchange_rates
                """))
                
                row = result.fetchone()
                return {
                    'total_records': row.total_records,
                    'currency_pairs': row.currency_pairs,
                    'earliest_time': row.earliest_time,
                    'latest_time': row.latest_time,
                    'unique_days': row.unique_days
                }
                
        except Exception as e:
            logger.error(f"❌ 获取数据摘要失败: {e}")
            return None
    
    def run_maintenance(self):
        """运行维护任务"""
        logger.info("🔧 开始Wise数据维护...")
        
        # 1. 修复序列
        sequence_success = self.fix_exchange_rates_sequence()
        
        # 2. 清理重复记录
        duplicate_success = self.clean_duplicate_records()
        
        # 3. 检查数据状态
        status_success = self.check_data_status()
        
        logger.info("✅ Wise数据维护完成")
        return {
            'sequence_fixed': sequence_success,
            'duplicates_cleaned': duplicate_success,
            'status_checked': status_success
        }


def main():
    """主函数 - 用于命令行执行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Wise数据管理工具')
    parser.add_argument('--action', choices=['check', 'maintenance', 'fix-sequence', 'clean-duplicates'], 
                       default='check', help='执行的操作')
    parser.add_argument('--database-url', help='数据库连接URL')
    
    args = parser.parse_args()
    
    try:
        manager = WiseDataManager(args.database_url)
        
        if args.action == 'check':
            manager.check_data_status()
        elif args.action == 'maintenance':
            manager.run_maintenance()
        elif args.action == 'fix-sequence':
            manager.fix_exchange_rates_sequence()
        elif args.action == 'clean-duplicates':
            manager.clean_duplicate_records()
            
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 