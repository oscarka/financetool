# 基金模块详细设计

## 🎯 基金模块核心功能

### 1. 基金操作记录
用户只需要记录投资决策，系统自动处理数据获取和计算

### 2. 净值自动同步
从外部API获取基金净值，支持手动确认和修正

### 3. 收益自动计算
基于操作记录和净值数据，自动计算收益和收益率

### 4. 定投计划管理
支持设置定投计划，自动提醒执行

## 📊 基金操作流程

### 买入操作流程
```
1. 用户录入：今天15:00前买入XX基金1000元
2. 系统处理：
   - 获取当天净值（预估）
   - 计算预估份额 = 1000 / 当天净值
   - 记录操作状态为"pending"
3. 第二天：
   - 获取实际净值
   - 计算实际份额
   - 用户确认或修正份额
   - 更新操作状态为"confirmed"
4. 后续：
   - 每日自动获取净值
   - 计算收益变化
```

### 卖出操作流程
```
1. 用户录入：卖出XX基金全部份额
2. 系统处理：
   - 获取当前持仓份额
   - 获取当天净值
   - 计算预估卖出金额
   - 记录操作状态为"pending"
3. 确认后：
   - 更新实际卖出金额
   - 计算总收益
   - 将基金移到历史记录
   - 将卖出的钱暂时放入一个单独的流动资金池
```

## 🔗 基金数据API集成

### 1. 天天基金网API
```python
# 基金净值API
GET https://fundgz.1234567.com.cn/js/{fund_code}.js

# 基金信息API
GET https://fund.eastmoney.com/pingzhongdata/{fund_code}.js
```

### 2. 雪球API
```python
# 基金净值API
GET https://stock.xueqiu.com/v5/stock/chart/kline.json
```

### 3. 备用数据源
- 蚂蚁财富API
- 腾讯理财通API

## 📋 基金操作界面设计

### 1. 基金操作录入表单
```typescript
interface FundOperation {
  operation_date: string;        // 操作日期
  operation_type: 'buy' | 'sell' | 'dividend';  // 操作类型
  fund_code: string;             // 基金代码
  fund_name: string;             // 基金名称
  amount: number;                // 操作金额
  strategy: string;              // 策略逻辑
  emotion_score: number;         // 情绪评分 1-10
  notes: string;                 // 备注
}
```

### 2. 基金持仓展示
```typescript
interface FundPosition {
  fund_code: string;             // 基金代码
  fund_name: string;             // 基金名称
  total_shares: number;          // 总份额
  avg_cost: number;              // 平均成本
  current_nav: number;           // 当前净值
  current_value: number;         // 当前市值
  total_invested: number;        // 累计投入
  total_profit: number;          // 累计收益
  profit_rate: number;           // 收益率
  last_updated: string;          // 最后更新时间
}
```

## 🧮 基金收益计算逻辑

### 1. 买入计算
```python
def calculate_buy_operation(amount, nav, fee_rate=0):
    """
    计算买入份额
    """
    fee = amount * fee_rate
    net_amount = amount - fee
    shares = net_amount / nav
    return shares, fee

def calculate_avg_cost(existing_shares, existing_cost, new_shares, new_cost):
    """
    计算平均成本
    """
    total_shares = existing_shares + new_shares
    total_cost = existing_cost + new_cost
    avg_cost = total_cost / total_shares
    return avg_cost
```

### 2. 卖出计算
```python
def calculate_sell_operation(shares, nav, fee_rate=0):
    """
    计算卖出金额
    """
    gross_amount = shares * nav
    fee = gross_amount * fee_rate
    net_amount = gross_amount - fee
    return net_amount, fee

def calculate_profit(avg_cost, current_nav, shares):
    """
    计算收益
    """
    total_cost = avg_cost * shares
    current_value = current_nav * shares
    profit = current_value - total_cost
    profit_rate = profit / total_cost if total_cost > 0 else 0
    return profit, profit_rate
```

## 📈 基金净值同步策略

### 1. 自动同步
```python
class FundNavSync:
    def __init__(self):
        self.data_sources = [
            TianTianFundAPI(),
            XueQiuAPI(),
            AntWealthAPI()
        ]
    
    async def sync_fund_nav(self, fund_code, date):
        """
        同步基金净值
        """
        for source in self.data_sources:
            try:
                nav_data = await source.get_nav(fund_code, date)
                if nav_data:
                    await self.save_nav_data(nav_data)
                    return nav_data
            except Exception as e:
                logger.error(f"同步失败: {e}")
                continue
        return None
```

### 2. 手动确认机制
```python
class FundNavConfirmation:
    async def confirm_nav(self, fund_code, date, user_nav):
        """
        用户确认净值
        """
        # 更新净值数据
        await self.update_nav(fund_code, date, user_nav, source='manual')
        
        # 重新计算相关持仓的收益
        await self.recalculate_positions(fund_code)
        
        # 记录确认日志
        await self.log_confirmation(fund_code, date, user_nav)
```

## 🎯 定投计划管理

### 1. 定投计划设置
```typescript
interface DCAPlan {
  plan_name: string;             // 计划名称
  fund_code: string;             // 基金代码
  amount: number;                // 定投金额
  frequency: 'daily' | 'weekly' | 'monthly';  // 频率
  frequency_value: number;       // 频率值
  start_date: string;            // 开始日期
  end_date?: string;             // 结束日期
  strategy: string;              // 定投策略
  status: 'active' | 'paused' | 'stopped';  // 状态
}
```

### 2. 定投执行逻辑
```python
class DCAScheduler:
    async def check_dca_plans(self):
        """
        检查定投计划
        """
        active_plans = await self.get_active_plans()
        
        for plan in active_plans:
            if self.should_execute(plan):
                await self.execute_dca(plan)
    
    async def execute_dca(self, plan):
        """
        执行定投
        """
        # 创建定投操作记录
        operation = {
            'operation_type': 'buy',
            'fund_code': plan.fund_code,
            'amount': plan.amount,
            'strategy': f"定投计划: {plan.plan_name}",
            'emotion_score': 5,  # 定投情绪中性
            'notes': f"自动定投执行 - {plan.strategy}"
        }
        
        await self.create_operation(operation)
```

## 📊 基金分析功能

### 1. 收益分析
- 累计收益趋势图
- 年化收益率计算
- 最大回撤分析
- 夏普比率计算

### 2. 操作分析
- 操作频率统计
- 策略效果分析
- 情绪评分与收益关系
- 最佳操作时机分析

### 3. 基金对比
- 多基金收益对比
- 风险收益分析
- 相关性分析

## 🔄 数据验证机制

### 1. 净值验证
```python
class NavValidator:
    def validate_nav_change(self, fund_code, old_nav, new_nav):
        """
        验证净值变化是否合理
        """
        change_rate = abs(new_nav - old_nav) / old_nav
        
        if change_rate > 0.1:  # 单日变化超过10%
            return False, f"净值变化异常: {change_rate:.2%}"
        
        return True, "净值变化正常"
```

### 2. 份额验证
```python
class ShareValidator:
    def validate_share_calculation(self, operation, calculated_shares, actual_shares):
        """
        验证份额计算
        """
        diff = abs(calculated_shares - actual_shares)
        diff_rate = diff / calculated_shares if calculated_shares > 0 else 0
        
        if diff_rate > 0.01:  # 差异超过1%
            return False, f"份额计算差异: {diff_rate:.2%}"
        
        return True, "份额计算正确"
```

## 🚀 基金模块开发计划

### 阶段1：基础功能 (1周)
- [ ] 基金操作记录界面
- [ ] 基础持仓计算
- [ ] 手动净值录入
- [ ] 简单收益计算

### 阶段2：API集成 (1周)
- [ ] 天天基金网API集成
- [ ] 自动净值同步
- [ ] 净值确认机制
- [ ] 数据验证

### 阶段3：高级功能 (1周)
- [ ] 定投计划管理
- [ ] 收益分析图表
- [ ] 操作分析功能
- [ ] 数据导出

### 验证目标
1. **操作记录准确性**：录入买入操作，验证份额计算
2. **净值同步准确性**：自动获取净值，验证收益计算
3. **定投执行准确性**：设置定投计划，验证自动执行
4. **数据分析准确性**：查看收益趋势，验证计算逻辑 