"""
OKX交易流水同步任务
"""
from typing import Dict, Any
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.okx_api_service import OKXAPIService
from datetime import datetime


class OKXTransactionSyncTask(BaseTask):
    """OKX交易流水同步任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行OKX交易流水同步"""
        try:
            context.log("开始执行OKX交易流水同步任务")
            
            # 获取配置参数
            days = context.get_config('days', 30)
            
            # 初始化OKX服务
            okx_service = OKXAPIService()
            
            # 同步交易流水到数据库
            sync_result = await okx_service.sync_transactions_to_db(days=days)
            
            if not sync_result.get('success'):
                context.log(f"OKX交易流水同步失败: {sync_result.get('message', '未知错误')}", "ERROR")
                return TaskResult(success=False, error=sync_result.get('message', '交易流水同步失败'))
            
            # 获取同步后的流水数量
            synced_count = sync_result.get('synced_count', 0)
            
            result_data = {
                'synced_count': synced_count,
                'message': sync_result.get('message', 'OKX交易流水同步完成'),
                'sync_result': sync_result,
                'sync_time': datetime.now().isoformat(),
                'days': days
            }
            
            context.log(f"OKX交易流水同步任务完成: {result_data['message']}")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('okx.transaction.synced', result_data)
            
            return TaskResult(
                success=True, 
                data=result_data,
                events=['okx.transaction.synced']
            )
            
        except Exception as e:
            context.log(f"OKX交易流水同步任务失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e)) 