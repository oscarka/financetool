import httpx
import time
import hmac
import base64
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.settings import settings
from app.utils.logger import log_okx_api
from app.utils.auto_logger import auto_log
from app.utils.database import SessionLocal
from app.models.database import Web3Balance, Web3Token, Web3Transaction
import logging

# 创建logger实例
logger = logging.getLogger(__name__)

class Web3APIService:
    """Web3 API集成服务"""
    def __init__(self):
        self.api_key = settings.web3_api_key
        self.secret_key = settings.web3_api_secret
        self.project_id = settings.web3_project_id
        self.account_id = settings.web3_account_id
        # 处理passphrase中的特殊字符
        original_passphrase = settings.web3_passphrase
        self.passphrase = original_passphrase.replace('～', '~') if original_passphrase else ""
        self.base_url = "https://web3.okx.com"
        self.headers = {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
        }
        
        # 打印调试信息
        log_okx_api(f"Web3 API初始化: api_key={self.api_key[:10] if self.api_key else 'None'}..., project_id={self.project_id}", level="INFO")

    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        if not all([self.api_key, self.secret_key, self.passphrase, self.project_id, self.account_id]):
            log_okx_api("Web3 API配置不完整，请检查环境变量", level="ERROR")
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
            'OK-ACCESS-PROJECT': self.project_id,  # 添加项目ID到请求头
        })
        logger.debug(f"生成认证头: timestamp={timestamp}, sign={sign[:20]}...")
        return headers

    async def _make_request(self, method: str, path: str, params: Dict = None, body: str = "", auth_required: bool = True) -> Optional[Dict[str, Any]]:
        """统一的请求方法"""
        try:
            # 构建完整的请求路径，包括查询参数
            request_path = path
            if params:
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                request_path = f"{path}?{query_string}"
            
            url = self.base_url + request_path
            
            # 使用完整的请求路径进行签名计算
            headers = self._auth_headers(method, request_path, body) if auth_required else {}
            
            logger.info(f"请求Web3接口: {method} {url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == 'GET':
                    resp = await client.get(url, headers=headers)
                elif method.upper() == 'POST':
                    resp = await client.post(url, headers=headers, content=body)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                logger.info(f"Web3接口响应状态: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    logger.debug(f"Web3接口响应数据: {data}")
                    return data
                else:
                    logger.error(f"Web3接口错误: {resp.status_code}, {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Web3接口请求异常: {e}")
            return None

    @auto_log("web3", log_result=True)
    async def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """获取Web3账户余额信息"""
        if not self._validate_config():
            return None
        
        # 根据Web3 API文档，获取账户总价值
        path = "/api/v5/wallet/asset/total-value"
        params = {
            'projectId': self.project_id,
            'accountId': self.account_id
        }
        return await self._make_request('GET', path, params=params)

    @auto_log("web3", log_result=True)
    async def get_account_tokens(self) -> Optional[Dict[str, Any]]:
        """获取Web3账户代币列表"""
        if not self._validate_config():
            return None
        
        # 获取账户代币列表
        path = "/api/v5/wallet/asset/tokens"
        params = {
            'projectId': self.project_id,
            'accountId': self.account_id
        }
        return await self._make_request('GET', path, params=params)

    @auto_log("web3", log_result=True)
    async def get_account_transactions(self, limit: int = 100) -> Optional[Dict[str, Any]]:
        """获取Web3账户交易记录"""
        if not self._validate_config():
            return None
        
        # 获取账户交易记录
        path = "/api/v5/wallet/asset/transactions"
        params = {
            'projectId': self.project_id,
            'accountId': self.account_id,
            'limit': str(limit)
        }
        return await self._make_request('GET', path, params=params)

    @auto_log("system")
    async def get_config(self) -> Dict[str, Any]:
        """获取Web3 API配置信息"""
        return {
            "api_configured": bool(self.api_key and self.secret_key and self.passphrase and self.project_id and self.account_id),
            "base_url": self.base_url,
            "api_key_prefix": self.api_key[:10] + "..." if self.api_key else None,
            "project_id": self.project_id,
            "account_id": self.account_id
        }

    @auto_log("system")
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        try:
            # 测试私有接口
            private_ok = False
            private_error = None
            if self._validate_config():
                private_result = await self.get_account_balance()
                private_ok = private_result is not None and private_result.get('code') == '0'
                if not private_ok:
                    private_error = "认证失败或账户接口异常"
            else:
                private_error = "API配置不完整"
            
            return {
                "public_api": True,  # Web3 API主要是私有接口
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

    @auto_log("database", log_result=True)
    async def sync_balance_to_db(self) -> Dict[str, Any]:
        """同步Web3余额到数据库"""
        try:
            if not self._validate_config():
                return {"success": False, "error": "API配置不完整"}
            
            # 获取余额数据
            balance_data = await self.get_account_balance()
            if not balance_data or balance_data.get('code') != '0':
                return {"success": False, "error": "获取余额数据失败"}
            
            # 解析数据
            data_list = balance_data.get('data', [])
            if not data_list:
                return {"success": False, "error": "余额数据为空"}
            
            balance_info = data_list[0]
            total_value = float(balance_info.get('totalValue', 0))
            
            # 保存到数据库
            db = SessionLocal()
            try:
                # 检查是否已存在相同时间的记录
                existing = db.query(Web3Balance).filter(
                    Web3Balance.project_id == self.project_id,
                    Web3Balance.account_id == self.account_id,
                    Web3Balance.update_time == datetime.now().replace(microsecond=0)
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.total_value = total_value
                    existing.currency = "USD"
                else:
                    # 创建新记录
                    new_balance = Web3Balance(
                        project_id=self.project_id,
                        account_id=self.account_id,
                        total_value=total_value,
                        currency="USD",
                        update_time=datetime.now().replace(microsecond=0)
                    )
                    db.add(new_balance)
                
                db.commit()
                
                return {
                    "success": True,
                    "message": "Web3余额同步成功",
                    "total_value": total_value,
                    "currency": "USD"
                }
                
            except Exception as e:
                db.rollback()
                log_okx_api(f"Web3余额同步到数据库失败: {e}", level="ERROR")
                return {"success": False, "error": f"数据库操作失败: {str(e)}"}
            finally:
                db.close()
                
        except Exception as e:
            log_okx_api(f"Web3余额同步异常: {e}", level="ERROR")
            return {"success": False, "error": str(e)}

    @auto_log("database", log_result=True)
    async def sync_tokens_to_db(self) -> Dict[str, Any]:
        """同步Web3代币到数据库"""
        try:
            if not self._validate_config():
                return {"success": False, "error": "API配置不完整"}
            
            # 获取代币数据
            tokens_data = await self.get_account_tokens()
            if not tokens_data or tokens_data.get('code') != '0':
                return {"success": False, "error": "获取代币数据失败"}
            
            # 解析数据
            data_list = tokens_data.get('data', [])
            if not data_list:
                return {"success": False, "error": "代币数据为空"}
            
            # 保存到数据库
            db = SessionLocal()
            try:
                update_time = datetime.now().replace(microsecond=0)
                
                for token_info in data_list:
                    token_symbol = token_info.get('symbol', '')
                    token_name = token_info.get('name', '')
                    token_address = token_info.get('contractAddress', '')
                    balance = float(token_info.get('balance', 0))
                    value_usd = float(token_info.get('valueUsd', 0))
                    price_usd = float(token_info.get('priceUsd', 0)) if token_info.get('priceUsd') else None
                    
                    # 检查是否已存在相同时间的记录
                    existing = db.query(Web3Token).filter(
                        Web3Token.project_id == self.project_id,
                        Web3Token.account_id == self.account_id,
                        Web3Token.token_symbol == token_symbol,
                        Web3Token.update_time == update_time
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.balance = balance
                        existing.value_usd = value_usd
                        existing.price_usd = price_usd
                    else:
                        # 创建新记录
                        new_token = Web3Token(
                            project_id=self.project_id,
                            account_id=self.account_id,
                            token_symbol=token_symbol,
                            token_name=token_name,
                            token_address=token_address,
                            balance=balance,
                            value_usd=value_usd,
                            price_usd=price_usd,
                            update_time=update_time
                        )
                        db.add(new_token)
                
                db.commit()
                
                return {
                    "success": True,
                    "message": "Web3代币同步成功",
                    "tokens_count": len(data_list)
                }
                
            except Exception as e:
                db.rollback()
                log_okx_api(f"Web3代币同步到数据库失败: {e}", level="ERROR")
                return {"success": False, "error": f"数据库操作失败: {str(e)}"}
            finally:
                db.close()
                
        except Exception as e:
            log_okx_api(f"Web3代币同步异常: {e}", level="ERROR")
            return {"success": False, "error": str(e)}

    @auto_log("database", log_result=True)
    async def sync_transactions_to_db(self, limit: int = 100) -> Dict[str, Any]:
        """同步Web3交易记录到数据库"""
        try:
            if not self._validate_config():
                return {"success": False, "error": "API配置不完整"}
            
            # 获取交易数据
            transactions_data = await self.get_account_transactions(limit=limit)
            if not transactions_data or transactions_data.get('code') != '0':
                return {"success": False, "error": "获取交易数据失败"}
            
            # 解析数据
            data_list = transactions_data.get('data', [])
            if not data_list:
                return {"success": False, "error": "交易数据为空"}
            
            # 保存到数据库
            db = SessionLocal()
            try:
                inserted_count = 0
                updated_count = 0
                
                for tx_info in data_list:
                    transaction_hash = tx_info.get('hash', '')
                    if not transaction_hash:
                        continue
                    
                    # 检查是否已存在
                    existing = db.query(Web3Transaction).filter(
                        Web3Transaction.transaction_hash == transaction_hash
                    ).first()
                    
                    if existing:
                        updated_count += 1
                        continue
                    
                    # 创建新记录
                    new_transaction = Web3Transaction(
                        project_id=self.project_id,
                        account_id=self.account_id,
                        transaction_hash=transaction_hash,
                        block_number=tx_info.get('blockNumber'),
                        from_address=tx_info.get('from'),
                        to_address=tx_info.get('to'),
                        token_symbol=tx_info.get('tokenSymbol'),
                        amount=float(tx_info.get('amount', 0)),
                        value_usd=float(tx_info.get('valueUsd', 0)) if tx_info.get('valueUsd') else None,
                        gas_used=float(tx_info.get('gasUsed', 0)) if tx_info.get('gasUsed') else None,
                        gas_price=float(tx_info.get('gasPrice', 0)) if tx_info.get('gasPrice') else None,
                        transaction_type=tx_info.get('type'),
                        status=tx_info.get('status', 'success'),
                        timestamp=datetime.fromtimestamp(int(tx_info.get('timestamp', 0)))
                    )
                    db.add(new_transaction)
                    inserted_count += 1
                
                db.commit()
                
                return {
                    "success": True,
                    "message": "Web3交易记录同步成功",
                    "inserted_count": inserted_count,
                    "updated_count": updated_count
                }
                
            except Exception as e:
                db.rollback()
                log_okx_api(f"Web3交易记录同步到数据库失败: {e}", level="ERROR")
                return {"success": False, "error": f"数据库操作失败: {str(e)}"}
            finally:
                db.close()
                
        except Exception as e:
            log_okx_api(f"Web3交易记录同步异常: {e}", level="ERROR")
            return {"success": False, "error": str(e)}