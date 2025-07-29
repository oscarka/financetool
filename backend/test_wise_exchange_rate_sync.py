#!/usr/bin/env python3
"""
测试Wise汇率同步功能
"""

import os
import asyncio
import sys
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ.setdefault('DATABASE_URL', 'postgresql://financetool_user:financetool_pass@localhost:5432/financetool_test')

async def test_wise_exchange_rate_sync():
    """测试Wise汇率同步"""
    try:
        print("🧪 开始测试Wise汇率同步功能...")
        print("=" * 60)
        
        # 导入必要的模块
        from app.plugins.financial_operations.tasks.wise_exchange_rate_sync import WiseExchangeRateSyncTask
        from app.core.context import TaskContext
        
        # 创建任务实例
        task = WiseExchangeRateSyncTask(
            task_id="test_wise_exchange_rate_sync",
            name="测试Wise汇率同步",
            description="手动测试Wise汇率同步功能"
        )
        
        # 创建任务上下文
        context = TaskContext(
            task_id="test_wise_exchange_rate_sync",
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
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_exchange_rate_service():
    """测试汇率服务"""
    try:
        print("\n🧪 测试汇率服务...")
        print("=" * 40)
        
        from app.services.wise_api_service import WiseAPIService
        from app.services.exchange_rate_service import ExchangeRateService
        
        # 初始化服务
        wise_service = WiseAPIService()
        exchange_service = ExchangeRateService(wise_service.api_token)
        
        # 测试币种对生成
        currencies = ['USD', 'CNY', 'AUD']
        currency_pairs = exchange_service._generate_currency_pairs(currencies)
        print(f"📈 生成的币种对: {currency_pairs}")
        
        # 测试API连接
        print("\n🔗 测试Wise API连接...")
        test_rates = await exchange_service._fetch_rates('USD', 'CNY', 7, 'day')
        print(f"📊 获取到 {len(test_rates)} 条测试数据")
        
        if test_rates:
            print(f"📅 最新汇率: {test_rates[-1] if test_rates else '无数据'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 汇率服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🎯 Wise汇率同步功能测试")
    print("=" * 60)
    
    # 测试汇率服务
    service_test = await test_exchange_rate_service()
    
    if service_test:
        # 测试完整任务
        task_test = await test_wise_exchange_rate_sync()
        
        if task_test and task_test.success:
            print("\n🎉 所有测试通过!")
        else:
            print("\n⚠️  任务测试失败，请检查配置和网络连接")
    else:
        print("\n❌ 服务测试失败，请检查API配置")

if __name__ == "__main__":
    asyncio.run(main())