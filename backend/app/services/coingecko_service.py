"""
CoinGecko价格服务
"""
import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from app.utils.database import SessionLocal
from app.models.database import Web3TokenPrice
from sqlalchemy import func


class CoinGeckoService:
    """CoinGecko API服务"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Web3-Wallet-Manager/1.0'
        }
        
        # 主流代币的CoinGecko ID映射
        self.token_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'BNB': 'binancecoin',
            'MATIC': 'matic-network',
            'SOL': 'solana',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'DAI': 'dai',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'AAVE': 'aave',
            'CRV': 'curve-dao-token',
            'COMP': 'compound-governance-token',
            'MKR': 'maker',
            'YFI': 'yearn-finance',
            'SUSHI': 'sushi',
            '1INCH': '1inch',
            'SNX': 'havven',
            'BAL': 'balancer',
            'LDO': 'lido-dao'
        }
    
    async def get_token_prices(self, token_symbols: List[str], vs_currency: str = 'usdt') -> Dict[str, float]:
        """批量获取代币价格"""
        try:
            # 转换代币符号为CoinGecko ID
            coingecko_ids = []
            symbol_to_id = {}
            
            for symbol in token_symbols:
                if symbol.upper() in self.token_mapping:
                    gecko_id = self.token_mapping[symbol.upper()]
                    coingecko_ids.append(gecko_id)
                    symbol_to_id[gecko_id] = symbol.upper()
            
            if not coingecko_ids:
                return {}
            
            # 批量查询价格
            ids_str = ','.join(coingecko_ids)
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ids_str,
                'vs_currencies': vs_currency,
                'include_24hr_change': 'true'
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            # 转换回代币符号格式
            prices = {}
            for gecko_id, price_data in data.items():
                if gecko_id in symbol_to_id:
                    symbol = symbol_to_id[gecko_id]
                    price = price_data.get(vs_currency, 0)
                    prices[symbol] = float(price) if price else 0.0
            
            logger.info(f"成功获取 {len(prices)} 个代币价格")
            return prices
            
        except Exception as e:
            logger.error(f"获取CoinGecko价格失败: {e}")
            return {}
    
    async def get_token_price(self, token_symbol: str, vs_currency: str = 'usdt') -> float:
        """获取单个代币价格"""
        prices = await self.get_token_prices([token_symbol], vs_currency)
        return prices.get(token_symbol.upper(), 0.0)
    
    async def update_price_cache(self, token_symbols: List[str] = None) -> int:
        """更新价格缓存到数据库"""
        try:
            db = SessionLocal()
            
            # 如果没有指定代币，更新所有主流代币
            if not token_symbols:
                token_symbols = list(self.token_mapping.keys())
            
            # 获取价格
            prices = await self.get_token_prices(token_symbols)
            
            updated_count = 0
            current_time = datetime.now()
            
            for symbol, price in prices.items():
                if price > 0:
                    # 查找现有记录
                    existing = db.query(Web3TokenPrice).filter(
                        Web3TokenPrice.token_symbol == symbol,
                        Web3TokenPrice.chain == 'all'  # 价格是通用的
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.usdt_price = price
                        existing.last_updated = current_time
                    else:
                        # 创建新记录
                        new_price = Web3TokenPrice(
                            token_symbol=symbol,
                            chain='all',
                            usdt_price=price,
                            coingecko_id=self.token_mapping.get(symbol),
                            last_updated=current_time
                        )
                        db.add(new_price)
                    
                    updated_count += 1
            
            db.commit()
            logger.info(f"成功更新 {updated_count} 个代币价格到缓存")
            return updated_count
            
        except Exception as e:
            logger.error(f"更新价格缓存失败: {e}")
            db.rollback()
            return 0
        finally:
            db.close()
    
    async def get_cached_price(self, token_symbol: str, max_age_minutes: int = 15) -> Optional[float]:
        """从缓存获取代币价格"""
        try:
            db = SessionLocal()
            
            cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
            
            cached_price = db.query(Web3TokenPrice).filter(
                Web3TokenPrice.token_symbol == token_symbol.upper(),
                Web3TokenPrice.last_updated >= cutoff_time
            ).first()
            
            if cached_price:
                return float(cached_price.usdt_price)
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存价格失败: {e}")
            return None
        finally:
            db.close()
    
    async def get_price_with_cache(self, token_symbol: str) -> float:
        """优先从缓存获取价格，缓存过期则从API获取"""
        # 先尝试从缓存获取
        cached_price = await self.get_cached_price(token_symbol)
        if cached_price is not None:
            return cached_price
        
        # 缓存未命中，从API获取并更新缓存
        price = await self.get_token_price(token_symbol)
        if price > 0:
            await self.update_price_cache([token_symbol])
        
        return price


# 全局实例
coingecko_service = CoinGeckoService()