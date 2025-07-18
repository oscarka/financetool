"""
金融操作插件 - 整合所有金融服务
"""
from typing import Dict, Any, List
from app.core.base_plugin import BaseTaskPlugin


class FinancialOperationsPlugin(BaseTaskPlugin):
    """金融操作插件 - 整合基金、Wise、OKX、IBKR等金融服务"""
    
    def __init__(self):
        super().__init__()
        self.plugin_id = "financial_operations"
        self.plugin_name = "金融操作插件"
        self.version = "1.0.0"
        self.description = "整合基金、Wise、OKX、IBKR等金融服务的定时任务"
        self.author = "FinanceTool Team"
        
    async def register_tasks(self) -> List[Dict[str, Any]]:
        """注册任务"""
        return [
            # 基金相关任务
            {
                "task_id": "fund_nav_update",
                "name": "基金净值更新",
                "description": "更新持仓基金的净值信息",
                "class": "app.plugins.financial_operations.tasks.fund_nav_update.FundNavUpdateTask"
            },
            {
                "task_id": "dca_execute",
                "name": "定投计划执行",
                "description": "执行到期的定投计划",
                "class": "app.plugins.financial_operations.tasks.dca_execute.DCAExecuteTask"
            },
            {
                "task_id": "fund_position_sync",
                "name": "基金持仓同步",
                "description": "同步基金持仓数据",
                "class": "app.plugins.financial_operations.tasks.fund_position_sync.FundPositionSyncTask"
            },
            
            # Wise相关任务
            {
                "task_id": "wise_balance_sync",
                "name": "Wise余额同步",
                "description": "同步Wise账户余额信息",
                "class": "app.plugins.financial_operations.tasks.wise_balance_sync.WiseBalanceSyncTask"
            },
            {
                "task_id": "wise_transaction_sync",
                "name": "Wise交易同步",
                "description": "同步Wise交易记录",
                "class": "app.plugins.financial_operations.tasks.wise_transaction_sync.WiseTransactionSyncTask"
            },
            {
                "task_id": "wise_exchange_rate_sync",
                "name": "Wise汇率同步",
                "description": "同步Wise汇率数据",
                "class": "app.plugins.financial_operations.tasks.wise_exchange_rate_sync.WiseExchangeRateSyncTask"
            },
            
            # OKX相关任务
            {
                "task_id": "okx_balance_sync",
                "name": "OKX余额同步",
                "description": "同步OKX账户余额信息",
                "class": "app.plugins.financial_operations.tasks.okx_balance_sync.OKXBalanceSyncTask"
            },
            {
                "task_id": "okx_position_sync",
                "name": "OKX持仓同步",
                "description": "同步OKX持仓信息",
                "class": "app.plugins.financial_operations.tasks.okx_position_sync.OKXPositionSyncTask"
            },
            {
                "task_id": "okx_market_data_sync",
                "name": "OKX市场数据同步",
                "description": "同步OKX市场行情数据",
                "class": "app.plugins.financial_operations.tasks.okx_market_data_sync.OKXMarketDataSyncTask"
            },
            {
                "task_id": "crypto_exchange_rate_cache",
                "name": "数字货币汇率缓存",
                "description": "缓存用户持有的数字货币对USDT汇率",
                "class": "app.plugins.financial_operations.tasks.crypto_exchange_rate_cache.CryptoExchangeRateCacheTask"
            },
            
            # IBKR相关任务
            {
                "task_id": "ibkr_balance_sync",
                "name": "IBKR余额同步",
                "description": "同步IBKR账户余额信息",
                "class": "app.plugins.financial_operations.tasks.ibkr_balance_sync.IBKRBalanceSyncTask"
            },
            {
                "task_id": "ibkr_position_sync",
                "name": "IBKR持仓同步",
                "description": "同步IBKR持仓信息",
                "class": "app.plugins.financial_operations.tasks.ibkr_position_sync.IBKRPositionSyncTask"
            },
            
            # 数据处理任务
            {
                "task_id": "data_cleanup",
                "name": "数据清理",
                "description": "清理过期和无效数据",
                "class": "app.plugins.financial_operations.tasks.data_cleanup.DataCleanupTask"
            },
            {
                "task_id": "data_backup",
                "name": "数据备份",
                "description": "备份重要数据",
                "class": "app.plugins.financial_operations.tasks.data_backup.DataBackupTask"
            },
            {
                "task_id": "report_generation",
                "name": "报表生成",
                "description": "生成投资报表",
                "class": "app.plugins.financial_operations.tasks.report_generation.ReportGenerationTask"
            }
        ] 