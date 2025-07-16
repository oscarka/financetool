"""
Wise交易同步任务
"""
from typing import Dict, Any
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.wise_api_service import WiseAPIService
from datetime import datetime


class WiseTransactionSyncTask(BaseTask):
    """Wise交易同步任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行Wise交易同步"""
        try:
            context.log("开始执行Wise交易同步任务")
            
            # 获取配置参数
            days = context.get_config('days', 30)
            
            # 初始化Wise服务
            wise_service = WiseAPIService()
            
            # 同步交易数据到数据库
            sync_result = await wise_service.sync_all_transactions_to_db(days=days)
            
            if not sync_result.get('success'):
                context.log(f"Wise交易同步失败: {sync_result.get('message', '未知错误')}", "ERROR")
                return TaskResult(success=False, error=sync_result.get('message', '交易同步失败'))
            
            # 获取同步后的交易数据
            transactions = await wise_service.get_recent_transactions(days=days)
            
            result_data = {
                'synced_count': len(transactions) if transactions else 0,
                'message': sync_result.get('message', 'Wise交易同步完成'),
                'sync_result': sync_result,
                'sync_time': datetime.now().isoformat(),
                'days': days
            }
            
            context.log(f"Wise交易同步任务完成: {result_data['message']}")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('wise.transaction.synced', result_data)
            
            return TaskResult(
                success=True, 
                data=result_data,
                events=['wise.transaction.synced']
            )
            
        except Exception as e:
            context.log(f"Wise交易同步任务失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e)) 