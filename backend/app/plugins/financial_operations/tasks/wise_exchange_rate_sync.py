"""Wise汇率同步任务"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.wise_api_service import WiseAPIService
from app.services.exchange_rate_service import ExchangeRateService
from app.utils.database import SessionLocal
from app.models.database import WiseBalance, WiseTransaction
from loguru import logger


class WiseExchangeRateSyncTask(BaseTask):
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行Wise汇率同步任务"""
        try:
            context.log("开始执行Wise汇率同步任务")
            
            # 获取配置参数
            days = context.get_config('days', 30)
            currencies = context.get_config('currencies', [])
            
            # 初始化Wise服务
            wise_service = WiseAPIService()
            
            # 如果没有指定币种，从数据库自动获取
            if not currencies:
                context.log("未指定币种，从数据库自动获取持有币种")
                db = SessionLocal()
                try:
                    # 从Wise余额表获取币种
                    balance_currencies = set()
                    for balance in db.query(WiseBalance).all():
                        if balance.currency:
                            balance_currencies.add(balance.currency)
                    
                    # 从Wise交易表获取币种
                    transaction_currencies = set()
                    for transaction in db.query(WiseTransaction).all():
                        if transaction.currency:
                            transaction_currencies.add(transaction.currency)
                    
                    # 合并所有币种
                    currencies = list(balance_currencies | transaction_currencies)
                    context.log(f"从数据库获取到币种: {currencies}")
                    
                except Exception as e:
                    context.log(f"获取数据库币种失败: {e}", "ERROR")
                    # 使用默认币种
                    currencies = ['USD', 'CNY', 'AUD', 'HKD', 'JPY', 'EUR', 'GBP']
                    context.log(f"使用默认币种: {currencies}")
                finally:
                    db.close()
            
            if not currencies:
                context.log("没有可用的币种进行汇率同步", "WARNING")
                return TaskResult(success=False, error="没有可用的币种")
            
            # 初始化汇率服务
            exchange_service = ExchangeRateService(wise_service.api_token)
            
            # 使用增量同步方法，避免重复获取历史数据
            sync_result = await exchange_service.fetch_and_store_history_incremental(
                currencies=currencies,
                group='day'
            )
            
            if not sync_result.get('success', False):
                context.log(f"Wise汇率同步失败: {sync_result.get('message', '未知错误')}", "ERROR")
                return TaskResult(success=False, error=sync_result.get('message', '汇率同步失败'))
            
            # 获取同步结果统计
            total_inserted = sync_result.get('total_inserted', 0)
            total_updated = sync_result.get('total_updated', 0)
            total_processed = sync_result.get('total_processed', 0)
            
            result_data = {
                'currencies': currencies,
                'days': days,
                'total_inserted': total_inserted,
                'total_updated': total_updated,
                'total_processed': total_processed,
                'sync_time': datetime.now().isoformat(),
                'message': f'Wise汇率同步完成，处理了{len(currencies)}个币种，新增{total_inserted}条，更新{total_updated}条记录'
            }
            
            context.log(f"Wise汇率同步任务完成: {result_data['message']}")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('wise.exchange_rate.synced', result_data)
            
            return TaskResult(
                success=True,
                data=result_data,
                events=['wise.exchange_rate.synced']
            )
            
        except Exception as e:
            context.log(f"Wise汇率同步任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查参数类型
        if 'days' in config and not isinstance(config['days'], int):
            return False
            
        if 'currencies' in config and not isinstance(config['currencies'], list):
            return False
            
        return True 