import time
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from loguru import logger

from app.settings import settings
from app.utils.database import SessionLocal, set_audit_context, clear_audit_context
from app.models.database import IBKRAccount, IBKRBalance, IBKRPosition, IBKRSyncLog
from app.models.schemas import IBKRSyncRequest, IBKRSyncResponse
from app.utils.auto_logger import auto_log


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
    
    @auto_log("database", log_result=True)
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
    
    @auto_log("database", log_result=True)
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
    
    @auto_log("database", log_result=True)
    def _sync_balances(self, db: Session, account_id: str, balances_data: Dict[str, Any], 
                      snapshot_time: datetime, sync_source: str = "gcp_scheduler") -> int:
        """同步账户余额数据"""
        try:
            snapshot_date = snapshot_time.date()
            
            # 详细日志：打印写入时的所有字段和类型
            logger.info(f"🔍 准备写入余额数据:")
            logger.info(f"   account_id: '{account_id}' (类型: {type(account_id)})")
            logger.info(f"   snapshot_time: {snapshot_time} (类型: {type(snapshot_time)})")
            logger.info(f"   snapshot_date: {snapshot_date} (类型: {type(snapshot_date)})")
            logger.info(f"   currency: '{balances_data.get('currency')}' (类型: {type(balances_data.get('currency'))})")
            logger.info(f"   total_cash: {balances_data.get('total_cash')} (类型: {type(balances_data.get('total_cash'))})")
            logger.info(f"   net_liquidation: {balances_data.get('net_liquidation')} (类型: {type(balances_data.get('net_liquidation'))})")
            logger.info(f"   buying_power: {balances_data.get('buying_power')} (类型: {type(balances_data.get('buying_power'))})")
            logger.info(f"   sync_source: '{sync_source}' (类型: {type(sync_source)})")
            
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
            logger.info(f"✅ 成功同步余额数据: {account_id} - {snapshot_time}")
            return 1
            
        except Exception as e:
            logger.error(f"❌ 同步余额数据失败: {e}")
            db.rollback()
            raise
    
    @auto_log("database", log_result=True)
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
    
    @auto_log("external", log_result=True)
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
            
            # 3. 准备审计上下文
            import uuid
            request_id = str(uuid.uuid4())
            audit_context = {
                "source_ip": client_ip,
                "user_agent": user_agent,
                "api_key": "IBKR_SYNC",  # 标识这是IBKR同步操作
                "request_id": request_id,
                "session_id": f"ibkr_sync_{request_data.account_id}"
            }
            
            # 4. 解析时间戳
            snapshot_time = datetime.fromisoformat(request_data.timestamp.replace('Z', '+00:00'))
            if snapshot_time.tzinfo:
                snapshot_time = snapshot_time.replace(tzinfo=None)
            
            # 5. 确保账户存在
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
            
            # 9. 更新audit_log记录，添加上下文信息
            try:
                from sqlalchemy import text
                # 更新本次请求产生的所有audit_log记录
                update_sql = """
                UPDATE audit_log 
                SET source_ip = :source_ip,
                    user_agent = :user_agent,
                    api_key = :api_key,
                    request_id = :request_id,
                    session_id = :session_id
                WHERE changed_at >= NOW() - INTERVAL '5 minutes'
                AND (source_ip IS NULL OR source_ip = '')
                """
                db.execute(text(update_sql), audit_context)
                db.commit()
                logger.info(f"✅ 已更新 {balance_count + position_count + 1} 条audit_log记录的上下文信息")
            except Exception as e:
                logger.error(f"❌ 更新audit_log上下文信息失败: {e}")
                # 不抛出异常，不影响主流程
            
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
    
    @auto_log("database", log_result=True)
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
    
    @auto_log("database", log_result=True)
    async def get_latest_balances(self, account_id: str = None) -> List[Dict[str, Any]]:
        """获取最新的账户余额"""
        logger.info(f"🔍 开始获取IBKR余额数据 - account_id: {account_id}")
        db = SessionLocal()
        try:
            # 检查数据库连接
            try:
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
                logger.info("✅ 数据库连接正常")
            except Exception as e:
                logger.error(f"❌ 数据库连接失败: {e}")
                return []
            
            # 检查表是否存在
            try:
                table_count = db.query(IBKRBalance).count()
                logger.info(f"📊 IBKRBalance表记录总数: {table_count}")
            except Exception as e:
                logger.error(f"❌ 查询IBKRBalance表失败: {e}")
                return []
            
            query = db.query(IBKRBalance)
            if account_id:
                query = query.filter(IBKRBalance.account_id == account_id)
                logger.info(f"🔍 过滤账户: {account_id}")
            
            # 简化查询逻辑：直接获取最新记录
            logger.info("🔍 执行余额查询...")
            if account_id:
                # 获取指定账户的最新余额
                logger.info(f"🔍 查询指定账户: {account_id}")
                latest_time = db.query(func.max(IBKRBalance.snapshot_time)).filter(
                    IBKRBalance.account_id == account_id
                ).scalar()
                logger.info(f"📊 账户 {account_id} 的最新时间: {latest_time} (类型: {type(latest_time)})")
                if latest_time:
                    balances = db.query(IBKRBalance).filter(
                        and_(
                            IBKRBalance.account_id == account_id,
                            IBKRBalance.snapshot_time == latest_time
                        )
                    ).all()
                    logger.info(f"📊 查询到 {len(balances)} 条余额记录")
                else:
                    balances = []
                    logger.info(f"❌ 账户 {account_id} 没有找到最新时间")
            else:
                # 获取所有账户的最新余额
                balances = []
                account_ids = db.query(IBKRBalance.account_id).distinct().all()
                logger.info(f"📊 所有账户ID: {[aid[0] for aid in account_ids]}")
                for (account_id,) in account_ids:
                    logger.info(f"🔍 查询账户: {account_id}")
                    latest_time = db.query(func.max(IBKRBalance.snapshot_time)).filter(
                        IBKRBalance.account_id == account_id
                    ).scalar()
                    logger.info(f"📊 账户 {account_id} 的最新时间: {latest_time} (类型: {type(latest_time)})")
                    if latest_time:
                        account_balances = db.query(IBKRBalance).filter(
                            and_(
                                IBKRBalance.account_id == account_id,
                                IBKRBalance.snapshot_time == latest_time
                            )
                        ).all()
                        logger.info(f"📊 账户 {account_id} 查询到 {len(account_balances)} 条余额记录")
                        balances.extend(account_balances)
                    else:
                        logger.info(f"❌ 账户 {account_id} 没有找到最新时间")
            
            logger.info(f"📊 查询到 {len(balances)} 条余额记录")
            
            result = [
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
            
            logger.info(f"✅ 成功返回 {len(result)} 条余额数据")
            for balance in result:
                logger.info(f"💰 账户 {balance['account_id']}: 现金 ${balance['total_cash']:.2f}, 净值 ${balance['net_liquidation']:.2f}")
            
            # 打印原始数据的详细信息
            for balance in balances:
                logger.info(f"🔍 余额原始数据:")
                logger.info(f"   account_id: '{balance.account_id}' (类型: {type(balance.account_id)})")
                logger.info(f"   snapshot_time: {balance.snapshot_time} (类型: {type(balance.snapshot_time)})")
                logger.info(f"   snapshot_date: {balance.snapshot_date} (类型: {type(balance.snapshot_date)})")
                logger.info(f"   currency: '{balance.currency}' (类型: {type(balance.currency)})")
                logger.info(f"   total_cash: {balance.total_cash} (类型: {type(balance.total_cash)})")
                logger.info(f"   net_liquidation: {balance.net_liquidation} (类型: {type(balance.net_liquidation)})")
                logger.info(f"   buying_power: {balance.buying_power} (类型: {type(balance.buying_power)})")
                logger.info(f"   sync_source: '{balance.sync_source}' (类型: {type(balance.sync_source)})")
            
            return result
        except Exception as e:
            logger.error(f"❌ 获取余额数据失败: {e}")
            return []
        finally:
            db.close()
    
    @auto_log("database", log_result=True)
    async def get_latest_positions(self, account_id: str = None) -> List[Dict[str, Any]]:
        """获取最新的持仓信息"""
        logger.info(f"🔍 开始获取IBKR持仓数据 - account_id: {account_id}")
        db = SessionLocal()
        try:
            # 检查表是否存在
            try:
                table_count = db.query(IBKRPosition).count()
                logger.info(f"📊 IBKRPosition表记录总数: {table_count}")
            except Exception as e:
                logger.error(f"❌ 查询IBKRPosition表失败: {e}")
                return []
            
            query = db.query(IBKRPosition)
            if account_id:
                query = query.filter(IBKRPosition.account_id == account_id)
                logger.info(f"🔍 过滤账户: {account_id}")
            
            # 获取每个账户每个符号的最新持仓记录
            subquery = db.query(
                IBKRPosition.account_id,
                IBKRPosition.symbol,
                func.max(IBKRPosition.snapshot_time).label('max_time')
            ).group_by(IBKRPosition.account_id, IBKRPosition.symbol).subquery()
            
            logger.info("🔍 执行持仓查询...")
            positions = query.join(
                subquery,
                and_(
                    IBKRPosition.account_id == subquery.c.account_id,
                    IBKRPosition.symbol == subquery.c.symbol,
                    IBKRPosition.snapshot_time == subquery.c.max_time
                )
            ).filter(IBKRPosition.quantity != 0).all()  # 过滤掉空仓
            
            logger.info(f"📊 查询到 {len(positions)} 条持仓记录")
            
            result = [
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
            
            logger.info(f"✅ 成功返回 {len(result)} 条持仓数据")
            for position in result:
                logger.info(f"📈 持仓 {position['symbol']}: 数量 {position['quantity']}, 市值 ${position['market_value']:.2f}")
            
            return result
        except Exception as e:
            logger.error(f"❌ 获取持仓数据失败: {e}")
            return []
        finally:
            db.close()
    
    @auto_log("database", log_result=True)
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
    
    @auto_log("system", log_result=True)
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
    
    @auto_log("system", log_result=True)
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        try:
            config_ok = self._validate_config()
            
            # 测试数据库连接
            db_ok = False
            db_error = None
            try:
                db = SessionLocal()
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
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