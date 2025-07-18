"""
数字货币汇率缓存任务
"""
from typing import Dict, Any, List
from datetime import datetime
from app.core.base_plugin import BaseTask
from app.core.context import TaskContext, TaskResult
from app.services.okx_api_service import OKXAPIService
from app.models.database import OKXBalance, OKXMarketData
from app.utils.database import SessionLocal
from sqlalchemy import and_


class CryptoExchangeRateCacheTask(BaseTask):
    """数字货币汇率缓存任务"""
    
    def __init__(self, task_id: str, name: str, description: str = ""):
        super().__init__(task_id, name, description)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行数字货币汇率缓存任务"""
        try:
            context.log("开始执行数字货币汇率缓存任务")
            
            # 获取配置参数
            cache_duration = context.get_config('cache_duration', 1800)  # 默认30分钟缓存
            batch_update = context.get_config('batch_update', True)
            
            # 初始化OKX服务
            okx_service = OKXAPIService()
            
            # 验证配置
            if not okx_service._validate_config():
                context.log("OKX API配置无效", "ERROR")
                return TaskResult(success=False, error="OKX API配置无效")
            
            db = SessionLocal()
            try:
                # 1. 获取用户持有的数字货币列表
                user_currencies = self._get_user_crypto_currencies(db)
                context.log(f"获取到用户持有的数字货币: {user_currencies}")
                
                if not user_currencies:
                    context.log("用户未持有任何数字货币，跳过汇率缓存", "WARNING")
                    return TaskResult(success=True, data={'cached_count': 0, 'message': '无数字货币需要缓存'})
                
                # 2. 构建需要查询的币种对（所有币种对USDT）
                currency_pairs = []
                for currency in user_currencies:
                    if currency != 'USDT':  # 跳过USDT本身
                        currency_pairs.append(f"{currency}-USDT")
                
                context.log(f"需要查询的币种对: {currency_pairs}")
                
                # 3. 批量获取汇率数据
                cached_count = 0
                failed_pairs = []
                
                for pair in currency_pairs:
                    try:
                        # 获取行情数据
                        ticker_data = await okx_service.get_ticker(pair)
                        
                        if ticker_data and ticker_data.get('code') == '0' and ticker_data.get('data'):
                            ticker = ticker_data['data'][0]
                            
                            # 提取汇率信息
                            rate_data = {
                                'inst_id': pair,
                                'inst_type': 'SPOT',  # 添加必需的inst_type字段
                                'last_price': float(ticker.get('last', 0)),
                                'bid_price': float(ticker.get('bidPx', 0)),
                                'ask_price': float(ticker.get('askPx', 0)),
                                'high_24h': float(ticker.get('high24h', 0)),
                                'low_24h': float(ticker.get('low24h', 0)),
                                'volume_24h': float(ticker.get('vol24h', 0)),
                                'timestamp': datetime.now()
                            }
                            
                            # 保存到数据库
                            success = self._save_market_data(db, rate_data)
                            if success:
                                cached_count += 1
                                context.log(f"成功缓存 {pair} 汇率: {rate_data['last_price']}")
                                
                                # 设置运行时变量
                                context.set_variable(f'crypto_rate_{pair}', rate_data['last_price'])
                            else:
                                failed_pairs.append(pair)
                                context.log(f"保存 {pair} 汇率到数据库失败", "WARNING")
                        else:
                            failed_pairs.append(pair)
                            context.log(f"获取 {pair} 行情数据失败", "WARNING")
                            
                    except Exception as e:
                        failed_pairs.append(pair)
                        context.log(f"处理 {pair} 汇率时出错: {e}", "ERROR")
                
                # 4. 清理过期缓存数据
                cleaned_count = self._cleanup_expired_cache(db, cache_duration)
                
                result_data = {
                    'cached_count': cached_count,
                    'total_pairs': len(currency_pairs),
                    'failed_pairs': failed_pairs,
                    'cleaned_count': cleaned_count,
                    'user_currencies': user_currencies,
                    'cache_duration': cache_duration,
                    'sync_time': datetime.now().isoformat()
                }
                
                context.log(f"数字货币汇率缓存任务完成，成功缓存 {cached_count}/{len(currency_pairs)} 个币种对，清理 {cleaned_count} 条过期数据")
                
                # 发布事件
                if context.event_bus:
                    await context.event_bus.publish('crypto.exchange_rate.cached', result_data)
                
                return TaskResult(
                    success=True,
                    data=result_data,
                    events=['crypto.exchange_rate.cached']
                )
                
            finally:
                db.close()
                
        except Exception as e:
            context.log(f"数字货币汇率缓存任务执行失败: {e}", "ERROR")
            return TaskResult(success=False, error=str(e))
    
    def _get_user_crypto_currencies(self, db) -> List[str]:
        """获取用户持有的数字货币列表"""
        try:
            # 从OKX余额表获取用户持有的币种
            balances = db.query(OKXBalance).filter(
                OKXBalance.total_balance > 0
            ).all()
            
            currencies = set()
            for balance in balances:
                if balance.currency:
                    currencies.add(balance.currency)
            
            # 添加常见的数字货币（如果用户没有持有，也缓存主要币种）
            common_cryptos = ['BTC', 'ETH', 'USDT', 'USDC', 'SOL', 'ADA', 'DOT', 'LINK']
            currencies.update(common_cryptos)
            
            return list(currencies)
            
        except Exception as e:
            # 这里不能使用context.log，因为是在类方法中
            return []
    
    def _save_market_data(self, db, rate_data: Dict[str, Any]) -> bool:
        """保存市场数据到数据库"""
        try:
            # 检查是否已存在相同时间戳的数据
            existing = db.query(OKXMarketData).filter(
                and_(
                    OKXMarketData.inst_id == rate_data['inst_id'],
                    OKXMarketData.inst_type == rate_data['inst_type'],
                    OKXMarketData.timestamp == rate_data['timestamp']
                )
            ).first()
            
            if existing:
                # 更新现有记录
                existing.last_price = rate_data['last_price']
                existing.bid_price = rate_data['bid_price']
                existing.ask_price = rate_data['ask_price']
                existing.high_24h = rate_data['high_24h']
                existing.low_24h = rate_data['low_24h']
                existing.volume_24h = rate_data['volume_24h']
            else:
                # 创建新记录
                market_data = OKXMarketData(**rate_data)
                db.add(market_data)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            # 这里不能使用context.log，因为是在类方法中
            return False
    
    def _cleanup_expired_cache(self, db, cache_duration: int) -> int:
        """清理过期的缓存数据"""
        try:
            from datetime import timedelta
            
            # 计算过期时间
            expire_time = datetime.now() - timedelta(seconds=cache_duration)
            
            # 删除过期数据
            deleted_count = db.query(OKXMarketData).filter(
                OKXMarketData.timestamp < expire_time
            ).delete()
            
            db.commit()
            return deleted_count
            
        except Exception as e:
            db.rollback()
            # 这里不能使用context.log，因为是在类方法中
            return 0 