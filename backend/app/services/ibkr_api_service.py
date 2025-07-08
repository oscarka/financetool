import time
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from loguru import logger

from app.config import settings
from app.utils.database import SessionLocal
from app.models.database import IBKRAccount, IBKRBalance, IBKRPosition, IBKRSyncLog


class IBKRSyncRequest(BaseModel):
    """IBKR同步请求数据模型"""
    account_id: str = Field(..., min_length=1, max_length=50, description="IBKR账户ID")
    timestamp: str = Field(..., description="数据时间戳 ISO 8601格式")
    balances: Dict[str, Any] = Field(..., description="账户余额信息")
    positions: List[Dict[str, Any]] = Field(default_factory=list, description="持仓信息列表")
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('时间戳格式无效，请使用ISO 8601格式')
    
    @validator('balances')
    def validate_balances(cls, v):
        required_fields = ['total_cash', 'net_liquidation', 'buying_power', 'currency']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'余额信息缺少必需字段: {field}')
        return v


class IBKRSyncResponse(BaseModel):
    """IBKR同步响应数据模型"""
    status: str
    message: str
    received_at: str
    records_updated: Dict[str, int]
    sync_id: Optional[int] = None
    errors: List[str] = Field(default_factory=list)


class IBKRAPIService:
    """IBKR API集成服务"""
    
    def __init__(self):
        self.api_key = settings.ibkr_api_key
        self.allowed_ips = [ip.strip() for ip in settings.ibkr_allowed_ips.split(',')]
        self.sync_timeout = settings.ibkr_sync_timeout
        self.enable_ip_whitelist = settings.ibkr_enable_ip_whitelist
        self.enable_request_logging = settings.ibkr_enable_request_logging
        logger.info(f"IBKR API服务初始化完成, API Key配置: {'已配置' if self.api_key else '未配置'}")
    
    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        if not self.api_key:
            logger.error("IBKR API Key未配置，请检查环境变量")
            return False
        return True
    
    def _validate_ip_address(self, client_ip: str) -> bool:
        """验证客户端IP地址是否在白名单中"""
        if not self.enable_ip_whitelist:
            return True
        
        import ipaddress
        client_ip_obj = ipaddress.ip_address(client_ip)
        
        for allowed_ip in self.allowed_ips:
            try:
                if '/' in allowed_ip:
                    # CIDR网段
                    if client_ip_obj in ipaddress.ip_network(allowed_ip, strict=False):
                        return True
                else:
                    # 单个IP
                    if client_ip_obj == ipaddress.ip_address(allowed_ip):
                        return True
            except ValueError as e:
                logger.warning(f"无效的IP配置: {allowed_ip}, 错误: {e}")
                continue
        
        return False
    
    def _validate_api_key(self, provided_key: str) -> bool:
        """验证API密钥"""
        return provided_key == self.api_key
    
    def _create_sync_log(self, db: Session, account_id: Optional[str], sync_type: str, 
                        status: str, request_data: Optional[str] = None, 
                        error_message: Optional[str] = None, source_ip: Optional[str] = None,
                        user_agent: Optional[str] = None, sync_duration_ms: Optional[int] = None) -> IBKRSyncLog:
        """创建同步日志记录"""
        sync_log = IBKRSyncLog(
            account_id=account_id,
            sync_type=sync_type,
            status=status,
            request_data=request_data,
            error_message=error_message,
            source_ip=source_ip,
            user_agent=user_agent,
            sync_duration_ms=sync_duration_ms
        )
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)
        return sync_log
    
    def _ensure_account_exists(self, db: Session, account_id: str) -> IBKRAccount:
        """确保账户记录存在，不存在则创建"""
        account = db.query(IBKRAccount).filter(IBKRAccount.account_id == account_id).first()
        if not account:
            account = IBKRAccount(
                account_id=account_id,
                account_name=f"IBKR Account {account_id}",
                account_type="INDIVIDUAL",
                base_currency="USD",
                status="ACTIVE"
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            logger.info(f"创建新的IBKR账户记录: {account_id}")
        return account
    
    def _sync_balances(self, db: Session, account_id: str, balances_data: Dict[str, Any], 
                      snapshot_time: datetime, sync_source: str = "gcp_scheduler") -> int:
        """同步账户余额数据"""
        try:
            snapshot_date = snapshot_time.date()
            
            # 检查是否已存在相同时间的余额记录
            existing_balance = db.query(IBKRBalance).filter(
                and_(
                    IBKRBalance.account_id == account_id,
                    IBKRBalance.snapshot_date == snapshot_date,
                    IBKRBalance.snapshot_time == snapshot_time
                )
            ).first()
            
            if existing_balance:
                logger.info(f"余额记录已存在，跳过: {account_id} - {snapshot_time}")
                return 0
            
            # 创建新的余额记录
            balance = IBKRBalance(
                account_id=account_id,
                total_cash=Decimal(str(balances_data.get('total_cash', 0))),
                net_liquidation=Decimal(str(balances_data.get('net_liquidation', 0))),
                buying_power=Decimal(str(balances_data.get('buying_power', 0))),
                currency=balances_data.get('currency', 'USD'),
                snapshot_date=snapshot_date,
                snapshot_time=snapshot_time,
                sync_source=sync_source
            )
            
            db.add(balance)
            db.commit()
            logger.info(f"成功同步余额数据: {account_id} - {snapshot_time}")
            return 1
            
        except Exception as e:
            logger.error(f"同步余额数据失败: {e}")
            db.rollback()
            raise
    
    def _sync_positions(self, db: Session, account_id: str, positions_data: List[Dict[str, Any]], 
                       snapshot_time: datetime, sync_source: str = "gcp_scheduler") -> int:
        """同步持仓数据"""
        try:
            snapshot_date = snapshot_time.date()
            inserted_count = 0
            
            for position_data in positions_data:
                symbol = position_data.get('symbol')
                if not symbol:
                    logger.warning("持仓数据缺少symbol字段，跳过")
                    continue
                
                # 检查是否已存在相同时间的持仓记录
                existing_position = db.query(IBKRPosition).filter(
                    and_(
                        IBKRPosition.account_id == account_id,
                        IBKRPosition.symbol == symbol,
                        IBKRPosition.snapshot_date == snapshot_date,
                        IBKRPosition.snapshot_time == snapshot_time
                    )
                ).first()
                
                if existing_position:
                    logger.info(f"持仓记录已存在，跳过: {account_id} - {symbol} - {snapshot_time}")
                    continue
                
                # 创建新的持仓记录
                position = IBKRPosition(
                    account_id=account_id,
                    symbol=symbol,
                    quantity=Decimal(str(position_data.get('quantity', 0))),
                    market_value=Decimal(str(position_data.get('market_value', 0))),
                    average_cost=Decimal(str(position_data.get('average_cost', 0))),
                    unrealized_pnl=Decimal(str(position_data.get('unrealized_pnl', 0))),
                    realized_pnl=Decimal(str(position_data.get('realized_pnl', 0))),
                    currency=position_data.get('currency', 'USD'),
                    asset_class=position_data.get('asset_class', 'STK'),
                    snapshot_date=snapshot_date,
                    snapshot_time=snapshot_time,
                    sync_source=sync_source
                )
                
                db.add(position)
                inserted_count += 1
            
            if inserted_count > 0:
                db.commit()
                logger.info(f"成功同步持仓数据: {account_id} - {inserted_count}条记录")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"同步持仓数据失败: {e}")
            db.rollback()
            raise
    
    async def sync_data(self, request_data: IBKRSyncRequest, client_ip: str = None, 
                       user_agent: str = None) -> IBKRSyncResponse:
        """处理IBKR数据同步请求"""
        start_time = time.time()
        db = SessionLocal()
        sync_log = None
        
        try:
            # 1. 验证API配置
            if not self._validate_config():
                raise ValueError("IBKR API配置无效")
            
            # 2. 验证IP地址
            if client_ip and not self._validate_ip_address(client_ip):
                raise ValueError(f"IP地址不在白名单中: {client_ip}")
            
            # 3. 解析时间戳
            snapshot_time = datetime.fromisoformat(request_data.timestamp.replace('Z', '+00:00'))
            if snapshot_time.tzinfo:
                snapshot_time = snapshot_time.replace(tzinfo=None)
            
            # 4. 确保账户存在
            self._ensure_account_exists(db, request_data.account_id)
            
            # 5. 同步余额数据
            balance_count = self._sync_balances(
                db, request_data.account_id, request_data.balances, snapshot_time
            )
            
            # 6. 同步持仓数据
            position_count = self._sync_positions(
                db, request_data.account_id, request_data.positions, snapshot_time
            )
            
            # 7. 记录成功日志
            sync_duration_ms = int((time.time() - start_time) * 1000)
            sync_log = self._create_sync_log(
                db=db,
                account_id=request_data.account_id,
                sync_type="full",
                status="success",
                request_data=request_data.json() if self.enable_request_logging else None,
                source_ip=client_ip,
                user_agent=user_agent,
                sync_duration_ms=sync_duration_ms
            )
            
            # 8. 更新同步日志统计
            sync_log.records_processed = len(request_data.positions) + 1  # positions + balances
            sync_log.records_inserted = balance_count + position_count
            sync_log.records_updated = 0
            db.commit()
            
            response = IBKRSyncResponse(
                status="success",
                message="IBKR data synchronized successfully",
                received_at=datetime.now().isoformat(),
                records_updated={
                    "balances": balance_count,
                    "positions": position_count
                },
                sync_id=sync_log.id
            )
            
            logger.info(f"IBKR数据同步成功: {request_data.account_id}, 耗时: {sync_duration_ms}ms")
            return response
            
        except Exception as e:
            # 记录错误日志
            sync_duration_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)
            
            try:
                error_account_id = None
                error_request_data = None
                
                if hasattr(request_data, 'account_id'):
                    error_account_id = request_data.account_id
                
                if self.enable_request_logging and hasattr(request_data, 'json'):
                    error_request_data = request_data.json()
                
                self._create_sync_log(
                    db=db,
                    account_id=error_account_id,
                    sync_type="full",
                    status="error",
                    request_data=error_request_data,
                    error_message=error_message,
                    source_ip=client_ip,
                    user_agent=user_agent,
                    sync_duration_ms=sync_duration_ms
                )
            except Exception as log_error:
                logger.error(f"记录同步错误日志失败: {log_error}")
            
            logger.error(f"IBKR数据同步失败: {error_message}")
            
            response = IBKRSyncResponse(
                status="error",
                message=f"Synchronization failed: {error_message}",
                received_at=datetime.now().isoformat(),
                records_updated={"balances": 0, "positions": 0},
                errors=[error_message]
            )
            return response
            
        finally:
            db.close()
    
    async def get_account_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """获取账户信息"""
        db = SessionLocal()
        try:
            account = db.query(IBKRAccount).filter(IBKRAccount.account_id == account_id).first()
            if not account:
                return None
            
            return {
                "account_id": account.account_id,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "base_currency": account.base_currency,
                "status": account.status,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            }
        finally:
            db.close()
    
    async def get_latest_balances(self, account_id: str = None) -> List[Dict[str, Any]]:
        """获取最新的账户余额"""
        db = SessionLocal()
        try:
            query = db.query(IBKRBalance)
            if account_id:
                query = query.filter(IBKRBalance.account_id == account_id)
            
            # 获取每个账户的最新余额记录
            subquery = db.query(
                IBKRBalance.account_id,
                func.max(IBKRBalance.snapshot_time).label('max_time')
            ).group_by(IBKRBalance.account_id).subquery()
            
            balances = query.join(
                subquery,
                and_(
                    IBKRBalance.account_id == subquery.c.account_id,
                    IBKRBalance.snapshot_time == subquery.c.max_time
                )
            ).all()
            
            return [
                {
                    "account_id": balance.account_id,
                    "total_cash": float(balance.total_cash),
                    "net_liquidation": float(balance.net_liquidation),
                    "buying_power": float(balance.buying_power),
                    "currency": balance.currency,
                    "snapshot_date": balance.snapshot_date.isoformat(),
                    "snapshot_time": balance.snapshot_time.isoformat(),
                    "sync_source": balance.sync_source
                }
                for balance in balances
            ]
        finally:
            db.close()
    
    async def get_latest_positions(self, account_id: str = None) -> List[Dict[str, Any]]:
        """获取最新的持仓信息"""
        db = SessionLocal()
        try:
            query = db.query(IBKRPosition)
            if account_id:
                query = query.filter(IBKRPosition.account_id == account_id)
            
            # 获取每个账户每个符号的最新持仓记录
            subquery = db.query(
                IBKRPosition.account_id,
                IBKRPosition.symbol,
                func.max(IBKRPosition.snapshot_time).label('max_time')
            ).group_by(IBKRPosition.account_id, IBKRPosition.symbol).subquery()
            
            positions = query.join(
                subquery,
                and_(
                    IBKRPosition.account_id == subquery.c.account_id,
                    IBKRPosition.symbol == subquery.c.symbol,
                    IBKRPosition.snapshot_time == subquery.c.max_time
                )
            ).filter(IBKRPosition.quantity != 0).all()  # 过滤掉空仓
            
            return [
                {
                    "account_id": position.account_id,
                    "symbol": position.symbol,
                    "quantity": float(position.quantity),
                    "market_value": float(position.market_value),
                    "average_cost": float(position.average_cost),
                    "unrealized_pnl": float(position.unrealized_pnl or 0),
                    "realized_pnl": float(position.realized_pnl or 0),
                    "currency": position.currency,
                    "asset_class": position.asset_class,
                    "snapshot_date": position.snapshot_date.isoformat(),
                    "snapshot_time": position.snapshot_time.isoformat(),
                    "sync_source": position.sync_source
                }
                for position in positions
            ]
        finally:
            db.close()
    
    async def get_sync_logs(self, account_id: str = None, limit: int = 50, 
                           status: str = None) -> List[Dict[str, Any]]:
        """获取同步日志"""
        db = SessionLocal()
        try:
            query = db.query(IBKRSyncLog)
            if account_id:
                query = query.filter(IBKRSyncLog.account_id == account_id)
            if status:
                query = query.filter(IBKRSyncLog.status == status)
            
            logs = query.order_by(desc(IBKRSyncLog.created_at)).limit(limit).all()
            
            return [
                {
                    "id": log.id,
                    "account_id": log.account_id,
                    "sync_type": log.sync_type,
                    "status": log.status,
                    "records_processed": log.records_processed,
                    "records_inserted": log.records_inserted,
                    "records_updated": log.records_updated,
                    "error_message": log.error_message,
                    "source_ip": log.source_ip,
                    "sync_duration_ms": log.sync_duration_ms,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        finally:
            db.close()
    
    async def get_config(self) -> Dict[str, Any]:
        """获取当前配置信息"""
        return {
            "api_configured": bool(self.api_key),
            "api_key_prefix": self.api_key[:10] + "..." if self.api_key else "未配置",
            "allowed_ips": self.allowed_ips,
            "sync_timeout": self.sync_timeout,
            "enable_ip_whitelist": self.enable_ip_whitelist,
            "enable_request_logging": self.enable_request_logging
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        try:
            config_ok = self._validate_config()
            
            # 测试数据库连接
            db_ok = False
            db_error = None
            try:
                db = SessionLocal()
                db.execute("SELECT 1")
                db.close()
                db_ok = True
            except Exception as e:
                db_error = str(e)
            
            return {
                "config_valid": config_ok,
                "database_ok": db_ok,
                "database_error": db_error,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "config_valid": False,
                "database_ok": False,
                "error": str(e),
                "timestamp": time.time()
            }