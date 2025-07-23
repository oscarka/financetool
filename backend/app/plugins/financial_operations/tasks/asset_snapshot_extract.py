from app.services.asset_snapshot_service import extract_asset_snapshot
from app.core.base_plugin import BaseTask
from app.core.database import get_db
from datetime import datetime

class AssetSnapshotExtractTask(BaseTask):
    task_id = "asset_snapshot_extract"
    name = "资产快照抽取"
    description = "定期抽取资产快照，支持多基准货币冗余"

    def run(self, config=None):
        db = next(get_db())
        try:
            extract_asset_snapshot(db, snapshot_time=datetime.now())
            self.logger.info("资产快照抽取成功")
            return {"success": True}
        except Exception as e:
            self.logger.error(f"资产快照抽取失败: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()