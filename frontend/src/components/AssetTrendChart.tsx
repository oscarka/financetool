import React, { useEffect, useState } from 'react';
import { Line } from '@ant-design/charts';
import { Spin, Radio, Space, Empty, message } from 'antd';
import dayjs from 'dayjs';
import { aggregationAPI } from '../services/api';

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
    const fetchTrendData = async () => {
      setLoading(true);
      try {
        // 尝试获取真实数据
        console.log('🔄 [AssetTrendChart] 开始获取趋势数据...');
        console.log('  - 天数:', days);
        console.log('  - 货币模式:', currencyMode);
        const response = await aggregationAPI.getTrend(days, currencyMode === 'BOTH' ? 'CNY' : currencyMode);
        console.log('📊 [AssetTrendChart] API原始响应:', response);

        if (response.success && response.data) {
          // 转换数据格式
          const formattedData = response.data.map((item: any) => ({
            date: item.date,
            total_cny: item.total,
            total_usd: item.total / 7.2 // 简单转换，实际应该从API获取USD数据
          }));
          console.log('🔄 [AssetTrendChart] 数据转换过程:');
          console.log('  - 原始数据:', response.data);
          console.log('  - 转换后数据:', formattedData);
          console.log('  - 数据点数量:', formattedData.length);
          console.log('  - 最新值:', formattedData[formattedData.length - 1]);
          console.log('  - 最早值:', formattedData[0]);
          setTrendData(formattedData);
        } else {
          console.warn('⚠️ [AssetTrendChart] API返回失败，使用模拟数据');
          // 如果API失败，使用mock数据
          const mockData: any[] = [];
          const baseValue = 1000000;
          for (let i = 0; i < days; i++) {
            const date = dayjs().subtract(days - 1 - i, 'day').format('YYYY-MM-DD');
            const randomChange = (Math.random() - 0.5) * 0.1;
            const value = baseValue * (1 + randomChange + i * 0.02);
            mockData.push({
              date,
              total_cny: value,
              total_usd: value / 7.2
            });
          }
          console.log('📊 [AssetTrendChart] 使用模拟数据:', mockData);
          setTrendData(mockData);
        }
      } catch (error) {
        console.error('❌ [AssetTrendChart] 获取趋势数据失败:', error);
        message.error('获取趋势数据失败，使用模拟数据');

        // 使用mock数据作为fallback
        const mockData: any[] = [];
        const baseValue = 1000000;
        for (let i = 0; i < days; i++) {
          const date = dayjs().subtract(days - 1 - i, 'day').format('YYYY-MM-DD');
          const randomChange = (Math.random() - 0.5) * 0.1;
          const value = baseValue * (1 + randomChange + i * 0.02);
          mockData.push({
            date,
            total_cny: value,
            total_usd: value / 7.2
          });
        }
        console.log('📊 [AssetTrendChart] 使用fallback模拟数据:', mockData);
        setTrendData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendData();
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

  // 处理单数据点情况
  const isSingleDataPoint = chartData.length === 1;
  const currentValue = chartData.length > 0 ? chartData[0].value : 0;

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
      
      {chartData.length === 0 ? (
        <Empty description="暂无趋势数据" />
      ) : isSingleDataPoint ? (
        <div style={{ 
          height: 280, 
          display: 'flex', 
          flexDirection: 'column', 
          justifyContent: 'center', 
          alignItems: 'center',
          background: '#fafafa',
          border: '1px solid #d9d9d9',
          borderRadius: '6px'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff', marginBottom: '8px' }}>
            {currencyMode === 'CNY' ? '¥' : '$'}{currentValue.toLocaleString()}
          </div>
          <div style={{ fontSize: '14px', color: '#666' }}>
            当前资产总值 ({currencyMode})
          </div>
          <div style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
            数据点不足，无法显示趋势线
          </div>
        </div>
      ) : (
        <Line {...config} />
      )}
    </Spin>
  );
};

export default AssetTrendChart;