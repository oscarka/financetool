import React, { useEffect, useState } from 'react';
import { Bar } from '@ant-design/charts';
import { Spin, message } from 'antd';
import { aggregationAPI } from '../services/api';

const AssetBarChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDistributionData = async () => {
      setLoading(true);
      try {
        // 尝试获取真实数据
        console.log('🔄 [AssetBarChart] 开始获取资产类型分布数据...');
        const response = await aggregationAPI.getAssetTypeDistribution('CNY');
        console.log('📊 [AssetBarChart] API原始响应:', response);
        
        if (response.success && response.data) {
          // 转换数据格式
          const formattedData = response.data.map((item: any) => ({
            type: item.type,
            value: item.value
          }));
          console.log('🔄 [AssetBarChart] 数据转换过程:');
          console.log('  - 原始数据:', response.data);
          console.log('  - 转换后数据:', formattedData);
          console.log('  - 总计:', formattedData.reduce((sum, item) => sum + item.value, 0));
          setData(formattedData);
        } else {
          console.warn('⚠️ [AssetBarChart] API返回失败，使用模拟数据');
          // 如果API失败，使用mock数据
          const mockData = [
            { type: '股票基金', value: 450000 },
            { type: '债券基金', value: 280000 },
            { type: '货币基金', value: 180000 },
            { type: '混合基金', value: 120000 },
            { type: '指数基金', value: 80000 },
            { type: 'QDII基金', value: 60000 },
            { type: '其他资产', value: 40000 }
          ];
          console.log('📊 [AssetBarChart] 使用模拟数据:', mockData);
          setData(mockData);
        }
      } catch (error) {
        console.error('❌ [AssetBarChart] 获取分布数据失败:', error);
        message.error('获取分布数据失败，使用模拟数据');
        
        // 使用mock数据作为fallback
        const mockData = [
          { type: '股票基金', value: 450000 },
          { type: '债券基金', value: 280000 },
          { type: '货币基金', value: 180000 },
          { type: '混合基金', value: 120000 },
          { type: '指数基金', value: 80000 },
          { type: 'QDII基金', value: 60000 },
          { type: '其他资产', value: 40000 }
        ];
        console.log('📊 [AssetBarChart] 使用fallback模拟数据:', mockData);
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchDistributionData();
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