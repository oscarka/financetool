import akshare as ak
import pandas as pd
import httpx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from loguru import logger
import itertools
from app.models.database import WiseExchangeRate, WiseTransaction
from app.utils.database import SessionLocal
from sqlalchemy import and_
from app.utils.auto_logger import auto_log
import re
from dateutil import parser

WISE_API_BASE = "https://api.transferwise.com"

class ExchangeRateService:
    """外币汇率服务"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    @staticmethod
    @auto_log("exchange", log_result=True)
    def get_currency_list() -> List[Dict[str, Any]]:
        """获取支持的货币列表"""
        try:
            # 使用akshare获取货币列表
            df = ak.currency_boc_sina()
            currencies = []
            
            # 根据实际数据结构处理
            for _, row in df.iterrows():
                currencies.append({
                    "code": "USD",  # 默认美元
                    "name": "美元",
                    "symbol": "$",
                    "rate": float(row.get('中行汇买价', 0)) if pd.notna(row.get('中行汇买价')) else 0,
                    "update_time": datetime.now().isoformat()
                })
            
            return currencies
        except Exception as e:
            logger.error(f"获取货币列表失败: {e}")
            return []
    
    @staticmethod
    @auto_log("exchange", log_result=True)
    def get_exchange_rate(currency: str = "USD") -> Optional[Dict[str, Any]]:
        """获取指定货币对人民币的汇率"""
        try:
            # 使用akshare获取汇率数据
            df = ak.currency_boc_sina()
            
            # 获取最新一行数据（美元汇率）
            if not df.empty:
                row = df.iloc[0]  # 最新数据
                return {
                    "currency": currency,
                    "currency_name": "美元",
                    "spot_buy": float(row.get('中行汇买价', 0)) if pd.notna(row.get('中行汇买价')) else 0,
                    "spot_sell": float(row.get('中行钞卖价/汇卖价', 0)) if pd.notna(row.get('中行钞卖价/汇卖价')) else 0,
                    "cash_buy": float(row.get('中行钞买价', 0)) if pd.notna(row.get('中行钞买价')) else 0,
                    "cash_sell": float(row.get('中行钞卖价/汇卖价', 0)) if pd.notna(row.get('中行钞卖价/汇卖价')) else 0,
                    "middle_rate": float(row.get('央行中间价', 0)) if pd.notna(row.get('央行中间价')) else 0,
                    "update_time": datetime.now().isoformat()
                }
            
            return None
        except Exception as e:
            logger.error(f"获取汇率失败: {currency}, {e}")
            return None
    
    @staticmethod
    @auto_log("exchange", log_result=True)
    def get_all_exchange_rates() -> List[Dict[str, Any]]:
        """获取所有货币的汇率"""
        try:
            df = ak.currency_boc_sina()
            rates = []
            
            # 获取最新一行数据（美元汇率）
            if not df.empty:
                row = df.iloc[0]  # 最新数据
                rates.append({
                    "currency": "USD",
                    "currency_name": "美元",
                    "spot_buy": float(row.get('中行汇买价', 0)) if pd.notna(row.get('中行汇买价')) else 0,
                    "spot_sell": float(row.get('中行钞卖价/汇卖价', 0)) if pd.notna(row.get('中行钞卖价/汇卖价')) else 0,
                    "cash_buy": float(row.get('中行钞买价', 0)) if pd.notna(row.get('中行钞买价')) else 0,
                    "cash_sell": float(row.get('中行钞卖价/汇卖价', 0)) if pd.notna(row.get('中行钞卖价/汇卖价')) else 0,
                    "middle_rate": float(row.get('央行中间价', 0)) if pd.notna(row.get('央行中间价')) else 0,
                    "update_time": datetime.now().isoformat()
                })
            
            return rates
        except Exception as e:
            logger.error(f"获取所有汇率失败: {e}")
            return []
    
    @staticmethod
    @auto_log("exchange", log_result=True)
    def get_historical_exchange_rate(currency: str = "USD", start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取历史汇率数据"""
        try:
            # 使用akshare获取历史汇率
            df = ak.currency_hist_fx_spot()
            
            # 过滤指定货币
            if currency and currency != "USD":
                # 这里需要根据实际API返回的数据结构进行调整
                pass
            
            # 过滤日期范围
            if start_date:
                df = df[df['日期'] >= start_date]
            if end_date:
                df = df[df['日期'] <= end_date]
            
            historical_data = []
            for _, row in df.iterrows():
                historical_data.append({
                    "date": str(row.get('日期', '')),
                    "currency": currency,
                    "rate": float(row.get('汇率', 0)) if pd.notna(row.get('汇率')) else 0,
                    "change": float(row.get('涨跌', 0)) if pd.notna(row.get('涨跌')) else 0,
                    "change_pct": float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0
                })
            
            return historical_data
        except Exception as e:
            logger.error(f"获取历史汇率失败: {currency}, {e}")
            return []
    
    @staticmethod
    @auto_log("exchange", log_result=True)
    def convert_currency(amount: float, from_currency: str, to_currency: str = "CNY") -> Optional[float]:
        """货币转换"""
        try:
            if from_currency == to_currency:
                return amount
            
            if to_currency == "CNY":
                # 转换为人民币
                rate_data = ExchangeRateService.get_exchange_rate(from_currency)
                if rate_data:
                    return amount * rate_data["middle_rate"]
            elif from_currency == "CNY":
                # 从人民币转换
                rate_data = ExchangeRateService.get_exchange_rate(to_currency)
                if rate_data:
                    return amount / rate_data["middle_rate"]
            else:
                # 通过人民币进行交叉转换
                from_rate = ExchangeRateService.get_exchange_rate(from_currency)
                to_rate = ExchangeRateService.get_exchange_rate(to_currency)
                
                if from_rate and to_rate:
                    cny_amount = amount * from_rate["middle_rate"]
                    return cny_amount / to_rate["middle_rate"]
            
            return None
        except Exception as e:
            logger.error(f"货币转换失败: {amount} {from_currency} -> {to_currency}, {e}")
            return None

    def _generate_currency_pairs(self, currencies: List[str]) -> List[Tuple[str, str]]:
        """生成所有币种对"""
        import itertools
        return list(itertools.permutations(currencies, 2))
    
    async def _fetch_rates(self, source_currency: str, target_currency: str, days: int, group: str) -> List[Dict]:
        """获取指定币种对的汇率数据"""
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        url = f"{WISE_API_BASE}/v1/rates"
        params = {
            'source': source_currency,
            'target': target_currency,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'group': group
        }

        logger.debug(f"[Wise汇率] 请求API: {url}, 参数: {params}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self.headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                logger.debug(f"[Wise汇率] API响应成功，数据条数: {len(data)}")
                return data
            else:
                logger.error(f"[Wise汇率] API请求失败: {resp.status_code}, {resp.text}")
                return []

    async def fetch_and_store_history(self, currencies: List[str], days: int = 30, group: str = 'day') -> Dict[str, Any]:
        """获取并存储历史汇率数据"""
        logger.info(f"[Wise汇率] 开始同步历史汇率数据，币种: {currencies}, 天数: {days}, 分组: {group}")
        db = SessionLocal()
        try:
            # 获取所有币种对
            currency_pairs = self._generate_currency_pairs(currencies)
            logger.info(f"[Wise汇率] 生成币种对: {currency_pairs}")
            
            total_inserted = 0
            total_updated = 0
            total_processed = 0
            
            for source_currency, target_currency in currency_pairs:
                logger.info(f"[Wise汇率] 处理币种对: {source_currency} -> {target_currency}")
                
                try:
                    # 获取汇率数据
                    rates_data = await self._fetch_rates(source_currency, target_currency, days, group)
                    logger.info(f"[Wise汇率] 获取到 {len(rates_data)} 条汇率数据")
                    
                    if not rates_data:
                        logger.warning(f"[Wise汇率] 币种对 {source_currency} -> {target_currency} 无数据")
                        continue
                    
                    # 处理每条汇率数据
                    for rate_data in rates_data:
                        total_processed += 1
                        rate = rate_data.get('rate')
                        time_str = rate_data.get('time')
                        
                        logger.debug(f"[Wise汇率] 处理汇率数据: rate={rate}, time={time_str}")
                        
                        if not rate or not time_str:
                            logger.warning(f"[Wise汇率] 跳过无效数据: rate={rate}, time={time_str}")
                            continue
                        
                        # 更健壮的时间格式解析
                        t = time_str.strip()
                        logger.debug(f"[Wise汇率] 原始时间字符串: '{t}'")
                        
                        try:
                            time_dt = parser.parse(t)
                            logger.debug(f"[Wise汇率] 解析成功: {time_dt}")
                        except Exception as e:
                            logger.error(f"[Wise汇率] 无法解析时间字符串: '{t}', 原始: '{time_str}', 错误: {e}")
                            continue
                        
                        # 检查是否已存在
                        existing_rate = db.query(WiseExchangeRate).filter(
                            WiseExchangeRate.source_currency == source_currency,
                            WiseExchangeRate.target_currency == target_currency,
                            WiseExchangeRate.time == time_dt
                        ).first()
                        
                        if existing_rate:
                            # 更新现有记录
                            existing_rate.rate = rate
                            existing_rate.updated_at = datetime.utcnow()
                            total_updated += 1
                            logger.debug(f"[Wise汇率] 更新汇率: {source_currency}->{target_currency} {time_dt}")
                        else:
                            # 新增记录
                            new_rate = WiseExchangeRate(
                                source_currency=source_currency,
                                target_currency=target_currency,
                                rate=rate,
                                time=time_dt
                            )
                            db.add(new_rate)
                            total_inserted += 1
                            logger.debug(f"[Wise汇率] 新增汇率: {source_currency}->{target_currency} {time_dt}")
                    
                    # 提交当前币种对的数据
                    db.commit()
                    logger.info(f"[Wise汇率] 币种对 {source_currency} -> {target_currency} 处理完成")
                    
                except Exception as e:
                    logger.error(f"[Wise汇率] 处理币种对 {source_currency} -> {target_currency} 时出错: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"[Wise汇率] 历史汇率同步完成，总处理: {total_processed}, 新增: {total_inserted}, 更新: {total_updated}")
            
            return {
                "success": True,
                "message": f"历史汇率同步完成，新增{total_inserted}条，更新{total_updated}条",
                "total_processed": total_processed,
                "total_inserted": total_inserted,
                "total_updated": total_updated
            }
        except Exception as e:
            logger.error(f"[Wise汇率] 历史汇率同步失败: {e}")
            db.rollback()
            return {
                "success": False,
                "message": f"历史汇率同步失败: {str(e)}"
            }
        finally:
            db.close()

    async def fetch_and_store_history_incremental(self, currencies: List[str], group: str = 'day') -> Dict[str, Any]:
        """增量获取并存储历史汇率数据"""
        logger.info(f"[Wise汇率] 开始增量同步历史汇率数据，币种: {currencies}, 分组: {group}")
        db = SessionLocal()
        try:
            # 获取所有币种对
            currency_pairs = self._generate_currency_pairs(currencies)
            logger.info(f"[Wise汇率] 生成币种对: {currency_pairs}")
            
            total_inserted = 0
            total_updated = 0
            total_processed = 0
            
            for source_currency, target_currency in currency_pairs:
                logger.info(f"[Wise汇率] 处理币种对: {source_currency} -> {target_currency}")
                
                try:
                    # 获取数据库中该币种对的最新记录时间
                    latest_record = db.query(WiseExchangeRate).filter(
                        WiseExchangeRate.source_currency == source_currency,
                        WiseExchangeRate.target_currency == target_currency
                    ).order_by(WiseExchangeRate.time.desc()).first()
                    
                    # 计算需要同步的时间范围
                    end_date = datetime.now()
                    if latest_record:
                        # 从最新记录的下一天开始同步
                        start_date = latest_record.time + timedelta(days=1)
                        logger.info(f"[Wise汇率] 增量同步: {source_currency}->{target_currency} 从 {start_date.date()} 到 {end_date.date()}")
                    else:
                        # 如果没有记录，同步最近30天
                        start_date = end_date - timedelta(days=30)
                        logger.info(f"[Wise汇率] 首次同步: {source_currency}->{target_currency} 最近30天")
                    
                    # 如果开始时间晚于结束时间，说明数据是最新的
                    if start_date >= end_date:
                        logger.info(f"[Wise汇率] 币种对 {source_currency} -> {target_currency} 数据已是最新")
                        continue
                    
                    # 计算需要同步的天数
                    days_to_sync = (end_date - start_date).days
                    if days_to_sync <= 0:
                        continue
                    
                    # 获取汇率数据
                    rates_data = await self._fetch_rates_with_date_range(source_currency, target_currency, start_date, end_date, group)
                    logger.info(f"[Wise汇率] 获取到 {len(rates_data)} 条新汇率数据")
                    
                    if not rates_data:
                        logger.warning(f"[Wise汇率] 币种对 {source_currency} -> {target_currency} 无新数据")
                        continue
                    
                    # 处理每条汇率数据
                    for rate_data in rates_data:
                        total_processed += 1
                        rate = rate_data.get('rate')
                        time_str = rate_data.get('time')
                        
                        if not rate or not time_str:
                            continue
                        
                        # 解析时间
                        try:
                            time_dt = parser.parse(time_str.strip())
                        except Exception as e:
                            logger.error(f"[Wise汇率] 无法解析时间字符串: '{time_str}', 错误: {e}")
                            continue
                        
                        # 检查是否已存在
                        existing_rate = db.query(WiseExchangeRate).filter(
                            WiseExchangeRate.source_currency == source_currency,
                            WiseExchangeRate.target_currency == target_currency,
                            WiseExchangeRate.time == time_dt
                        ).first()
                        
                        if existing_rate:
                            # 更新现有记录
                            existing_rate.rate = rate
                            existing_rate.updated_at = datetime.utcnow()
                            total_updated += 1
                        else:
                            # 新增记录
                            new_rate = WiseExchangeRate(
                                source_currency=source_currency,
                                target_currency=target_currency,
                            rate=rate,
                            time=time_dt
                            )
                            db.add(new_rate)
                            total_inserted += 1
                    
                    # 提交当前币种对的数据
                    db.commit()
                    logger.info(f"[Wise汇率] 币种对 {source_currency} -> {target_currency} 增量同步完成")
                    
                except Exception as e:
                    logger.error(f"[Wise汇率] 处理币种对 {source_currency} -> {target_currency} 时出错: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"[Wise汇率] 增量同步完成，总处理: {total_processed}, 新增: {total_inserted}, 更新: {total_updated}")
            
            return {
                "success": True,
                "message": f"增量同步完成，新增{total_inserted}条，更新{total_updated}条",
                "total_processed": total_processed,
                "total_inserted": total_inserted,
                "total_updated": total_updated
            }
        except Exception as e:
            logger.error(f"[Wise汇率] 增量同步失败: {e}")
            db.rollback()
            return {
                "success": False,
                "message": f"增量同步失败: {str(e)}"
            }
        finally:
            db.close()

    async def _fetch_rates_with_date_range(self, source_currency: str, target_currency: str, start_date: datetime, end_date: datetime, group: str) -> List[Dict]:
        """获取指定日期范围的汇率数据"""
        url = f"{WISE_API_BASE}/v1/rates"
        params = {
            'source': source_currency,
            'target': target_currency,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'group': group
        }
        
        logger.debug(f"[Wise汇率] 请求API: {url}, 参数: {params}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self.headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                logger.debug(f"[Wise汇率] API响应成功，数据条数: {len(data)}")
                return data
            else:
                logger.error(f"[Wise汇率] API请求失败: {resp.status_code}, {resp.text}")
                return []

    @staticmethod
    def get_my_currencies(db=None):
        """从wise余额和交易表自动识别持有币种集合"""
        if db is None:
            db = SessionLocal()
        # 从余额表
        from app.models.database import WiseBalance
        balance_curs = set([b.currency for b in db.query(WiseBalance).all() if b.currency])
        # 从交易表
        tx_curs = set([t.currency for t in db.query(WiseTransaction).all() if t.currency])
        return list(balance_curs | tx_curs) 

    @staticmethod
    def sync_wise_balance_to_db(db, balance_data):
        """同步Wise余额到数据库（增量快照模式）"""
        from app.models.database import WiseBalance
        from datetime import datetime
        now = datetime.now()
        new_balance = WiseBalance(
            account_id=balance_data['account_id'],
            currency=balance_data['currency'],
            available_balance=balance_data['available_balance'],
            reserved_balance=balance_data['reserved_balance'],
            cash_amount=balance_data['cash_amount'],
            total_worth=balance_data['total_worth'],
            type=balance_data['type'],
            investment_state=balance_data['investment_state'],
            creation_time=balance_data['creation_time'],
            modification_time=balance_data['modification_time'],
            visible=balance_data.get('visible', True),
            primary=balance_data.get('primary', False),
            update_time=now
        )
        db.add(new_balance)
        db.commit()
        return new_balance 