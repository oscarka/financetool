import httpx
import time
import hmac
import base64
import hashlib
from typing import Optional, Dict, Any, List
from app.settings import settings
from app.utils.logger import log_okx_api
from app.utils.auto_logger import auto_log
import logging

# 创建logger实例
logger = logging.getLogger(__name__)

class OKXAPIService:
    """OKX API集成服务"""
    def __init__(self):
        self.api_key = settings.okx_api_key
        self.secret_key = settings.okx_secret_key
        self.passphrase = settings.okx_passphrase
        self.base_url = settings.okx_api_base_url
        self.sandbox = settings.okx_sandbox
        self.headers = {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
        }
        # OKX API URL - 根据OKX官方文档，沙盒和正式环境使用相同的域名
        # 沙盒环境通过API Key的权限控制，而不是不同的域名
        self.base_url = 'https://www.okx.com'
        
        # 打印调试信息
        log_okx_api(f"OKX API初始化: api_key={self.api_key[:10] if self.api_key else 'None'}..., sandbox={self.sandbox}", level="INFO")

    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        if not all([self.api_key, self.secret_key, self.passphrase]):
            log_okx_api("OKX API配置不完整，请检查环境变量", level="ERROR")
            return False
        return True

    def _get_timestamp(self) -> str:
        return str(time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()))

    def _sign(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        message = f"{timestamp}{method}{request_path}{body}"
        # 确保所有字符串都使用UTF-8编码
        mac = hmac.new(self.secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
        d = mac.digest()
        return base64.b64encode(d).decode('utf-8')

    def _auth_headers(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        timestamp = self._get_timestamp()
        sign = self._sign(timestamp, method, request_path, body)
        headers = self.headers.copy()
        headers.update({
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-SIGN': sign,
        })
        logger.debug(f"生成认证头: timestamp={timestamp}, sign={sign[:20]}...")
        return headers

    async def _make_request(self, method: str, path: str, params: Dict = None, body: str = "", auth_required: bool = True) -> Optional[Dict[str, Any]]:
        """统一的请求方法"""
        try:
            url = self.base_url + path
            if params:
                url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            headers = self._auth_headers(method, path, body) if auth_required else {}
            
            logger.info(f"请求OKX接口: {method} {url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == 'GET':
                    resp = await client.get(url, headers=headers)
                elif method.upper() == 'POST':
                    resp = await client.post(url, headers=headers, content=body)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                logger.info(f"OKX接口响应状态: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    logger.debug(f"OKX接口响应数据: {data}")
                    return data
                else:
                    logger.error(f"OKX接口错误: {resp.status_code}, {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"OKX接口请求异常: {e}")
            return None

    @auto_log("okx", log_result=True)
    async def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """获取账户资产信息"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', '/api/v5/account/balance')

    @auto_log("okx", log_result=True)
    async def get_ticker(self, inst_id: str) -> Optional[Dict[str, Any]]:
        """获取某个币种行情"""
        params = {'instId': inst_id}
        return await self._make_request('GET', '/api/v5/market/ticker', params=params, auth_required=False)

    @auto_log("okx", log_result=True)
    async def get_all_tickers(self, inst_type: str = 'SPOT') -> Optional[Dict[str, Any]]:
        """获取所有币种行情"""
        params = {'instType': inst_type}
        return await self._make_request('GET', '/api/v5/market/tickers', params=params, auth_required=False)

    async def get_instruments(self, inst_type: str = 'SPOT') -> Optional[Dict[str, Any]]:
        """获取交易产品基础信息"""
        params = {'instType': inst_type}
        return await self._make_request('GET', '/api/v5/public/instruments', params=params, auth_required=False)

    @auto_log("okx", log_result=True)
    async def get_account_positions(self) -> Optional[Dict[str, Any]]:
        """获取持仓信息"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', '/api/v5/account/positions')

    async def get_bills(self, inst_type: str = None, limit: int = 100) -> Optional[Dict[str, Any]]:
        """获取账单流水"""
        if not self._validate_config():
            return None
        params = {'limit': str(limit)}
        if inst_type:
            params['instType'] = inst_type
        return await self._make_request('GET', '/api/v5/account/bills', params=params)

    @auto_log("system")
    async def get_config(self) -> Dict[str, Any]:
        """获取OKX API配置信息"""
        return {
            "api_configured": bool(self.api_key and self.secret_key and self.passphrase),
            "sandbox_mode": self.sandbox,
            "base_url": self.base_url,
            "api_key_prefix": self.api_key[:10] + "..." if self.api_key else None
        }

    @auto_log("system")
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        try:
            # 测试公共接口
            public_result = await self.get_ticker("BTC-USDT")
            public_ok = public_result is not None
            
            # 测试私有接口
            private_ok = False
            private_error = None
            if self._validate_config():
                private_result = await self.get_account_balance()
                private_ok = private_result is not None
                if not private_ok:
                    private_error = "认证失败或账户接口异常"
            else:
                private_error = "API配置不完整"
            
            return {
                "public_api": public_ok,
                "private_api": private_ok,
                "private_error": private_error,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "public_api": False,
                "private_api": False,
                "error": str(e),
                "timestamp": time.time()
            }

    @auto_log("okx", log_result=True)
    async def get_asset_balances(self, ccy: str = None) -> Optional[Dict[str, Any]]:
        """获取资金账户余额 (GET /api/v5/asset/balances)"""
        if not self._validate_config():
            return None
        params = {}
        if ccy:
            params['ccy'] = ccy
        return await self._make_request('GET', '/api/v5/asset/balances', params=params)

    @auto_log("okx", log_result=True)
    async def get_savings_balance(self, ccy: str = None) -> Optional[Dict[str, Any]]:
        """获取储蓄账户余额 (GET /api/v5/finance/savings/balance)"""
        if not self._validate_config():
            return None
        params = {}
        if ccy:
            params['ccy'] = ccy
        return await self._make_request('GET', '/api/v5/finance/savings/balance', params=params)

    @auto_log("okx", log_result=True)
    async def get_positions(self, inst_type: str = None) -> Optional[Dict[str, Any]]:
        """获取持仓信息 (GET /api/v5/account/positions)"""
        if not self._validate_config():
            return None
        params = {}
        if inst_type:
            params['instType'] = inst_type
        return await self._make_request('GET', '/api/v5/account/positions', params=params)

    @auto_log("okx", log_result=True)
    async def get_trades(self, inst_id: str = None, limit: int = 100) -> Optional[Dict[str, Any]]:
        """获取成交记录 (GET /api/v5/trade/orders-pending)"""
        if not self._validate_config():
            return None
        params = {'limit': str(limit)}
        if inst_id:
            params['instId'] = inst_id
        return await self._make_request('GET', '/api/v5/trade/orders-pending', params=params)

    @auto_log("database", log_result=True)
    async def sync_balances_to_db(self) -> Dict[str, Any]:
        """同步OKX余额数据到数据库（增量快照模式）"""
        from app.models.database import OKXBalance
        from app.utils.database import SessionLocal
        from datetime import datetime
        db = SessionLocal()
        try:
            trading_balances = await self.get_account_balance()
            asset_balances = await self.get_asset_balances()
            savings_balances = await self.get_savings_balance()
            total_inserted = 0
            now = datetime.now()
            # 交易账户
            trading_currencies = set()
            trading_account_ids = set()
            if trading_balances and trading_balances.get('data'):
                for account in trading_balances['data']:
                    acct_id = account.get('acctId', 'trading')
                    trading_account_ids.add(acct_id)
                    if 'details' in account:
                        for detail in account['details']:
                            currency = detail.get('ccy', '')
                            trading_currencies.add((acct_id, currency))
                            balance_data = {
                                "account_id": acct_id,
                                "currency": currency,
                                "available_balance": float(detail.get('availBal', 0)),
                                "frozen_balance": float(detail.get('frozenBal', 0)),
                                "total_balance": float(detail.get('eq', 0)),
                                "account_type": "trading",
                                "update_time": now
                            }
                            new_balance = OKXBalance(**balance_data)
                            db.add(new_balance)
                            total_inserted += 1
            # 检查历史上有但本次没有的币种，插入余额为0的快照（trading）
            history_trading = set([
                (b.account_id, b.currency) for b in db.query(OKXBalance.account_id, OKXBalance.currency).filter_by(account_type="trading").distinct()
            ])
            missing_trading = history_trading - trading_currencies
            for acct_id, currency in missing_trading:
                latest = db.query(OKXBalance).filter_by(
                    account_id=acct_id,
                    currency=currency,
                    account_type="trading"
                ).order_by(OKXBalance.update_time.desc(), OKXBalance.id.desc()).first()
                if latest and latest.total_balance != 0:
                    balance_data = {
                        "account_id": acct_id,
                        "currency": currency,
                        "available_balance": 0,
                        "frozen_balance": 0,
                        "total_balance": 0,
                        "account_type": "trading",
                        "update_time": now
                    }
                    db.add(OKXBalance(**balance_data))
                    total_inserted += 1
            # 资金账户
            funding_currencies = set()
            if asset_balances and asset_balances.get('data'):
                for balance in asset_balances['data']:
                    currency = balance.get('ccy', '')
                    funding_currencies.add(currency)
                    balance_data = {
                        "account_id": "funding",
                        "currency": currency,
                        "available_balance": float(balance.get('availBal', 0)),
                        "frozen_balance": float(balance.get('frozenBal', 0)),
                        "total_balance": float(balance.get('bal', 0)),
                        "account_type": "funding",
                        "update_time": now
                    }
                    new_balance = OKXBalance(**balance_data)
                    db.add(new_balance)
                    total_inserted += 1
            # 检查历史上有但本次没有的币种，插入余额为0的快照（funding）
            history_funding = set([
                b.currency for b in db.query(OKXBalance.currency).filter_by(account_id="funding", account_type="funding").distinct()
            ])
            missing_funding = history_funding - funding_currencies
            for currency in missing_funding:
                latest = db.query(OKXBalance).filter_by(
                    account_id="funding",
                    currency=currency,
                    account_type="funding"
                ).order_by(OKXBalance.update_time.desc(), OKXBalance.id.desc()).first()
                if latest and latest.total_balance != 0:
                    balance_data = {
                        "account_id": "funding",
                        "currency": currency,
                        "available_balance": 0,
                        "frozen_balance": 0,
                        "total_balance": 0,
                        "account_type": "funding",
                        "update_time": now
                    }
                    db.add(OKXBalance(**balance_data))
                    total_inserted += 1
            # 储蓄账户
            savings_currencies = set()
            if savings_balances and savings_balances.get('data'):
                for balance in savings_balances['data']:
                    currency = balance.get('ccy', '')
                    savings_currencies.add(currency)
                    balance_data = {
                        "account_id": "savings",
                        "currency": currency,
                        "available_balance": float(balance.get('amt', 0)),
                        "frozen_balance": 0,
                        "total_balance": float(balance.get('amt', 0)),
                        "account_type": "savings",
                        "update_time": now
                    }
                    new_balance = OKXBalance(**balance_data)
                    db.add(new_balance)
                    total_inserted += 1
            # 检查历史上有但本次没有的币种，插入余额为0的快照（savings）
            history_savings = set([
                b.currency for b in db.query(OKXBalance.currency).filter_by(account_id="savings", account_type="savings").distinct()
            ])
            missing_savings = history_savings - savings_currencies
            for currency in missing_savings:
                latest = db.query(OKXBalance).filter_by(
                    account_id="savings",
                    currency=currency,
                    account_type="savings"
                ).order_by(OKXBalance.update_time.desc(), OKXBalance.id.desc()).first()
                if latest and latest.total_balance != 0:
                    balance_data = {
                        "account_id": "savings",
                        "currency": currency,
                        "available_balance": 0,
                        "frozen_balance": 0,
                        "total_balance": 0,
                        "account_type": "savings",
                        "update_time": now
                    }
                    db.add(OKXBalance(**balance_data))
                    total_inserted += 1
            db.commit()
            return {
                "success": True,
                "message": f"余额快照同步完成，新增{total_inserted}条",
                "total_inserted": total_inserted
            }
        except Exception as e:
            db.rollback()
            logger.error(f"同步OKX余额数据失败: {e}")
            return {"success": False, "message": f"同步失败: {str(e)}"}
        finally:
            db.close()

    @auto_log("database", log_result=True)
    async def sync_transactions_to_db(self, days: int = 30) -> Dict[str, Any]:
        """同步OKX交易记录到数据库"""
        from app.models.database import OKXTransaction
        from app.utils.database import SessionLocal
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        try:
            # 获取账单流水
            bills = await self.get_bills(limit=1000)
            
            if not bills or not bills.get('data'):
                return {"success": False, "message": "未获取到交易数据"}
            
            total_new = 0
            total_updated = 0
            
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            for bill in bills['data']:
                # 解析时间戳
                bill_time = datetime.fromisoformat(bill.get('ts', '').replace('Z', '+00:00'))
                
                # 只处理指定时间范围内的记录
                if bill_time < start_time:
                    continue
                
                # 准备交易数据
                transaction_data = {
                    "transaction_id": bill.get('billId', ''),
                    "account_id": bill.get('acctId', ''),
                    "inst_type": bill.get('instType', ''),
                    "inst_id": bill.get('instId', ''),
                    "trade_id": bill.get('tradeId'),
                    "order_id": bill.get('ordId'),
                    "bill_id": bill.get('billId'),
                    "type": bill.get('type', ''),
                    "side": bill.get('side'),
                    "amount": float(bill.get('bal', 0)),
                    "currency": bill.get('ccy', ''),
                    "fee": float(bill.get('fee', 0)),
                    "fee_currency": bill.get('feeCcy'),
                    "price": float(bill.get('px', 0)) if bill.get('px') else None,
                    "quantity": float(bill.get('sz', 0)) if bill.get('sz') else None,
                    "timestamp": bill_time
                }
                
                # 检查是否已存在
                existing = db.query(OKXTransaction).filter_by(
                    transaction_id=transaction_data["transaction_id"]
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in transaction_data.items():
                        if key != 'transaction_id':  # 不更新唯一键
                            setattr(existing, key, value)
                    total_updated += 1
                else:
                    # 插入新记录
                    new_tx = OKXTransaction(**transaction_data)
                    db.add(new_tx)
                    total_new += 1
            
            db.commit()
            
            return {
                "success": True, 
                "message": f"交易记录同步完成，新增{total_new}条，更新{total_updated}条",
                "total_new": total_new,
                "total_updated": total_updated
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"同步OKX交易记录失败: {e}")
            return {"success": False, "message": f"同步失败: {str(e)}"}
        finally:
            db.close()

    @auto_log("database", log_result=True)
    async def sync_positions_to_db(self) -> Dict[str, Any]:
        """同步OKX持仓数据到数据库"""
        from app.models.database import OKXPosition
        from app.utils.database import SessionLocal
        from datetime import datetime
        
        db = SessionLocal()
        try:
            # 获取持仓信息
            positions = await self.get_positions()
            
            if not positions or not positions.get('data'):
                return {"success": False, "message": "未获取到持仓数据"}
            
            total_new = 0
            total_updated = 0
            current_time = datetime.now()
            
            for position in positions['data']:
                # 准备持仓数据
                position_data = {
                    "account_id": position.get('acctId', ''),
                    "inst_type": position.get('instType', ''),
                    "inst_id": position.get('instId', ''),
                    "position_side": position.get('posSide', ''),
                    "position_id": position.get('posId', ''),
                    "quantity": float(position.get('pos', 0)),
                    "avg_price": float(position.get('avgPx', 0)),
                    "unrealized_pnl": float(position.get('upl', 0)),
                    "realized_pnl": float(position.get('realizedPnl', 0)),
                    "margin_ratio": float(position.get('mgnRatio', 0)) if position.get('mgnRatio') else None,
                    "leverage": float(position.get('lever', 0)) if position.get('lever') else None,
                    "mark_price": float(position.get('markPx', 0)) if position.get('markPx') else None,
                    "liquidation_price": float(position.get('liqPx', 0)) if position.get('liqPx') else None,
                    "currency": position.get('ccy', ''),
                    "timestamp": current_time
                }
                
                # 检查是否已存在
                existing = db.query(OKXPosition).filter_by(
                    account_id=position_data["account_id"],
                    inst_id=position_data["inst_id"],
                    position_side=position_data["position_side"],
                    timestamp=position_data["timestamp"]
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in position_data.items():
                        if key not in ['account_id', 'inst_id', 'position_side', 'timestamp']:
                            setattr(existing, key, value)
                    total_updated += 1
                else:
                    # 插入新记录
                    new_position = OKXPosition(**position_data)
                    db.add(new_position)
                    total_new += 1
            
            db.commit()
            
            return {
                "success": True, 
                "message": f"持仓数据同步完成，新增{total_new}条，更新{total_updated}条",
                "total_new": total_new,
                "total_updated": total_updated
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"同步OKX持仓数据失败: {e}")
            return {"success": False, "message": f"同步失败: {str(e)}"}
        finally:
            db.close()

    @auto_log("database", log_result=True)
    async def sync_market_data_to_db(self, inst_ids: List[str] = None) -> Dict[str, Any]:
        """同步OKX市场数据到数据库"""
        from app.models.database import OKXMarketData
        from app.utils.database import SessionLocal
        from datetime import datetime
        
        db = SessionLocal()
        try:
            # 如果没有指定产品，获取所有SPOT产品
            if not inst_ids:
                instruments = await self.get_instruments('SPOT')
                if instruments and instruments.get('data'):
                    inst_ids = [inst['instId'] for inst in instruments['data'][:50]]  # 限制数量
                else:
                    inst_ids = ['BTC-USDT', 'ETH-USDT', 'LTC-USDT']  # 默认产品
            
            total_new = 0
            total_updated = 0
            current_time = datetime.now()
            
            for inst_id in inst_ids:
                # 获取单个产品行情
                ticker = await self.get_ticker(inst_id)
                
                if not ticker or not ticker.get('data'):
                    continue
                
                ticker_data = ticker['data'][0]
                
                # 准备市场数据
                market_data = {
                    "inst_id": inst_id,
                    "inst_type": "SPOT",
                    "last_price": float(ticker_data.get('last', 0)),
                    "bid_price": float(ticker_data.get('bidPx', 0)) if ticker_data.get('bidPx') else None,
                    "ask_price": float(ticker_data.get('askPx', 0)) if ticker_data.get('askPx') else None,
                    "high_24h": float(ticker_data.get('high24h', 0)) if ticker_data.get('high24h') else None,
                    "low_24h": float(ticker_data.get('low24h', 0)) if ticker_data.get('low24h') else None,
                    "volume_24h": float(ticker_data.get('vol24h', 0)) if ticker_data.get('vol24h') else None,
                    "change_24h": float(ticker_data.get('change24h', 0)) if ticker_data.get('change24h') else None,
                    "change_rate_24h": float(ticker_data.get('changeRate24h', 0)) if ticker_data.get('changeRate24h') else None,
                    "timestamp": current_time
                }
                
                # 检查是否已存在（同一时间戳）
                existing = db.query(OKXMarketData).filter_by(
                    inst_id=market_data["inst_id"],
                    timestamp=market_data["timestamp"]
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in market_data.items():
                        if key not in ['inst_id', 'timestamp']:
                            setattr(existing, key, value)
                    total_updated += 1
                else:
                    # 插入新记录
                    new_market_data = OKXMarketData(**market_data)
                    db.add(new_market_data)
                    total_new += 1
            
            db.commit()
            
            return {
                "success": True, 
                "message": f"市场数据同步完成，新增{total_new}条，更新{total_updated}条",
                "total_new": total_new,
                "total_updated": total_updated
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"同步OKX市场数据失败: {e}")
            return {"success": False, "message": f"同步失败: {str(e)}"}
        finally:
            db.close()

    @auto_log("okx", log_result=True)
    async def get_summary(self) -> Dict[str, Any]:
        """获取OKX账户汇总信息"""
        try:
            # 获取余额数据
            balances = await self.get_asset_balances()
            positions = await self.get_positions()
            bills = await self.get_bills(limit=100)
            
            # 计算总余额（USD）
            total_balance_usd = 0
            balance_by_currency = {}
            
            if balances and balances.get('data'):
                for balance in balances['data']:
                    for detail in balance.get('details', []):
                        currency = detail.get('ccy', '')
                        amount = float(detail.get('bal', 0))
                        balance_by_currency[currency] = amount
                        
                        # 简单转换为USD（实际应该使用汇率）
                        if currency == 'USDT' or currency == 'USD':
                            total_balance_usd += amount
                        elif currency == 'BTC':
                            total_balance_usd += amount * 50000  # 估算价格
                        elif currency == 'ETH':
                            total_balance_usd += amount * 3000   # 估算价格
            
            # 计算持仓数量
            position_count = len(positions.get('data', [])) if positions else 0
            
            # 计算24小时交易数量
            transaction_count_24h = len(bills.get('data', [])) if bills else 0
            
            # 计算未实现盈亏
            unrealized_pnl = 0
            realized_pnl = 0
            if positions and positions.get('data'):
                for position in positions['data']:
                    unrealized_pnl += float(position.get('upl', 0))
                    realized_pnl += float(position.get('realizedPnl', 0))
            
            return {
                "total_balance_usd": total_balance_usd,
                "total_balance_cny": total_balance_usd * 7.2,  # 简单汇率转换
                "balance_by_currency": balance_by_currency,
                "position_count": position_count,
                "transaction_count_24h": transaction_count_24h,
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": realized_pnl,
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取OKX汇总信息失败: {e}")
            return {
                "total_balance_usd": 0,
                "total_balance_cny": 0,
                "balance_by_currency": {},
                "position_count": 0,
                "transaction_count_24h": 0,
                "unrealized_pnl": 0,
                "realized_pnl": 0,
                "last_update": datetime.now().isoformat(),
                "error": str(e)
            } 