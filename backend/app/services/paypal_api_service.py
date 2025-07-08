import httpx
import time
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from app.config import settings
from loguru import logger
from app.utils.database import SessionLocal
import sqlalchemy
import re


class PayPalAPIService:
    """PayPal API集成服务"""
    
    def __init__(self):
        self.client_id = settings.paypal_client_id if hasattr(settings, 'paypal_client_id') else "Ae89JqKPrJ6lLJz1dfIHqZr2VLbjrMCuT7A7Ul99NTWSJrDA93T5R-GZQ45ZkSBgZZDSUCIJVgnanqbE"
        self.client_secret = settings.paypal_client_secret if hasattr(settings, 'paypal_client_secret') else "EGIgD2Of3L5IR80GB9JcRoXuSsDXeVyhv6CtdvHyqhJLkaPFQC9KK5BCVj7cL_DN32r8wGw8pyBpZ6yO"
        self.base_url = "https://api-m.sandbox.paypal.com"  # 沙盒环境
        self.access_token = None
        self.token_expires_at = None
        logger.info(f"PayPal API初始化: client_id={self.client_id[:10] if self.client_id else 'None'}...")

    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        if not self.client_id or not self.client_secret:
            logger.error("PayPal API Client ID或Secret未配置，请检查环境变量")
            return False
        return True

    async def _get_access_token(self) -> Optional[str]:
        """获取访问令牌，使用OAuth 2.0客户端凭证流"""
        try:
            # 检查是否有有效的token
            if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
                return self.access_token

            # 使用基本认证头
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = "grant_type=client_credentials"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(f"{self.base_url}/v1/oauth2/token", headers=headers, content=data)
                
                if resp.status_code == 200:
                    token_data = resp.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 60  # 提前60秒过期
                    logger.info("PayPal访问令牌获取成功")
                    return self.access_token
                else:
                    logger.error(f"PayPal Token获取失败: {resp.status_code}, {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"PayPal Token获取异常: {e}")
            return None

    async def _make_request(self, method: str, path: str, params: Dict = None, body: Dict = None) -> Optional[Dict[str, Any]]:
        """统一的请求方法"""
        try:
            if not self._validate_config():
                return None

            # 获取访问令牌
            token = await self._get_access_token()
            if not token:
                return None

            url = self.base_url + path
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"请求PayPal接口: {method} {url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == 'GET':
                    resp = await client.get(url, headers=headers, params=params)
                elif method.upper() == 'POST':
                    resp = await client.post(url, headers=headers, json=body)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                logger.info(f"PayPal接口响应状态: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    logger.debug(f"PayPal接口响应数据: {data}")
                    return data
                else:
                    logger.error(f"PayPal接口错误: {resp.status_code}, {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"PayPal接口请求异常: {e}")
            return None

    async def get_config(self) -> Dict[str, Any]:
        """获取当前配置信息"""
        return {
            "api_configured": bool(self.client_id and self.client_secret),
            "base_url": self.base_url,
            "client_id_prefix": self.client_id[:10] + "..." if self.client_id else "未配置",
            "environment": "sandbox" if "sandbox" in self.base_url else "live"
        }

    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        try:
            # 测试获取访问令牌
            token = await self._get_access_token()
            if not token:
                return {
                    "token_auth": False,
                    "balance_api": False,
                    "transaction_api": False,
                    "error": "无法获取访问令牌",
                    "timestamp": time.time()
                }

            # 测试余额接口
            balance_ok = False
            balance_error = None
            try:
                balance_result = await self.get_balance_accounts()
                balance_ok = balance_result is not None
            except Exception as e:
                balance_error = str(e)

            # 测试交易接口
            transaction_ok = False
            transaction_error = None
            try:
                # 测试最近7天的交易
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                transaction_result = await self.get_transactions(
                    start_date.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                )
                transaction_ok = transaction_result is not None
            except Exception as e:
                transaction_error = str(e)
            
            return {
                "token_auth": True,
                "balance_api": balance_ok,
                "transaction_api": transaction_ok,
                "balance_error": balance_error,
                "transaction_error": transaction_error,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "token_auth": False,
                "balance_api": False,
                "transaction_api": False,
                "error": str(e),
                "timestamp": time.time()
            }

    async def get_balance_accounts(self) -> Optional[Dict[str, Any]]:
        """获取PayPal余额账户"""
        return await self._make_request('GET', '/v2/wallet/balance-accounts')

    async def get_all_balances(self) -> List[Dict[str, Any]]:
        """获取所有余额信息，格式化为统一格式"""
        try:
            if not self._validate_config():
                logger.error("[PayPal] 配置无效，无法获取账户余额")
                return []

            balance_result = await self.get_balance_accounts()
            logger.info(f"[PayPal] 获取到balance_accounts: {balance_result}")
            
            if not balance_result:
                logger.warning("[PayPal] balance_accounts为空")
                return []

            all_balances = []
            balance_accounts = balance_result.get('balance_accounts', [])
            
            for balance in balance_accounts:
                available = balance.get('available', {})
                reserved = balance.get('reserved', {})
                
                all_balances.append({
                    "account_id": f"paypal_{available.get('currency_code', 'UNKNOWN')}",
                    "currency": available.get('currency_code', 'UNKNOWN'),
                    "available_balance": float(available.get('value', 0)),
                    "reserved_balance": float(reserved.get('value', 0)),
                    "total_balance": float(available.get('value', 0)) + float(reserved.get('value', 0)),
                    "type": "PAYPAL_WALLET",
                    "name": f"PayPal {available.get('currency_code', 'UNKNOWN')} 账户",
                    "primary": available.get('currency_code') == 'USD',  # 假设USD为主要货币
                    "update_time": datetime.now().isoformat()
                })
            
            # 添加总计信息
            total_available = balance_result.get('total_available', {})
            total_reserved = balance_result.get('total_reserved', {})
            
            if total_available.get('currency_code'):
                all_balances.append({
                    "account_id": "paypal_total",
                    "currency": total_available.get('currency_code', 'USD'),
                    "available_balance": float(total_available.get('value', 0)),
                    "reserved_balance": float(total_reserved.get('value', 0)),
                    "total_balance": float(total_available.get('value', 0)) + float(total_reserved.get('value', 0)),
                    "type": "TOTAL_SUMMARY",
                    "name": "PayPal 总计",
                    "primary": True,
                    "update_time": datetime.now().isoformat()
                })
            
            logger.info(f"[PayPal] all_balances最终结果: {all_balances}")
            return all_balances
        except Exception as e:
            logger.error(f"获取PayPal所有账户余额失败: {e}")
            return []

    async def get_transactions(self, start_date: str, end_date: str, page_size: int = 100, page: int = 1) -> Optional[Dict[str, Any]]:
        """获取交易记录"""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "page_size": page_size,
            "page": page,
            "fields": "all"  # 获取所有字段
        }
        return await self._make_request('GET', '/v1/reporting/transactions', params=params)

    async def get_recent_transactions(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近的交易记录"""
        try:
            if not self._validate_config():
                logger.error("[PayPal] 配置无效，无法获取交易记录")
                return []
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 格式化日期为PayPal API要求的格式
            start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S-0700')  # Pacific Time
            end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S-0700')
            
            logger.info(f"[PayPal] 获取交易记录: {start_date_str} 到 {end_date_str}")
            
            all_transactions = []
            page = 1
            
            while True:
                transactions_result = await self.get_transactions(
                    start_date_str, 
                    end_date_str, 
                    page_size=100, 
                    page=page
                )
                
                if not transactions_result:
                    break
                
                transaction_details = transactions_result.get('transaction_details', [])
                if not transaction_details:
                    break
                
                logger.info(f"[PayPal] 第{page}页获取到 {len(transaction_details)} 条交易记录")
                
                for transaction in transaction_details:
                    transaction_info = transaction.get('transaction_info', {})
                    payer_info = transaction.get('payer_info', {})
                    
                    # 解析交易金额
                    transaction_amount = transaction_info.get('transaction_amount', {})
                    amount_value = float(transaction_amount.get('value', 0))
                    currency = transaction_amount.get('currency_code', 'USD')
                    
                    # 确定交易类型（收入/支出）
                    transaction_type = 'credit' if amount_value > 0 else 'debit'
                    
                    all_transactions.append({
                        "transaction_id": transaction_info.get('transaction_id'),
                        "paypal_account_id": transaction_info.get('paypal_account_id'),
                        "type": transaction_type,
                        "amount": abs(amount_value),  # 使用绝对值，类型通过type字段区分
                        "currency": currency,
                        "description": transaction_info.get('transaction_subject', '') or transaction_info.get('transaction_note', ''),
                        "status": self._format_transaction_status(transaction_info.get('transaction_status')),
                        "date": transaction_info.get('transaction_initiation_date'),
                        "update_date": transaction_info.get('transaction_updated_date'),
                        "reference_number": transaction_info.get('paypal_reference_id'),
                        "fee_amount": float(transaction_info.get('fee_amount', {}).get('value', 0)),
                        "payer_email": payer_info.get('email_address'),
                        "payer_name": self._format_payer_name(payer_info.get('payer_name', {})),
                        "event_code": transaction_info.get('transaction_event_code'),
                        "custom_field": transaction_info.get('custom_field'),
                        "invoice_id": transaction_info.get('invoice_id')
                    })
                
                # 检查是否还有更多页面
                total_pages = transactions_result.get('total_pages', 1)
                if page >= total_pages:
                    break
                page += 1
            
            # 按日期排序
            all_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
            logger.info(f"[PayPal] 最终获取到 {len(all_transactions)} 条交易记录")
            return all_transactions
        except Exception as e:
            logger.error(f"获取PayPal最近交易记录失败: {e}")
            return []

    def _format_transaction_status(self, status: str) -> str:
        """格式化交易状态"""
        status_mapping = {
            'S': 'completed',
            'P': 'pending', 
            'D': 'denied',
            'V': 'reversed'
        }
        return status_mapping.get(status, status.lower() if status else 'unknown')

    def _format_payer_name(self, payer_name: Dict) -> str:
        """格式化付款人姓名"""
        if not payer_name:
            return ""
        
        given_name = payer_name.get('given_name', '')
        surname = payer_name.get('surname', '')
        full_name = payer_name.get('full_name', '')
        alternate_name = payer_name.get('alternate_full_name', '')
        
        if full_name:
            return full_name
        elif given_name and surname:
            return f"{given_name} {surname}"
        elif alternate_name:
            return alternate_name
        else:
            return given_name or surname or ""

    async def get_account_summary(self) -> Dict[str, Any]:
        """获取账户汇总信息"""
        try:
            # 获取余额信息
            balances = await self.get_all_balances()
            
            # 获取最近7天的交易
            recent_transactions = await self.get_recent_transactions(7)
            
            # 计算统计数据
            total_accounts = len([b for b in balances if b.get('type') != 'TOTAL_SUMMARY'])
            currencies = list(set([b.get('currency') for b in balances if b.get('currency')]))
            total_balance = sum([b.get('total_balance', 0) for b in balances if b.get('type') != 'TOTAL_SUMMARY'])
            
            # 按货币分组余额
            balance_by_currency = {}
            for balance in balances:
                if balance.get('type') != 'TOTAL_SUMMARY':
                    currency = balance.get('currency')
                    if currency:
                        balance_by_currency[currency] = balance_by_currency.get(currency, 0) + balance.get('total_balance', 0)
            
            return {
                "total_accounts": total_accounts,
                "total_currencies": len(currencies),
                "total_balance": total_balance,
                "recent_transactions_count": len(recent_transactions),
                "balance_by_currency": balance_by_currency,
                "supported_currencies": currencies,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取PayPal账户汇总失败: {e}")
            return {
                "total_accounts": 0,
                "total_currencies": 0,
                "total_balance": 0,
                "recent_transactions_count": 0,
                "balance_by_currency": {},
                "supported_currencies": [],
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            }

    async def get_balances_list(self) -> Optional[Dict[str, Any]]:
        """获取所有余额信息（使用reporting API）"""
        return await self._make_request('GET', '/v1/reporting/balances')