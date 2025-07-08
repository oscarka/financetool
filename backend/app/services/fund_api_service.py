import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import json
import re
from app.config import settings
from app.utils.logger import log_fund_api, log_error


class FundAPIService:
    """基金API集成服务"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def get_fund_nav_tiantian(self, fund_code: str, nav_date: date) -> Optional[Dict[str, Any]]:
        """从天天基金网获取基金净值"""
        try:
            url = f"{settings.tiantian_fund_api_base_url}/js/{fund_code}.js"
            async with httpx.AsyncClient(timeout=settings.fund_api_timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                content = response.text
                print(f"[调试] 天天基金API返回内容: {content}")
                # 解析JSONP格式的数据
                if content.startswith("jsonpgz(") and content.endswith(")"):
                    json_str = content[8:-1]  # 去掉 jsonpgz( 和 )
                    data = json.loads(json_str)
                    print(f"[调试] 天天基金API解析后数据: {data}")
                    if data.get("fundcode") == fund_code and data.get("dwjz") and data.get("jzrq"):
                        nav = Decimal(data["dwjz"])
                        nav_date_api = datetime.strptime(data["jzrq"], "%Y-%m-%d").date()
                        return {
                            "fund_code": fund_code,
                            "nav_date": nav_date_api,  # 用API返回的日期
                            "nav": nav,
                            "accumulated_nav": Decimal(data["ljjz"]) if data.get("ljjz") else None,
                            "growth_rate": float(data["gszzl"]) if data.get("gszzl") else None,
                            "source": "tiantian"
                        }
                return None
        except Exception as e:
            log_fund_api(f"获取天天基金网净值失败: {fund_code}, {nav_date}, {e}", level="ERROR")
            return None
    
    async def get_fund_nav_xueqiu(self, fund_code: str, nav_date: date) -> Optional[Dict[str, Any]]:
        """从雪球获取基金净值"""
        try:
            url = settings.xueqiu_api_base_url
            params = {
                "symbol": f"SH{fund_code}" if fund_code.startswith("5") else f"SZ{fund_code}",
                "period": "1d",
                "type": "before",
                "count": 1
            }
            
            async with httpx.AsyncClient(timeout=settings.fund_api_timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                print(f"[调试] 雪球API返回内容: {data}")
                
                if data.get("data") and data["data"].get("item"):
                    item = data["data"]["item"][0]
                    nav = Decimal(str(item[2]))  # 收盘价作为净值
                    
                    return {
                        "fund_code": fund_code,
                        "nav_date": nav_date,
                        "nav": nav,
                        "source": "xueqiu"
                    }
                
                return None
                
        except Exception as e:
            log_fund_api(f"获取雪球净值失败: {fund_code}, {nav_date}, {e}", level="ERROR")
            return None
    
    async def get_fund_info_tiantian(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """从天天基金网获取基金信息"""
        try:
            url = f"{settings.tiantian_fund_info_base_url}/{fund_code}.js"
            
            async with httpx.AsyncClient(timeout=settings.fund_api_timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                content = response.text
                
                # 解析关键信息
                fund_name_match = re.search(r'fS_name\s*=\s*"([^"]+)"', content)
                fund_code_match = re.search(r'fS_code\s*=\s*"([^"]+)"', content)
                min_purchase_match = re.search(r'fund_minsg\s*=\s*"([^"]+)"', content)
                purchase_fee_match = re.search(r'fund_sourceRate\s*=\s*"([^"]+)"', content)
                management_fee_match = re.search(r'fund_Rate\s*=\s*"([^"]+)"', content)
                redemption_fee_match = re.search(r'fund_redemptionRate\s*=\s*"([^"]+)"', content)
                
                if fund_name_match and fund_code_match:
                    return {
                        "fund_code": fund_code_match.group(1),
                        "fund_name": fund_name_match.group(1),
                        "fund_type": None,  # API无此字段
                        "management_fee": float(management_fee_match.group(1)) if management_fee_match else None,
                        "purchase_fee": float(purchase_fee_match.group(1)) if purchase_fee_match else None,
                        "redemption_fee": float(redemption_fee_match.group(1)) if redemption_fee_match else None,
                        "min_purchase": float(min_purchase_match.group(1)) if min_purchase_match else None,
                        "risk_level": None,  # API无此字段
                        "source": "tiantian"
                    }
                
                return None
                
        except Exception as e:
            log_fund_api(f"获取天天基金网基金信息失败: {fund_code}, {e}", level="ERROR")
            return None
    
    async def get_fund_nav(self, fund_code: str, nav_date: date) -> Optional[Dict[str, Any]]:
        """获取基金净值（多数据源）"""
        # 尝试天天基金网
        nav_data = await self.get_fund_nav_tiantian(fund_code, nav_date)
        if nav_data:
            return nav_data
        
        # 尝试雪球
        nav_data = await self.get_fund_nav_xueqiu(fund_code, nav_date)
        if nav_data:
            return nav_data
        
        return None
    
    async def get_fund_info(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """获取基金信息（多数据源）"""
        # 尝试天天基金网
        fund_info = await self.get_fund_info_tiantian(fund_code)
        if fund_info:
            return fund_info
        
        return None
    
    async def batch_get_fund_nav(self, fund_codes: list, nav_date: date) -> Dict[str, Dict[str, Any]]:
        """批量获取基金净值"""
        tasks = []
        for fund_code in fund_codes:
            task = self.get_fund_nav(fund_code, nav_date)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        nav_data = {}
        for i, result in enumerate(results):
            if isinstance(result, dict):
                nav_data[fund_codes[i]] = result
            else:
                log_fund_api(f"获取基金净值失败: {fund_codes[i]}, {result}", level="ERROR")
        
        return nav_data

    async def get_fund_nav_latest_tiantian(self, fund_code: str) -> Optional[Dict[str, Any]]:
        print("[调试] 进入 get_fund_nav_latest_tiantian 方法")
        try:
            url = f"{settings.tiantian_fund_api_base_url}/js/{fund_code}.js"
            print(f"[调试] 请求URL: {url}")
            async with httpx.AsyncClient(timeout=settings.fund_api_timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                content = response.text
                print(f"[调试] 天天基金API返回内容: {content}")
                # 修复内容格式判断，支持以分号结尾
                if content.startswith("jsonpgz(") and content.endswith(";"):
                    json_str = content[8:-2]  # 去掉 jsonpgz( 和 );
                    data = json.loads(json_str)
                    print(f"[调试] 天天基金API解析后数据: {data}")
                    print(f"[调试] fundcode对比: data.get('fundcode')={data.get('fundcode')}({type(data.get('fundcode'))}), fund_code={fund_code}({type(fund_code)})")
                    print(f"[调试] dwjz={data.get('dwjz')}({type(data.get('dwjz'))}), jzrq={data.get('jzrq')}({type(data.get('jzrq'))})")
                    if data.get("fundcode") == fund_code and data.get("dwjz") and data.get("jzrq"):
                        print("[调试] if判断通过，准备返回数据")
                        nav = Decimal(data["dwjz"])
                        nav_date_api = datetime.strptime(data["jzrq"], "%Y-%m-%d").date()
                        return {
                            "fund_code": fund_code,
                            "nav_date": nav_date_api,
                            "nav": nav,
                            "accumulated_nav": Decimal(data["ljjz"]) if data.get("ljjz") else None,
                            "growth_rate": float(data["gszzl"]) if data.get("gszzl") else None,
                            "source": "tiantian",
                            "gsz": data.get("gsz"),
                            "gztime": data.get("gztime"),
                        }
                    else:
                        print(f"[调试] 不满足条件: fundcode={data.get('fundcode')}, dwjz={data.get('dwjz')}, jzrq={data.get('jzrq')}")
                else:
                    print("[调试] API内容格式不符")
                return None
        except Exception as e:
            print(f"[调试] get_fund_nav_latest_tiantian 异常: {e}")
            log_fund_api(f"获取天天基金网最新净值失败: {fund_code}, {e}", level="ERROR")
            return None

    async def sync_latest_fund_nav(self, db, fund_code: str):
        """同步最新基金净值（只用API返回的最新净值）"""
        from app.services.fund_service import FundNavService
        try:
            print(f"[调试] 开始同步最新基金净值: {fund_code}")
            nav_data = await self.get_fund_nav_latest_tiantian(fund_code)
            print(f"[调试] API返回的最新净值数据: {nav_data}")
            if nav_data:
                print(f"[调试] 获取到最新净值数据，准备插入数据库...")
                print(f"[调试] 插入参数: fund_code={fund_code}, nav_date={nav_data['nav_date']}, nav={nav_data['nav']}, accumulated_nav={nav_data.get('accumulated_nav')}, growth_rate={nav_data.get('growth_rate')}, source={nav_data['source']}")
                try:
                    FundNavService.create_nav(
                        db=db,
                        fund_code=fund_code,
                        nav_date=nav_data["nav_date"],
                        nav=nav_data["nav"],
                        accumulated_nav=nav_data.get("accumulated_nav"),
                        growth_rate=nav_data.get("growth_rate"),
                        source=nav_data["source"]
                    )
                    print(f"[调试] 数据库插入成功！")
                    log_fund_api(f"同步最新基金净值成功: {fund_code}, {nav_data['nav_date']}, {nav_data['nav']}", level="INFO")
                    return True
                except Exception as db_error:
                    print(f"[调试] 数据库插入失败: {db_error}")
                    log_fund_api(f"数据库插入失败: {fund_code}, {nav_data['nav_date']}, {db_error}", level="ERROR")
                    return False
            else:
                print(f"[调试] 未获取到最新净值数据")
                log_fund_api(f"未获取到最新基金净值: {fund_code}", level="WARNING")
                return False
        except Exception as e:
            print(f"[调试] 同步最新基金净值异常: {e}")
            log_fund_api(f"同步最新基金净值失败: {fund_code}, {e}", level="ERROR")
            return False


class FundSyncService:
    """基金数据同步服务"""
    
    def __init__(self):
        self.api_service = FundAPIService()
    
    async def sync_fund_nav(self, db, fund_code: str, nav_date: date):
        """同步基金净值"""
        from app.services.fund_service import FundNavService
        try:
            print(f"[调试] 开始同步基金净值: {fund_code}, {nav_date}")
            print(f"[调试] 正在从API获取净值数据...")
            nav_data = await self.api_service.get_fund_nav(fund_code, nav_date)
            print(f"[调试] API返回的净值数据: {nav_data}")
            if nav_data:
                print(f"[调试] 获取到净值数据，准备插入数据库...")
                print(f"[调试] 插入参数: fund_code={fund_code}, nav_date={nav_data['nav_date']}, nav={nav_data['nav']}, accumulated_nav={nav_data.get('accumulated_nav')}, growth_rate={nav_data.get('growth_rate')}, source={nav_data['source']}")
                try:
                    FundNavService.create_nav(
                        db=db,
                        fund_code=fund_code,
                        nav_date=nav_data["nav_date"],  # 用API返回的日期
                        nav=nav_data["nav"],
                        accumulated_nav=nav_data.get("accumulated_nav"),
                        growth_rate=nav_data.get("growth_rate"),
                        source=nav_data["source"]
                    )
                    print(f"[调试] 数据库插入成功！")
                    log_fund_api(f"同步基金净值成功: {fund_code}, {nav_data['nav_date']}, {nav_data['nav']}", level="INFO")
                    return True
                except Exception as db_error:
                    print(f"[调试] 数据库插入失败: {db_error}")
                    log_fund_api(f"数据库插入失败: {fund_code}, {nav_data['nav_date']}, {db_error}", level="ERROR")
                    return False
            else:
                print(f"[调试] 未获取到净值数据")
                log_fund_api(f"未获取到基金净值: {fund_code}, {nav_date}", level="WARNING")
                return False
        except Exception as e:
            print(f"[调试] 同步基金净值异常: {e}")
            log_fund_api(f"同步基金净值失败: {fund_code}, {nav_date}, {e}", level="ERROR")
            return False
    
    async def sync_fund_info(self, db, fund_code: str):
        """同步基金信息"""
        from app.services.fund_service import FundInfoService
        
        try:
            # 获取基金信息
            fund_info = await self.api_service.get_fund_info(fund_code)
            
            if fund_info:
                # 检查是否已存在
                existing = FundInfoService.get_fund_info(db, fund_code)
                
                if existing:
                    # 强制覆盖所有字段
                    for key, value in fund_info.items():
                        if key != "fund_code" and hasattr(existing, key):
                            setattr(existing, key, value)
                    db.commit()
                    db.refresh(existing)
                else:
                    # 创建新信息
                    FundInfoService.create_fund_info(
                        db=db,
                        fund_code=fund_code,
                        fund_name=fund_info["fund_name"],
                        fund_type=fund_info.get("fund_type"),
                        management_fee=fund_info.get("management_fee"),
                        purchase_fee=fund_info.get("purchase_fee"),
                        redemption_fee=fund_info.get("redemption_fee"),
                        min_purchase=fund_info.get("min_purchase"),
                        risk_level=fund_info.get("risk_level")
                    )
                
                log_fund_api(f"同步基金信息成功: {fund_code}", level="INFO")
                return True
            else:
                log_fund_api(f"未获取到基金信息: {fund_code}", level="WARNING")
                return False
                
        except Exception as e:
            log_fund_api(f"同步基金信息失败: {fund_code}, {e}", level="ERROR")
            return False 