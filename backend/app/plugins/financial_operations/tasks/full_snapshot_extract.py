from app.services.asset_snapshot_service import extract_exchange_rate_snapshot, extract_asset_snapshot
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.core.database import get_db
from datetime import datetime

class FullSnapshotExtractTask(BaseTask):
    """全量快照抽取任务（先汇率后资产）"""
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)

    async def execute(self, context: TaskContext) -> TaskResult:
        try:
            context.log("开始执行全量快照任务（汇率+资产）")
            db = next(get_db())
            try:
                extract_exchange_rate_snapshot(db, snapshot_time=datetime.now())
                context.log("汇率快照抽取成功")
                extract_asset_snapshot(db, snapshot_time=datetime.now())
                context.log("资产快照抽取成功")
                return TaskResult(success=True)
            finally:
                db.close()
        except Exception as e:
            context.log(f"全量快照任务失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))

    async def validate_config(self, config):
        # 全量快照任务无需特殊配置
        return True