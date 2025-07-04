import akshare as ak
import traceback

def test_fund_dividend():
    fund_code = "003547"
    print(f"测试基金 {fund_code} 的分红数据")
    
    # 1. 测试基金分红接口 fund_fh_em
    try:
        print("\n1. 测试基金分红接口 fund_fh_em:")
        df = ak.fund_fh_em()
        df = df[df['基金代码'] == fund_code]
        print(f"返回字段: {df.columns.tolist() if not df.empty else '无数据'}")
        print(f"数据行数: {len(df) if not df.empty else 0}")
        if not df.empty:
            print("前3行数据:")
            print(df.head(3))
        else:
            print("无分红数据")
    except Exception as e:
        print(f"fund_fh_em接口调用失败: {e}")
    
    # 2. 测试基金详情接口
    try:
        print("\n2. 测试基金详情接口:")
        df = ak.fund_individual_detail_info_xq(symbol=fund_code)
        print(f"返回字段: {df.columns.tolist() if not df.empty else '无数据'}")
        print(f"数据行数: {len(df) if not df.empty else 0}")
        if not df.empty:
            print("前3行数据:")
            print(df.head(3))
    except Exception as e:
        print(f"基金详情接口调用失败: {e}")
    
    # 3. 测试ETF分红接口（虽然可能不适用）
    try:
        print("\n3. 测试ETF分红接口:")
        df = ak.fund_etf_dividend_sina(symbol=fund_code)
        print(f"返回字段: {df.columns.tolist() if not df.empty else '无数据'}")
        print(f"数据行数: {len(df) if not df.empty else 0}")
        if not df.empty:
            print("前3行数据:")
            print(df.head(3))
    except Exception as e:
        print(f"ETF分红接口调用失败: {e}")

if __name__ == "__main__":
    test_fund_dividend() 