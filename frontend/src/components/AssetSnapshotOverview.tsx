import React, { useState, useEffect } from 'react';
import { Card, Table, Select, DatePicker, Button, Spin, message, Row, Col, Input, Affix, Divider } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import { snapshotAPI } from '../services/api';
import AssetTrendChart from './AssetTrendChart';
import AssetPieChart from './AssetPieChart';
// import AssetTrendChart from './AssetTrendChart'; // 如有趋势图可解开

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Search } = Input;

type AssetSnapshot = {
  id: number;
  platform: string;
  asset_type: string;
  asset_code: string;
  asset_name?: string;
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
  // 设置默认日期范围为当前日期前后7天
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>([
    dayjs().subtract(7, 'day'),
    dayjs().add(7, 'day')
  ]);
  const [assetData, setAssetData] = useState<AssetSnapshot[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 新增筛选器状态
  const [platform, setPlatform] = useState<string>('');
  const [assetType, setAssetType] = useState<string>('');
  const [currency, setCurrency] = useState<string>('');
  const [searchText, setSearchText] = useState<string>('');
  
  // 从数据中提取可用的筛选选项
  const platforms = Array.from(new Set(assetData.map(item => item.platform))).sort();
  const assetTypes = Array.from(new Set(assetData.map(item => item.asset_type))).sort();
  const currencies = Array.from(new Set(assetData.map(item => item.currency))).sort();

  const columns: ColumnsType<AssetSnapshot> = [
    { title: '平台', dataIndex: 'platform', key: 'platform', width: 100 },
    { title: '资产类型', dataIndex: 'asset_type', key: 'asset_type', width: 120 },
    { title: '资产代码', dataIndex: 'asset_code', key: 'asset_code', width: 150 },
    { title: '币种', dataIndex: 'currency', key: 'currency', width: 80 },
    {
      title: `${baseCurrency}金额`,
      dataIndex: 'base_value',
      key: 'base_value',
      width: 120,
      render: (val: number) =>
        val == null ? '-' : val.toLocaleString('zh-CN', { style: 'currency', currency: baseCurrency }),
    },
    { 
      title: '快照时间', 
      dataIndex: 'snapshot_time', 
      key: 'snapshot_time',
      width: 180,
      render: (val: string) => dayjs(val).format('YYYY-MM-DD HH:mm:ss')
    },
  ];

  const loadData = async () => {
    setLoading(true);
    let params: any = {};
    params.base_currency = baseCurrency;
    if (dateRange && dateRange[0] && dateRange[1]) {
      params.start = dateRange[0].format('YYYY-MM-DD');
      params.end = dateRange[1].format('YYYY-MM-DD');
    }
    if (platform) params.platform = platform;
    if (assetType) params.asset_type = assetType;
    if (currency) params.currency = currency;
    
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
  }, [baseCurrency, dateRange, platform, assetType, currency]);

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
        message.error(response.message || '快照失败');
      }
    } catch (error: any) {
      message.error('快照请求异常');
    }
    setLoading(false);
  };

  // 清空筛选器
  const clearFilters = () => {
    setPlatform('');
    setAssetType('');
    setCurrency('');
    setSearchText('');
    setDateRange([dayjs().subtract(7, 'day'), dayjs().add(7, 'day')]);
  };

  // 根据搜索文本过滤数据
  const filteredData = assetData.filter(item => {
    if (!searchText) return true;
    const searchLower = searchText.toLowerCase();
    return (
      item.platform.toLowerCase().includes(searchLower) ||
      item.asset_type.toLowerCase().includes(searchLower) ||
      item.asset_code.toLowerCase().includes(searchLower) ||
      item.currency.toLowerCase().includes(searchLower) ||
      item.asset_name?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <Card title="资产快照多基准货币展示" style={{ margin: 24 }}>
      {/* 筛选器区域 - 卡片分组+吸顶+分隔线+紧凑间距+动效+高亮 */}
      <Affix offsetTop={0}>
        <Card
          bordered={false}
          style={{ marginBottom: 16, boxShadow: '0 2px 8px #f0f1f2', borderRadius: 10, background: '#fafcff' }}
          bodyStyle={{ padding: 16 }}
        >
          <Row gutter={[8, 8]} align="middle" style={{ marginBottom: 8 }}>
            <Col xs={24} sm={12} md={6}>
              <Button type="primary" onClick={handleExtractSnapshot} block style={{ transition: 'all 0.2s' }}>
                主动快照
              </Button>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Select
                value={baseCurrency}
                onChange={setBaseCurrency}
                style={{ width: '100%', transition: 'all 0.2s' }}
                placeholder="基准货币"
                dropdownStyle={{ borderRadius: 8 }}
                dropdownMatchSelectWidth={false}
              >
                {baseCurrencies.map((c) => (
                  <Option key={c} value={c}>{c}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Select
                value={platform}
                onChange={setPlatform}
                style={{ width: '100%', transition: 'all 0.2s' }}
                placeholder="选择平台"
                allowClear
                dropdownStyle={{ borderRadius: 8 }}
                dropdownMatchSelectWidth={false}
              >
                {platforms.map((p) => (
                  <Option key={p} value={p}>{p}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Select
                value={assetType}
                onChange={setAssetType}
                style={{ width: '100%', transition: 'all 0.2s' }}
                placeholder="资产类型"
                allowClear
                dropdownStyle={{ borderRadius: 8 }}
                dropdownMatchSelectWidth={false}
              >
                {assetTypes.map((t) => (
                  <Option key={t} value={t}>{t}</Option>
                ))}
              </Select>
            </Col>
          </Row>
          <Divider style={{ margin: '8px 0' }} />
          <Row gutter={[8, 8]} align="middle">
            <Col xs={24} sm={12} md={6}>
              <Select
                value={currency}
                onChange={setCurrency}
                style={{ width: '100%', transition: 'all 0.2s' }}
                placeholder="选择币种"
                allowClear
                dropdownStyle={{ borderRadius: 8 }}
                dropdownMatchSelectWidth={false}
              >
                {currencies.map((c) => (
                  <Option key={c} value={c}>{c}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={12}>
              <RangePicker
                value={dateRange}
                onChange={handleRangeChange}
                allowClear
                style={{ width: '100%', transition: 'all 0.2s' }}
                placeholder={['开始日期', '结束日期']}
                popupStyle={{ borderRadius: 8 }}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Button onClick={clearFilters} block style={{ transition: 'all 0.2s' }}>
                清空筛选
              </Button>
            </Col>
          </Row>
          <Row style={{ marginTop: 8 }}>
            <Col span={24}>
              <Search
                placeholder="搜索平台、资产类型、代码、币种等..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
                style={{ width: '100%', transition: 'all 0.2s' }}
              />
            </Col>
          </Row>
        </Card>
      </Affix>

      {/* 数据统计 */}
      <Row style={{ marginBottom: 16 }}>
        <Col span={24}>
          <div style={{ 
            padding: '8px 16px', 
            backgroundColor: '#f5f5f5', 
            borderRadius: '6px',
            fontSize: '14px'
          }}>
            共找到 <strong>{filteredData.length}</strong> 条记录
            {platform && ` | 平台: ${platform}`}
            {assetType && ` | 类型: ${assetType}`}
            {currency && ` | 币种: ${currency}`}
            {searchText && ` | 搜索: "${searchText}"`}
          </div>
        </Col>
      </Row>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={filteredData}
          rowKey="id"
          pagination={{ 
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
          }}
          scroll={{ x: 800 }}
          size="small"
        />
      </Spin>
      <Row gutter={24} style={{ marginTop: 32 }}>
        <Col xs={24} md={12}>
          <Card title="资产分布饼图" bordered={false}>
            <AssetPieChart baseCurrency={baseCurrency} />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="资产趋势折线图" bordered={false}>
            <AssetTrendChart baseCurrency={baseCurrency} days={30} />
          </Card>
        </Col>
      </Row>
    </Card>
  );
};

export default AssetSnapshotOverview;