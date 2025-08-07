#!/usr/bin/env python3
"""
AI分析师API测试脚本
直接测试各个API接口，模拟数据返回
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal

# 模拟数据生成函数
def generate_mock_asset_data():
    """生成模拟的资产数据"""
    snapshot_time = datetime.now()
    
    holdings = [
        {
            "id": 1001,
            "platform": "支付宝基金",
            "asset_type": "基金",
            "asset_code": "000001",
            "asset_name": "华夏成长混合",
            "currency": "CNY",
            "balance_original": 25000.00,
            "balance_cny": 25000.00,
            "balance_usd": 3571.43,
            "balance_eur": 3289.47,
            "base_currency_value": 25000.00,
            "snapshot_time": snapshot_time.isoformat(),
            "extra_data": {
                "fund_type": "混合型",
                "risk_level": "中高风险",
                "management_fee": 0.015
            }
        },
        {
            "id": 1002,
            "platform": "IBKR",
            "asset_type": "股票",
            "asset_code": "AAPL",
            "asset_name": "苹果公司",
            "currency": "USD",
            "balance_original": 5000.00,
            "balance_cny": 35000.00,
            "balance_usd": 5000.00,
            "balance_eur": 4605.26,
            "base_currency_value": 35000.00,
            "snapshot_time": snapshot_time.isoformat(),
            "extra_data": {
                "shares": 25.5,
                "avg_cost": 196.08,
                "sector": "Technology"
            }
        },
        {
            "id": 1003,
            "platform": "支付宝基金",
            "asset_type": "基金",
            "asset_code": "110022",
            "asset_name": "易方达消费行业",
            "currency": "CNY",
            "balance_original": 18000.00,
            "balance_cny": 18000.00,
            "balance_usd": 2571.43,
            "balance_eur": 2368.42,
            "base_currency_value": 18000.00,
            "snapshot_time": snapshot_time.isoformat(),
            "extra_data": {
                "fund_type": "股票型",
                "risk_level": "高风险",
                "management_fee": 0.015
            }
        }
    ]
    
    # 计算汇总数据
    total_by_currency = {"CNY": 43000.00, "USD": 5571.43, "EUR": 5131.58}
    
    platform_summary = [
        {
            "platform": "支付宝基金",
            "asset_count": 2,
            "total_value": 43000.00,
            "currencies": ["CNY"]
        },
        {
            "platform": "IBKR", 
            "asset_count": 1,
            "total_value": 35000.00,
            "currencies": ["USD"]
        }
    ]
    
    asset_type_summary = [
        {
            "asset_type": "基金",
            "asset_count": 2,
            "total_value": 43000.00,
            "unique_assets": 2
        },
        {
            "asset_type": "股票",
            "asset_count": 1,
            "total_value": 35000.00,
            "unique_assets": 1
        }
    ]
    
    return {
        "current_holdings": holdings,
        "total_value_by_currency": total_by_currency,
        "platform_summary": platform_summary,
        "asset_type_summary": asset_type_summary,
        "snapshot_time": snapshot_time.isoformat()
    }

def generate_mock_transaction_data():
    """生成模拟的交易数据"""
    transactions = []
    
    # 生成最近3个月的交易记录
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(20):
        transaction_date = base_date + timedelta(days=i*4 + 2)
        transactions.append({
            "id": 2000 + i,
            "date": transaction_date.isoformat(),
            "platform": "支付宝基金" if i % 3 != 0 else "IBKR",
            "asset_type": "基金" if i % 3 != 0 else "股票",
            "operation_type": "buy" if i % 5 != 4 else "sell",
            "asset_code": "000001" if i % 3 == 0 else ("110022" if i % 3 == 1 else "AAPL"),
            "asset_name": "华夏成长混合" if i % 3 == 0 else ("易方达消费行业" if i % 3 == 1 else "苹果公司"),
            "amount": 1000.00 + (i * 50),
            "currency": "CNY" if i % 3 != 2 else "USD",
            "quantity": 952.38 + (i * 10) if i % 3 != 2 else 5.2 + (i * 0.1),
            "price": None if i % 3 != 2 else 195.50 + i,
            "nav": 1.0500 + (i * 0.01) if i % 3 != 2 else None,
            "fee": 1.50,
            "strategy": "定投计划" if i % 4 == 0 else "价值投资",
            "emotion_score": 6 + (i % 5),
            "notes": f"第{i+1}次投资操作",
            "status": "completed",
            "dca_plan_id": 5 if i % 4 == 0 else None,
            "dca_execution_type": "scheduled" if i % 4 == 0 else None
        })
    
    # 计算统计数据
    buy_count = len([t for t in transactions if t['operation_type'] == 'buy'])
    sell_count = len([t for t in transactions if t['operation_type'] == 'sell'])
    
    summary_stats = {
        "total_operations": len(transactions),
        "operation_types": {
            "buy": {"count": buy_count, "total_amount": buy_count * 1200.00},
            "sell": {"count": sell_count, "total_amount": sell_count * 1500.00}
        },
        "currencies": {
            "CNY": {"count": 14, "total_amount": 18000.00},
            "USD": {"count": 6, "total_amount": 6000.00}
        },
        "platforms": {
            "支付宝基金": {"count": 14},
            "IBKR": {"count": 6}
        },
        "date_range": {
            "start": transactions[0]['date'],
            "end": transactions[-1]['date']
        }
    }
    
    # 时间序列数据
    time_series_data = [
        {"period": "2024-01", "operation_count": 8},
        {"period": "2024-02", "operation_count": 7},
        {"period": "2024-03", "operation_count": 5}
    ]
    
    return {
        "transactions": transactions,
        "summary_stats": summary_stats,
        "time_series_data": time_series_data
    }

def generate_mock_historical_data():
    """生成模拟的历史数据"""
    asset_values = []
    nav_data = []
    price_data = []
    
    # 生成90天的历史数据
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(90):
        current_date = base_date + timedelta(days=i)
        
        # 模拟资产价值波动
        base_value = 75000 + (i * 50) + (i % 10 * 500) - (i % 7 * 300)
        
        asset_values.append({
            "date": current_date.isoformat(),
            "platform": "支付宝基金",
            "asset_type": "基金",
            "asset_code": "000001",
            "asset_name": "华夏成长混合",
            "currency": "CNY",
            "balance_original": base_value * 0.6,
            "balance_cny": base_value * 0.6,
            "balance_usd": base_value * 0.6 / 7,
            "balance_eur": None,
            "base_value": base_value * 0.6,
            "extra_data": {}
        })
        
        # 每5天添加一个净值记录
        if i % 5 == 0:
            nav_data.append({
                "date": current_date.date().isoformat(),
                "fund_code": "000001",
                "nav": 1.0500 + (i * 0.001) + (i % 10 * 0.01),
                "accumulated_nav": 2.8940 + (i * 0.002),
                "growth_rate": 0.0095 + (i % 15 * 0.001),
                "source": "api"
            })
        
        # 每10天添加一个价格记录
        if i % 10 == 0:
            price_data.append({
                "date": current_date.isoformat(),
                "asset_code": "AAPL",
                "asset_name": "苹果公司",
                "price": 195.50 + (i * 0.5) + (i % 8 * 2),
                "nav": None,
                "operation_type": "buy",
                "platform": "IBKR"
            })
    
    return {
        "asset_values": asset_values,
        "nav_data": nav_data,
        "price_data": price_data
    }

def generate_mock_market_data():
    """生成模拟的市场数据"""
    exchange_rates = [
        {
            "from_currency": "CNY",
            "to_currency": "USD",
            "rate": 0.1429,
            "snapshot_time": datetime.now().isoformat(),
            "source": "akshare",
            "extra_data": {"provider": "央行", "update_frequency": "daily"}
        },
        {
            "from_currency": "CNY",
            "to_currency": "EUR",
            "rate": 0.1316,
            "snapshot_time": datetime.now().isoformat(),
            "source": "akshare",
            "extra_data": {"provider": "ECB", "update_frequency": "daily"}
        },
        {
            "from_currency": "USD",
            "to_currency": "CNY",
            "rate": 7.00,
            "snapshot_time": datetime.now().isoformat(),
            "source": "akshare",
            "extra_data": {"provider": "央行", "update_frequency": "daily"}
        }
    ]
    
    fund_navs = [
        {
            "fund_code": "000001",
            "nav_date": datetime.now().date().isoformat(),
            "nav": 1.0520,
            "accumulated_nav": 2.8940,
            "growth_rate": 0.0095,
            "source": "api"
        },
        {
            "fund_code": "110022",
            "nav_date": datetime.now().date().isoformat(),
            "nav": 3.2150,
            "accumulated_nav": 3.2150,
            "growth_rate": 0.0125,
            "source": "api"
        }
    ]
    
    market_indicators = {
        "total_funds_tracked": 156,
        "active_funds_last_week": 142,
        "total_user_operations": 1247,
        "operations_last_30_days": 45,
        "data_freshness": {
            "latest_snapshot": datetime.now().isoformat(),
            "latest_exchange_rate": datetime.now().isoformat(),
            "latest_fund_nav": datetime.now().date().isoformat()
        }
    }
    
    return {
        "exchange_rates": exchange_rates,
        "fund_navs": fund_navs,
        "market_indicators": market_indicators
    }

def generate_mock_dca_data():
    """生成模拟的定投数据"""
    dca_plans = [
        {
            "id": 5,
            "plan_name": "华夏成长定投",
            "platform": "支付宝基金",
            "asset_type": "基金",
            "asset_code": "000001",
            "asset_name": "华夏成长混合",
            "amount": 1000.00,
            "currency": "CNY",
            "frequency": "monthly",
            "frequency_value": 30,
            "start_date": "2023-01-01",
            "end_date": None,
            "status": "active",
            "strategy": "长期定投",
            "execution_time": "15:00",
            "next_execution_date": "2024-02-01",
            "last_execution_date": "2024-01-01",
            "execution_count": 12,
            "total_invested": 12000.00,
            "total_shares": 11428.57,
            "smart_dca": False,
            "base_amount": None,
            "max_amount": None,
            "increase_rate": None
        },
        {
            "id": 6,
            "plan_name": "消费行业定投",
            "platform": "支付宝基金",
            "asset_type": "基金", 
            "asset_code": "110022",
            "asset_name": "易方达消费行业",
            "amount": 500.00,
            "currency": "CNY",
            "frequency": "weekly",
            "frequency_value": 7,
            "start_date": "2023-06-01",
            "end_date": None,
            "status": "active",
            "strategy": "行业定投",
            "execution_time": "10:00",
            "next_execution_date": "2024-01-29",
            "last_execution_date": "2024-01-22",
            "execution_count": 32,
            "total_invested": 16000.00,
            "total_shares": 4968.94,
            "smart_dca": True,
            "base_amount": 500.00,
            "max_amount": 1000.00,
            "increase_rate": 0.5
        }
    ]
    
    execution_history = []
    for i in range(15):
        execution_date = datetime.now() - timedelta(days=i*7)
        execution_history.append({
            "operation_id": 3000 + i,
            "dca_plan_id": 5 if i % 2 == 0 else 6,
            "execution_date": execution_date.isoformat(),
            "amount": 1000.00 if i % 2 == 0 else 500.00,
            "quantity": 952.38 + (i * 5) if i % 2 == 0 else 155.28 + (i * 2),
            "nav": 1.0500 + (i * 0.01) if i % 2 == 0 else 3.2150 + (i * 0.02),
            "fee": 1.50,
            "execution_type": "scheduled",
            "asset_code": "000001" if i % 2 == 0 else "110022",
            "platform": "支付宝基金"
        })
    
    statistics = {
        "total_plans": 2,
        "active_plans": 2,
        "total_invested": 28000.00,
        "total_operations": 44,
        "plan_statistics": {
            "5": {
                "operation_count": 12,
                "total_invested": 12000.00,
                "avg_nav": [1.0500, 1.0520, 1.0480, 1.0510]
            },
            "6": {
                "operation_count": 32,
                "total_invested": 16000.00,
                "avg_nav": [3.2150, 3.2180, 3.2120, 3.2160]
            }
        }
    }
    
    return {
        "dca_plans": dca_plans,
        "execution_history": execution_history,
        "statistics": statistics
    }

def test_api_responses():
    """测试各个API接口的响应数据"""
    
    print("=" * 80)
    print("🔍 AI分析师数据API - 模拟测试结果")
    print("=" * 80)
    
    # 1. 资产数据
    print("\n📊 1. 资产数据 (/asset-data)")
    print("-" * 50)
    asset_data = generate_mock_asset_data()
    print(f"✓ 总持仓数: {len(asset_data['current_holdings'])}")
    print(f"✓ 总价值: ¥{sum(asset_data['total_value_by_currency'].values()):,.2f}")
    print(f"✓ 平台数: {len(asset_data['platform_summary'])}")
    print(f"✓ 资产类型数: {len(asset_data['asset_type_summary'])}")
    
    print("\n📋 持仓明细示例:")
    for holding in asset_data['current_holdings'][:2]:
        print(f"  • {holding['asset_name']} ({holding['asset_code']})")
        print(f"    平台: {holding['platform']}")
        print(f"    价值: ¥{holding['base_currency_value']:,.2f}")
        print(f"    类型: {holding['asset_type']}")
    
    # 2. 交易数据  
    print("\n💰 2. 交易数据 (/transaction-data)")
    print("-" * 50)
    transaction_data = generate_mock_transaction_data()
    print(f"✓ 交易记录数: {len(transaction_data['transactions'])}")
    print(f"✓ 买入操作: {transaction_data['summary_stats']['operation_types']['buy']['count']}")
    print(f"✓ 卖出操作: {transaction_data['summary_stats']['operation_types']['sell']['count']}")
    
    print("\n📈 最近交易示例:")
    for tx in transaction_data['transactions'][-3:]:
        print(f"  • {tx['date'][:10]}: {tx['operation_type']} {tx['asset_name']}")
        print(f"    金额: {tx['currency']} {tx['amount']:,.2f}, 情绪评分: {tx['emotion_score']}/10")
    
    # 3. 历史数据
    print("\n📈 3. 历史数据 (/historical-data)")
    print("-" * 50)
    historical_data = generate_mock_historical_data()
    print(f"✓ 资产价值记录: {len(historical_data['asset_values'])}")
    print(f"✓ 净值记录: {len(historical_data['nav_data'])}")
    print(f"✓ 价格记录: {len(historical_data['price_data'])}")
    
    # 计算简单趋势
    values = [av['base_value'] for av in historical_data['asset_values']]
    if len(values) >= 2:
        trend = "上升" if values[-1] > values[0] else "下降"
        change_pct = ((values[-1] - values[0]) / values[0]) * 100
        print(f"✓ 90天趋势: {trend} ({change_pct:+.2f}%)")
    
    # 4. 市场数据
    print("\n🌍 4. 市场数据 (/market-data)")
    print("-" * 50)
    market_data = generate_mock_market_data()
    print(f"✓ 汇率数据: {len(market_data['exchange_rates'])}")
    print(f"✓ 基金净值: {len(market_data['fund_navs'])}")
    print(f"✓ 跟踪基金数: {market_data['market_indicators']['total_funds_tracked']}")
    
    print("\n💱 主要汇率:")
    for rate in market_data['exchange_rates']:
        print(f"  • {rate['from_currency']}/{rate['to_currency']}: {rate['rate']:.4f}")
    
    # 5. 定投数据
    print("\n🔄 5. 定投数据 (/dca-data)")
    print("-" * 50)
    dca_data = generate_mock_dca_data()
    print(f"✓ 定投计划数: {len(dca_data['dca_plans'])}")
    print(f"✓ 执行记录: {len(dca_data['execution_history'])}")
    print(f"✓ 总投入: ¥{dca_data['statistics']['total_invested']:,.2f}")
    
    print("\n📋 定投计划示例:")
    for plan in dca_data['dca_plans']:
        print(f"  • {plan['plan_name']}")
        print(f"    金额: ¥{plan['amount']:,.2f} / {plan['frequency']}")
        print(f"    状态: {plan['status']}, 已执行: {plan['execution_count']}次")
    
    return {
        "asset_data": asset_data,
        "transaction_data": transaction_data,
        "historical_data": historical_data,
        "market_data": market_data,
        "dca_data": dca_data
    }

def analyze_data_for_ai(mock_data):
    """演示AI分析师如何解读这些数据"""
    
    print("\n" + "=" * 80)
    print("🤖 AI分析师数据解读示例")
    print("=" * 80)
    
    asset_data = mock_data["asset_data"]
    transaction_data = mock_data["transaction_data"]
    historical_data = mock_data["historical_data"]
    dca_data = mock_data["dca_data"]
    
    # 1. 投资组合配置分析
    print("\n📊 投资组合配置分析")
    print("-" * 40)
    
    total_value = sum(asset_data['total_value_by_currency'].values())
    holdings = asset_data['current_holdings']
    
    # 计算权重和集中度
    weights = [h['base_currency_value'] / total_value for h in holdings]
    hhi = sum(w**2 for w in weights) * 10000
    max_weight = max(weights) * 100
    
    print(f"📈 总资产价值: ¥{total_value:,.2f}")
    print(f"📊 集中度指数(HHI): {hhi:.0f} ({'低' if hhi < 1500 else '中' if hhi < 2500 else '高'}集中度)")
    print(f"🔝 最大持仓权重: {max_weight:.1f}%")
    
    # 平台分散度
    platform_count = len(asset_data['platform_summary'])
    asset_type_count = len(asset_data['asset_type_summary'])
    print(f"🏢 平台分散度: {platform_count}个平台")
    print(f"📁 资产类型: {asset_type_count}种类型")
    
    # 分散化评分
    diversification_score = min(100, 
        (platform_count * 15) + 
        (asset_type_count * 20) + 
        (30 if max_weight < 20 else 10) +
        (35 if hhi < 2000 else 15)
    )
    print(f"⭐ 分散化评分: {diversification_score:.0f}/100")
    
    # 2. 投资行为分析
    print("\n💰 投资行为分析")
    print("-" * 40)
    
    transactions = transaction_data['transactions']
    buy_ops = [t for t in transactions if t['operation_type'] == 'buy']
    
    # 投资纪律性
    if buy_ops:
        amounts = [t['amount'] for t in buy_ops]
        avg_amount = sum(amounts) / len(amounts)
        amount_std = (sum([(a - avg_amount)**2 for a in amounts]) / len(amounts)) ** 0.5
        consistency = 1 - (amount_std / avg_amount) if avg_amount > 0 else 0
        
        print(f"📊 平均投资金额: ¥{avg_amount:,.2f}")
        print(f"📈 投资一致性: {consistency:.2f} ({'高' if consistency > 0.7 else '中' if consistency > 0.4 else '低'}纪律性)")
    
    # 情绪分析
    emotions = [t['emotion_score'] for t in transactions if t['emotion_score']]
    if emotions:
        avg_emotion = sum(emotions) / len(emotions)
        print(f"😊 平均情绪评分: {avg_emotion:.1f}/10")
    
    # 3. 绩效计算
    print("\n📈 绩效指标计算")
    print("-" * 40)
    
    asset_values = historical_data['asset_values']
    if len(asset_values) >= 2:
        values = [av['base_value'] for av in asset_values]
        
        # 总收益率
        total_return = ((values[-1] - values[0]) / values[0]) * 100
        print(f"📊 90天总收益率: {total_return:+.2f}%")
        
        # 年化收益率
        annual_return = ((values[-1] / values[0]) ** (365/90) - 1) * 100
        print(f"📈 年化收益率: {annual_return:+.2f}%")
        
        # 简单波动率计算
        daily_returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
        if daily_returns:
            volatility = (sum([(r - sum(daily_returns)/len(daily_returns))**2 for r in daily_returns]) / len(daily_returns)) ** 0.5
            annual_volatility = volatility * (252 ** 0.5) * 100
            print(f"📊 年化波动率: {annual_volatility:.2f}%")
            
            # 风险等级
            risk_level = "低风险" if annual_volatility < 10 else "中低风险" if annual_volatility < 15 else "中风险" if annual_volatility < 25 else "高风险"
            print(f"⚠️ 风险等级: {risk_level}")
    
    # 4. 定投效果分析
    print("\n🔄 定投效果分析")
    print("-" * 40)
    
    dca_plans = dca_data['dca_plans']
    executions = dca_data['execution_history']
    
    for plan in dca_plans:
        plan_executions = [e for e in executions if e['dca_plan_id'] == plan['id']]
        if plan_executions:
            total_invested = sum(e['amount'] for e in plan_executions)
            total_shares = sum(e['quantity'] for e in plan_executions if e['quantity'])
            avg_cost = total_invested / total_shares if total_shares > 0 else 0
            
            navs = [e['nav'] for e in plan_executions if e['nav']]
            avg_nav = sum(navs) / len(navs) if navs else 0
            
            cost_efficiency = "良好" if avg_cost < avg_nav * 0.98 else "一般" if avg_cost < avg_nav * 1.02 else "较差"
            
            print(f"📋 {plan['plan_name']}:")
            print(f"   💰 平均成本: {avg_cost:.4f}")
            print(f"   📊 成本效率: {cost_efficiency}")
            print(f"   🔄 执行次数: {len(plan_executions)}")
    
    # 5. 投资建议生成
    print("\n💡 AI分析建议")
    print("-" * 40)
    
    suggestions = []
    
    if max_weight > 40:
        suggestions.append(f"⚠️ 单一资产权重过高({max_weight:.1f}%)，建议适当分散")
    
    if platform_count < 2:
        suggestions.append("🏢 建议增加投资平台，提高分散度")
        
    if hhi > 2500:
        suggestions.append("📊 投资集中度较高，建议增加持仓品种")
    
    if diversification_score < 60:
        suggestions.append("⭐ 投资组合分散化程度较低，建议优化配置")
    
    if not suggestions:
        suggestions.append("✅ 投资组合配置合理，继续保持")
    
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print("\n" + "=" * 80)
    print("📝 数据解读总结")
    print("=" * 80)
    print("""
🔍 这些API提供了丰富的原始数据，AI分析师可以基于这些数据：

1️⃣ 计算各种投资指标 (收益率、波动率、夏普比率等)
2️⃣ 分析投资行为模式 (频率、一致性、情绪变化)
3️⃣ 评估投资组合质量 (分散度、集中度、配置合理性)
4️⃣ 监控定投执行效果 (成本平均、执行纪律)
5️⃣ 生成个性化建议 (基于用户具体情况)

💡 关键价值:
   - 数据完整性高，包含多维度信息
   - 支持时间序列分析和趋势识别
   - 提供丰富的元数据用于深度分析
   - 支持多币种和跨平台数据整合
""")

if __name__ == "__main__":
    # 运行测试
    mock_data = test_api_responses()
    
    # 演示AI分析
    analyze_data_for_ai(mock_data)