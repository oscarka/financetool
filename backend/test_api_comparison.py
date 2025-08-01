#!/usr/bin/env python3
"""
测试天天基金网API的数据
"""
import urllib.request
import urllib.parse
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any

class APITester:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # 天天基金网API
        self.tiantian_fund_api_base_url = "http://fundgz.1234567.com.cn"
    
    def get_fund_nav_tiantian(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """从天天基金网获取基金净值"""
        try:
            url = f"{self.tiantian_fund_api_base_url}/js/{fund_code}.js"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')
            
            print(f"天天基金网API返回内容: {content[:200]}...")
            
            # 解析JSONP格式的数据
            if content.startswith("jsonpgz(") and content.endswith(")"):
                json_str = content[8:-1]  # 去掉 jsonpgz( 和 )
                data = json.loads(json_str)
                
                if data.get("fundcode") == fund_code and data.get("dwjz") and data.get("jzrq"):
                    nav = Decimal(data["dwjz"])
                    nav_date_api = datetime.strptime(data["jzrq"], "%Y-%m-%d").date()
                    
                    return {
                        "fund_code": fund_code,
                        "nav_date": nav_date_api,
                        "nav": nav,
                        "accumulated_nav": Decimal(data["ljjz"]) if data.get("ljjz") else None,
                        "growth_rate": float(data["gszzl"]) if data.get("gszzl") else None,
                        "source": "tiantian"
                    }
            return None
        except Exception as e:
            print(f"天天基金网API失败: {e}")
            return None
    
    def test_fund_api(self, fund_code: str):
        """测试天天基金网API"""
        print(f"\n=== 测试基金 {fund_code} ===")
        
        # 测试当前基金
        data = self.get_fund_nav_tiantian(fund_code)
        
        if data:
            print(f"基金代码: {data['fund_code']}")
            print(f"净值日期: {data['nav_date']}")
            print(f"单位净值: {data['nav']}")
            print(f"累计净值: {data['accumulated_nav']}")
            print(f"增长率: {data['growth_rate']}%")
            print(f"数据来源: {data['source']}")
        else:
            print("获取数据失败")
        
        # 避免请求过快
        import time
        time.sleep(1)

def main():
    tester = APITester()
    
    # 测试几个不同的基金
    test_funds = [
        "000001",  # 华夏成长混合
        "110022",  # 易方达消费行业股票
        "519674",  # 银河创新成长混合
        "161725",  # 招商中证白酒指数
        "005827",  # 易方达蓝筹精选混合
    ]
    
    for fund_code in test_funds:
        tester.test_fund_api(fund_code)

if __name__ == "__main__":
    main()