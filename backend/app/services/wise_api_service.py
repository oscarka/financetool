import httpx
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from app.config import settings
from loguru import logger
from app.utils.database import SessionLocal
from app.models.database import WiseTransaction
import sqlalchemy
import re


class WiseAPIService:
    """Wise API集成服务"""
    
    def __init__(self):
        self.api_token = settings.wise_api_token
        self.base_url = "https://api.transferwise.com"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        logger.info(f"Wise API初始化: token={self.api_token[:10] if self.api_token else 'None'}...")

    def _validate_config(self) -> bool:
        """验证API配置是否完整"""
        if not self.api_token:
            logger.error("Wise API Token未配置，请检查环境变量")
            return False
        return True

    async def _make_request(self, method: str, path: str, params: Dict = None, body: Dict = None) -> Optional[Dict[str, Any]]:
        """统一的请求方法"""
        try:
            url = self.base_url + path
            if params:
                url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            # 只在debug模式下记录请求详情
            logger.debug(f"请求Wise接口: {method} {url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == 'GET':
                    resp = await client.get(url, headers=self.headers)
                elif method.upper() == 'POST':
                    resp = await client.post(url, headers=self.headers, json=body)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                # 只在非200状态或debug模式下记录响应状态
                if resp.status_code != 200:
                    logger.warning(f"Wise接口响应状态: {resp.status_code}")
                else:
                    logger.debug(f"Wise接口响应状态: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    logger.debug(f"Wise接口响应数据: {data}")
                    return data
                else:
                    logger.error(f"Wise接口错误: {resp.status_code}, {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Wise接口请求异常: {e}")
            return None

    async def get_profile(self) -> Optional[Dict[str, Any]]:
        """获取用户资料信息"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', '/v1/profiles')

    async def get_accounts(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """获取账户列表"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', f'/v3/profiles/{profile_id}/borderless-accounts')

    async def get_account_balance(self, profile_id: str, account_id: str) -> Optional[Dict[str, Any]]:
        """获取账户余额"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', f'/v3/profiles/{profile_id}/borderless-accounts/{account_id}/balances')

    async def get_transactions(self, profile_id: str, account_id: str, limit: int = 50, offset: int = 0) -> Optional[Dict[str, Any]]:
        """获取交易记录"""
        if not self._validate_config():
            return None
        params = {
            'limit': str(limit),
            'offset': str(offset)
        }
        return await self._make_request('GET', f'/v3/profiles/{profile_id}/borderless-accounts/{account_id}/activities', params=params)

    async def get_exchange_rates(self, source: str = "USD", target: str = "CNY") -> Optional[Dict[str, Any]]:
        """获取汇率信息"""
        if not self._validate_config():
            return None
        params = {
            'source': source,
            'target': target
        }
        return await self._make_request('GET', '/v1/rates', params=params)

    async def get_historical_rates(self, source: str, target: str, from_date: str, to_date: str, interval: int = 24) -> Optional[Dict[str, Any]]:
        """获取历史汇率"""
        if not self._validate_config():
            return None
        params = {
            'source': source,
            'target': target,
            'from': from_date,
            'to': to_date,
            'interval': str(interval)
        }
        return await self._make_request('GET', '/v1/rates', params=params)

    async def get_available_currencies(self) -> Optional[Dict[str, Any]]:
        """获取可用货币列表"""
        if not self._validate_config():
            return None
        return await self._make_request('GET', '/v1/rates')

    async def get_config(self) -> Dict[str, Any]:
        """获取当前配置信息"""
        return {
            "api_configured": bool(self.api_token),
            "base_url": self.base_url,
            "token_prefix": self.api_token[:10] + "..." if self.api_token else "未配置"
        }

    async def test_connection(self) -> Dict[str, Any]:
        """测试连接状态"""
        try:
            # 测试公共接口（汇率）
            public_result = await self.get_exchange_rates("USD", "CNY")
            public_ok = public_result is not None
            
            # 测试私有接口（用户资料）
            private_ok = False
            private_error = None
            if self._validate_config():
                private_result = await self.get_profile()
                private_ok = private_result is not None
                if not private_ok:
                    private_error = "认证失败或用户资料接口异常"
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

    async def get_all_account_balances(self) -> List[Dict[str, Any]]:
        """获取所有账户余额，自动合并STANDARD、SAVINGS、JAR类型"""
        try:
            if not self._validate_config():
                logger.error("[Wise] 配置无效，无法获取账户余额")
                return []
            profiles = await self.get_profile()
            logger.info(f"[Wise] 获取到{len(profiles) if profiles else 0}个profile")
            logger.debug(f"[Wise] profiles详情: {profiles}")
            if not profiles:
                logger.warning("[Wise] profiles为空")
                return []
            all_balances = []
            types_list = ["STANDARD", "SAVINGS", "JAR"]
            for profile in profiles:
                profile_id = profile.get('id')
                if not profile_id:
                    logger.warning(f"[Wise] profile缺少id: {profile}")
                    continue
                for types in types_list:
                    balances = await self.get_balances(profile_id, types=types)
                    logger.info(f"[Wise] profile_id={profile_id} types={types} 获取到{len(balances) if balances else 0}个余额")
                    logger.debug(f"[Wise] balances详情: {balances}")
                    if not balances:
                        continue
                    for balance in balances:
                        balance_id = balance.get('id')
                        if not balance_id:
                            logger.warning(f"[Wise] balance缺少id: {balance}")
                            continue
                        all_balances.append({
                            "account_id": balance_id,
                            "currency": balance.get('currency'),
                            "available_balance": float(balance.get('amount', {}).get('value', 0)),
                            "reserved_balance": float(balance.get('reservedAmount', {}).get('value', 0)),
                            "cash_amount": float(balance.get('cashAmount', {}).get('value', 0)),
                            "total_worth": float(balance.get('totalWorth', {}).get('value', 0)),
                            "type": balance.get('type'),
                            "name": balance.get('name'),
                            "icon": balance.get('icon'),
                            "investment_state": balance.get('investmentState'),
                            "creation_time": balance.get('creationTime'),
                            "modification_time": balance.get('modificationTime'),
                            "visible": balance.get('visible'),
                            "primary": balance.get('primary'),
                            "update_time": datetime.now().isoformat()
                        })
            logger.info(f"[Wise] all_balances最终结果: {all_balances}")
            return all_balances
        except Exception as e:
            logger.error(f"获取所有账户余额失败: {e}")
            return []

    async def get_recent_transactions(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近的交易记录，使用正确的activities接口"""
        try:
            if not self._validate_config():
                logger.error("[Wise] 配置无效，无法获取交易记录")
                return []
            
            # 获取用户资料
            profiles = await self.get_profile()
            logger.info(f"[Wise] 获取到profiles: {profiles}")
            if not profiles:
                logger.warning("[Wise] profiles为空")
                return []
            
            all_transactions = []
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            for profile in profiles:
                profile_id = profile.get('id')
                if not profile_id:
                    logger.warning(f"[Wise] profile缺少id: {profile}")
                    continue
                
                logger.info(f"[Wise] 开始获取profile {profile_id} 的活动记录")
                
                # 使用正确的 /v1/profiles/{profileId}/activities 接口
                try:
                    activities_result = await self.get_profile_activities(profile_id, limit=100)
                    if activities_result and 'activities' in activities_result:
                        activities = activities_result['activities']
                        logger.info(f"[Wise] 获取到 {len(activities)} 条活动记录")
                        
                        for activity in activities:
                            created_on = activity.get('createdOn')
                            if created_on and created_on >= from_date:
                                # 解析金额信息
                                primary_amount = activity.get('primaryAmount', '')
                                amount_value = 0.0
                                currency = 'USD'
                                
                                # 解析金额字符串，如 "+ 279.77 AUD" 或 "3.27 USD"
                                if primary_amount:
                                    import re
                                    # 匹配金额和货币
                                    amount_match = re.search(r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})', primary_amount)
                                    if amount_match:
                                        amount_str = amount_match.group(1).replace(' ', '')
                                        currency = amount_match.group(2)
                                        try:
                                            amount_value = float(amount_str)
                                        except ValueError:
                                            amount_value = 0.0
                                
                                all_transactions.append({
                                    "profile_id": profile_id,
                                    "account_id": activity.get('resource', {}).get('id', ''),
                                    "transaction_id": activity.get('id'),
                                    "type": activity.get('type'),
                                    "amount": amount_value,
                                    "currency": currency,
                                    "description": activity.get('description', ''),
                                    "title": activity.get('title', ''),
                                    "date": created_on,
                                    "status": activity.get('status'),
                                    "reference_number": activity.get('resource', {}).get('id', '')
                                })
                    else:
                        logger.warning(f"[Wise] profile {profile_id} 没有活动记录")
                        
                except Exception as e:
                    logger.error(f"[Wise] 获取profile {profile_id} 活动记录失败: {e}")
            
            # 按日期排序
            all_transactions.sort(key=lambda x: x['date'], reverse=True)
            logger.info(f"[Wise] 最终获取到 {len(all_transactions)} 条交易记录")
            return all_transactions
        except Exception as e:
            logger.error(f"获取最近交易记录失败: {e}")
            return []

    async def get_multi_currency_eligibility(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """检查多币种账户开通资格"""
        if not self._validate_config():
            return None
        # 注意：沙盒环境和正式环境base_url不同，如需支持沙盒可加参数
        path = f"/v4/multi-currency-account/eligibility"
        params = {"profileId": profile_id}
        return await self._make_request('GET', path, params=params)

    async def get_balance_statement(self, profile_id: str, balance_id: str, currency: str = "EUR", interval_start: str = None, interval_end: str = None, statement_type: str = "COMPACT") -> Optional[Dict[str, Any]]:
        """获取账户余额对账单"""
        if not self._validate_config():
            return None
        
        # 如果没有指定时间范围，默认获取最近30天
        if not interval_start:
            interval_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        if not interval_end:
            interval_end = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.999Z')
        
        path = f"/v1/profiles/{profile_id}/balance-statements/{balance_id}/statement.json"
        params = {
            "currency": currency,
            "intervalStart": interval_start,
            "intervalEnd": interval_end,
            "type": statement_type
        }
        return await self._make_request('GET', path, params=params)

    async def get_all_balance_statements(self, currency: str = "EUR", days: int = 30) -> List[Dict[str, Any]]:
        """获取所有账户的余额对账单"""
        try:
            if not self._validate_config():
                return []
            
            # 获取用户资料
            profiles = await self.get_profile()
            if not profiles:
                return []
            
            all_statements = []
            interval_start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            interval_end = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.999Z')
            
            for profile in profiles:
                profile_id = profile.get('id')
                if not profile_id:
                    continue
                
                # 获取账户列表
                accounts = await self.get_accounts(profile_id)
                if not accounts:
                    continue
                
                for account in accounts:
                    account_id = account.get('id')
                    if not account_id:
                        continue
                    
                    # 获取余额对账单
                    statement = await self.get_balance_statement(
                        profile_id, 
                        account_id, 
                        currency, 
                        interval_start, 
                        interval_end
                    )
                    if statement:
                        all_statements.append({
                            "profile_id": profile_id,
                            "account_id": account_id,
                            "statement": statement,
                            "currency": currency,
                            "period": {
                                "start": interval_start,
                                "end": interval_end
                            }
                        })
            
            return all_statements
        except Exception as e:
            logger.error(f"获取所有余额对账单失败: {e}")
            return []

    async def get_balances(self, profile_id: str, types: str = "STANDARD") -> Optional[Dict[str, Any]]:
        """获取多币种账户余额列表"""
        if not self._validate_config():
            return None
        path = f"/v4/profiles/{profile_id}/balances"
        params = {"types": types}
        return await self._make_request('GET', path, params=params)

    async def get_balance_by_id(self, profile_id: str, balance_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取特定余额账户"""
        if not self._validate_config():
            return None
        path = f"/v4/profiles/{profile_id}/balances/{balance_id}"
        return await self._make_request('GET', path)

    async def create_balance(self, profile_id: str, currency: str, balance_type: str = "STANDARD", name: str = None) -> Optional[Dict[str, Any]]:
        """创建新的余额账户"""
        if not self._validate_config():
            return None
        path = f"/v4/profiles/{profile_id}/balances"
        body = {
            "currency": currency,
            "type": balance_type
        }
        if name:
            body["name"] = name
        return await self._make_request('POST', path, body=body)

    async def test_aud_transactions(self) -> Optional[Dict[str, Any]]:
        """测试AUD账户交易记录"""
        if not self._validate_config():
            return None
        
        profile_id = "71376028"
        balance_id = "124405547"
        
        logger.info(f"[Wise] 开始测试AUD账户交易记录: profile_id={profile_id}, balance_id={balance_id}")
        
        # 方法1: 尝试 /v4/profiles/{profileId}/balances/{balanceId}/transactions
        try:
            path1 = f"/v4/profiles/{profile_id}/balances/{balance_id}/transactions"
            logger.info(f"[Wise] 尝试接口1: {path1}")
            result1 = await self._make_request('GET', path1)
            if result1:
                logger.info(f"[Wise] 接口1成功: {result1}")
                return {"method": "v4_transactions", "data": result1}
        except Exception as e:
            logger.error(f"[Wise] 接口1失败: {e}")
        
        # 方法2: 尝试 /v1/profiles/{profileId}/balance-statements/{balanceId}/statement.json
        try:
            path2 = f"/v1/profiles/{profile_id}/balance-statements/{balance_id}/statement.json"
            params2 = {
                "currency": "AUD",
                "intervalStart": "2025-06-01T00:00:00.000Z",
                "intervalEnd": "2025-07-06T23:59:59.999Z"
            }
            logger.info(f"[Wise] 尝试接口2: {path2}")
            result2 = await self._make_request('GET', path2, params=params2)
            if result2:
                logger.info(f"[Wise] 接口2成功: {result2}")
                return {"method": "v1_statement", "data": result2}
        except Exception as e:
            logger.error(f"[Wise] 接口2失败: {e}")
        
        # 方法3: 尝试 /v3/profiles/{profileId}/borderless-accounts/{accountId}/activities
        try:
            path3 = f"/v3/profiles/{profile_id}/borderless-accounts/{balance_id}/activities"
            logger.info(f"[Wise] 尝试接口3: {path3}")
            result3 = await self._make_request('GET', path3)
            if result3:
                logger.info(f"[Wise] 接口3成功: {result3}")
                return {"method": "v3_activities", "data": result3}
        except Exception as e:
            logger.error(f"[Wise] 接口3失败: {e}")
        
        logger.error("[Wise] 所有接口都失败了")
        return None

    async def get_profile_activities(self, profile_id: str, limit: int = 100, offset: int = 0) -> Optional[Dict[str, Any]]:
        """获取用户所有活动记录"""
        if not self._validate_config():
            return None
        
        logger.info(f"[Wise] 获取用户活动记录: profile_id={profile_id}")
        path = f"/v1/profiles/{profile_id}/activities"
        params = {
            "limit": limit,
            "offset": offset
        }
        return await self._make_request('GET', path, params=params)

    async def sync_all_transactions_to_db(self, days: int = 365) -> Dict[str, Any]:
        """主动拉取所有profile的所有活动，批量写入wise_transactions表，已存在的自动跳过"""
        from app.utils.database import SessionLocal
        from app.models.database import WiseTransaction
        import sqlalchemy
        import re
        from datetime import datetime
        db = SessionLocal()
        try:
            profiles = await self.get_profile()
            if not profiles:
                return {"success": False, "message": "未获取到Wise profile"}
            total_new = 0
            for profile in profiles:
                profile_id = profile.get('id')
                if not profile_id:
                    continue
                # 拉取全部活动（可根据需要调整limit）
                offset = 0
                limit = 100
                fetched = 0
                while True:
                    activities_result = await self.get_profile_activities(profile_id, limit=limit, offset=offset)
                    if not activities_result or 'activities' not in activities_result:
                        break
                    activities = activities_result['activities']
                    if not activities:
                        break
                    for activity in activities:
                        created_on = activity.get('createdOn')
                        # 修复：将字符串转为datetime对象
                        created_on_dt = None
                        if created_on:
                            try:
                                # 支持带Z的ISO格式
                                created_on_dt = datetime.fromisoformat(created_on.replace('Z', '+00:00'))
                            except Exception:
                                created_on_dt = None
                        primary_amount = activity.get('primaryAmount', '')
                        amount_value = 0.0
                        currency = 'USD'
                        if primary_amount:
                            amount_match = re.search(r'([+-]?\s*\d+\.?\d*)\s*([A-Z]{3})', primary_amount)
                            if amount_match:
                                amount_str = amount_match.group(1).replace(' ', '')
                                currency = amount_match.group(2)
                                try:
                                    amount_value = float(amount_str)
                                except ValueError:
                                    amount_value = 0.0
                        # 检查是否已存在
                        exists = db.query(WiseTransaction).filter_by(transaction_id=activity.get('id')).first()
                        if exists:
                            continue
                        # 新增
                        tx = WiseTransaction(
                            profile_id=str(profile_id),
                            account_id=activity.get('resource', {}).get('id', ''),
                            transaction_id=activity.get('id'),
                            type=activity.get('type'),
                            amount=amount_value,
                            currency=currency,
                            description=activity.get('description', ''),
                            title=activity.get('title', ''),
                            date=created_on_dt,
                            status=activity.get('status'),
                            reference_number=activity.get('resource', {}).get('id', ''),
                        )
                        db.add(tx)
                        total_new += 1
                    db.commit()
                    fetched += len(activities)
                    if len(activities) < limit:
                        break
                    offset += limit
            return {"success": True, "message": f"同步完成，新增{total_new}条交易记录"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"同步失败: {e}"}
        finally:
            db.close()

    async def sync_all_balances_to_db(self) -> Dict[str, Any]:
        """同步所有账户余额到数据库"""
        from app.utils.database import SessionLocal
        from app.models.database import WiseBalance
        from datetime import datetime
        
        db = SessionLocal()
        try:
            balances = await self.get_all_account_balances()
            if not balances:
                return {"success": False, "message": "未获取到余额数据"}
            
            updated_count = 0
            for balance_data in balances:
                account_id = balance_data.get('account_id')
                if not account_id:
                    continue
                
                # 检查是否已存在
                existing = db.query(WiseBalance).filter_by(account_id=account_id).first()
                
                if existing:
                    # 更新现有记录
                    existing.currency = balance_data.get('currency')
                    existing.available_balance = balance_data.get('available_balance', 0.0)
                    existing.reserved_balance = balance_data.get('reserved_balance', 0.0)
                    existing.cash_amount = balance_data.get('cash_amount', 0.0)
                    existing.total_worth = balance_data.get('total_worth', 0.0)
                    existing.type = balance_data.get('type')
                    existing.name = balance_data.get('name')
                    existing.icon = balance_data.get('icon')
                    existing.investment_state = balance_data.get('investment_state')
                    existing.creation_time = balance_data.get('creation_time')
                    existing.modification_time = balance_data.get('modification_time')
                    existing.visible = balance_data.get('visible')
                    existing.primary = balance_data.get('primary')
                    existing.updated_at = datetime.now()
                else:
                    # 创建新记录
                    new_balance = WiseBalance(
                        account_id=account_id,
                        currency=balance_data.get('currency'),
                        available_balance=balance_data.get('available_balance', 0.0),
                        reserved_balance=balance_data.get('reserved_balance', 0.0),
                        cash_amount=balance_data.get('cash_amount', 0.0),
                        total_worth=balance_data.get('total_worth', 0.0),
                        type=balance_data.get('type'),
                        name=balance_data.get('name'),
                        icon=balance_data.get('icon'),
                        investment_state=balance_data.get('investment_state'),
                        creation_time=balance_data.get('creation_time'),
                        modification_time=balance_data.get('modification_time'),
                        visible=balance_data.get('visible'),
                        primary=balance_data.get('primary')
                    )
                    db.add(new_balance)
                
                updated_count += 1
            
            db.commit()
            return {"success": True, "message": f"同步完成，更新{updated_count}条余额记录"}
        except Exception as e:
            db.rollback()
            logger.error(f"同步余额失败: {e}")
            return {"success": False, "message": f"同步失败: {e}"}
        finally:
            db.close()

    async def sync_exchange_rates_to_db(self, currency_pairs: List[tuple] = None) -> Dict[str, Any]:
        """同步汇率数据到数据库"""
        from app.utils.database import SessionLocal
        from app.models.database import WiseExchangeRate
        from datetime import datetime
        
        if currency_pairs is None:
            # 默认的主要货币对
            currency_pairs = [
                ("USD", "CNY"),
                ("EUR", "CNY"),
                ("GBP", "CNY"),
                ("AUD", "CNY"),
                ("JPY", "CNY"),
                ("USD", "EUR"),
                ("GBP", "USD"),
                ("AUD", "USD")
            ]
        
        db = SessionLocal()
        try:
            updated_count = 0
            for source, target in currency_pairs:
                try:
                    rate_data = await self.get_exchange_rates(source, target)
                    if not rate_data:
                        continue
                    
                    # 解析汇率数据
                    rate_value = None
                    if isinstance(rate_data, list) and len(rate_data) > 0:
                        rate_info = rate_data[0]
                        rate_value = rate_info.get('rate')
                    elif isinstance(rate_data, dict):
                        rate_value = rate_data.get('rate')
                    
                    if rate_value is None:
                        continue
                    
                    # 检查今天是否已有记录
                    today = datetime.now().date()
                    existing = db.query(WiseExchangeRate).filter_by(
                        source_currency=source,
                        target_currency=target,
                        time=today
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.rate = float(rate_value)
                        existing.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        new_rate = WiseExchangeRate(
                            source_currency=source,
                            target_currency=target,
                            rate=float(rate_value),
                            time=today
                        )
                        db.add(new_rate)
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"同步汇率 {source}->{target} 失败: {e}")
                    continue
            
            db.commit()
            return {"success": True, "message": f"同步完成，更新{updated_count}条汇率记录"}
        except Exception as e:
            db.rollback()
            logger.error(f"同步汇率失败: {e}")
            return {"success": False, "message": f"同步失败: {e}"}
        finally:
            db.close()

    async def sync_all_data_to_db(self, days: int = 7) -> Dict[str, Any]:
        """综合同步所有Wise数据到数据库"""
        results = {
            "transactions": {"success": False, "message": "未执行"},
            "balances": {"success": False, "message": "未执行"},
            "exchange_rates": {"success": False, "message": "未执行"}
        }
        
        try:
            # 同步交易记录
            logger.info("[Wise] 开始同步交易记录...")
            results["transactions"] = await self.sync_all_transactions_to_db(days)
            
            # 同步余额
            logger.info("[Wise] 开始同步余额...")
            results["balances"] = await self.sync_all_balances_to_db()
            
            # 同步汇率
            logger.info("[Wise] 开始同步汇率...")
            results["exchange_rates"] = await self.sync_exchange_rates_to_db()
            
            # 统计总体结果
            success_count = sum(1 for r in results.values() if r["success"])
            overall_success = success_count == len(results)
            
            return {
                "success": overall_success,
                "message": f"同步完成，{success_count}/{len(results)}个任务成功",
                "details": results
            }
            
        except Exception as e:
            logger.error(f"综合同步失败: {e}")
            return {
                "success": False,
                "message": f"综合同步失败: {e}",
                "details": results
            } 