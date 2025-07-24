import React, { useState, useEffect } from 'react';
import { Card, Table, Select, DatePicker, Button, Spin, message, Row, Col, Input, Statistic } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import { snapshotAPI } from '../services/api';
import AssetTrendChart from './AssetTrendChart';
import AssetPieChart from './AssetPieChart';
import { DollarCircleOutlined, RiseOutlined, AppstoreOutlined, UserOutlined } from '@ant-design/icons';
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

  // 统计信息
  const totalAsset = assetData.reduce((sum, item) => sum + (item.base_value || 0), 0);
  const assetTypesCount = new Set(assetData.map(item => item.asset_type)).size;
  const platformCount = new Set(assetData.map(item => item.platform)).size;
  // 这里24h涨跌和账户数可根据实际数据补充
  const change24h = 0; // TODO: 可根据趋势数据计算
  const accountCount = platformCount;

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
      {/* Summary 卡片区 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} style={{ background: '#f0f5ff' }}>
            <Statistic
              title="总资产"
              value={totalAsset}
              precision={2}
              prefix={<DollarCircleOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff', fontWeight: 'bold', fontSize: 22 }}
              suffix={baseCurrency}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} style={{ background: '#f6ffed' }}>
            <Statistic
              title="24h涨跌"
              value={change24h}
              precision={2}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontWeight: 'bold', fontSize: 22 }}
              suffix="%"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} style={{ background: '#fffbe6' }}>
            <Statistic
              title="资产种类"
              value={assetTypesCount}
              prefix={<AppstoreOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14', fontWeight: 'bold', fontSize: 22 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} style={{ background: '#fff0f6' }}>
            <Statistic
              title="账户数"
              value={accountCount}
              prefix={<UserOutlined style={{ color: '#eb2f96' }} />}
              valueStyle={{ color: '#eb2f96', fontWeight: 'bold', fontSize: 22 }}
            />
          </Card>
        </Col>
      </Row>
      {/* 快捷时间筛选按钮 */}
      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col>
          <Button size="small" onClick={() => setDateRange([dayjs().startOf('week'), dayjs().endOf('week')])}>本周</Button>
        </Col>
        <Col>
          <Button size="small" onClick={() => setDateRange([dayjs().startOf('month'), dayjs().endOf('month')])}>本月</Button>
        </Col>
        <Col>
          <Button size="small" onClick={() => setDateRange([dayjs().subtract(3, 'month'), dayjs()])}>近三月</Button>
        </Col>
        <Col>
          <Button size="small" onClick={() => setDateRange([dayjs().startOf('year'), dayjs()])}>今年</Button>
        </Col>
      </Row>
      {/* 筛选器区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Button type="primary" onClick={handleExtractSnapshot} block>
            主动快照
          </Button>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Select 
            value={baseCurrency} 
            onChange={setBaseCurrency} 
            style={{ width: '100%' }}
            placeholder="基准货币"
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
            style={{ width: '100%' }}
            placeholder="选择平台"
            allowClear
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
            style={{ width: '100%' }}
            placeholder="资产类型"
            allowClear
          >
            {assetTypes.map((t) => (
              <Option key={t} value={t}>{t}</Option>
            ))}
          </Select>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Select 
            value={currency} 
            onChange={setCurrency} 
            style={{ width: '100%' }}
            placeholder="选择币种"
            allowClear
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
            style={{ width: '100%' }}
            placeholder={['开始日期', '结束日期']}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Button onClick={clearFilters} block>
            清空筛选
          </Button>
        </Col>
      </Row>

      {/* 搜索框 */}
      <Row style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Search
            placeholder="搜索平台、资产类型、代码、币种等..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
            style={{ width: '100%' }}
          />
        </Col>
      </Row>

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