import React, { useEffect, useState } from 'react';
import { Pie } from '@ant-design/charts';
import { Spin, Radio, Space, Empty, message } from 'antd';
import { aggregationAPI } from '../services/api';

interface AssetPieChartProps {
  baseCurrency: string | 'BOTH'; // 'CNY' | 'USD' | 'BOTH'
}

const AssetPieChart: React.FC<AssetPieChartProps> = ({ baseCurrency }) => {
  const [pieData, setPieData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currencyMode, setCurrencyMode] = useState<string>(baseCurrency);

  useEffect(() => {
    setCurrencyMode(baseCurrency);
  }, [baseCurrency]);

  useEffect(() => {
    const fetchDistributionData = async () => {
      setLoading(true);
      try {
        // 尝试获取真实数据
        console.log('🔄 [AssetPieChart] 开始获取资产类型分布数据...');
        const response = await aggregationAPI.getAssetTypeDistribution(currencyMode === 'BOTH' ? 'CNY' : currencyMode);
        console.log('📊 [AssetPieChart] API原始响应:', response);
        
        if (response.success && response.data) {
          // 转换数据格式
          const formattedData = response.data.map((item: any) => ({
            asset_type: item.type,
            total_cny: item.value,
            total_usd: item.value / 7.2 // 简单转换，实际应该从API获取USD数据
          }));
          console.log('🔄 [AssetPieChart] 数据转换过程:');
          console.log('  - 原始数据:', response.data);
          console.log('  - 转换后数据:', formattedData);
          console.log('  - CNY总计:', formattedData.reduce((sum, item) => sum + item.total_cny, 0));
          console.log('  - USD总计:', formattedData.reduce((sum, item) => sum + item.total_usd, 0));
          setPieData(formattedData);
        } else {
          console.warn('⚠️ [AssetPieChart] API返回失败，使用模拟数据');
          // 如果API失败，使用mock数据
          setTimeout(() => {
            const mockData = [
              { asset_type: 'BTC', total_cny: 5000, total_usd: 700 },
              { asset_type: 'ETH', total_cny: 3000, total_usd: 420 },
              { asset_type: 'USDT', total_cny: 2000, total_usd: 280 },
            ];
            console.log('📊 [AssetPieChart] 使用模拟数据:', mockData);
            setPieData(mockData);
          }, 300);
        }
      } catch (error) {
        console.error('❌ [AssetPieChart] 获取分布数据失败:', error);
        message.error('获取分布数据失败，使用模拟数据');
        
        // 使用mock数据作为fallback
        setTimeout(() => {
          const mockData = [
            { asset_type: 'BTC', total_cny: 5000, total_usd: 700 },
            { asset_type: 'ETH', total_cny: 3000, total_usd: 420 },
            { asset_type: 'USDT', total_cny: 2000, total_usd: 280 },
          ];
          console.log('📊 [AssetPieChart] 使用fallback模拟数据:', mockData);
          setPieData(mockData);
        }, 300);
      } finally {
        setLoading(false);
      }
    };

    fetchDistributionData();
  }, [currencyMode]);

  // 处理双基准数据
  let chartData: any[] = [];
  if (currencyMode === 'BOTH') {
    chartData = pieData.flatMap((item: any) => [
      { type: item.asset_type, value: item.total_cny, currency: 'CNY' },
      { type: item.asset_type, value: item.total_usd, currency: 'USD' },
    ]);
  } else {
    chartData = pieData.map((item: any) => ({
      type: item.asset_type,
      value: currencyMode === 'CNY' ? item.total_cny : item.total_usd,
      currency: currencyMode,
    }));
  }
  // 饼图只显示前10大资产，其他合并为"其他"
  if (chartData.length > 10) {
    const sorted = chartData.sort((a, b) => b.value - a.value);
    const top10 = sorted.slice(0, 10);
    const otherValue = sorted.slice(10).reduce((sum, item) => sum + item.value, 0);
    top10.push({ type: '其他', value: otherValue, currency: chartData[0].currency });
    chartData = top10;
  }

  const config = {
    appendPadding: 10,
    data: chartData,
    angleField: 'value',
    colorField: 'type',
    seriesField: 'currency',
    radius: 0.9,
    label: {
      type: 'spider',
      formatter: (datum: any) => `${datum.type}: ${(datum.percent * 100).toFixed(2)}%`,
    },
    interactions: [{ type: 'element-active' }],
    legend: { position: 'top' },
    tooltip: { showMarkers: true },
    animation: true,
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
      {chartData.length === 0 ? <Empty description="暂无分布数据" /> : <Pie {...config} />}
    </Spin>
  );
};

export default AssetPieChart;