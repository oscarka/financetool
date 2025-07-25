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
        const params: any = { latest_only: true };
        if (currencyMode !== 'BOTH') params.base_currency = currencyMode;
        const resp = await snapshotAPI.getAssetSnapshots(params);
        if (resp.success && resp.data) {
          setPieData(resp.data);
        } else {
          setPieData([]);
        }
      } catch (e) {
        setPieData([]);
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