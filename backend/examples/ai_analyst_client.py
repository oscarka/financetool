#!/usr/bin/env python3
"""
AI分析师数据API客户端示例

这个脚本演示了如何使用Python调用AI分析师数据API获取原始数据，
并基于这些数据进行独立的投资分析和计算。
"""

import requests
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AIAnalystDataClient:
    """AI分析师数据API客户端"""
    
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
            'User-Agent': 'AIAnalystDataClient/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, 
                     max_retries: int = 3) -> Optional[Dict]:
        """发送HTTP请求并处理错误"""
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
                    time.sleep(2 ** attempt)
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
    
    # 原始数据获取方法
    def get_asset_data(self, base_currency: str = "CNY", include_small_amounts: bool = False) -> Optional[Dict]:
        """获取当前资产持仓数据"""
        logger.info(f"获取资产数据 (基准货币: {base_currency})")
        return self._make_request('GET', '/asset-data', {
            'base_currency': base_currency,
            'include_small_amounts': include_small_amounts
        })
    
    def get_transaction_data(self, start_date: str = None, end_date: str = None,
                           platform: str = None, asset_type: str = None,
                           operation_type: str = None, limit: int = 1000) -> Optional[Dict]:
        """获取交易数据"""
        params = {'limit': limit}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if platform:
            params['platform'] = platform
        if asset_type:
            params['asset_type'] = asset_type
        if operation_type:
            params['operation_type'] = operation_type
            
        logger.info(f"获取交易数据 (参数: {params})")
        return self._make_request('GET', '/transaction-data', params)
    
    def get_historical_data(self, days: int = 90, asset_codes: str = None, 
                          base_currency: str = "CNY") -> Optional[Dict]:
        """获取历史数据"""
        params = {'days': days, 'base_currency': base_currency}
        if asset_codes:
            params['asset_codes'] = asset_codes
            
        logger.info(f"获取历史数据 (参数: {params})")
        return self._make_request('GET', '/historical-data', params)
    
    def get_market_data(self) -> Optional[Dict]:
        """获取市场数据"""
        logger.info("获取市场数据")
        return self._make_request('GET', '/market-data')
    
    def get_dca_data(self) -> Optional[Dict]:
        """获取定投数据"""
        logger.info("获取定投数据")
        return self._make_request('GET', '/dca-data')
    
    def health_check(self) -> Optional[Dict]:
        """健康检查"""
        return self._make_request('GET', '/health')


class InvestmentAnalyzer:
    """基于原始数据的投资分析器"""
    
    def __init__(self, client: AIAnalystDataClient):
        self.client = client
    
    def analyze_portfolio_allocation(self, base_currency: str = "CNY") -> Dict[str, Any]:
        """分析投资组合配置"""
        data = self.client.get_asset_data(base_currency=base_currency)
        if not data:
            return {"error": "无法获取资产数据"}
        
        holdings = data['current_holdings']
        if not holdings:
            return {"error": "没有持仓数据"}
        
        # 计算总价值和权重
        total_value = sum(h['base_currency_value'] for h in holdings)
        weights = [h['base_currency_value'] / total_value for h in holdings]
        
        # 集中度分析 - 赫芬达尔指数
        hhi = sum(w**2 for w in weights) * 10000
        
        # 平台分散度
        platforms = {}
        asset_types = {}
        
        for holding in holdings:
            platform = holding['platform']
            asset_type = holding['asset_type']
            value = holding['base_currency_value']
            
            if platform not in platforms:
                platforms[platform] = 0
            platforms[platform] += value
            
            if asset_type not in asset_types:
                asset_types[asset_type] = 0
            asset_types[asset_type] += value
        
        # 计算分散化评分
        platform_count = len(platforms)
        asset_type_count = len(asset_types)
        max_weight = max(weights) * 100
        
        # 简单的分散化评分算法
        diversification_score = min(100, 
            (platform_count * 15) + 
            (asset_type_count * 20) + 
            (30 if max_weight < 20 else 10) +
            (35 if hhi < 2000 else 15)
        )
        
        return {
            "total_value": total_value,
            "currency": base_currency,
            "holdings_count": len(holdings),
            "concentration_metrics": {
                "hhi_index": hhi,
                "hhi_level": "低" if hhi < 1500 else "中" if hhi < 2500 else "高",
                "max_holding_weight": max_weight,
                "top_5_weight": sum(sorted(weights, reverse=True)[:5]) * 100
            },
            "diversification": {
                "platform_count": platform_count,
                "asset_type_count": asset_type_count,
                "diversification_score": diversification_score
            },
            "allocation_breakdown": {
                "by_platform": [
                    {"name": k, "value": v, "weight": v/total_value*100} 
                    for k, v in sorted(platforms.items(), key=lambda x: x[1], reverse=True)
                ],
                "by_asset_type": [
                    {"name": k, "value": v, "weight": v/total_value*100} 
                    for k, v in sorted(asset_types.items(), key=lambda x: x[1], reverse=True)
                ]
            }
        }
    
    def analyze_trading_behavior(self, days: int = 90) -> Dict[str, Any]:
        """分析交易行为模式"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        data = self.client.get_transaction_data(
            start_date=start_date, 
            end_date=end_date,
            limit=1000
        )
        
        if not data or not data['transactions']:
            return {"error": "没有交易数据"}
        
        transactions = data['transactions']
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # 交易频率分析
        monthly_freq = df.groupby(df['date'].dt.to_period('M')).size()
        weekly_freq = df.groupby(df['date'].dt.to_period('W')).size()
        
        # 操作类型分析
        operation_stats = df.groupby('operation_type').agg({
            'amount': ['count', 'sum', 'mean'],
            'emotion_score': 'mean'
        }).round(2)
        
        # 投资纪律性分析
        buy_operations = df[df['operation_type'] == 'buy']
        if len(buy_operations) > 1:
            buy_amounts = buy_operations['amount']
            amount_consistency = 1 - (buy_amounts.std() / buy_amounts.mean())  # 金额一致性
        else:
            amount_consistency = 0
        
        # 情绪分析
        emotion_scores = df['emotion_score'].dropna()
        avg_emotion = emotion_scores.mean() if len(emotion_scores) > 0 else None
        emotion_trend = None
        if len(emotion_scores) >= 10:
            # 简单的线性趋势
            x = np.arange(len(emotion_scores))
            slope, _ = np.polyfit(x, emotion_scores, 1)
            emotion_trend = "上升" if slope > 0.1 else "下降" if slope < -0.1 else "稳定"
        
        return {
            "analysis_period": f"{start_date} 至 {end_date}",
            "total_transactions": len(transactions),
            "trading_frequency": {
                "monthly_average": monthly_freq.mean() if len(monthly_freq) > 0 else 0,
                "weekly_average": weekly_freq.mean() if len(weekly_freq) > 0 else 0,
                "consistency": amount_consistency
            },
            "operation_breakdown": operation_stats.to_dict(),
            "behavioral_indicators": {
                "investment_discipline": "高" if amount_consistency > 0.7 else "中" if amount_consistency > 0.4 else "低",
                "average_emotion_score": avg_emotion,
                "emotion_trend": emotion_trend,
                "trading_pattern": "定期" if amount_consistency > 0.6 else "随机"
            }
        }
    
    def calculate_performance_metrics(self, days: int = 90, base_currency: str = "CNY") -> Dict[str, Any]:
        """计算投资绩效指标"""
        data = self.client.get_historical_data(days=days, base_currency=base_currency)
        if not data or not data['asset_values']:
            return {"error": "没有历史数据"}
        
        # 转换为DataFrame
        df = pd.DataFrame(data['asset_values'])
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['base_value'] = pd.to_numeric(df['base_value'])
        
        # 按日期聚合总资产
        daily_totals = df.groupby('date')['base_value'].sum().sort_index()
        
        if len(daily_totals) < 2:
            return {"error": "数据点不足"}
        
        # 计算收益率
        returns = daily_totals.pct_change().dropna()
        
        # 绩效指标计算
        total_return = (daily_totals.iloc[-1] / daily_totals.iloc[0] - 1) * 100
        annual_return = ((daily_totals.iloc[-1] / daily_totals.iloc[0]) ** (365/days) - 1) * 100
        volatility = returns.std() * np.sqrt(252) * 100  # 年化波动率
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min() * 100
        
        # 夏普比率 (假设无风险利率2%)
        risk_free_rate = 0.02 / 252
        excess_returns = returns - risk_free_rate
        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # 风险评级
        def get_risk_level(vol):
            if vol < 10:
                return "低风险"
            elif vol < 15:
                return "中低风险"
            elif vol < 25:
                return "中风险"
            elif vol < 35:
                return "中高风险"
            else:
                return "高风险"
        
        return {
            "analysis_period": f"{days}天",
            "data_points": len(daily_totals),
            "return_metrics": {
                "total_return_pct": round(total_return, 2),
                "annualized_return_pct": round(annual_return, 2),
                "best_day_pct": round(returns.max() * 100, 2),
                "worst_day_pct": round(returns.min() * 100, 2)
            },
            "risk_metrics": {
                "annual_volatility_pct": round(volatility, 2),
                "max_drawdown_pct": round(max_drawdown, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "risk_level": get_risk_level(volatility)
            },
            "portfolio_values": {
                "start_value": round(daily_totals.iloc[0], 2),
                "end_value": round(daily_totals.iloc[-1], 2),
                "peak_value": round(daily_totals.max(), 2)
            }
        }
    
    def analyze_dca_effectiveness(self) -> Dict[str, Any]:
        """分析定投效果"""
        data = self.client.get_dca_data()
        if not data:
            return {"error": "无法获取定投数据"}
        
        plans = data['dca_plans']
        executions = data['execution_history']
        
        if not plans:
            return {"error": "没有定投计划"}
        
        # 按计划分析
        plan_analysis = {}
        
        for plan in plans:
            plan_id = plan['id']
            plan_executions = [e for e in executions if e['dca_plan_id'] == plan_id]
            
            if not plan_executions:
                continue
            
            # 计算成本平均效果
            total_invested = sum(e['amount'] for e in plan_executions)
            total_shares = sum(e['quantity'] for e in plan_executions if e['quantity'])
            avg_cost = total_invested / total_shares if total_shares > 0 else 0
            
            # 获取净值数据
            navs = [e['nav'] for e in plan_executions if e['nav']]
            if navs:
                nav_volatility = np.std(navs) / np.mean(navs) if len(navs) > 1 else 0
                cost_vs_avg_nav = avg_cost / np.mean(navs) if np.mean(navs) > 0 else 1
            else:
                nav_volatility = 0
                cost_vs_avg_nav = 1
            
            plan_analysis[plan_id] = {
                "plan_name": plan['plan_name'],
                "asset_name": plan['asset_name'],
                "status": plan['status'],
                "execution_count": len(plan_executions),
                "total_invested": total_invested,
                "average_cost": avg_cost,
                "cost_efficiency": "良好" if cost_vs_avg_nav < 0.98 else "一般" if cost_vs_avg_nav < 1.02 else "较差",
                "nav_volatility": nav_volatility,
                "consistency": "高" if plan['execution_count'] >= len(plan_executions) * 0.9 else "中等"
            }
        
        # 整体统计
        active_plans = len([p for p in plans if p['status'] == 'active'])
        total_monthly_investment = sum(
            float(p['amount']) for p in plans 
            if p['status'] == 'active' and p['frequency'] == 'monthly'
        )
        
        return {
            "overall_stats": {
                "total_plans": len(plans),
                "active_plans": active_plans,
                "total_executions": len(executions),
                "monthly_investment": total_monthly_investment
            },
            "plan_analysis": plan_analysis,
            "recommendations": self._generate_dca_recommendations(plan_analysis)
        }
    
    def _generate_dca_recommendations(self, plan_analysis: Dict) -> List[str]:
        """生成定投建议"""
        recommendations = []
        
        for plan_id, analysis in plan_analysis.items():
            if analysis['cost_efficiency'] == '较差':
                recommendations.append(f"计划 {analysis['plan_name']}: 考虑调整定投时机或金额")
            
            if analysis['consistency'] != '高':
                recommendations.append(f"计划 {analysis['plan_name']}: 建议提高执行一致性")
        
        if not recommendations:
            recommendations.append("定投计划执行良好，继续保持")
        
        return recommendations


class DataFormatter:
    """数据格式化工具"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "CNY") -> str:
        """格式化货币金额"""
        symbols = {"CNY": "¥", "USD": "$", "EUR": "€", "GBP": "£", "HKD": "HK$"}
        symbol = symbols.get(currency, currency + " ")
        return f"{symbol}{amount:,.2f}"
    
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
    """主函数 - 演示数据获取和分析"""
    
    # 配置
    API_BASE_URL = "http://localhost:8000/api/v1/ai-analyst"
    API_KEY = "ai_analyst_key_2024"  # 替换为实际的API密钥
    
    # 创建客户端和分析器
    client = AIAnalystDataClient(API_BASE_URL, API_KEY)
    analyzer = InvestmentAnalyzer(client)
    formatter = DataFormatter()
    
    print("=" * 70)
    print("AI分析师数据分析演示")
    print("=" * 70)
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    health = client.health_check()
    if health:
        print(f"✓ API服务正常: {health['message']}")
    else:
        print("✗ API服务不可用，请检查配置")
        return
    
    # 2. 投资组合配置分析
    print("\n2. 投资组合配置分析...")
    portfolio_analysis = analyzer.analyze_portfolio_allocation()
    if 'error' not in portfolio_analysis:
        print(f"总资产: {formatter.format_currency(portfolio_analysis['total_value'])}")
        print(f"持仓数量: {portfolio_analysis['holdings_count']}")
        print(f"分散化评分: {formatter.format_percentage(portfolio_analysis['diversification']['diversification_score'])}")
        
        concentration = portfolio_analysis['concentration_metrics']
        print(f"集中度指数: {concentration['hhi_index']:.0f} ({concentration['hhi_level']})")
        print(f"最大持仓权重: {formatter.format_percentage(concentration['max_holding_weight'])}")
        
        print("\n平台分布:")
        for platform in portfolio_analysis['allocation_breakdown']['by_platform'][:3]:
            print(f"  - {platform['name']}: {formatter.format_currency(platform['value'])} "
                  f"({formatter.format_percentage(platform['weight'])})")
    else:
        print(f"✗ {portfolio_analysis['error']}")
    
    # 3. 交易行为分析
    print("\n3. 交易行为分析...")
    trading_analysis = analyzer.analyze_trading_behavior(days=90)
    if 'error' not in trading_analysis:
        print(f"分析期间: {trading_analysis['analysis_period']}")
        print(f"总交易次数: {trading_analysis['total_transactions']}")
        
        freq = trading_analysis['trading_frequency']
        print(f"月均交易: {freq['monthly_average']:.1f}次")
        print(f"投资纪律: {trading_analysis['behavioral_indicators']['investment_discipline']}")
        
        if trading_analysis['behavioral_indicators']['average_emotion_score']:
            print(f"平均情绪评分: {trading_analysis['behavioral_indicators']['average_emotion_score']:.1f}/10")
    else:
        print(f"✗ {trading_analysis['error']}")
    
    # 4. 绩效指标计算
    print("\n4. 投资绩效分析...")
    performance = analyzer.calculate_performance_metrics(days=90)
    if 'error' not in performance:
        returns = performance['return_metrics']
        risks = performance['risk_metrics']
        
        print(f"分析期间: {performance['analysis_period']} ({performance['data_points']}个数据点)")
        print(f"总收益率: {formatter.format_percentage(returns['total_return_pct'])}")
        print(f"年化收益率: {formatter.format_percentage(returns['annualized_return_pct'])}")
        print(f"年化波动率: {formatter.format_percentage(risks['annual_volatility_pct'])}")
        print(f"最大回撤: {formatter.format_percentage(risks['max_drawdown_pct'])}")
        print(f"夏普比率: {risks['sharpe_ratio']:.2f}")
        print(f"风险等级: {risks['risk_level']}")
    else:
        print(f"✗ {performance['error']}")
    
    # 5. 定投效果分析
    print("\n5. 定投计划分析...")
    dca_analysis = analyzer.analyze_dca_effectiveness()
    if 'error' not in dca_analysis:
        stats = dca_analysis['overall_stats']
        print(f"定投计划总数: {stats['total_plans']} (活跃: {stats['active_plans']})")
        print(f"执行次数: {stats['total_executions']}")
        print(f"月度投入: {formatter.format_currency(stats['monthly_investment'])}")
        
        if dca_analysis['plan_analysis']:
            print("\n计划详情:")
            for plan_id, analysis in list(dca_analysis['plan_analysis'].items())[:2]:
                print(f"  - {analysis['plan_name']}: 执行{analysis['execution_count']}次, "
                      f"成本效率{analysis['cost_efficiency']}")
        
        print("\n建议:")
        for rec in dca_analysis['recommendations'][:2]:
            print(f"  • {rec}")
    else:
        print(f"✗ {dca_analysis['error']}")
    
    # 6. 市场环境数据
    print("\n6. 市场环境数据...")
    market_data = client.get_market_data()
    if market_data:
        indicators = market_data['market_indicators']
        print(f"跟踪基金数: {indicators['total_funds_tracked']}")
        print(f"活跃基金数: {indicators['active_funds_last_week']}")
        print(f"用户操作数: {indicators['total_user_operations']}")
        
        rates = market_data['exchange_rates'][:3]
        if rates:
            print("\n主要汇率:")
            for rate in rates:
                print(f"  {rate['from_currency']}/{rate['to_currency']}: {rate['rate']:.4f}")
    
    print("\n" + "=" * 70)
    print("数据分析完成！")
    print("\n注意: 以上分析基于API提供的原始数据，")
    print("具体的投资决策需要结合更多因素综合考虑。")


if __name__ == "__main__":
    main()