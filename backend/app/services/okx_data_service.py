import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from decimal import Decimal

from app.models.database import (
    OKXAccountBalance, OKXPosition, OKXTransaction, 
    OKXMarketData, OKXSyncLog, OKXInstrument
)
from app.services.okx_api_service import OKXAPIService
from loguru import logger


class OKXDataService:
    """OKX数据管理服务"""
    
    def __init__(self):
        self.api_service = OKXAPIService()
    
    # ==================== 余额数据管理 ====================
    
    def save_account_balance(self, db: Session, balance_data: Dict[str, Any], account_type: str = "trading", data_timestamp: datetime = None) -> bool:
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
                                OKXAccountBalance.account_type == account_type,
                                OKXAccountBalance.currency == currency,
                                OKXAccountBalance.data_timestamp == data_timestamp
                            )
                        ).first()
                        
                        if existing:
                            # 更新现有记录
                            self._update_balance_record(existing, detail)
                            existing.updated_at = datetime.now()
                        else:
                            # 创建新记录
                            balance_record = self._create_balance_record(detail, account_type, currency, data_timestamp)
                            db.add(balance_record)
                
                db.commit()
                logger.info(f"成功保存OKX账户余额数据，账户类型: {account_type}，时间: {data_timestamp}")
                return True
            else:
                logger.warning(f"OKX余额数据格式异常: {balance_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX账户余额失败: {e}")
            db.rollback()
            return False
    
    def _update_balance_record(self, record: OKXAccountBalance, detail: Dict[str, Any]):
        """更新余额记录"""
        record.equity = Decimal(detail.get('eq', '0'))
        record.available_balance = Decimal(detail.get('availBal', '0'))
        record.frozen_balance = Decimal(detail.get('frozenBal', '0'))
        record.position_value = Decimal(detail.get('notionalLever', '0'))
        record.unrealized_pnl = Decimal(detail.get('upl', '0'))
        record.interest = Decimal(detail.get('interest', '0'))
        record.margin_required = Decimal(detail.get('imr', '0'))
        record.borrowed = Decimal(detail.get('liab', '0'))
        record.cash_amount = Decimal(detail.get('cashBal', '0'))
        record.cross_liab = Decimal(detail.get('crossLiab', '0'))
        record.isolated_liab = Decimal(detail.get('isoLiab', '0'))
        record.margin_ratio = Decimal(detail.get('mgnRatio', '0')) if detail.get('mgnRatio') else None
        record.max_loan = Decimal(detail.get('maxLoan', '0')) if detail.get('maxLoan') else None
        record.strategy_equity = Decimal(detail.get('stgyEq', '0')) if detail.get('stgyEq') else None
        record.spot_in_use = Decimal(detail.get('spotInUseAmt', '0')) if detail.get('spotInUseAmt') else None
    
    def _create_balance_record(self, detail: Dict[str, Any], account_type: str, currency: str, data_timestamp: datetime) -> OKXAccountBalance:
        """创建新的余额记录"""
        return OKXAccountBalance(
            account_type=account_type,
            currency=currency,
            equity=Decimal(detail.get('eq', '0')),
            available_balance=Decimal(detail.get('availBal', '0')),
            frozen_balance=Decimal(detail.get('frozenBal', '0')),
            position_value=Decimal(detail.get('notionalLever', '0')),
            unrealized_pnl=Decimal(detail.get('upl', '0')),
            interest=Decimal(detail.get('interest', '0')),
            margin_required=Decimal(detail.get('imr', '0')),
            borrowed=Decimal(detail.get('liab', '0')),
            cash_amount=Decimal(detail.get('cashBal', '0')),
            cross_liab=Decimal(detail.get('crossLiab', '0')),
            isolated_liab=Decimal(detail.get('isoLiab', '0')),
            margin_ratio=Decimal(detail.get('mgnRatio', '0')) if detail.get('mgnRatio') else None,
            max_loan=Decimal(detail.get('maxLoan', '0')) if detail.get('maxLoan') else None,
            strategy_equity=Decimal(detail.get('stgyEq', '0')) if detail.get('stgyEq') else None,
            spot_in_use=Decimal(detail.get('spotInUseAmt', '0')) if detail.get('spotInUseAmt') else None,
            data_timestamp=data_timestamp
        )
    
    def get_latest_balance(self, db: Session, account_type: str = None, currency: str = None) -> List[OKXAccountBalance]:
        """获取最新余额数据"""
        try:
            query = db.query(OKXAccountBalance)
            
            if account_type:
                query = query.filter(OKXAccountBalance.account_type == account_type)
            if currency:
                query = query.filter(OKXAccountBalance.currency == currency)
            
            # 获取每个账户类型和币种的最新记录
            subquery = db.query(
                OKXAccountBalance.account_type,
                OKXAccountBalance.currency,
                func.max(OKXAccountBalance.data_timestamp).label('latest_time')
            ).group_by(OKXAccountBalance.account_type, OKXAccountBalance.currency).subquery()
            
            latest_balances = query.join(
                subquery,
                and_(
                    OKXAccountBalance.account_type == subquery.c.account_type,
                    OKXAccountBalance.currency == subquery.c.currency,
                    OKXAccountBalance.data_timestamp == subquery.c.latest_time
                )
            ).all()
            
            return latest_balances
            
        except Exception as e:
            logger.error(f"获取OKX最新余额失败: {e}")
            return []
    
    # ==================== 持仓数据管理 ====================
    
    def save_positions(self, db: Session, position_data: Dict[str, Any], account_type: str = "trading", data_timestamp: datetime = None) -> bool:
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
                            OKXPosition.account_type == account_type,
                            OKXPosition.inst_id == inst_id,
                            OKXPosition.position_side == position_side,
                            OKXPosition.data_timestamp == data_timestamp
                        )
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        self._update_position_record(existing, position)
                        existing.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        position_record = self._create_position_record(position, account_type, inst_id, position_side, data_timestamp)
                        db.add(position_record)
                
                db.commit()
                logger.info(f"成功保存OKX持仓数据，账户类型: {account_type}，时间: {data_timestamp}")
                return True
            else:
                logger.warning(f"OKX持仓数据格式异常: {position_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX持仓数据失败: {e}")
            db.rollback()
            return False
    
    def _update_position_record(self, record: OKXPosition, position: Dict[str, Any]):
        """更新持仓记录"""
        record.inst_type = position.get('instType', '')
        record.margin_mode = position.get('mgnMode', '')
        record.currency = position.get('ccy', '')
        record.quantity = Decimal(position.get('pos', '0'))
        record.available_quantity = Decimal(position.get('availPos', '0'))
        record.avg_price = Decimal(position.get('avgPx', '0'))
        record.mark_price = Decimal(position.get('markPx', '0'))
        record.last_price = Decimal(position.get('last', '0')) if position.get('last') else None
        record.notional_value = Decimal(position.get('notionalUsd', '0'))
        record.notional_usd = Decimal(position.get('notionalUsd', '0'))
        record.unrealized_pnl = Decimal(position.get('upl', '0'))
        record.unrealized_pnl_ratio = Decimal(position.get('uplRatio', '0'))
        record.realized_pnl = Decimal(position.get('realizedPnl', '0'))
        record.initial_margin = Decimal(position.get('imr', '0')) if position.get('imr') else None
        record.maintenance_margin = Decimal(position.get('mmr', '0')) if position.get('mmr') else None
        record.margin_ratio = Decimal(position.get('mgnRatio', '0')) if position.get('mgnRatio') else None
        record.delta = Decimal(position.get('delta', '0')) if position.get('delta') else None
        record.gamma = Decimal(position.get('gamma', '0')) if position.get('gamma') else None
        record.theta = Decimal(position.get('theta', '0')) if position.get('theta') else None
        record.vega = Decimal(position.get('vega', '0')) if position.get('vega') else None
        record.leverage = Decimal(position.get('lever', '0')) if position.get('lever') else None
        record.liquidation_price = Decimal(position.get('liqPx', '0')) if position.get('liqPx') else None
    
    def _create_position_record(self, position: Dict[str, Any], account_type: str, inst_id: str, position_side: str, data_timestamp: datetime) -> OKXPosition:
        """创建新的持仓记录"""
        return OKXPosition(
            account_type=account_type,
            inst_id=inst_id,
            inst_type=position.get('instType', ''),
            position_side=position_side,
            margin_mode=position.get('mgnMode', ''),
            currency=position.get('ccy', ''),
            quantity=Decimal(position.get('pos', '0')),
            available_quantity=Decimal(position.get('availPos', '0')),
            avg_price=Decimal(position.get('avgPx', '0')),
            mark_price=Decimal(position.get('markPx', '0')),
            last_price=Decimal(position.get('last', '0')) if position.get('last') else None,
            notional_value=Decimal(position.get('notionalUsd', '0')),
            notional_usd=Decimal(position.get('notionalUsd', '0')),
            unrealized_pnl=Decimal(position.get('upl', '0')),
            unrealized_pnl_ratio=Decimal(position.get('uplRatio', '0')),
            realized_pnl=Decimal(position.get('realizedPnl', '0')),
            initial_margin=Decimal(position.get('imr', '0')) if position.get('imr') else None,
            maintenance_margin=Decimal(position.get('mmr', '0')) if position.get('mmr') else None,
            margin_ratio=Decimal(position.get('mgnRatio', '0')) if position.get('mgnRatio') else None,
            delta=Decimal(position.get('delta', '0')) if position.get('delta') else None,
            gamma=Decimal(position.get('gamma', '0')) if position.get('gamma') else None,
            theta=Decimal(position.get('theta', '0')) if position.get('theta') else None,
            vega=Decimal(position.get('vega', '0')) if position.get('vega') else None,
            leverage=Decimal(position.get('lever', '0')) if position.get('lever') else None,
            liquidation_price=Decimal(position.get('liqPx', '0')) if position.get('liqPx') else None,
            data_timestamp=data_timestamp
        )
    
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
    
    def save_transactions(self, db: Session, transaction_data: Dict[str, Any], account_type: str = "trading") -> bool:
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
                            account_type=account_type,
                            bill_id=bill_id,
                            inst_id=transaction.get('instId', ''),
                            inst_type=transaction.get('instType', ''),
                            currency=transaction.get('ccy', ''),
                            bill_type=transaction.get('type', ''),
                            bill_sub_type=transaction.get('subType', ''),
                            amount=Decimal(transaction.get('balChg', '0')),
                            balance=Decimal(transaction.get('bal', '0')),
                            balance_change=Decimal(transaction.get('balChg', '0')),
                            fee=Decimal(transaction.get('fee', '0')),
                            fill_price=Decimal(transaction.get('fillPx', '0')) if transaction.get('fillPx') and transaction.get('fillPx') != '' else None,
                            fill_quantity=Decimal(transaction.get('fillSz', '0')) if transaction.get('fillSz') and transaction.get('fillSz') != '' else None,
                            trade_id=transaction.get('tradeId', ''),
                            order_id=transaction.get('ordId', ''),
                            client_id=transaction.get('clOrdId', ''),
                            margin_mode=transaction.get('mgnMode', ''),
                            position_side=transaction.get('posSide', ''),
                            interest=Decimal(transaction.get('interest', '0')) if transaction.get('interest') else None,
                            from_account=transaction.get('from', ''),
                            to_account=transaction.get('to', ''),
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
    
    def create_sync_log(self, db: Session, sync_type: str, sync_params: Dict = None, account_type: str = None, inst_type: str = None) -> OKXSyncLog:
        """创建同步日志"""
        try:
            sync_log = OKXSyncLog(
                sync_type=sync_type,
                sync_scope='all' if not account_type and not inst_type else f"{account_type or ''}-{inst_type or ''}",
                account_type=account_type,
                inst_type=inst_type,
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
    
    # ==================== 产品信息管理 ====================
    
    def save_instruments(self, db: Session, instrument_data: Dict[str, Any]) -> bool:
        """保存产品信息数据"""
        try:
            if instrument_data.get('code') == '0' and instrument_data.get('data'):
                new_records = 0
                updated_records = 0
                
                for inst in instrument_data['data']:
                    inst_id = inst.get('instId', '')
                    if not inst_id:
                        continue
                    
                    # 检查是否已存在
                    existing = db.query(OKXInstrument).filter(
                        OKXInstrument.inst_id == inst_id
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        self._update_instrument_record(existing, inst)
                        updated_records += 1
                    else:
                        # 创建新记录
                        instrument_record = self._create_instrument_record(inst)
                        db.add(instrument_record)
                        new_records += 1
                
                db.commit()
                logger.info(f"成功保存OKX产品信息，新增 {new_records} 条，更新 {updated_records} 条")
                return True
            else:
                logger.warning(f"OKX产品信息数据格式异常: {instrument_data}")
                return False
                
        except Exception as e:
            logger.error(f"保存OKX产品信息失败: {e}")
            db.rollback()
            return False
    
    def _update_instrument_record(self, record: OKXInstrument, inst: Dict[str, Any]):
        """更新产品信息记录"""
        record.inst_type = inst.get('instType', '')
        record.uly = inst.get('uly', '')
        record.category = inst.get('category', '')
        record.base_currency = inst.get('baseCcy', '')
        record.quote_currency = inst.get('quoteCcy', '')
        record.settle_currency = inst.get('settleCcy', '')
        record.contract_value = Decimal(inst.get('ctVal', '0')) if inst.get('ctVal') else None
        record.min_size = Decimal(inst.get('minSz', '0')) if inst.get('minSz') else None
        record.lot_size = Decimal(inst.get('lotSz', '0')) if inst.get('lotSz') else None
        record.tick_size = Decimal(inst.get('tickSz', '0')) if inst.get('tickSz') else None
        record.option_type = inst.get('optType', '')
        record.strike_price = Decimal(inst.get('stk', '0')) if inst.get('stk') else None
        record.listing_time = datetime.fromtimestamp(int(inst.get('listTime', '0')) / 1000) if inst.get('listTime') else None
        record.expiry_time = datetime.fromtimestamp(int(inst.get('expTime', '0')) / 1000) if inst.get('expTime') else None
        record.lever = inst.get('lever', '')
        record.state = inst.get('state', '')
        record.updated_at = datetime.now()
    
    def _create_instrument_record(self, inst: Dict[str, Any]) -> OKXInstrument:
        """创建新的产品信息记录"""
        return OKXInstrument(
            inst_id=inst.get('instId', ''),
            inst_type=inst.get('instType', ''),
            uly=inst.get('uly', ''),
            category=inst.get('category', ''),
            base_currency=inst.get('baseCcy', ''),
            quote_currency=inst.get('quoteCcy', ''),
            settle_currency=inst.get('settleCcy', ''),
            contract_value=Decimal(inst.get('ctVal', '0')) if inst.get('ctVal') else None,
            min_size=Decimal(inst.get('minSz', '0')) if inst.get('minSz') else None,
            lot_size=Decimal(inst.get('lotSz', '0')) if inst.get('lotSz') else None,
            tick_size=Decimal(inst.get('tickSz', '0')) if inst.get('tickSz') else None,
            option_type=inst.get('optType', ''),
            strike_price=Decimal(inst.get('stk', '0')) if inst.get('stk') else None,
            listing_time=datetime.fromtimestamp(int(inst.get('listTime', '0')) / 1000) if inst.get('listTime') else None,
            expiry_time=datetime.fromtimestamp(int(inst.get('expTime', '0')) / 1000) if inst.get('expTime') else None,
            lever=inst.get('lever', ''),
            state=inst.get('state', '')
        )
    
    # ==================== 多账户类型数据同步 ====================
    
    async def sync_all_accounts_data(self, db: Session) -> Dict[str, Any]:
        """同步所有账户类型的数据"""
        results = {
            'accounts': {},
            'instruments': False,
            'market_data': {},
            'total_errors': []
        }
        
        # 支持的账户类型
        account_types = ['funding', 'trading', 'spot', 'futures', 'swap', 'option', 'margin']
        
        # 同步各种账户类型的余额和持仓
        for account_type in account_types:
            account_result = await self._sync_account_data(db, account_type)
            results['accounts'][account_type] = account_result
            if account_result.get('errors'):
                results['total_errors'].extend([f"{account_type}: {err}" for err in account_result['errors']])
        
        # 同步产品信息
        results['instruments'] = await self._sync_instruments_data(db)
        
        # 同步不同产品类型的行情数据
        inst_types = ['SPOT', 'SWAP', 'FUTURES', 'OPTION']
        for inst_type in inst_types:
            market_result = await self._sync_market_data_by_type(db, inst_type)
            results['market_data'][inst_type] = market_result
            if not market_result:
                results['total_errors'].append(f"同步{inst_type}行情数据失败")
        
        return results
    
    async def _sync_account_data(self, db: Session, account_type: str) -> Dict[str, Any]:
        """同步特定账户类型的数据"""
        result = {
            'balance': False,
            'positions': False,
            'transactions': False,
            'errors': []
        }
        
        try:
            # 同步账户余额
            balance_log = self.create_sync_log(db, 'balance', {'account_type': account_type}, account_type)
            # 注意：实际API调用需要根据OKX文档调整参数
            balance_data = await self.api_service.get_account_balance()
            if balance_data:
                success = self.save_account_balance(db, balance_data, account_type)
                result['balance'] = success
                self.update_sync_log(db, balance_log, 'success' if success else 'failed')
            else:
                result['errors'].append('获取账户余额失败')
                self.update_sync_log(db, balance_log, 'failed', error_message='获取账户余额失败')
        except Exception as e:
            result['errors'].append(f'同步账户余额异常: {e}')
            logger.error(f"同步{account_type}账户余额异常: {e}")
        
        try:
            # 同步持仓数据
            position_log = self.create_sync_log(db, 'position', {'account_type': account_type}, account_type)
            position_data = await self.api_service.get_account_positions()
            if position_data:
                success = self.save_positions(db, position_data, account_type)
                result['positions'] = success
                self.update_sync_log(db, position_log, 'success' if success else 'failed')
            else:
                result['errors'].append('获取持仓数据失败')
                self.update_sync_log(db, position_log, 'failed', error_message='获取持仓数据失败')
        except Exception as e:
            result['errors'].append(f'同步持仓数据异常: {e}')
            logger.error(f"同步{account_type}持仓数据异常: {e}")
        
        try:
            # 同步交易记录
            transaction_log = self.create_sync_log(db, 'transaction', {'account_type': account_type, 'limit': 100}, account_type)
            transaction_data = await self.api_service.get_bills(limit=100)
            if transaction_data:
                success = self.save_transactions(db, transaction_data, account_type)
                result['transactions'] = success
                self.update_sync_log(db, transaction_log, 'success' if success else 'failed')
            else:
                result['errors'].append('获取交易记录失败')
                self.update_sync_log(db, transaction_log, 'failed', error_message='获取交易记录失败')
        except Exception as e:
            result['errors'].append(f'同步交易记录异常: {e}')
            logger.error(f"同步{account_type}交易记录异常: {e}")
        
        return result
    
    async def _sync_instruments_data(self, db: Session) -> bool:
        """同步产品信息数据"""
        try:
            instruments_log = self.create_sync_log(db, 'instrument')
            
            # 同步所有产品类型的信息
            inst_types = ['SPOT', 'SWAP', 'FUTURES', 'OPTION']
            all_success = True
            
            for inst_type in inst_types:
                try:
                    instrument_data = await self.api_service.get_instruments(inst_type)
                    if instrument_data:
                        success = self.save_instruments(db, instrument_data)
                        if not success:
                            all_success = False
                    else:
                        all_success = False
                        logger.warning(f"获取{inst_type}产品信息失败")
                except Exception as e:
                    all_success = False
                    logger.error(f"同步{inst_type}产品信息异常: {e}")
            
            self.update_sync_log(db, instruments_log, 'success' if all_success else 'failed')
            return all_success
            
        except Exception as e:
            logger.error(f"同步产品信息数据异常: {e}")
            return False
    
    async def _sync_market_data_by_type(self, db: Session, inst_type: str) -> bool:
        """同步特定产品类型的行情数据"""
        try:
            market_log = self.create_sync_log(db, 'market', {'inst_type': inst_type})
            market_data = await self.api_service.get_all_tickers(inst_type)
            if market_data:
                success = self.save_market_data(db, market_data)
                self.update_sync_log(db, market_log, 'success' if success else 'failed')
                return success
            else:
                self.update_sync_log(db, market_log, 'failed', error_message=f'获取{inst_type}行情数据失败')
                return False
        except Exception as e:
            logger.error(f"同步{inst_type}行情数据异常: {e}")
            return False
    
    # ==================== 兼容性方法 ====================
    
    async def sync_all_data(self, db: Session) -> Dict[str, Any]:
        """同步所有OKX数据（简化版本，主要用于向后兼容）"""
        results = {
            'balance': False,
            'positions': False,
            'transactions': False,
            'market_data': False,
            'errors': []
        }
        
        # 同步交易账户的主要数据
        try:
            # 同步账户余额
            balance_log = self.create_sync_log(db, 'balance')
            balance_data = await self.api_service.get_account_balance()
            if balance_data:
                success = self.save_account_balance(db, balance_data, 'trading')
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
                success = self.save_positions(db, position_data, 'trading')
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
                success = self.save_transactions(db, transaction_data, 'trading')
                results['transactions'] = success
                self.update_sync_log(db, transaction_log, 'success' if success else 'failed')
            else:
                results['errors'].append('获取交易记录失败')
                self.update_sync_log(db, transaction_log, 'failed', error_message='获取交易记录失败')
        except Exception as e:
            results['errors'].append(f'同步交易记录异常: {e}')
            logger.error(f"同步交易记录异常: {e}")
        
        # 同步现货行情数据
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