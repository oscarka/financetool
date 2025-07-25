import React, { useEffect, useState } from 'react';
import { Pie } from '@ant-design/charts';
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
    // 彻底mock数据，无论API如何都注入
    const mockData = [
      { type: '股票基金', value: 450000 },
      { type: '债券基金', value: 280000 },
      { type: '货币基金', value: 180000 },
      { type: '混合基金', value: 120000 },
      { type: '指数基金', value: 80000 },
      { type: 'QDII基金', value: 60000 },
      { type: '其他资产', value: 40000 }
    ];
    setPieData(mockData);
    setLoading(false);
  }, [currencyMode]);

  // 处理双基准数据
  let chartData: any[] = [];
  if (currencyMode === 'BOTH') {
    // 为双基准模式生成数据
    chartData = pieData.flatMap((item: any) => [
      { type: item.type, value: item.value, currency: 'CNY' },
      { type: item.type, value: item.value * 0.14, currency: 'USD' },
    ]);
  } else {
    // 单基准模式，直接使用mock数据
    chartData = pieData;
  }

  const config = {
    appendPadding: 10,
    data: chartData,
    angleField: 'value',
    colorField: 'type',
    seriesField: currencyMode === 'BOTH' ? 'currency' : undefined,
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
    height: 280,
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