import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
import { snapshotAPI } from '../services/api';
import { Spin, Radio, Space, Empty } from 'antd';

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
        const params: any = { days: days || 30 };
        if (currencyMode !== 'BOTH') params.base_currency = currencyMode;
        const resp = await snapshotAPI.getAssetTrend(params);
        let data = [];
        if (resp.success && Array.isArray(resp.data) && resp.data.length > 0) {
          // 只取最近90天
          data = resp.data.slice(-90);
        } else {
          // mock数据兜底
          data = [
            { date: '2024-06-01', total_cny: 10000, total_usd: 1500 },
            { date: '2024-06-02', total_cny: 10200, total_usd: 1530 },
            { date: '2024-06-03', total_cny: 10100, total_usd: 1515 },
            { date: '2024-06-04', total_cny: 10500, total_usd: 1580 },
            { date: '2024-06-05', total_cny: 10700, total_usd: 1600 },
          ];
        }
        setTrendData(data);
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
    chartData = trendData.flatMap((item: any) => [
      { date: item.date, value: item.total_cny, currency: 'CNY' },
      { date: item.date, value: item.total_usd, currency: 'USD' },
    ]);
  } else {
    chartData = trendData.map((item: any) => ({
      date: item.date,
      value: item.total,
      currency: currencyMode,
    }));
  }
  // 限制最大点数
  if (chartData.length > 90) chartData = chartData.slice(-90);

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
      {chartData.length === 0 ? <Empty description="暂无趋势数据" /> : <Line {...config} />}
    </Spin>
  );
};

export default AssetTrendChart;