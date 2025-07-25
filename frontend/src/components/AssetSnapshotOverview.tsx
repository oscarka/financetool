import React, { useState, useEffect } from 'react';
import { Card, Table, Select, DatePicker, Button, Spin, message, Row, Col, Input, Affix, Divider } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import { snapshotAPI } from '../services/api';
import AssetTrendChart from './AssetTrendChart';
import AssetPieChart from './AssetPieChart';
import './AssetSnapshotOverview.css';
import CountUp from 'react-countup';
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

  // 优化表头icon显示，避免TS类型错误
  const columnsWithIcon = columns.map(col => {
    let baseTitle = col.title;
    if (typeof baseTitle === 'function') baseTitle = '';
    return {
      ...col,
      title: (
        <span>
          {col.key === 'platform' && '🏦'}
          {col.key === 'asset_type' && '📦'}
          {col.key === 'asset_code' && '🔢'}
          {col.key === 'currency' && '💱'}
          {col.key === 'base_value' && '💰'}
          {col.key === 'snapshot_time' && '⏰'}
          {baseTitle}
        </span>
      ),
      ellipsis: true,
    };
  });

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
            padding: '12px 24px', 
            background: 'linear-gradient(90deg, #e0e7ff 0%, #f0f5ff 100%)',
            borderRadius: '8px',
            fontSize: '16px',
            marginBottom: 8,
            boxShadow: '0 1px 8px #f0f1f2',
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            fontWeight: 500,
            color: '#1d39c4',
            letterSpacing: 1
          }}>
            <span style={{ fontWeight: 700, color: '#1890ff', fontSize: 22, marginRight: 8 }}>📊</span>
            <span>共找到 <CountUp end={filteredData.length} duration={0.8} /> 条记录</span>
            {platform && <span>| 平台: <b>{platform}</b></span>}
            {assetType && <span>| 类型: <b>{assetType}</b></span>}
            {currency && <span>| 币种: <b>{currency}</b></span>}
            {searchText && <span>| 搜索: <b>"{searchText}"</b></span>}
          </div>
        </Col>
      </Row>

      {/* 表格卡片化+极致体验 */}
      <Card
        bordered={false}
        style={{ marginBottom: 24, borderRadius: 10, boxShadow: '0 2px 8px #f0f1f2' }}
        bodyStyle={{ padding: 0 }}
      >
        <Spin spinning={loading} tip="数据加载中..." size="large">
          <Table
            columns={columnsWithIcon}
            dataSource={filteredData}
            rowKey="id"
            pagination={{ 
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
            }}
            scroll={{ x: 900 }}
            size="middle"
            bordered
            sticky
            rowClassName={(_, idx) => idx % 2 === 0 ? 'zebra-row' : ''}
            locale={{
              emptyText: <div style={{ padding: 32, color: '#999', fontSize: 16 }}>暂无数据，试试调整筛选条件或主动快照</div>
            }}
            style={{ minHeight: 320 }}
          />
        </Spin>
      </Card>
      {/* 图表区块极致体验 */}
      <Row gutter={24} style={{ marginTop: 32 }}>
        <Col xs={24} md={12}>
          <Card 
            title={<span style={{fontWeight:600, color:'#1d39c4', fontSize:16}}>资产分布饼图 🥧</span>} 
            bordered={false}
            style={{ 
              background: 'linear-gradient(135deg, #f0f5ff 0%, #e0e7ff 100%)',
              borderRadius: 12,
              boxShadow: '0 2px 8px #f0f1f2',
              marginBottom: 24
            }}
            bodyStyle={{ minHeight: 380, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <AssetPieChart baseCurrency={baseCurrency} />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card 
            title={<span style={{fontWeight:600, color:'#1d39c4', fontSize:16}}>资产趋势折线图 📈</span>} 
            bordered={false}
            style={{ 
              background: 'linear-gradient(135deg, #e0e7ff 0%, #f0f5ff 100%)',
              borderRadius: 12,
              boxShadow: '0 2px 8px #f0f1f2',
              marginBottom: 24
            }}
            bodyStyle={{ minHeight: 380, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <AssetTrendChart baseCurrency={baseCurrency} days={30} />
          </Card>
        </Col>
      </Row>
    </Card>
  );
};

export default AssetSnapshotOverview;