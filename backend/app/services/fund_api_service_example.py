"""
基金API服务示例 - 展示如何使用自动化日志系统
只需要1-2行代码就能获得完整的日志功能！
"""

import httpx
from datetime import date
from decimal import Decimal
from app.config import settings
from app.utils.auto_logger import auto_log, log_api_call, log_context, quick_log

class FundAPIServiceExample:
    """基金API服务示例 - 展示自动化日志的使用"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    # 🎯 方法1: 装饰器 - 一行代码自动记录函数调用
    @auto_log("fund")  # 只需要这一行！
    async def get_fund_nav_simple(self, fund_code: str, nav_date: date):
        """获取基金净值 - 自动记录调用、参数、执行时间、异常"""
        url = f"{settings.tiantian_fund_api_base_url}/js/{fund_code}.js"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            # 处理响应...
            return {"fund_code": fund_code, "nav": 1.2345}
    
    # 🎯 方法2: API调用装饰器 - 专门用于外部API
    @log_api_call("fund", "/api/fund/nav", "GET")  # 只需要这一行！
    async def get_fund_nav_api(self, fund_code: str):
        """获取基金净值 - 自动记录API调用详情"""
        url = f"{settings.tiantian_fund_api_base_url}/js/{fund_code}.js"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    # 🎯 方法3: 上下文管理器 - 记录代码块执行
    async def batch_get_fund_nav(self, fund_codes: list):
        """批量获取基金净值 - 使用上下文管理器"""
        results = []
        
        with log_context("fund", "批量获取基金净值"):  # 只需要这一行！
            for fund_code in fund_codes:
                try:
                    result = await self.get_fund_nav_simple(fund_code, date.today())
                    results.append(result)
                except Exception as e:
                    # 使用便捷函数记录失败
                    quick_log(f"获取基金 {fund_code} 失败", "fund", "ERROR", 
                             fund_code=fund_code, error=str(e))
        
        return results
    
    # 🎯 方法4: 便捷函数 - 一行代码记录日志
    async def sync_fund_data(self, fund_code: str):
        """同步基金数据 - 使用便捷函数"""
        try:
            # 业务逻辑...
            nav_data = await self.get_fund_nav_simple(fund_code, date.today())
            
            # 记录成功 - 一行代码
            quick_log("基金数据同步成功", "fund", "INFO", 
                     fund_code=fund_code, nav=nav_data.get("nav"))
            
            return nav_data
            
        except Exception as e:
            # 记录失败 - 一行代码
            quick_log("基金数据同步失败", "fund", "ERROR", 
                     fund_code=fund_code, error=str(e))
            raise
    
    # 🎯 方法5: 高级配置 - 记录更多信息
    @auto_log("fund", level="INFO", log_args=True, log_result=True, log_time=True)
    async def get_fund_info_detailed(self, fund_code: str):
        """获取基金详细信息 - 记录参数和结果"""
        url = f"{settings.tiantian_fund_info_base_url}/{fund_code}.js"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            
            # 解析数据...
            fund_info = {
                "fund_code": fund_code,
                "fund_name": "示例基金",
                "management_fee": 0.015,
                "purchase_fee": 0.001
            }
            
            return fund_info

# 🎯 使用示例 - 在现有代码中快速集成
class FundServiceExample:
    """基金服务示例 - 展示如何快速集成到现有代码"""
    
    def __init__(self):
        self.api_service = FundAPIServiceExample()
    
    # 只需要添加一行装饰器！
    @auto_log("business")
    async def process_fund_order(self, user_id: int, fund_code: str, amount: float):
        """处理基金订单 - 自动记录整个业务流程"""
        
        # 1. 验证用户
        with log_context("business", "验证用户"):
            user = await self.validate_user(user_id)
        
        # 2. 获取基金信息
        fund_info = await self.api_service.get_fund_info_detailed(fund_code)
        
        # 3. 计算份额
        with log_context("business", "计算基金份额"):
            shares = amount / fund_info["nav"]
        
        # 4. 记录订单
        with log_context("database", "保存订单"):
            order = await self.save_order(user_id, fund_code, amount, shares)
        
        # 5. 记录成功
        quick_log("基金订单处理成功", "business", "INFO", 
                 user_id=user_id, fund_code=fund_code, amount=amount, shares=shares)
        
        return order
    
    async def validate_user(self, user_id: int):
        """验证用户 - 模拟"""
        return {"id": user_id, "name": "测试用户"}
    
    async def save_order(self, user_id: int, fund_code: str, amount: float, shares: float):
        """保存订单 - 模拟"""
        return {"order_id": "12345", "user_id": user_id, "fund_code": fund_code}

# 🎯 快速集成指南
"""
如何在现有代码中快速集成自动化日志：

1. 导入自动化日志工具
   from app.utils.auto_logger import auto_log, log_context, quick_log

2. 为函数添加装饰器（一行代码）
   @auto_log("fund")  # 或者 "okx", "wise", "paypal" 等
   async def your_function():
       pass

3. 为代码块添加上下文管理器（一行代码）
   with log_context("business", "操作描述"):
       your_code_here()

4. 使用便捷函数记录日志（一行代码）
   quick_log("消息", "service", "level", key=value)

就这么简单！所有日志都会自动分类、格式化，并在Web界面中显示。
"""