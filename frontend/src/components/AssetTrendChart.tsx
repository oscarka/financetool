import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
import { snapshotAPI } from '../services/api';
import { Spin, Radio, Space } from 'antd';

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
    const fetchTrend = async () => {
      setLoading(true);
      try {
        const params: any = { days };
        if (currencyMode !== 'BOTH') params.base_currency = currencyMode;
        const resp = await snapshotAPI.getAssetTrend(params);
        if (resp.success && resp.data && resp.data.length > 0) {
          setTrendData(resp.data);
        } else {
          // mock数据兜底
          setTrendData([
            { date: '2024-06-01', total_cny: 10000, total_usd: 1500 },
            { date: '2024-06-02', total_cny: 10200, total_usd: 1530 },
            { date: '2024-06-03', total_cny: 10100, total_usd: 1515 },
            { date: '2024-06-04', total_cny: 10500, total_usd: 1580 },
            { date: '2024-06-05', total_cny: 10700, total_usd: 1600 },
          ]);
        }
      } catch (e) {
        setTrendData([
          { date: '2024-06-01', total_cny: 10000, total_usd: 1500 },
          { date: '2024-06-02', total_cny: 10200, total_usd: 1530 },
          { date: '2024-06-03', total_cny: 10100, total_usd: 1515 },
          { date: '2024-06-04', total_cny: 10500, total_usd: 1580 },
          { date: '2024-06-05', total_cny: 10700, total_usd: 1600 },
        ]);
      }
      setLoading(false);
    };
    fetchTrend();
  }, [currencyMode, days]);

  // 处理双基准数据
  let chartData: any[] = [];
  if (currencyMode === 'BOTH') {
    // 假设API返回格式为 [{date, total_cny, total_usd}]
    chartData = trendData.flatMap((item: any) => [
      { date: item.date, value: item.total_cny, currency: 'CNY' },
      { date: item.date, value: item.total_usd, currency: 'USD' },
    ]);
  } else {
    // [{date, total}]
    chartData = trendData.map((item: any) => ({
      date: item.date,
      value: item.total,
      currency: currencyMode,
    }));
  }

  const config = {
    data: chartData,
    xField: 'date',
    yField: 'value',
    seriesField: 'currency',
    smooth: true,
    height: 320,
    color: ['#1890ff', '#52c41a'],
    legend: { position: 'top' },
    tooltip: { showMarkers: true },
    animation: true,
    xAxis: { type: 'time', title: { text: '日期' } },
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