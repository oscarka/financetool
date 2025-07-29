#!/usr/bin/env python3
"""
使用实际API token测试Wise汇率同步功能
"""

import os
import asyncio
import sys
from datetime import datetime
import uuid

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ.setdefault('DATABASE_URL', 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test')
os.environ['WISE_API_TOKEN'] = '77d8e168-a2e9-46f1-80e8-853bd5026d58'

async def test_wise_api_connection():
    """测试Wise API连接"""
    try:
        print("🔗 测试Wise API连接...")
        print("=" * 40)
        
        from app.services.wise_api_service import WiseAPIService
        from app.services.exchange_rate_service import ExchangeRateService
        
        # 初始化服务
        wise_service = WiseAPIService()
        print(f"✅ Wise API初始化成功，Token: {wise_service.api_token[:10]}...")
        
        # 测试API连接
        print("\n📡 测试API连接...")
        test_result = await wise_service.test_connection()
        print(f"🔍 连接测试结果: {test_result}")
        
        # 测试汇率服务
        exchange_service = ExchangeRateService(wise_service.api_token)
        
        # 测试获取汇率数据
        print("\n📊 测试获取汇率数据...")
        test_rates = await exchange_service._fetch_rates('USD', 'CNY', 7, 'day')
        print(f"📈 获取到 {len(test_rates)} 条汇率数据")
        
        if test_rates:
            print(f"📅 最新汇率数据: {test_rates[-1] if test_rates else '无数据'}")
            print(f"📅 最早汇率数据: {test_rates[0] if test_rates else '无数据'}")
        
        return True
        
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_exchange_rate_sync():
    """测试汇率同步功能"""
    try:
        print("\n🧪 测试汇率同步功能...")
        print("=" * 40)
        
        from app.plugins.financial_operations.tasks.wise_exchange_rate_sync import WiseExchangeRateSyncTask
        from app.core.context import TaskContext
        
        # 创建任务实例
        task = WiseExchangeRateSyncTask(
            task_id="test_wise_exchange_rate_sync",
            name="测试Wise汇率同步",
            description="使用实际API token测试汇率同步"
        )
        
        # 创建任务上下文
        context = TaskContext(
            job_id="test_wise_exchange_rate_sync",
            execution_id=str(uuid.uuid4()),
            config={
                'days': 30,
                'currencies': ['USD', 'CNY', 'AUD', 'HKD', 'JPY', 'EUR', 'GBP']
            }
        )
        
        print("📋 任务配置:")
        print(f"  任务ID: {task.task_id}")
        print(f"  任务名称: {task.name}")
        print(f"  同步天数: {context.get_config('days')}")
        print(f"  币种列表: {context.get_config('currencies')}")
        
        # 执行任务
        print("\n🚀 开始执行汇率同步任务...")
        start_time = datetime.now()
        
        result = await task.execute(context)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️  任务执行时间: {duration:.2f}秒")
        
        if result.success:
            print("✅ 任务执行成功!")
            print(f"📊 执行结果: {result.data}")
        else:
            print("❌ 任务执行失败!")
            print(f"🔍 错误信息: {result.error}")
        
        return result
        
    except Exception as e:
        print(f"❌ 汇率同步测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def check_database_after_sync():
    """同步后检查数据库"""
    try:
        print("\n🔍 检查同步后的数据库状态...")
        print("=" * 40)
        
        from sqlalchemy import create_engine, text
        
        engine = create_engine(os.environ['DATABASE_URL'])
        
        with engine.connect() as conn:
            # 检查总记录数
            result = conn.execute(text("SELECT COUNT(*) FROM wise_exchange_rates"))
            total_count = result.scalar()
            print(f"📊 总记录数: {total_count}")
            
            if total_count > 0:
                # 检查币种对分布
                result = conn.execute(text("""
                    SELECT source_currency, target_currency, COUNT(*) as count
                    FROM wise_exchange_rates 
                    GROUP BY source_currency, target_currency
                    ORDER BY count DESC
                """))
                
                print("\n📈 币种对分布:")
                for row in result:
                    print(f"  {row.source_currency}->{row.target_currency}: {row.count} 条")
                
                # 检查最新记录
                result = conn.execute(text("""
                    SELECT source_currency, target_currency, MAX(time) as latest_time
                    FROM wise_exchange_rates 
                    GROUP BY source_currency, target_currency
                    ORDER BY latest_time DESC
                """))
                
                print("\n📅 各币种对最新记录:")
                for row in result:
                    days_ago = (datetime.now() - row.latest_time).days
                    print(f"  {row.source_currency}->{row.target_currency}: {row.latest_time} ({days_ago}天前)")
            else:
                print("❌ 数据库中没有汇率数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🎯 Wise汇率同步功能测试 (使用实际API Token)")
    print("=" * 60)
    
    # 测试API连接
    api_test = await test_wise_api_connection()
    
    if api_test:
        # 测试汇率同步
        sync_test = await test_exchange_rate_sync()
        
        if sync_test and sync_test.success:
            # 检查数据库
            db_check = await check_database_after_sync()
            
            if db_check:
                print("\n🎉 所有测试通过! Wise汇率同步功能正常工作!")
            else:
                print("\n⚠️  数据库检查失败，但同步功能可能正常")
        else:
            print("\n❌ 汇率同步测试失败")
    else:
        print("\n❌ API连接测试失败，请检查网络和API配置")

if __name__ == "__main__":
    asyncio.run(main())