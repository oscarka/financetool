"""
测试可扩展调度器
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.extensible_scheduler_service import ExtensibleSchedulerService
from app.config.scheduler_examples import FUND_NAV_UPDATE_CONFIG, WISE_BALANCE_SYNC_CONFIG


async def test_scheduler():
    """测试调度器功能"""
    print("🚀 开始测试可扩展调度器...")
    
    # 创建调度器实例
    scheduler = ExtensibleSchedulerService()
    
    try:
        # 初始化调度器
        print("📦 初始化调度器...")
        await scheduler.initialize()
        
        # 获取插件和任务信息
        print("\n📋 已加载的插件:")
        plugins = scheduler.get_plugins()
        for plugin in plugins:
            print(f"  - {plugin['plugin_name']} (v{plugin['version']})")
        
        print("\n📋 可用的任务:")
        tasks = scheduler.get_tasks()
        for task in tasks:
            print(f"  - {task['name']} ({task['task_id']})")
        
        # 创建测试任务
        print("\n🔧 创建测试任务...")
        job_id = await scheduler.create_job(FUND_NAV_UPDATE_CONFIG)
        print(f"  基金净值更新任务已创建: {job_id}")
        
        # 获取所有任务
        print("\n📋 当前定时任务:")
        jobs = scheduler.get_jobs()
        for job in jobs:
            print(f"  - {job['name']} (下次执行: {job['next_run_time']})")
        
        # 测试立即执行任务
        print("\n⚡ 测试立即执行任务...")
        result = await scheduler.execute_task_now("fund_nav_update", {
            "update_all": False,
            "fund_codes": ["000001"]
        })
        
        if result.success:
            print(f"  ✅ 任务执行成功: {result.data}")
        else:
            print(f"  ❌ 任务执行失败: {result.error}")
        
        # 测试事件系统
        print("\n📡 测试事件系统...")
        events = scheduler.event_bus.get_event_history(limit=5)
        print(f"  最近事件数量: {len(events)}")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭调度器
        await scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(test_scheduler()) 