import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
import { snapshotAPI } from '../services/api';
import { Spin, Radio, Space, Select } from 'antd';

const { Option } = Select;

interface AssetTrendChartProps {
  baseCurrency: string | 'BOTH'; // 'CNY' | 'USD' | 'BOTH'
  days?: number;
  showTimeGranularity?: boolean; // 是否显示时间粒度选择器
}

const AssetTrendChart: React.FC<AssetTrendChartProps> = ({ 
  baseCurrency, 
  days = 30, 
  showTimeGranularity = true 
}) => {
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currencyMode, setCurrencyMode] = useState<string>(baseCurrency);
  const [timeGranularity, setTimeGranularity] = useState<'day' | 'half_day' | 'hour'>('day');

  useEffect(() => {
    setCurrencyMode(baseCurrency);
  }, [baseCurrency]);

  useEffect(() => {
    const fetchTrend = async () => {
      setLoading(true);
      try {
        const params: any = { 
          days,
          time_granularity: timeGranularity
        };
        if (currencyMode !== 'BOTH') params.base_currency = currencyMode;
        const resp = await snapshotAPI.getAssetTrend(params);
        if (resp.success && resp.data) {
          setTrendData(resp.data);
        } else {
          setTrendData([]);
        }
      } catch (e) {
        console.error('获取资产趋势失败:', e);
        setTrendData([]);
      }
      setLoading(false);
    };
    fetchTrend();
  }, [currencyMode, days, timeGranularity]);

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
    xAxis: { 
      type: 'time', 
      title: { text: '日期' },
      // 根据时间粒度调整x轴显示
      tickCount: timeGranularity === 'hour' ? 8 : timeGranularity === 'half_day' ? 6 : 7
    },
    yAxis: { title: { text: '总资产' } },
  };

  const getTimeGranularityLabel = (granularity: string) => {
    switch (granularity) {
      case 'hour': return '小时';
      case 'half_day': return '半天';
      case 'day': return '天';
      default: return '天';
    }
  };

  return (
    <Spin spinning={loading}>
      <Space style={{ marginBottom: 8 }} wrap>
        <Radio.Group
          value={currencyMode}
          onChange={e => setCurrencyMode(e.target.value)}
          buttonStyle="solid"
        >
          <Radio.Button value="CNY">人民币</Radio.Button>
          <Radio.Button value="USD">美元</Radio.Button>
          <Radio.Button value="BOTH">双基准</Radio.Button>
        </Radio.Group>
        
        {showTimeGranularity && (
          <Select
            value={timeGranularity}
            onChange={setTimeGranularity}
            style={{ width: 100 }}
            size="small"
          >
            <Option value="day">按天</Option>
            <Option value="half_day">按半天</Option>
            <Option value="hour">按小时</Option>
          </Select>
        )}
      </Space>
      <Line {...config} />
    </Spin>
  );
};

export default AssetTrendChart;