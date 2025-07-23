from app.services.asset_snapshot_service import extract_exchange_rate_snapshot
from app.core.base_plugin import BaseTask
from app.core.database import get_db
from datetime import datetime

class ExchangeRateSnapshotExtractTask(BaseTask):
    task_id = "exchange_rate_snapshot_extract"
    name = "汇率快照抽取"
    description = "定期抽取汇率快照，支持多基准货币冗余"

    def run(self, config=None):
        db = next(get_db())
        try:
            extract_exchange_rate_snapshot(db, snapshot_time=datetime.now())
            self.logger.info("汇率快照抽取成功")
            return {"success": True}
        except Exception as e:
            self.logger.error(f"汇率快照抽取失败: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()