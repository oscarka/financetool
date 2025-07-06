import asyncio
import os
import sys
sys.path.append('.')

from app.services.okx_api_service import OKXAPIService

async def test_our_okx():
    """测试我们自己的OKX服务"""
    print("测试我们自己的OKX服务...")
    
    # 设置环境变量
    os.environ['OKX_API_KEY'] = '8f8940ab-869b-4b38-93e3-dbd170fa0022'
    os.environ['OKX_SECRET_KEY'] = 'C46FB5BE7538434CE356235AEE71725E'
    os.environ['OKX_PASSPHRASE'] = 'Okx13579！'
    os.environ['OKX_SANDBOX'] = 'true'
    
    try:
        service = OKXAPIService()
        
        # 测试账户余额
        print("测试账户余额接口...")
        account_result = await service.get_account_balance()
        print(f"账户余额结果: {account_result}")
        
        # 测试行情接口
        print("\n测试行情接口...")
        ticker_result = await service.get_ticker("BTC-USDT")
        print(f"行情结果: {ticker_result}")
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_our_okx()) 