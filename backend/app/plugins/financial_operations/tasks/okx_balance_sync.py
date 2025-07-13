"""
OKX余额同步任务
"""
from typing import Dict, Any, List
from datetime import datetime
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.okx_api_service import OKXAPIService


class OKXBalanceSyncTask(BaseTask):
    """OKX余额同步任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行OKX余额同步"""
        try:
            context.log("开始执行OKX余额同步任务")
            
            # 获取配置参数
            sync_positions = context.get_config('sync_positions', True)
            inst_types = context.get_config('inst_types', ['SPOT', 'MARGIN'])
            
            # 初始化OKX服务
            okx_service = OKXAPIService()
            
            # 验证配置
            if not okx_service._validate_config():
                context.log("OKX API配置无效", "ERROR")
                return TaskResult(success=False, error="OKX API配置无效")
            
            # 获取账户余额
            balance_data = await okx_service.get_account_balance()
            
            if not balance_data:
                context.log("获取OKX账户余额失败", "WARNING")
                return TaskResult(success=False, error="获取OKX账户余额失败")
            
            # 处理余额数据
            processed_balances = []
            total_balance = 0
            
            if 'data' in balance_data:
                for account in balance_data['data']:
                    for detail in account.get('details', []):
                        balance_info = {
                            'currency': detail.get('ccy'),
                            'available_balance': float(detail.get('availBal', 0)),
                            'frozen_balance': float(detail.get('frozenBal', 0)),
                            'total_balance': float(detail.get('bal', 0)),
                            'account_type': account.get('acctId'),
                            'sync_time': datetime.now().isoformat()
                        }
                        processed_balances.append(balance_info)
                        total_balance += balance_info['available_balance']
                        
                        # 设置运行时变量
                        context.set_variable(f'okx_balance_{detail.get("ccy")}', balance_info['available_balance'])
            
            # 获取持仓信息（如果需要）
            positions_data = None
            if sync_positions:
                positions_data = await okx_service.get_account_positions()
            
            # 处理持仓数据
            processed_positions = []
            if positions_data and 'data' in positions_data:
                for position in positions_data['data']:
                    if float(position.get('pos', 0)) != 0:  # 只处理有持仓的
                        position_info = {
                            'instrument_id': position.get('instId'),
                            'position_side': position.get('posSide'),
                            'position_size': float(position.get('pos', 0)),
                            'market_value': float(position.get('markPx', 0)),
                            'unrealized_pnl': float(position.get('upl', 0)),
                            'currency': position.get('ccy'),
                            'sync_time': datetime.now().isoformat()
                        }
                        processed_positions.append(position_info)
            
            result_data = {
                'balances': processed_balances,
                'positions': processed_positions,
                'total_balance': total_balance,
                'currency_count': len(set(b['currency'] for b in processed_balances)),
                'position_count': len(processed_positions),
                'sync_time': datetime.now().isoformat()
            }
            
            context.log(f"OKX余额同步任务完成，同步了 {len(processed_balances)} 个币种余额，{len(processed_positions)} 个持仓")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('okx.balance.synced', result_data)
            
            return TaskResult(
                success=True,
                data=result_data,
                events=['okx.balance.synced']
            )
            
        except Exception as e:
            context.log(f"OKX余额同步任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查参数类型
        if 'sync_positions' in config and not isinstance(config['sync_positions'], bool):
            return False
            
        if 'inst_types' in config and not isinstance(config['inst_types'], list):
            return False
            
        return True 