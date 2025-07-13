"""
Wise余额同步任务
"""
from typing import Dict, Any, List
from datetime import datetime
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.wise_api_service import WiseAPIService


class WiseBalanceSyncTask(BaseTask):
    """Wise余额同步任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行Wise余额同步"""
        try:
            context.log("开始执行Wise余额同步任务")
            
            # 获取配置参数
            sync_all_accounts = context.get_config('sync_all_accounts', True)
            account_ids = context.get_config('account_ids', [])
            currencies = context.get_config('currencies', [])
            
            # 初始化Wise服务
            wise_service = WiseAPIService()
            
            # 同步账户余额
            balances = await wise_service.get_all_account_balances()
            
            if not balances:
                context.log("获取Wise账户余额失败", "WARNING")
                return TaskResult(success=False, error="获取Wise账户余额失败")
            
            # 过滤账户
            filtered_balances = balances
            if not sync_all_accounts and account_ids:
                filtered_balances = [b for b in balances if b['account_id'] in account_ids]
            
            # 过滤币种
            if currencies:
                filtered_balances = [b for b in filtered_balances if b['currency'] in currencies]
            
            context.log(f"成功获取Wise账户余额，共 {len(filtered_balances)} 个账户")
            
            # 处理余额数据
            processed_balances = []
            for balance in filtered_balances:
                processed_balance = {
                    'account_id': balance['account_id'],
                    'currency': balance['currency'],
                    'available_balance': balance['available_balance'],
                    'reserved_balance': balance['reserved_balance'],
                    'total_worth': balance['total_worth'],
                    'type': balance['type'],
                    'name': balance.get('name'),
                    'sync_time': datetime.now().isoformat()
                }
                processed_balances.append(processed_balance)
                
                # 设置运行时变量
                context.set_variable(f'wise_balance_{balance["currency"]}', balance['available_balance'])
            
            # 计算汇总信息
            total_balance = sum(b['available_balance'] for b in filtered_balances)
            currency_count = len(set(b['currency'] for b in filtered_balances))
            
            result_data = {
                'balances': processed_balances,
                'total_balance': total_balance,
                'currency_count': currency_count,
                'account_count': len(filtered_balances),
                'sync_time': datetime.now().isoformat()
            }
            
            context.log(f"Wise余额同步任务完成，同步了 {len(filtered_balances)} 个账户")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('wise.balance.synced', result_data)
            
            return TaskResult(
                success=True,
                data=result_data,
                events=['wise.balance.synced']
            )
            
        except Exception as e:
            context.log(f"Wise余额同步任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查参数类型
        if 'sync_all_accounts' in config and not isinstance(config['sync_all_accounts'], bool):
            return False
            
        if 'account_ids' in config and not isinstance(config['account_ids'], list):
            return False
            
        if 'currencies' in config and not isinstance(config['currencies'], list):
            return False
            
        return True 