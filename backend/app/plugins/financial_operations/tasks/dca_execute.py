"""
定投计划执行任务
"""
from typing import Dict, Any
from datetime import date
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.fund_service import DCAService
from app.utils.database import get_db


class DCAExecuteTask(BaseTask):
    """定投计划执行任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行定投计划"""
        try:
            context.log("开始执行定投计划任务")
            
            # 获取配置参数
            dry_run = context.get_config('dry_run', False)
            plan_ids = context.get_config('plan_ids', [])
            
            db = next(get_db())
            
            try:
                # 检查并执行到期的定投计划
                if dry_run:
                    context.log("试运行模式：只检查不执行")
                    # 在试运行模式下，只检查计划状态
                    all_plans = DCAService.get_dca_plans(db, status="active")
                    context.log(f"找到 {len(all_plans)} 个活跃的定投计划")
                    
                    result_data = {
                        'executed_count': 0,
                        'total_count': len(all_plans),
                        'failed_plans': [],
                        'dry_run': True
                    }
                else:
                    # 实际执行定投计划
                    executed_operations = DCAService.check_and_execute_dca_plans(db)
                    
                    context.log(f"执行了 {len(executed_operations)} 个定投操作")
                    
                    result_data = {
                        'executed_count': len(executed_operations),
                        'total_count': len(executed_operations),
                        'failed_plans': [],
                        'dry_run': False,
                        'operations': [
                            {
                                'id': op.id,
                                'operation_type': op.operation_type,
                                'asset_code': op.asset_code,
                                'amount': float(op.amount) if op.amount else 0,
                                'status': op.status
                            } for op in executed_operations
                        ]
                    }
                
                context.log(f"定投计划执行任务完成，成功执行 {result_data['executed_count']} 个操作")
                
                # 提交数据库事务
                try:
                    db.commit()
                    context.log("✅ 数据库事务提交成功")
                except Exception as e:
                    db.rollback()
                    context.log(f"❌ 数据库事务提交失败: {e}", "ERROR")
                    return TaskResult(success=False, error=f"数据库提交失败: {e}")
                
                # 发布事件
                if context.event_bus:
                    await context.event_bus.publish('dca.executed', result_data)
                
                return TaskResult(
                    success=True,
                    data=result_data,
                    events=['dca.executed']
                )
                
            finally:
                db.close()
                
        except Exception as e:
            context.log(f"定投计划执行任务失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查参数类型
        if 'dry_run' in config and not isinstance(config['dry_run'], bool):
            return False
            
        if 'plan_ids' in config and not isinstance(config['plan_ids'], list):
            return False
            
        return True 