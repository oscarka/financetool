import httpx
import time
import hmac
import base64
import hashlib
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logger import log_okx_api

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

    async def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """获取账户资产信息"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', '/api/v5/account/balance')

    async def get_ticker(self, inst_id: str) -> Optional[Dict[str, Any]]:
        """获取某个币种行情"""
        params = {'instId': inst_id}
        return await self._make_request('GET', '/api/v5/market/ticker', params=params, auth_required=False)

    async def get_all_tickers(self, inst_type: str = 'SPOT') -> Optional[Dict[str, Any]]:
        """获取所有币种行情"""
        params = {'instType': inst_type}
        return await self._make_request('GET', '/api/v5/market/tickers', params=params, auth_required=False)

    async def get_instruments(self, inst_type: str = 'SPOT') -> Optional[Dict[str, Any]]:
        """获取交易产品基础信息"""
        params = {'instType': inst_type}
        return await self._make_request('GET', '/api/v5/public/instruments', params=params, auth_required=False)

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

    async def get_config(self) -> Dict[str, Any]:
        """获取当前配置信息"""
        return {
            "api_configured": bool(self.api_key and self.secret_key and self.passphrase),
            "sandbox_mode": self.sandbox,
            "base_url": self.base_url,
            "api_key_prefix": self.api_key[:10] + "..." if self.api_key else "未配置"
        }

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

    async def get_asset_balances(self, ccy: str = None) -> Optional[Dict[str, Any]]:
        """获取资金账户余额 (GET /api/v5/asset/balances)"""
        if not self._validate_config():
            return None
        params = {}
        if ccy:
            params['ccy'] = ccy
        return await self._make_request('GET', '/api/v5/asset/balances', params=params)

    async def get_savings_balance(self, ccy: str = None) -> Optional[Dict[str, Any]]:
        """获取储蓄账户余额 (GET /api/v5/finance/savings/balance)"""
        if not self._validate_config():
            return None
        params = {}
        if ccy:
            params['ccy'] = ccy
        return await self._make_request('GET', '/api/v5/finance/savings/balance', params=params) 