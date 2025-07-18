"""
Web3余额同步任务
"""
from typing import Dict, Any, List
from datetime import datetime
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.web3_api_service import Web3APIService


class Web3BalanceSyncTask(BaseTask):
    """Web3余额同步任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行Web3余额同步"""
        try:
            context.log("开始执行Web3余额同步任务")
            
            # 获取配置参数
            sync_all_accounts = context.get_config('sync_all_accounts', True)
            account_ids = context.get_config('account_ids', [])
            
            # 初始化Web3服务
            web3_service = Web3APIService()
            
            # 验证配置
            if not web3_service._validate_config():
                context.log("Web3 API配置无效", "ERROR")
                return TaskResult(success=False, error="Web3 API配置无效")
            
            # 同步余额数据到数据库
            sync_result = await web3_service.sync_balance_to_db()
            
            if not sync_result.get('success'):
                context.log(f"Web3余额同步失败: {sync_result.get('message', '未知错误')}", "ERROR")
                return TaskResult(success=False, error=sync_result.get('message', '余额同步失败'))
            
            # 获取同步后的余额数据
            balance_data = await web3_service.get_account_balance()
            
            if not balance_data or balance_data.get('code') != '0':
                context.log("获取Web3账户余额失败", "WARNING")
                return TaskResult(success=False, error="获取Web3账户余额失败")
            
            # 处理余额数据
            balance_info = balance_data.get('data', [])
            if not balance_info:
                context.log("Web3账户余额数据为空", "WARNING")
                return TaskResult(success=False, error="Web3账户余额数据为空")
            
            # 获取第一个账户的余额信息
            account_balance = balance_info[0] if balance_info else {}
            
            # 处理余额数据
            processed_balance = {
                'account_id': account_balance.get('acctId', ''),
                'total_balance': account_balance.get('totalBal', '0'),
                'available_balance': account_balance.get('availBal', '0'),
                'frozen_balance': account_balance.get('frozenBal', '0'),
                'currency': 'USD',  # Web3账户通常使用USD
                'sync_time': datetime.now().isoformat()
            }
            
            # 设置运行时变量
            context.set_variable('web3_total_balance', processed_balance['total_balance'])
            context.set_variable('web3_available_balance', processed_balance['available_balance'])
            
            result_data = {
                'balance': processed_balance,
                'total_balance': processed_balance['total_balance'],
                'available_balance': processed_balance['available_balance'],
                'frozen_balance': processed_balance['frozen_balance'],
                'sync_time': datetime.now().isoformat(),
                'sync_result': sync_result
            }
            
            context.log(f"Web3余额同步任务完成，总余额: {processed_balance['total_balance']}")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('web3.balance.synced', result_data)
            
            return TaskResult(
                success=True,
                data=result_data,
                events=['web3.balance.synced']
            )
            
        except Exception as e:
            context.log(f"Web3余额同步任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查参数类型
        if 'sync_all_accounts' in config and not isinstance(config['sync_all_accounts'], bool):
            return False
            
        if 'account_ids' in config and not isinstance(config['account_ids'], list):
            return False
            
        return True 