import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
<<<<<<< HEAD
import { Spin, Radio, Space } from 'antd';
import dayjs from 'dayjs';
=======
import { Spin, Radio, Space, Empty } from 'antd';
>>>>>>> origin/feature/asset-dashboard-enhance

interface AssetTrendChartProps {
  baseCurrency: string | 'BOTH'; // 'CNY' | 'USD' | 'BOTH'
  days?: number;
}

const AssetTrendChart: React.FC<AssetTrendChartProps> = ({ baseCurrency, days = 30 }) => {
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currencyMode, setCurrencyMode] = useState<string>(baseCurrency);

  useEffect(() => {
    setCurrencyMode(baseCurrency);
  }, [baseCurrency]);

  useEffect(() => {
<<<<<<< HEAD
    // 彻底mock数据，无论API如何都注入
    setLoading(true);
    const mockData: any[] = [];
    const baseValue = 1000000;
    for (let i = 0; i < 30; i++) {
      const date = dayjs().subtract(29 - i, 'day').format('YYYY-MM-DD');
      const randomChange = (Math.random() - 0.5) * 0.1;
      const value = baseValue * (1 + randomChange + i * 0.02);
      mockData.push({ date, value });
    }
    setTrendData(mockData);
    setLoading(false);
  }, [currencyMode, days]);

  // 简化数据处理
  const chartData = trendData;
=======
    // 只用mock数据，不请求API
    setLoading(true);
    setTimeout(() => {
      setTrendData([
        { date: '2024-06-01', total_cny: 10000, total_usd: 1500 },
        { date: '2024-06-02', total_cny: 10200, total_usd: 1530 },
        { date: '2024-06-03', total_cny: 10100, total_usd: 1515 },
        { date: '2024-06-04', total_cny: 10500, total_usd: 1580 },
        { date: '2024-06-05', total_cny: 10700, total_usd: 1600 },
      ]);
      setLoading(false);
    }, 300);
  }, [currencyMode, days]);

  // 处理双基准数据
  let chartData: any[] = [];
  if (currencyMode === 'BOTH') {
    chartData = trendData.flatMap((item: any) => [
      { date: item.date, value: item.total_cny, currency: 'CNY' },
      { date: item.date, value: item.total_usd, currency: 'USD' },
    ]);
  } else {
    chartData = trendData.map((item: any) => ({
      date: item.date,
      value: currencyMode === 'CNY' ? item.total_cny : item.total_usd,
      currency: currencyMode,
    }));
  }
  // 限制最大点数
  if (chartData.length > 90) chartData = chartData.slice(-90);
>>>>>>> origin/feature/asset-dashboard-enhance

  const config = {
    data: chartData,
    xField: 'date',
    yField: 'value',
    smooth: true,
    height: 280,
    color: ['#1890ff'],
    legend: { position: 'top' },
    tooltip: { showMarkers: true },
    animation: true,
    xAxis: { type: 'time' },
    yAxis: { title: { text: '总资产' } },
  };

  return (
    <Spin spinning={loading}>
      <Space style={{ marginBottom: 8 }}>
        <Radio.Group
          value={currencyMode}
          onChange={e => setCurrencyMode(e.target.value)}
          buttonStyle="solid"
        >
          <Radio.Button value="CNY">人民币</Radio.Button>
          <Radio.Button value="USD">美元</Radio.Button>
          <Radio.Button value="BOTH">双基准</Radio.Button>
        </Radio.Group>
      </Space>
      {chartData.length === 0 ? <Empty description="暂无趋势数据" /> : <Line {...config} />}
    </Spin>
  );
};

export default AssetTrendChart;