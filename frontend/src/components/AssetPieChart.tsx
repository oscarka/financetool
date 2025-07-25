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
      { type: 'qdii基金', value: 60000 },
      { type: '其他资产', value: 40000 }
    ];
    console.log('PieData:', mockData);
    setPieData(mockData);
    setLoading(false);
  }, [currencyMode]);

  const config = {
    data: pieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.6,
    label: {
      type: 'spider',
      labelHeight: 28,
      content: '{type}',
    },
    legend: { position: 'bottom' },
    tooltip: {},
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