import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
import { Spin, Radio, Space } from 'antd';
import dayjs from 'dayjs';

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
      <Line {...config} />
    </Spin>
  );
};

export default AssetTrendChart;