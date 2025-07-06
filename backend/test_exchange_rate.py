import akshare as ak
import pandas as pd
from app.services.exchange_rate_service import ExchangeRateService

def test_exchange_rate_service():
    """测试汇率服务"""
    print("=== 测试汇率服务 ===")
    
    # 1. 测试获取货币列表
    print("\n1. 测试获取货币列表:")
    try:
        currencies = ExchangeRateService.get_currency_list()
        print(f"获取到 {len(currencies)} 种货币")
        if currencies:
            print("前5种货币:")
            for i, currency in enumerate(currencies[:5]):
                print(f"  {i+1}. {currency['code']} - {currency['name']} (汇率: {currency['rate']})")
    except Exception as e:
        print(f"获取货币列表失败: {e}")
    
    # 2. 测试获取所有汇率
    print("\n2. 测试获取所有汇率:")
    try:
        rates = ExchangeRateService.get_all_exchange_rates()
        print(f"获取到 {len(rates)} 种货币的汇率")
        if rates:
            print("前5种货币汇率:")
            for i, rate in enumerate(rates[:5]):
                print(f"  {i+1}. {rate['currency']} - 中行折算价: {rate['middle_rate']}")
    except Exception as e:
        print(f"获取所有汇率失败: {e}")
    
    # 3. 测试获取指定货币汇率
    print("\n3. 测试获取美元汇率:")
    try:
        usd_rate = ExchangeRateService.get_exchange_rate("美元")
        if usd_rate:
            print(f"美元汇率: {usd_rate}")
        else:
            print("未找到美元汇率")
    except Exception as e:
        print(f"获取美元汇率失败: {e}")
    
    # 4. 测试货币转换
    print("\n4. 测试货币转换:")
    try:
        converted = ExchangeRateService.convert_currency(100, "美元", "CNY")
        if converted:
            print(f"100美元 = {converted} 人民币")
        else:
            print("货币转换失败")
    except Exception as e:
        print(f"货币转换失败: {e}")
    
    # 5. 测试akshare原始数据
    print("\n5. 测试akshare原始数据:")
    try:
        df = ak.currency_boc_sina()
        print(f"akshare返回数据行数: {len(df)}")
        print(f"数据列: {df.columns.tolist()}")
        if not df.empty:
            print("前3行数据:")
            print(df.head(3))
    except Exception as e:
        print(f"akshare原始数据获取失败: {e}")

if __name__ == "__main__":
    test_exchange_rate_service() 