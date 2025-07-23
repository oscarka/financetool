import React, { useEffect, useState } from 'react';
import { Table, Select, DatePicker, Card, Spin } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
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
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
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
    let params = new URLSearchParams();
    params.append('base_currency', baseCurrency);
    if (dateRange && dateRange.length === 2) {
      params.append('start', dateRange[0].format('YYYY-MM-DD'));
      params.append('end', dateRange[1].format('YYYY-MM-DD'));
    }
    const resp = await fetch('/api/snapshot/assets?' + params.toString());
    const data = await resp.json();
    setAssetData(data);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line
  }, [baseCurrency, dateRange]);

  return (
    <Card title="资产快照多基准货币展示" style={{ margin: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
        <Select value={baseCurrency} onChange={setBaseCurrency} style={{ width: 120 }}>
          {baseCurrencies.map((c) => (
            <Option key={c} value={c}>
              {c}
            </Option>
          ))}
        </Select>
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
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