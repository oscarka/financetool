import React, { useEffect, useState } from 'react';
import { Table, Select, DatePicker, Card, Spin, Button, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { Dayjs } from 'dayjs';
import { snapshotAPI } from '../services/api';
// import AssetTrendChart from './AssetTrendChart'; // 如有趋势图可解开

const { Option } = Select;
const { RangePicker } = DatePicker;

type AssetSnapshot = {
  id: number;
  platform: string;
  asset_type: string;
  asset_code: string;
  currency: string;
  balance: number;
  balance_cny?: number;
  balance_usd?: number;
  balance_eur?: number;
  base_value?: number;
  snapshot_time: string;
};

const baseCurrencies = ['CNY', 'USD', 'EUR'];

const AssetSnapshotOverview: React.FC = () => {
  const [baseCurrency, setBaseCurrency] = useState<string>('CNY');
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);
  const [assetData, setAssetData] = useState<AssetSnapshot[]>([]);
  const [loading, setLoading] = useState(false);

  const columns: ColumnsType<AssetSnapshot> = [
    { title: '平台', dataIndex: 'platform', key: 'platform' },
    { title: '资产类型', dataIndex: 'asset_type', key: 'asset_type' },
    { title: '资产代码', dataIndex: 'asset_code', key: 'asset_code' },
    { title: '币种', dataIndex: 'currency', key: 'currency' },
    {
      title: `${baseCurrency}金额`,
      dataIndex: 'base_value',
      key: 'base_value',
      render: (val: number) =>
        val == null ? '-' : val.toLocaleString('zh-CN', { style: 'currency', currency: baseCurrency }),
    },
    { title: '快照时间', dataIndex: 'snapshot_time', key: 'snapshot_time' },
  ];

  const loadData = async () => {
    setLoading(true);
    let params: any = {};
    params.base_currency = baseCurrency;
    if (dateRange && dateRange[0] && dateRange[1]) {
      params.start = dateRange[0].format('YYYY-MM-DD');
      params.end = dateRange[1].format('YYYY-MM-DD');
    }
    try {
      const response = await snapshotAPI.getAssetSnapshots(params);
      if (response.success) {
        setAssetData(response.data || []);
      } else {
        message.error(response.message || '获取快照数据失败');
      }
    } catch (error: any) {
      message.error('获取快照数据失败');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line
  }, [baseCurrency, dateRange]);

  // 修正onChange类型
  const handleRangeChange = (dates: [Dayjs | null, Dayjs | null] | null) => {
    setDateRange(dates);
  };

  // 主动快照
  const handleExtractSnapshot = async () => {
    setLoading(true);
    try {
      const response = await snapshotAPI.extractAssetSnapshot();
      if (response.success) {
        message.success(response.message || '快照成功');
        await loadData();
      } else {
        message.error(response.error || '快照失败');
      }
    } catch (error: any) {
      message.error('快照请求异常');
    }
    setLoading(false);
  };

  return (
    <Card title="资产快照多基准货币展示" style={{ margin: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
        <Button type="primary" onClick={handleExtractSnapshot}>主动快照</Button>
        <Select value={baseCurrency} onChange={setBaseCurrency} style={{ width: 120 }}>
          {baseCurrencies.map((c) => (
            <Option key={c} value={c}>{c}</Option>
          ))}
        </Select>
        <RangePicker
          value={dateRange}
          onChange={handleRangeChange}
          allowClear
          style={{ width: 300 }}
        />
      </div>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={assetData}
          rowKey="id"
          pagination={{ pageSize: 20 }}
        />
      </Spin>
      {/* <div style={{ marginTop: 32 }}>
        <AssetTrendChart baseCurrency={baseCurrency} days={30} />
      </div> */}
    </Card>
  );
};

export default AssetSnapshotOverview;