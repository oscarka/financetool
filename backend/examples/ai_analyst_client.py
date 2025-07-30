#!/usr/bin/env python3
"""
AI分析师API客户端示例

这个脚本演示了如何使用Python调用AI分析师API获取资产数据和分析结果。
包含完整的错误处理、重试机制和数据格式化。
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AIAnalystClient:
    """AI分析师API客户端"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'AIAnalystClient/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, 
                     max_retries: int = 3) -> Optional[Dict]:
        """
        发送HTTP请求并处理错误
        
        Args:
            method: HTTP方法
            endpoint: API端点
            params: 查询参数
            max_retries: 最大重试次数
            
        Returns:
            响应数据或None
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logger.error("API密钥无效或已过期")
                    return None
                elif response.status_code == 429:
                    logger.warning("请求频率超限，等待后重试")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                elif response.status_code >= 500:
                    logger.warning(f"服务器错误 {response.status_code}，重试中...")
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"请求失败: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，重试 {attempt + 1}/{max_retries}")
                time.sleep(1)
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                return None
        
        logger.error(f"请求失败，已重试 {max_retries} 次")
        return None
    
    def get_asset_summary(self, base_currency: str = "CNY") -> Optional[Dict]:
        """获取资产总览"""
        logger.info(f"获取资产总览 (基准货币: {base_currency})")
        return self._make_request('GET', '/asset-summary', {'base_currency': base_currency})
    
    def get_investment_history(self, start_date: str = None, end_date: str = None,
                             platform: str = None, asset_type: str = None,
                             limit: int = 100) -> Optional[Dict]:
        """获取投资历史"""
        params = {'limit': limit}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if platform:
            params['platform'] = platform
        if asset_type:
            params['asset_type'] = asset_type
            
        logger.info(f"获取投资历史 (参数: {params})")
        return self._make_request('GET', '/investment-history', params)
    
    def get_performance_analysis(self, base_currency: str = "CNY", days: int = 30) -> Optional[Dict]:
        """获取绩效分析"""
        params = {'base_currency': base_currency, 'days': days}
        logger.info(f"获取绩效分析 (参数: {params})")
        return self._make_request('GET', '/performance-analysis', params)
    
    def get_exchange_rates(self, base_currency: str = "CNY", 
                          target_currencies: str = None) -> Optional[Dict]:
        """获取汇率数据"""
        params = {'base_currency': base_currency}
        if target_currencies:
            params['target_currencies'] = target_currencies
            
        logger.info(f"获取汇率数据 (参数: {params})")
        return self._make_request('GET', '/exchange-rates', params)
    
    def get_market_data(self, fund_codes: str = None, days: int = 7) -> Optional[Dict]:
        """获取市场数据"""
        params = {'days': days}
        if fund_codes:
            params['fund_codes'] = fund_codes
            
        logger.info(f"获取市场数据 (参数: {params})")
        return self._make_request('GET', '/market-data', params)
    
    def get_portfolio_analysis(self, base_currency: str = "CNY") -> Optional[Dict]:
        """获取投资组合分析"""
        params = {'base_currency': base_currency}
        logger.info(f"获取投资组合分析 (参数: {params})")
        return self._make_request('GET', '/portfolio-analysis', params)
    
    def get_dca_analysis(self) -> Optional[Dict]:
        """获取定投计划分析"""
        logger.info("获取定投计划分析")
        return self._make_request('GET', '/dca-analysis')
    
    def get_risk_assessment(self, base_currency: str = "CNY", days: int = 90) -> Optional[Dict]:
        """获取风险评估"""
        params = {'base_currency': base_currency, 'days': days}
        logger.info(f"获取风险评估 (参数: {params})")
        return self._make_request('GET', '/risk-assessment', params)
    
    def health_check(self) -> Optional[Dict]:
        """健康检查"""
        return self._make_request('GET', '/health')


class DataFormatter:
    """数据格式化工具"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "CNY") -> str:
        """格式化货币金额"""
        if currency == "CNY":
            return f"¥{amount:,.2f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """格式化百分比"""
        return f"{value:.2f}%"
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """格式化日期"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str


def main():
    """主函数 - 演示API使用"""
    
    # 配置
    API_BASE_URL = "https://your-domain.com/api/v1/ai-analyst"
    API_KEY = "ai_analyst_key_2024"  # 替换为实际的API密钥
    
    # 创建客户端
    client = AIAnalystClient(API_BASE_URL, API_KEY)
    formatter = DataFormatter()
    
    print("=" * 60)
    print("AI分析师数据获取演示")
    print("=" * 60)
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    health = client.health_check()
    if health:
        print(f"✓ API服务正常: {health['message']}")
    else:
        print("✗ API服务不可用，请检查配置")
        return
    
    # 2. 资产总览
    print("\n2. 资产总览...")
    summary = client.get_asset_summary()
    if summary:
        print(f"总资产: {summary['total_assets']}")
        print(f"资产数量: {summary.get('total_assets', {})}")
        print(f"最后更新: {formatter.format_date(summary['last_update_time'])}")
        
        print("\n平台分布:")
        for platform in summary['platform_breakdown'][:3]:
            print(f"  - {platform['platform']}: {formatter.format_currency(platform['value'])} "
                  f"({formatter.format_percentage(platform['percentage'])})")
    
    # 3. 投资历史（最近30天）
    print("\n3. 投资历史...")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    history = client.get_investment_history(start_date=start_date, end_date=end_date, limit=5)
    
    if history:
        print(f"总操作次数: {len(history['operations'])}")
        print(f"总投入: {history['total_invested']}")
        
        print("\n最近操作:")
        for op in history['operations'][:3]:
            print(f"  - {formatter.format_date(op['date'])}: "
                  f"{op['operation_type']} {op['asset_name']} "
                  f"{formatter.format_currency(op['amount'], op['currency'])}")
    
    # 4. 绩效分析
    print("\n4. 绩效分析...")
    performance = client.get_performance_analysis(days=30)
    if performance:
        overall = performance['overall_return']
        print(f"30天收益率: {formatter.format_percentage(overall.get('cny', 0))}")
        print(f"期初价值: {formatter.format_currency(overall.get('start_value', 0))}")
        print(f"期末价值: {formatter.format_currency(overall.get('end_value', 0))}")
    
    # 5. 投资组合分析
    print("\n5. 投资组合分析...")
    portfolio = client.get_portfolio_analysis()
    if portfolio:
        summary = portfolio['portfolio_summary']
        print(f"组合总价值: {formatter.format_currency(summary['total_value'])}")
        print(f"资产数量: {summary['number_of_assets']}")
        print(f"平台数量: {summary['number_of_platforms']}")
        print(f"分散化评分: {formatter.format_percentage(portfolio['diversification_score'])}")
        
        # 风险提示
        if portfolio['rebalancing_suggestions']:
            print("\n⚠️ 再平衡建议:")
            for suggestion in portfolio['rebalancing_suggestions'][:2]:
                print(f"  - {suggestion['reason']}")
    
    # 6. 风险评估
    print("\n6. 风险评估...")
    risk = client.get_risk_assessment(days=90)
    if risk:
        metrics = risk['risk_metrics']
        print(f"年化波动率: {formatter.format_percentage(metrics['annual_volatility'] * 100)}")
        print(f"最大回撤: {formatter.format_percentage(metrics['max_drawdown'] * 100)}")
        print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
        print(f"风险等级: {metrics['risk_level']}")
    
    # 7. 汇率数据
    print("\n7. 汇率数据...")
    rates = client.get_exchange_rates(target_currencies="USD,EUR")
    if rates:
        print("当前汇率:")
        for rate in rates['rates'][:3]:
            print(f"  {rate['from_currency']}/{rate['to_currency']}: {rate['rate']:.4f}")
    
    print("\n" + "=" * 60)
    print("数据获取完成！")


if __name__ == "__main__":
    main()