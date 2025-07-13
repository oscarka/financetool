"""
定投计划执行任务
"""
from typing import Dict, Any
from datetime import date
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.fund_service import FundOperationService
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
                # 获取到期的定投计划
                today = date.today()
                expired_plans = FundOperationService.get_expired_dca_plans(db, today)
                
                if not expired_plans:
                    context.log("没有到期的定投计划")
                    return TaskResult(success=True, data={'executed_count': 0})
                
                context.log(f"找到 {len(expired_plans)} 个到期的定投计划")
                
                # 执行定投计划
                executed_count = 0
                failed_plans = []
                
                for plan in expired_plans:
                    try:
                        if dry_run:
                            context.log(f"试运行: 执行定投计划 {plan.id}")
                            executed_count += 1
                        else:
                            # 实际执行定投
                            success = FundOperationService.execute_dca_plan(db, plan.id)
                            if success:
                                executed_count += 1
                                context.log(f"成功执行定投计划 {plan.id}")
                            else:
                                failed_plans.append(plan.id)
                                context.log(f"执行定投计划 {plan.id} 失败", "WARNING")
                    except Exception as e:
                        failed_plans.append(plan.id)
                        context.log(f"执行定投计划 {plan.id} 时出错: {e}", "ERROR")
                
                result_data = {
                    'executed_count': executed_count,
                    'total_count': len(expired_plans),
                    'failed_plans': failed_plans,
                    'dry_run': dry_run
                }
                
                context.log(f"定投计划执行任务完成，成功执行 {executed_count}/{len(expired_plans)} 个计划")
                
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