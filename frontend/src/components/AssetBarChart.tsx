import React, { useEffect, useState } from 'react';
import { Bar } from '@ant-design/charts';
import { Spin } from 'antd';

const AssetBarChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    const mockData = [
      { type: '股票基金', value: 450000 },
      { type: '债券基金', value: 280000 },
      { type: '货币基金', value: 180000 },
      { type: '混合基金', value: 120000 },
      { type: '指数基金', value: 80000 },
      { type: 'QDII基金', value: 60000 },
      { type: '其他资产', value: 40000 }
    ];
    setData(mockData);
    setLoading(false);
  }, []);

  const config = {
    data,
    xField: 'value',
    yField: 'type',
    seriesField: undefined,
    color: '#1890ff',
    legend: false,
    height: 280,
    label: { position: 'right' },
  };

  return (
    <Spin spinning={loading}>
      <Bar {...config} />
    </Spin>
  );
};

export default AssetBarChart;