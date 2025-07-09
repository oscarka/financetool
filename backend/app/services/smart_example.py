"""
智能日志系统示例 - 展示最少的代码获得最多的功能
"""

from app.utils.smart_logger import log, context, log_msg

# 🎯 示例1: 最简单的使用 - 只需要一行装饰器！
@log  # 自动检测服务类型，自动记录一切
async def get_fund_nav(fund_code: str):
    """获取基金净值 - 系统自动检测这是基金相关函数"""
    # 你的业务代码...
    return {"fund_code": fund_code, "nav": 1.2345}

# 🎯 示例2: 自动检测文件名 - fund_api_service.py
@log  # 自动检测到这是fund服务
async def sync_fund_data(fund_codes: list):
    """同步基金数据 - 自动归类到基金API分类"""
    results = []
    for code in fund_codes:
        result = await get_fund_nav(code)
        results.append(result)
    return results

# 🎯 示例3: 自动检测函数名 - get_okx_balance
@log  # 自动检测到这是okx服务
async def get_okx_balance():
    """获取OKX余额 - 自动归类到OKX交易所分类"""
    # 你的业务代码...
    return {"balance": 1000.0, "currency": "USDT"}

# 🎯 示例4: 自动检测类名
class PayPalService:
    @log  # 自动检测到这是paypal服务
    async def process_payment(self, amount: float):
        """处理PayPal支付 - 自动归类到PayPal支付分类"""
        # 你的业务代码...
        return {"transaction_id": "abc123", "status": "success"}

# 🎯 示例5: 智能上下文管理器
async def process_order():
    """处理订单 - 自动检测服务类型"""
    
    with context("验证用户"):  # 自动检测到这是business服务
        user = await validate_user(123)
    
    with context("获取基金信息"):  # 自动检测到这是fund服务
        fund = await get_fund_nav("000001")
    
    with context("保存订单"):  # 自动检测到这是database服务
        order = await save_order(user, fund)
    
    # 一行代码记录成功
    log_msg("订单处理成功", order_id=order["id"])

# 🎯 示例6: 数据库操作 - 自动检测
class DatabaseService:
    @log  # 自动检测到这是database服务
    async def create_user(self, user_data: dict):
        """创建用户 - 自动归类到数据库分类"""
        # 你的业务代码...
        return {"user_id": 456, "name": user_data["name"]}
    
    @log  # 自动检测到这是database服务
    async def query_users(self, filters: dict):
        """查询用户 - 自动归类到数据库分类"""
        # 你的业务代码...
        return [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]

# 🎯 示例7: 定时任务 - 自动检测
class SchedulerService:
    @log  # 自动检测到这是scheduler服务
    async def sync_all_funds(self):
        """同步所有基金 - 自动归类到定时任务分类"""
        fund_codes = ["000001", "000002", "000003"]
        await sync_fund_data(fund_codes)
        log_msg("基金同步完成", count=len(fund_codes))

# 🎯 示例8: API接口 - 自动检测
class APIService:
    @log  # 自动检测到这是api服务
    async def handle_request(self, request_data: dict):
        """处理API请求 - 自动归类到API接口分类"""
        # 你的业务代码...
        return {"status": "success", "data": request_data}

# 🎯 实际使用场景示例
class InvestmentService:
    """投资服务 - 展示真实业务场景"""
    
    def __init__(self):
        self.db = DatabaseService()
        self.paypal = PayPalService()
    
    @log  # 自动检测到这是business服务
    async def process_investment(self, user_id: int, fund_code: str, amount: float):
        """处理投资 - 完整的业务流程"""
        
        # 1. 获取用户信息
        with context("获取用户信息"):
            user = await self.db.query_users({"id": user_id})
        
        # 2. 获取基金信息
        with context("获取基金信息"):
            fund = await get_fund_nav(fund_code)
        
        # 3. 处理支付
        with context("处理支付"):
            payment = await self.paypal.process_payment(amount)
        
        # 4. 保存投资记录
        with context("保存投资记录"):
            investment = await self.db.create_user({
                "user_id": user_id,
                "fund_code": fund_code,
                "amount": amount,
                "payment_id": payment["transaction_id"]
            })
        
        # 5. 记录成功
        log_msg("投资处理成功", 
                user_id=user_id, 
                fund_code=fund_code, 
                amount=amount,
                investment_id=investment["user_id"])
        
        return investment

# 🎯 使用说明
"""
智能日志系统的神奇之处：

1. 零配置 - 不需要任何设置
2. 自动检测 - 根据文件名、函数名、类名自动判断服务类型
3. 一行代码 - 只需要添加 @log 装饰器
4. 自动记录 - 参数、时间、异常、结果全部自动记录
5. 自动分类 - 在Web界面中自动归类显示

检测规则：
- 文件名包含 'fund' -> 基金API分类
- 文件名包含 'okx' -> OKX交易所分类  
- 文件名包含 'paypal' -> PayPal支付分类
- 文件名包含 'database' -> 数据库分类
- 函数名包含 'get_fund' -> 基金API分类
- 函数名包含 'okx_' -> OKX交易所分类
- 类名包含 'PayPal' -> PayPal支付分类

现在开发者只需要关心业务逻辑，日志系统会自动处理一切！
"""