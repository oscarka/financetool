import akshare as ak
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from loguru import logger
import itertools
from app.models.database import WiseExchangeRate, WiseTransaction
from app.utils.database import SessionLocal
import httpx
from sqlalchemy import and_

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

    async def fetch_and_store_history(self, currencies, days=365, group='day'):
        """
        拉取所有币种对的历史汇率并存储
        currencies: List[str]，如['USD','AUD','CNY']
        days: int，历史天数
        group: 'day'/'hour'/'minute'
        """
        db = SessionLocal()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        pairs = list(itertools.permutations(currencies, 2))
        for source, target in pairs:
            url = f"{WISE_API_BASE}/v1/rates"
            params = {
                'source': source,
                'target': target,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'group': group
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data:
                        rate = item.get('rate')
                        time_str = item.get('time')
                        if not rate or not time_str:
                            continue
                        time_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00')) if 'Z' in time_str else datetime.fromisoformat(time_str)
                        # 查重
                        exists = db.query(WiseExchangeRate).filter(and_(
                            WiseExchangeRate.source_currency==source,
                            WiseExchangeRate.target_currency==target,
                            WiseExchangeRate.time==time_dt
                        )).first()
                        if exists:
                            continue
                        db.add(WiseExchangeRate(
                            source_currency=source,
                            target_currency=target,
                            rate=rate,
                            time=time_dt
                        ))
                    db.commit()
        db.close()

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