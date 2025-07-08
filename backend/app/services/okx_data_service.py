import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from decimal import Decimal

from app.models.database import (
    OKXAccountBalance, OKXPosition, OKXTransaction, 
    OKXMarketData, OKXSyncLog
)
from app.services.okx_api_service import OKXAPIService
from loguru import logger


class OKXDataService:
    """OKX数据管理服务"""
    
    def __init__(self):
        self.api_service = OKXAPIService()
    
    # ==================== 余额数据管理 ====================
    
    def save_account_balance(self, db: Session, balance_data: Dict[str, Any], data_timestamp: datetime = None) -> bool:
        """保存账户余额数据"""
        try:
            if not data_timestamp:
                data_timestamp = datetime.now()
            
            # 解析OKX余额数据格式
            if balance_data.get('code') == '0' and balance_data.get('data'):
                for account in balance_data['data']:
                    for detail in account.get('details', []):
                        currency = detail.get('ccy', '')
                        if not currency:
                            continue
                        
                        # 检查是否已存在相同时间的记录
                        existing = db.query(OKXAccountBalance).filter(
                            and_(
                                OKXAccountBalance.currency == currency,
                                OKXAccountBalance.data_timestamp == data_timestamp
                            )
                        ).first()
                        
                        if existing:
                            # 更新现有记录
                            existing.equity = Decimal(detail.get('eq', '0'))
                            existing.available_balance = Decimal(detail.get('availBal', '0'))
                            existing.frozen_balance = Decimal(detail.get('frozenBal', '0'))
                            existing.position_value = Decimal(detail.get('notionalLever', '0'))
                            existing.unrealized_pnl = Decimal(detail.get('upl', '0'))
                            existing.interest = Decimal(detail.get('interest', '0'))
                            existing.margin_required = Decimal(detail.get('imr', '0'))
                            existing.borrowed = Decimal(detail.get('liab', '0'))
                            existing.updated_at = datetime.now()
                        else:
                            # 创建新记录
                            balance_record = OKXAccountBalance(
                                currency=currency,
                                equity=Decimal(detail.get('eq', '0')),
                                available_balance=Decimal(detail.get('availBal', '0')),
                                frozen_balance=Decimal(detail.get('frozenBal', '0')),
                                position_value=Decimal(detail.get('notionalLever', '0')),
                                unrealized_pnl=Decimal(detail.get('upl', '0')),
                                interest=Decimal(detail.get('interest', '0')),
                                margin_required=Decimal(detail.get('imr', '0')),
                                borrowed=Decimal(detail.get('liab', '0')),
                                data_timestamp=data_timestamp
                            )
                            db.add(balance_record)
                
                db.commit()
                logger.info(f"成功保存OKX账户余额数据，时间: {data_timestamp}")
                return True
            else:
                logger.warning(f"OKX余额数据格式异常: {balance_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX账户余额失败: {e}")
            db.rollback()
            return False
    
    def get_latest_balance(self, db: Session, currency: str = None) -> List[OKXAccountBalance]:
        """获取最新余额数据"""
        try:
            query = db.query(OKXAccountBalance)
            
            if currency:
                query = query.filter(OKXAccountBalance.currency == currency)
            
            # 获取每个币种的最新记录
            subquery = db.query(
                OKXAccountBalance.currency,
                func.max(OKXAccountBalance.data_timestamp).label('latest_time')
            ).group_by(OKXAccountBalance.currency).subquery()
            
            latest_balances = query.join(
                subquery,
                and_(
                    OKXAccountBalance.currency == subquery.c.currency,
                    OKXAccountBalance.data_timestamp == subquery.c.latest_time
                )
            ).all()
            
            return latest_balances
            
        except Exception as e:
            logger.error(f"获取OKX最新余额失败: {e}")
            return []
    
    # ==================== 持仓数据管理 ====================
    
    def save_positions(self, db: Session, position_data: Dict[str, Any], data_timestamp: datetime = None) -> bool:
        """保存持仓数据"""
        try:
            if not data_timestamp:
                data_timestamp = datetime.now()
            
            # 解析OKX持仓数据格式
            if position_data.get('code') == '0' and position_data.get('data'):
                for position in position_data['data']:
                    inst_id = position.get('instId', '')
                    position_side = position.get('posSide', 'long')
                    
                    if not inst_id:
                        continue
                    
                    # 检查是否已存在相同时间的记录
                    existing = db.query(OKXPosition).filter(
                        and_(
                            OKXPosition.inst_id == inst_id,
                            OKXPosition.position_side == position_side,
                            OKXPosition.data_timestamp == data_timestamp
                        )
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.inst_type = position.get('instType', '')
                        existing.currency = position.get('ccy', '')
                        existing.quantity = Decimal(position.get('pos', '0'))
                        existing.available_quantity = Decimal(position.get('availPos', '0'))
                        existing.avg_price = Decimal(position.get('avgPx', '0'))
                        existing.mark_price = Decimal(position.get('markPx', '0'))
                        existing.notional_value = Decimal(position.get('notionalUsd', '0'))
                        existing.unrealized_pnl = Decimal(position.get('upl', '0'))
                        existing.unrealized_pnl_ratio = Decimal(position.get('uplRatio', '0'))
                        existing.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        position_record = OKXPosition(
                            inst_id=inst_id,
                            inst_type=position.get('instType', ''),
                            position_side=position_side,
                            currency=position.get('ccy', ''),
                            quantity=Decimal(position.get('pos', '0')),
                            available_quantity=Decimal(position.get('availPos', '0')),
                            avg_price=Decimal(position.get('avgPx', '0')),
                            mark_price=Decimal(position.get('markPx', '0')),
                            notional_value=Decimal(position.get('notionalUsd', '0')),
                            unrealized_pnl=Decimal(position.get('upl', '0')),
                            unrealized_pnl_ratio=Decimal(position.get('uplRatio', '0')),
                            data_timestamp=data_timestamp
                        )
                        db.add(position_record)
                
                db.commit()
                logger.info(f"成功保存OKX持仓数据，时间: {data_timestamp}")
                return True
            else:
                logger.warning(f"OKX持仓数据格式异常: {position_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX持仓数据失败: {e}")
            db.rollback()
            return False
    
    def get_latest_positions(self, db: Session, inst_id: str = None) -> List[OKXPosition]:
        """获取最新持仓数据"""
        try:
            query = db.query(OKXPosition)
            
            if inst_id:
                query = query.filter(OKXPosition.inst_id == inst_id)
            
            # 获取每个产品的最新记录
            subquery = db.query(
                OKXPosition.inst_id,
                OKXPosition.position_side,
                func.max(OKXPosition.data_timestamp).label('latest_time')
            ).group_by(OKXPosition.inst_id, OKXPosition.position_side).subquery()
            
            latest_positions = query.join(
                subquery,
                and_(
                    OKXPosition.inst_id == subquery.c.inst_id,
                    OKXPosition.position_side == subquery.c.position_side,
                    OKXPosition.data_timestamp == subquery.c.latest_time
                )
            ).filter(OKXPosition.quantity > 0).all()  # 只返回有持仓的记录
            
            return latest_positions
            
        except Exception as e:
            logger.error(f"获取OKX最新持仓失败: {e}")
            return []
    
    # ==================== 交易记录管理 ====================
    
    def save_transactions(self, db: Session, transaction_data: Dict[str, Any]) -> bool:
        """保存交易记录数据"""
        try:
            # 解析OKX交易记录数据格式
            if transaction_data.get('code') == '0' and transaction_data.get('data'):
                new_records = 0
                for transaction in transaction_data['data']:
                    bill_id = transaction.get('billId', '')
                    if not bill_id:
                        continue
                    
                    # 检查是否已存在
                    existing = db.query(OKXTransaction).filter(
                        OKXTransaction.bill_id == bill_id
                    ).first()
                    
                    if not existing:
                        # 创建新记录
                        transaction_record = OKXTransaction(
                            bill_id=bill_id,
                            inst_id=transaction.get('instId', ''),
                            inst_type=transaction.get('instType', ''),
                            currency=transaction.get('ccy', ''),
                            bill_type=transaction.get('type', ''),
                            bill_sub_type=transaction.get('subType', ''),
                            amount=Decimal(transaction.get('balChg', '0')),
                            balance=Decimal(transaction.get('bal', '0')),
                            fee=Decimal(transaction.get('fee', '0')),
                            fill_price=Decimal(transaction.get('fillPx', '0')) if transaction.get('fillPx') and transaction.get('fillPx') != '' else None,
                            fill_quantity=Decimal(transaction.get('fillSz', '0')) if transaction.get('fillSz') and transaction.get('fillSz') != '' else None,
                            trade_id=transaction.get('tradeId', ''),
                            order_id=transaction.get('ordId', ''),
                            bill_time=datetime.fromtimestamp(int(transaction.get('ts', '0')) / 1000)
                        )
                        db.add(transaction_record)
                        new_records += 1
                
                db.commit()
                logger.info(f"成功保存OKX交易记录，新增 {new_records} 条记录")
                return True
            else:
                logger.warning(f"OKX交易记录数据格式异常: {transaction_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX交易记录失败: {e}")
            db.rollback()
            return False
    
    def get_recent_transactions(self, db: Session, days: int = 7, currency: str = None) -> List[OKXTransaction]:
        """获取最近的交易记录"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = db.query(OKXTransaction).filter(
                OKXTransaction.bill_time >= start_date
            )
            
            if currency:
                query = query.filter(OKXTransaction.currency == currency)
            
            transactions = query.order_by(desc(OKXTransaction.bill_time)).all()
            return transactions
            
        except Exception as e:
            logger.error(f"获取OKX最近交易记录失败: {e}")
            return []
    
    # ==================== 行情数据管理 ====================
    
    def save_market_data(self, db: Session, market_data: Dict[str, Any], data_timestamp: datetime = None) -> bool:
        """保存行情数据"""
        try:
            if not data_timestamp:
                data_timestamp = datetime.now()
            
            # 解析OKX行情数据格式
            if market_data.get('code') == '0' and market_data.get('data'):
                for ticker in market_data['data']:
                    inst_id = ticker.get('instId', '')
                    if not inst_id:
                        continue
                    
                    # 检查是否已存在相同时间的记录
                    existing = db.query(OKXMarketData).filter(
                        and_(
                            OKXMarketData.inst_id == inst_id,
                            OKXMarketData.data_timestamp == data_timestamp
                        )
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.inst_type = ticker.get('instType', '')
                        existing.last_price = Decimal(ticker.get('last', '0'))
                        existing.best_bid = Decimal(ticker.get('bidPx', '0'))
                        existing.best_ask = Decimal(ticker.get('askPx', '0'))
                        existing.open_24h = Decimal(ticker.get('open24h', '0'))
                        existing.high_24h = Decimal(ticker.get('high24h', '0'))
                        existing.low_24h = Decimal(ticker.get('low24h', '0'))
                        existing.volume_24h = Decimal(ticker.get('vol24h', '0'))
                        existing.volume_currency_24h = Decimal(ticker.get('volCcy24h', '0'))
                        existing.change_24h = Decimal(ticker.get('chgPct', '0'))
                    else:
                        # 创建新记录
                        market_record = OKXMarketData(
                            inst_id=inst_id,
                            inst_type=ticker.get('instType', ''),
                            last_price=Decimal(ticker.get('last', '0')),
                            best_bid=Decimal(ticker.get('bidPx', '0')),
                            best_ask=Decimal(ticker.get('askPx', '0')),
                            open_24h=Decimal(ticker.get('open24h', '0')),
                            high_24h=Decimal(ticker.get('high24h', '0')),
                            low_24h=Decimal(ticker.get('low24h', '0')),
                            volume_24h=Decimal(ticker.get('vol24h', '0')),
                            volume_currency_24h=Decimal(ticker.get('volCcy24h', '0')),
                            change_24h=Decimal(ticker.get('chgPct', '0')),
                            data_timestamp=data_timestamp
                        )
                        db.add(market_record)
                
                db.commit()
                logger.info(f"成功保存OKX行情数据，时间: {data_timestamp}")
                return True
            else:
                logger.warning(f"OKX行情数据格式异常: {market_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX行情数据失败: {e}")
            db.rollback()
            return False
    
    def get_latest_market_data(self, db: Session, inst_id: str = None) -> List[OKXMarketData]:
        """获取最新行情数据"""
        try:
            query = db.query(OKXMarketData)
            
            if inst_id:
                query = query.filter(OKXMarketData.inst_id == inst_id)
            
            # 获取每个产品的最新行情
            subquery = db.query(
                OKXMarketData.inst_id,
                func.max(OKXMarketData.data_timestamp).label('latest_time')
            ).group_by(OKXMarketData.inst_id).subquery()
            
            latest_market_data = query.join(
                subquery,
                and_(
                    OKXMarketData.inst_id == subquery.c.inst_id,
                    OKXMarketData.data_timestamp == subquery.c.latest_time
                )
            ).all()
            
            return latest_market_data
            
        except Exception as e:
            logger.error(f"获取OKX最新行情数据失败: {e}")
            return []
    
    # ==================== 同步日志管理 ====================
    
    def create_sync_log(self, db: Session, sync_type: str, sync_params: Dict = None) -> OKXSyncLog:
        """创建同步日志"""
        try:
            sync_log = OKXSyncLog(
                sync_type=sync_type,
                sync_status='running',
                start_time=datetime.now(),
                sync_params=json.dumps(sync_params) if sync_params else None
            )
            db.add(sync_log)
            db.commit()
            return sync_log
        except Exception as e:
            logger.error(f"创建同步日志失败: {e}")
            db.rollback()
            return None
    
    def update_sync_log(self, db: Session, sync_log: OKXSyncLog, status: str, 
                       records_processed: int = 0, records_success: int = 0, 
                       records_failed: int = 0, error_message: str = None):
        """更新同步日志"""
        try:
            sync_log.sync_status = status
            sync_log.end_time = datetime.now()
            sync_log.duration = int((sync_log.end_time - sync_log.start_time).total_seconds())
            sync_log.records_processed = records_processed
            sync_log.records_success = records_success
            sync_log.records_failed = records_failed
            sync_log.error_message = error_message
            db.commit()
        except Exception as e:
            logger.error(f"更新同步日志失败: {e}")
            db.rollback()
    
    def get_sync_logs(self, db: Session, sync_type: str = None, limit: int = 50) -> List[OKXSyncLog]:
        """获取同步日志"""
        try:
            query = db.query(OKXSyncLog)
            
            if sync_type:
                query = query.filter(OKXSyncLog.sync_type == sync_type)
            
            logs = query.order_by(desc(OKXSyncLog.start_time)).limit(limit).all()
            return logs
        except Exception as e:
            logger.error(f"获取同步日志失败: {e}")
            return []
    
    # ==================== 数据同步主方法 ====================
    
    async def sync_all_data(self, db: Session) -> Dict[str, Any]:
        """同步所有OKX数据"""
        results = {
            'balance': False,
            'positions': False,
            'transactions': False,
            'market_data': False,
            'errors': []
        }
        
        # 同步账户余额
        try:
            balance_log = self.create_sync_log(db, 'balance')
            balance_data = await self.api_service.get_account_balance()
            if balance_data:
                success = self.save_account_balance(db, balance_data)
                results['balance'] = success
                self.update_sync_log(db, balance_log, 'success' if success else 'failed')
            else:
                results['errors'].append('获取账户余额失败')
                self.update_sync_log(db, balance_log, 'failed', error_message='获取账户余额失败')
        except Exception as e:
            results['errors'].append(f'同步账户余额异常: {e}')
            logger.error(f"同步账户余额异常: {e}")
        
        # 同步持仓数据
        try:
            position_log = self.create_sync_log(db, 'position')
            position_data = await self.api_service.get_account_positions()
            if position_data:
                success = self.save_positions(db, position_data)
                results['positions'] = success
                self.update_sync_log(db, position_log, 'success' if success else 'failed')
            else:
                results['errors'].append('获取持仓数据失败')
                self.update_sync_log(db, position_log, 'failed', error_message='获取持仓数据失败')
        except Exception as e:
            results['errors'].append(f'同步持仓数据异常: {e}')
            logger.error(f"同步持仓数据异常: {e}")
        
        # 同步交易记录 (最近100条)
        try:
            transaction_log = self.create_sync_log(db, 'transaction', {'limit': 100})
            transaction_data = await self.api_service.get_bills(limit=100)
            if transaction_data:
                success = self.save_transactions(db, transaction_data)
                results['transactions'] = success
                self.update_sync_log(db, transaction_log, 'success' if success else 'failed')
            else:
                results['errors'].append('获取交易记录失败')
                self.update_sync_log(db, transaction_log, 'failed', error_message='获取交易记录失败')
        except Exception as e:
            results['errors'].append(f'同步交易记录异常: {e}')
            logger.error(f"同步交易记录异常: {e}")
        
        # 同步行情数据 (主要币种)
        try:
            market_log = self.create_sync_log(db, 'market', {'inst_type': 'SPOT'})
            market_data = await self.api_service.get_all_tickers('SPOT')
            if market_data:
                success = self.save_market_data(db, market_data)
                results['market_data'] = success
                self.update_sync_log(db, market_log, 'success' if success else 'failed')
            else:
                results['errors'].append('获取行情数据失败')
                self.update_sync_log(db, market_log, 'failed', error_message='获取行情数据失败')
        except Exception as e:
            results['errors'].append(f'同步行情数据异常: {e}')
            logger.error(f"同步行情数据异常: {e}")
        
        return results