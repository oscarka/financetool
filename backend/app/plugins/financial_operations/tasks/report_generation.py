"""报表生成任务"""
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult

class ReportGenerationTask(BaseTask):
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        try:
            context.log("开始执行报表生成任务")
            return TaskResult(success=True, data={'message': '报表生成功能待实现'})
        except Exception as e:
            return TaskResult(success=False, error=str(e)) 