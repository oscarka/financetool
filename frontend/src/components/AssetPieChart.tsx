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
        if (resp.success && resp.data && resp.data.length > 0) {
          setPieData(resp.data);
        } else {
          // mock数据兜底
          setPieData([
            { asset_type: 'BTC', total_cny: 5000, total_usd: 700 },
            { asset_type: 'ETH', total_cny: 3000, total_usd: 420 },
            { asset_type: 'USDT', total_cny: 2000, total_usd: 280 },
          ]);
        }
      } catch (e) {
        setPieData([
          { asset_type: 'BTC', total_cny: 5000, total_usd: 700 },
          { asset_type: 'ETH', total_cny: 3000, total_usd: 420 },
          { asset_type: 'USDT', total_cny: 2000, total_usd: 280 },
        ]);
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
      <Pie {...config} />
    </Spin>
  );
};

export default AssetPieChart;