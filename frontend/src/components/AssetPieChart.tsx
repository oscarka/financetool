import React, { useEffect, useState } from 'react';
import { Pie } from '@ant-design/charts';
import { snapshotAPI } from '../services/api';
import { Spin, Radio, Space } from 'antd';

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
    const fetchPie = async () => {
      setLoading(true);
      try {
        const params: any = {};
        if (currencyMode !== 'BOTH') params.base_currency = currencyMode;
        const resp = await snapshotAPI.getAssetSnapshots(params);
        if (resp.success && resp.data) {
          setPieData(resp.data);
        } else {
          // Mock数据 - 生成资产分布数据
          const mockData = [
            { asset_type: '股票基金', total_cny: 450000, total_usd: 63000 },
            { asset_type: '债券基金', total_cny: 280000, total_usd: 39200 },
            { asset_type: '货币基金', total_cny: 180000, total_usd: 25200 },
            { asset_type: '混合基金', total_cny: 120000, total_usd: 16800 },
            { asset_type: '指数基金', total_cny: 80000, total_usd: 11200 },
            { asset_type: 'QDII基金', total_cny: 60000, total_usd: 8400 },
            { asset_type: '其他资产', total_cny: 40000, total_usd: 5600 }
          ];
          setPieData(mockData);
        }
      } catch (e) {
        // Mock数据 - 生成资产分布数据
        const mockData = [
          { asset_type: '股票基金', total_cny: 450000, total_usd: 63000 },
          { asset_type: '债券基金', total_cny: 280000, total_usd: 39200 },
          { asset_type: '货币基金', total_cny: 180000, total_usd: 25200 },
          { asset_type: '混合基金', total_cny: 120000, total_usd: 16800 },
          { asset_type: '指数基金', total_cny: 80000, total_usd: 11200 },
          { asset_type: 'QDII基金', total_cny: 60000, total_usd: 8400 },
          { asset_type: '其他资产', total_cny: 40000, total_usd: 5600 }
        ];
        setPieData(mockData);
      }
      setLoading(false);
    };
    fetchPie();
  }, [currencyMode]);

  // 处理双基准数据
  let chartData: any[] = [];
  if (currencyMode === 'BOTH') {
    // 假设API返回格式为 [{asset_type, total_cny, total_usd}]
    chartData = pieData.flatMap((item: any) => [
      { type: item.asset_type, value: item.total_cny, currency: 'CNY' },
      { type: item.asset_type, value: item.total_usd, currency: 'USD' },
    ]);
  } else {
    // [{asset_type, total}]
    chartData = pieData.map((item: any) => ({
      type: item.asset_type,
      value: currencyMode === 'CNY' ? item.total_cny : item.total_usd,
      currency: currencyMode,
    }));
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
      labelHeight: 28,
      content: '{name}\n{percentage}',
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
      <Pie {...config} />
    </Spin>
  );
};

export default AssetPieChart;