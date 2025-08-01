import dayjs from 'dayjs';

export interface SampleAssetData {
  total_assets: {
    [currency: string]: number;
  };
  platform_distribution: Array<{
    platform: string;
    value: number;
    percentage: number;
  }>;
  asset_types: Array<{
    type: string;
    value: number;
    percentage: number;
  }>;
  holdings: Array<{
    asset_code: string;
    asset_name: string;
    platform: string;
    quantity: number;
    unit_price: number;
    current_value: number;
    cost_basis: number;
    unrealized_pnl: number;
    pnl_percentage: number;
  }>;
}

export interface SampleTransactionData {
  total_transactions: number;
  date_range: {
    start_date: string;
    end_date: string;
  };
  summary: {
    total_buy_amount: number;
    total_sell_amount: number;
    net_flow: number;
    transaction_count_by_type: {
      buy: number;
      sell: number;
    };
    fees_total: number;
  };
  transactions: Array<{
    date: string;
    platform: string;
    asset_code: string;
    asset_name: string;
    type: 'buy' | 'sell';
    quantity: number;
    unit_price: number;
    total_amount: number;
    fees: number;
    notes?: string;
  }>;
}

export interface SampleHistoricalData {
  query_params: {
    days: number;
    asset_codes: string[];
  };
  data_points: Array<{
    date: string;
    total_value: number;
    daily_change: number;
    daily_change_percentage: number;
  }>;
  asset_performance: Array<{
    asset_code: string;
    asset_name: string;
    start_value: number;
    end_value: number;
    total_return: number;
    total_return_percentage: number;
    max_drawdown: number;
    volatility: number;
  }>;
}

export interface SampleMarketData {
  exchange_rates: {
    [pair: string]: {
      rate: number;
      change_24h: number;
      last_updated: string;
    };
  };
  fund_navs: Array<{
    fund_code: string;
    fund_name: string;
    nav: number;
    change: number;
    change_percentage: number;
    date: string;
  }>;
  market_indicators: {
    vix: number;
    fear_greed_index: number;
    crypto_fear_greed: number;
  };
}

export interface SampleDCAData {
  active_plans: Array<{
    plan_id: string;
    asset_code: string;
    asset_name: string;
    frequency: string;
    amount_per_execution: number;
    next_execution_date: string;
    status: 'active' | 'paused' | 'completed';
  }>;
  execution_history: Array<{
    date: string;
    plan_id: string;
    asset_code: string;
    amount: number;
    units_purchased: number;
    unit_price: number;
    status: 'executed' | 'failed' | 'skipped';
  }>;
  performance_summary: {
    total_invested: number;
    current_value: number;
    total_return: number;
    total_return_percentage: number;
    average_cost: number;
    total_units: number;
  };
}

export const generateSampleAssetData = (baseCurrency: string = 'CNY', includeSmall: boolean = true): SampleAssetData => {
  const holdings = [
    {
      asset_code: 'AAPL',
      asset_name: 'Apple Inc.',
      platform: 'IBKR',
      quantity: 10,
      unit_price: 150.25,
      current_value: 1502.5,
      cost_basis: 1400,
      unrealized_pnl: 102.5,
      pnl_percentage: 7.32
    },
    {
      asset_code: '000001',
      asset_name: '平安银行',
      platform: 'IBKR',
      quantity: 500,
      unit_price: 12.35,
      current_value: 6175,
      cost_basis: 6000,
      unrealized_pnl: 175,
      pnl_percentage: 2.92
    },
    {
      asset_code: 'BTC',
      asset_name: 'Bitcoin',
      platform: 'OKX',
      quantity: 0.5,
      unit_price: 45000,
      current_value: 22500,
      cost_basis: 20000,
      unrealized_pnl: 2500,
      pnl_percentage: 12.5
    },
    {
      asset_code: '110003',
      asset_name: '易方达稳健收益债券A',
      platform: 'Wise',
      quantity: 1000,
      unit_price: 1.156,
      current_value: 1156,
      cost_basis: 1100,
      unrealized_pnl: 56,
      pnl_percentage: 5.09
    }
  ];

  if (!includeSmall) {
    // 过滤掉小额资产（< 1000）
    holdings.splice(3, 1);
  }

  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
  
  const platformDist = holdings.reduce((acc, h) => {
    const existing = acc.find(p => p.platform === h.platform);
    if (existing) {
      existing.value += h.current_value;
    } else {
      acc.push({ platform: h.platform, value: h.current_value, percentage: 0 });
    }
    return acc;
  }, [] as Array<{platform: string; value: number; percentage: number}>);

  platformDist.forEach(p => {
    p.percentage = (p.value / totalValue) * 100;
  });

  const exchangeRate = baseCurrency === 'USD' ? 0.14 : baseCurrency === 'EUR' ? 0.13 : 1;
  
  return {
    total_assets: {
      [baseCurrency]: totalValue * exchangeRate
    },
    platform_distribution: platformDist,
    asset_types: [
      { type: '股票', value: 7677.5 * exchangeRate, percentage: 24.6 },
      { type: '加密货币', value: 22500 * exchangeRate, percentage: 72.1 },
      { type: '债券基金', value: includeSmall ? 1156 * exchangeRate : 0, percentage: includeSmall ? 3.7 : 0 }
    ],
    holdings: holdings.map(h => ({
      ...h,
      current_value: h.current_value * exchangeRate,
      cost_basis: h.cost_basis * exchangeRate,
      unrealized_pnl: h.unrealized_pnl * exchangeRate,
      unit_price: h.unit_price * exchangeRate
    }))
  };
};

export const generateSampleTransactionData = (startDate: string, endDate: string, platform?: string, limit: number = 50): SampleTransactionData => {
  const transactions = [
    {
      date: dayjs().subtract(5, 'day').format('YYYY-MM-DD'),
      platform: 'IBKR',
      asset_code: 'AAPL',
      asset_name: 'Apple Inc.',
      type: 'buy' as const,
      quantity: 5,
      unit_price: 148.50,
      total_amount: 742.50,
      fees: 1.50,
      notes: '定期定投'
    },
    {
      date: dayjs().subtract(10, 'day').format('YYYY-MM-DD'),
      platform: 'OKX',
      asset_code: 'BTC',
      asset_name: 'Bitcoin',
      type: 'buy' as const,
      quantity: 0.1,
      unit_price: 44000,
      total_amount: 4400,
      fees: 22.00
    },
    {
      date: dayjs().subtract(15, 'day').format('YYYY-MM-DD'),
      platform: 'IBKR',
      asset_code: '000001',
      asset_name: '平安银行',
      type: 'sell' as const,
      quantity: 100,
      unit_price: 12.80,
      total_amount: 1280,
      fees: 5.12
    },
    {
      date: dayjs().subtract(20, 'day').format('YYYY-MM-DD'),
      platform: 'Wise',
      asset_code: '110003',
      asset_name: '易方达稳健收益债券A',
      type: 'buy' as const,
      quantity: 500,
      unit_price: 1.140,
      total_amount: 570,
      fees: 0
    }
  ];

  let filteredTransactions = transactions;
  
  if (platform) {
    filteredTransactions = transactions.filter(t => t.platform === platform);
  }
  
  filteredTransactions = filteredTransactions.slice(0, limit);

  const buyTransactions = filteredTransactions.filter(t => t.type === 'buy');
  const sellTransactions = filteredTransactions.filter(t => t.type === 'sell');
  
  const totalBuyAmount = buyTransactions.reduce((sum, t) => sum + t.total_amount, 0);
  const totalSellAmount = sellTransactions.reduce((sum, t) => sum + t.total_amount, 0);
  const totalFees = filteredTransactions.reduce((sum, t) => sum + t.fees, 0);

  return {
    total_transactions: filteredTransactions.length,
    date_range: { start_date: startDate, end_date: endDate },
    summary: {
      total_buy_amount: totalBuyAmount,
      total_sell_amount: totalSellAmount,
      net_flow: totalBuyAmount - totalSellAmount,
      transaction_count_by_type: {
        buy: buyTransactions.length,
        sell: sellTransactions.length
      },
      fees_total: totalFees
    },
    transactions: filteredTransactions
  };
};

export const generateSampleHistoricalData = (days: number, assetCodes?: string): SampleHistoricalData => {
  const dataPoints = [];
  let baseValue = 30000;
  
  for (let i = days; i >= 0; i--) {
    const date = dayjs().subtract(i, 'day').format('YYYY-MM-DD');
    const randomChange = (Math.random() - 0.5) * 0.1; // ±5%的随机波动
    const dailyChange = baseValue * randomChange;
    baseValue += dailyChange;
    
    dataPoints.push({
      date,
      total_value: baseValue,
      daily_change: dailyChange,
      daily_change_percentage: (dailyChange / (baseValue - dailyChange)) * 100
    });
  }

  const assetPerformance = [
    {
      asset_code: 'AAPL',
      asset_name: 'Apple Inc.',
      start_value: 1400,
      end_value: 1502.5,
      total_return: 102.5,
      total_return_percentage: 7.32,
      max_drawdown: -3.2,
      volatility: 18.5
    },
    {
      asset_code: 'BTC',
      asset_name: 'Bitcoin',
      start_value: 20000,
      end_value: 22500,
      total_return: 2500,
      total_return_percentage: 12.5,
      max_drawdown: -15.8,
      volatility: 65.2
    }
  ];

  return {
    query_params: {
      days,
      asset_codes: assetCodes ? assetCodes.split(',') : []
    },
    data_points: dataPoints,
    asset_performance: assetPerformance
  };
};

export const generateSampleMarketData = (): SampleMarketData => {
  return {
    exchange_rates: {
      'USD/CNY': {
        rate: 7.23,
        change_24h: 0.05,
        last_updated: dayjs().format('YYYY-MM-DD HH:mm:ss')
      },
      'EUR/CNY': {
        rate: 7.85,
        change_24h: -0.12,
        last_updated: dayjs().format('YYYY-MM-DD HH:mm:ss')
      },
      'GBP/CNY': {
        rate: 9.12,
        change_24h: 0.08,
        last_updated: dayjs().format('YYYY-MM-DD HH:mm:ss')
      }
    },
    fund_navs: [
      {
        fund_code: '110003',
        fund_name: '易方达稳健收益债券A',
        nav: 1.156,
        change: 0.003,
        change_percentage: 0.26,
        date: dayjs().format('YYYY-MM-DD')
      },
      {
        fund_code: '000001',
        fund_name: '华夏成长混合',
        nav: 2.145,
        change: -0.015,
        change_percentage: -0.69,
        date: dayjs().format('YYYY-MM-DD')
      }
    ],
    market_indicators: {
      vix: 18.5,
      fear_greed_index: 65,
      crypto_fear_greed: 42
    }
  };
};

export const generateSampleDCAData = (): SampleDCAData => {
  return {
    active_plans: [
      {
        plan_id: 'dca_001',
        asset_code: 'AAPL',
        asset_name: 'Apple Inc.',
        frequency: 'weekly',
        amount_per_execution: 500,
        next_execution_date: dayjs().add(3, 'day').format('YYYY-MM-DD'),
        status: 'active'
      },
      {
        plan_id: 'dca_002',
        asset_code: 'BTC',
        asset_name: 'Bitcoin',
        frequency: 'monthly',
        amount_per_execution: 1000,
        next_execution_date: dayjs().add(15, 'day').format('YYYY-MM-DD'),
        status: 'active'
      }
    ],
    execution_history: [
      {
        date: dayjs().subtract(7, 'day').format('YYYY-MM-DD'),
        plan_id: 'dca_001',
        asset_code: 'AAPL',
        amount: 500,
        units_purchased: 3.36,
        unit_price: 148.50,
        status: 'executed'
      },
      {
        date: dayjs().subtract(14, 'day').format('YYYY-MM-DD'),
        plan_id: 'dca_001',
        asset_code: 'AAPL',
        amount: 500,
        units_purchased: 3.42,
        unit_price: 146.20,
        status: 'executed'
      },
      {
        date: dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
        plan_id: 'dca_002',
        asset_code: 'BTC',
        amount: 1000,
        units_purchased: 0.025,
        unit_price: 40000,
        status: 'executed'
      }
    ],
    performance_summary: {
      total_invested: 2000,
      current_value: 2180.50,
      total_return: 180.50,
      total_return_percentage: 9.02,
      average_cost: 147.35,
      total_units: 6.805
    }
  };
};