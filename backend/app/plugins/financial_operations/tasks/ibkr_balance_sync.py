"""
IBKR余额同步任务
"""
from typing import Dict, Any, List
from datetime import datetime
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.ibkr_api_service import IBKRAPIService


class IBKRBalanceSyncTask(BaseTask):
    """IBKR余额同步任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行IBKR余额同步"""
        try:
            context.log("开始执行IBKR余额同步任务")
            
            # 获取配置参数
            account_id = context.get_config('account_id', None)
            sync_positions = context.get_config('sync_positions', True)
            
            # 初始化IBKR服务
            ibkr_service = IBKRAPIService()
            
            # 验证配置
            if not ibkr_service._validate_config():
                context.log("IBKR API配置无效", "ERROR")
                return TaskResult(success=False, error="IBKR API配置无效")
            
            # 获取最新余额
            balances = await ibkr_service.get_latest_balances(account_id)
            
            if not balances:
                context.log("获取IBKR余额失败", "WARNING")
                return TaskResult(success=False, error="获取IBKR余额失败")
            
            # 处理余额数据
            processed_balances = []
            total_net_liquidation = 0
            total_cash = 0
            
            for balance in balances:
                balance_info = {
                    'account_id': balance['account_id'],
                    'total_cash': float(balance['total_cash']),
                    'net_liquidation': float(balance['net_liquidation']),
                    'buying_power': float(balance['buying_power']),
                    'currency': balance['currency'],
                    'snapshot_date': balance['snapshot_date'],
                    'snapshot_time': balance['snapshot_time'],
                    'sync_time': datetime.now().isoformat()
                }
                processed_balances.append(balance_info)
                total_net_liquidation += balance_info['net_liquidation']
                total_cash += balance_info['total_cash']
                
                # 设置运行时变量
                context.set_variable(f'ibkr_balance_{balance["currency"]}', balance_info['total_cash'])
            
            # 获取持仓信息（如果需要）
            positions_data = None
            if sync_positions:
                positions_data = await ibkr_service.get_latest_positions(account_id)
            
            # 处理持仓数据
            processed_positions = []
            if positions_data:
                for position in positions_data:
                    position_info = {
                        'account_id': position['account_id'],
                        'symbol': position['symbol'],
                        'quantity': float(position['quantity']),
                        'market_value': float(position['market_value']),
                        'average_cost': float(position['average_cost']),
                        'unrealized_pnl': float(position.get('unrealized_pnl', 0)),
                        'realized_pnl': float(position.get('realized_pnl', 0)),
                        'currency': position['currency'],
                        'asset_class': position.get('asset_class', 'STK'),
                        'snapshot_date': position['snapshot_date'],
                        'snapshot_time': position['snapshot_time'],
                        'sync_time': datetime.now().isoformat()
                    }
                    processed_positions.append(position_info)
            
            result_data = {
                'balances': processed_balances,
                'positions': processed_positions,
                'total_net_liquidation': total_net_liquidation,
                'total_cash': total_cash,
                'account_count': len(set(b['account_id'] for b in processed_balances)),
                'position_count': len(processed_positions),
                'sync_time': datetime.now().isoformat()
            }
            
            context.log(f"IBKR余额同步任务完成，同步了 {len(processed_balances)} 个账户余额，{len(processed_positions)} 个持仓")
            
            # 发布事件
            if context.event_bus:
                await context.event_bus.publish('ibkr.balance.synced', result_data)
            
            return TaskResult(
                success=True,
                data=result_data,
                events=['ibkr.balance.synced']
            )
            
        except Exception as e:
            context.log(f"IBKR余额同步任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
            
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查参数类型
        if 'sync_positions' in config and not isinstance(config['sync_positions'], bool):
            return False
            
        if 'account_id' in config and not isinstance(config['account_id'], str):
            return False
            
        return True 