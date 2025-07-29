import React, { useState, useEffect } from 'react';
import { Card, Table, Select, DatePicker, Button, Spin, message, Row, Col, Input, Affix, Divider, Statistic, Progress, Tag, Alert, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import { snapshotAPI, aggregationAPI } from '../services/api';
import AssetTrendChart from './AssetTrendChart';
import AssetBarChart from './AssetBarChart';
import './AssetSnapshotOverview.css';
import CountUp from 'react-countup';
import { ArrowUpOutlined, PlusOutlined, DownloadOutlined, ReloadOutlined, ExclamationCircleOutlined, TrophyOutlined, RiseOutlined, DollarOutlined, BankOutlined, AppstoreOutlined, UserOutlined } from '@ant-design/icons';

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
  
  // 聚合统计数据
  const [aggregatedStats, setAggregatedStats] = useState<any>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  
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

  // 加载聚合统计数据
  const loadAggregatedStats = async () => {
    setStatsLoading(true);
    try {
      const response = await aggregationAPI.getStats(baseCurrency);
      if (response.success && response.data) {
        setAggregatedStats(response.data);
      }
    } catch (error) {
      console.error('获取聚合统计数据失败:', error);
      message.error('获取聚合统计数据失败');
    } finally {
      setStatsLoading(false);
    }
  };

  // 加载资产快照数据
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
        // Mock数据 - 生成丰富的资产快照数据
        const mockData = [
          { id: 1, platform: '蚂蚁财富', asset_type: '股票基金', asset_code: '000001', asset_name: '华夏成长混合', currency: 'CNY', balance: 100000, base_value: 120000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 2, platform: '天天基金', asset_type: '债券基金', asset_code: '000002', asset_name: '易方达债券A', currency: 'CNY', balance: 80000, base_value: 82000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 3, platform: '招商银行', asset_type: '货币基金', asset_code: '000003', asset_name: '招商现金A', currency: 'CNY', balance: 50000, base_value: 50000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 4, platform: '工商银行', asset_type: '混合基金', asset_code: '000004', asset_name: '工银瑞信混合', currency: 'CNY', balance: 150000, base_value: 165000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 5, platform: '建设银行', asset_type: '指数基金', asset_code: '000005', asset_name: '建信沪深300', currency: 'CNY', balance: 90000, base_value: 95000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 6, platform: '中国银行', asset_type: 'QDII基金', asset_code: '000006', asset_name: '中银全球策略', currency: 'USD', balance: 10000, base_value: 70000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 7, platform: '交通银行', asset_type: '股票基金', asset_code: '000007', asset_name: '交银成长混合', currency: 'CNY', balance: 120000, base_value: 135000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 8, platform: '兴业银行', asset_type: '债券基金', asset_code: '000008', asset_name: '兴业债券A', currency: 'CNY', balance: 60000, base_value: 61000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 9, platform: '平安银行', asset_type: '货币基金', asset_code: '000009', asset_name: '平安现金A', currency: 'CNY', balance: 40000, base_value: 40000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 10, platform: '浦发银行', asset_type: '混合基金', asset_code: '000010', asset_name: '浦发混合A', currency: 'CNY', balance: 110000, base_value: 118000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 11, platform: '中信银行', asset_type: '指数基金', asset_code: '000011', asset_name: '中信中证500', currency: 'CNY', balance: 70000, base_value: 72000, snapshot_time: '2024-01-15 10:30:00' },
          { id: 12, platform: '民生银行', asset_type: 'QDII基金', asset_code: '000012', asset_name: '民生全球精选', currency: 'USD', balance: 8000, base_value: 56000, snapshot_time: '2024-01-15 10:30:00' }
        ];
        setAssetData(mockData);
      }
    } catch (error: any) {
      // Mock数据 - 生成丰富的资产快照数据
      const mockData = [
        { id: 1, platform: '蚂蚁财富', asset_type: '股票基金', asset_code: '000001', asset_name: '华夏成长混合', currency: 'CNY', balance: 100000, base_value: 120000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 2, platform: '天天基金', asset_type: '债券基金', asset_code: '000002', asset_name: '易方达债券A', currency: 'CNY', balance: 80000, base_value: 82000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 3, platform: '招商银行', asset_type: '货币基金', asset_code: '000003', asset_name: '招商现金A', currency: 'CNY', balance: 50000, base_value: 50000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 4, platform: '工商银行', asset_type: '混合基金', asset_code: '000004', asset_name: '工银瑞信混合', currency: 'CNY', balance: 150000, base_value: 165000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 5, platform: '建设银行', asset_type: '指数基金', asset_code: '000005', asset_name: '建信沪深300', currency: 'CNY', balance: 90000, base_value: 95000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 6, platform: '中国银行', asset_type: 'QDII基金', asset_code: '000006', asset_name: '中银全球策略', currency: 'USD', balance: 10000, base_value: 70000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 7, platform: '交通银行', asset_type: '股票基金', asset_code: '000007', asset_name: '交银成长混合', currency: 'CNY', balance: 120000, base_value: 135000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 8, platform: '兴业银行', asset_type: '债券基金', asset_code: '000008', asset_name: '兴业债券A', currency: 'CNY', balance: 60000, base_value: 61000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 9, platform: '平安银行', asset_type: '货币基金', asset_code: '000009', asset_name: '平安现金A', currency: 'CNY', balance: 40000, base_value: 40000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 10, platform: '浦发银行', asset_type: '混合基金', asset_code: '000010', asset_name: '浦发混合A', currency: 'CNY', balance: 110000, base_value: 118000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 11, platform: '中信银行', asset_type: '指数基金', asset_code: '000011', asset_name: '中信中证500', currency: 'CNY', balance: 70000, base_value: 72000, snapshot_time: '2024-01-15 10:30:00' },
        { id: 12, platform: '民生银行', asset_type: 'QDII基金', asset_code: '000012', asset_name: '民生全球精选', currency: 'USD', balance: 8000, base_value: 56000, snapshot_time: '2024-01-15 10:30:00' }
      ];
      setAssetData(mockData);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
    loadAggregatedStats();
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
        await loadAggregatedStats(); // 重新加载聚合数据
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

  // 计算统计数据
  const calculateStats = () => {
    if (!filteredData.length) return null;
    
    const totalValue = filteredData.reduce((sum, item) => sum + (item.base_value || 0), 0);
    const platformStats = filteredData.reduce((acc, item) => {
      acc[item.platform] = (acc[item.platform] || 0) + (item.base_value || 0);
      return acc;
    }, {} as Record<string, number>);
    
    const assetTypeStats = filteredData.reduce((acc, item) => {
      acc[item.asset_type] = (acc[item.asset_type] || 0) + (item.base_value || 0);
      return acc;
    }, {} as Record<string, number>);
    
    const topPlatforms = Object.entries(platformStats)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([platform, value]) => ({ platform, value, percentage: (value / totalValue * 100).toFixed(1) }));
    
    const topAssetTypes = Object.entries(assetTypeStats)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([type, value]) => ({ type, value, percentage: (value / totalValue * 100).toFixed(1) }));
    
    return { totalValue, topPlatforms, topAssetTypes };
  };
  
  const stats = calculateStats();

  // 使用聚合统计数据
  const useAggregatedStats = aggregatedStats && !statsLoading;
  const displayStats = useAggregatedStats ? {
    totalValue: aggregatedStats.total_value,
    topPlatforms: Object.entries(aggregatedStats.platform_stats || {})
      .sort(([,a], [,b]) => (b as number) - (a as number))
      .slice(0, 5)
      .map(([platform, value]) => ({ 
        platform, 
        value: value as number, 
        percentage: ((value as number) / aggregatedStats.total_value * 100).toFixed(1) 
      })),
    topAssetTypes: Object.entries(aggregatedStats.asset_type_stats || {})
      .sort(([,a], [,b]) => (b as number) - (a as number))
      .slice(0, 5)
      .map(([type, value]) => ({ 
        type, 
        value: value as number, 
        percentage: ((value as number) / aggregatedStats.total_value * 100).toFixed(1) 
      }))
  } : stats;

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
            <Col xs={24} sm={12} md={6}>
              <RangePicker
                value={dateRange}
                onChange={handleRangeChange}
                style={{ width: '100%', transition: 'all 0.2s' }}
                format="YYYY-MM-DD"
                placeholder={['开始日期', '结束日期']}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Search
                placeholder="搜索资产..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ transition: 'all 0.2s' }}
                allowClear
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Button onClick={clearFilters} block style={{ transition: 'all 0.2s' }}>
                清空筛选
              </Button>
            </Col>
          </Row>
        </Card>
      </Affix>

      {/* 统计卡片区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="总资产价值"
              value={useAggregatedStats ? aggregatedStats.total_value : totalAsset}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              prefix={<DollarOutlined />}
              suffix={baseCurrency}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="资产类型数"
              value={useAggregatedStats ? aggregatedStats.asset_type_count : assetTypesCount}
              valueStyle={{ color: '#1890ff' }}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="平台数量"
              value={useAggregatedStats ? aggregatedStats.platform_count : platformCount}
              valueStyle={{ color: '#722ed1' }}
              prefix={<BankOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="资产数量"
              value={useAggregatedStats ? aggregatedStats.asset_count : filteredData.length}
              valueStyle={{ color: '#eb2f96' }}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={24} style={{ marginBottom: 32 }}>
        <Col xs={24} md={12}>
          <Card 
            title={<span style={{fontWeight:600, color:'#1d39c4', fontSize:16}}>资产类型分布条形图 📊</span>} 
            bordered={false}
            style={{ 
              background: 'linear-gradient(135deg, #f0f5ff 0%, #e0e7ff 100%)',
              borderRadius: 12,
              boxShadow: '0 2px 8px #f0f1f2',
              marginBottom: 24
            }}
            bodyStyle={{ padding: 16 }}
          >
            <AssetBarChart />
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
            bodyStyle={{ padding: 16 }}
          >
            <AssetTrendChart baseCurrency={baseCurrency} days={30} />
          </Card>
        </Col>
      </Row>

      {/* 快捷操作 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            block 
            size="large"
            style={{ height: 48, borderRadius: 8 }}
          >
            添加资产
          </Button>
        </Col>
        <Col xs={24} sm={8}>
          <Button 
            icon={<DownloadOutlined />} 
            block 
            size="large"
            style={{ height: 48, borderRadius: 8 }}
          >
            导出数据
          </Button>
        </Col>
        <Col xs={24} sm={8}>
          <Button 
            icon={<ReloadOutlined />} 
            block 
            size="large"
            onClick={() => {
              loadData();
              loadAggregatedStats();
            }}
            style={{ height: 48, borderRadius: 8 }}
          >
            刷新数据
          </Button>
        </Col>
      </Row>

      {/* 分布统计 */}
      {displayStats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} md={12}>
            <Card 
              title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:16}}>🏆 平台分布 Top5</span>} 
              bordered={false}
              className="top-distribution-card"
            >
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                {displayStats.topPlatforms.map((item, index) => (
                  <div key={item.platform} className="top-item">
                    <div className="top-rank">#{index + 1}</div>
                    <div className="top-content">
                      <div className="top-name">{item.platform}</div>
                      <div className="top-value">
                        {item.value.toLocaleString()} {baseCurrency}
                      </div>
                    </div>
                    <div className="top-percentage">
                      <Progress 
                        percent={parseFloat(item.percentage)} 
                        size="small" 
                        showInfo={false}
                        strokeColor={['#1890ff', '#52c41a', '#faad14', '#722ed1', '#eb2f96'][index]}
                      />
                      <span className="percentage-text">{item.percentage}%</span>
                    </div>
                  </div>
                ))}
              </Space>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card 
              title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:16}}>📊 资产类型分布 Top5</span>} 
              bordered={false}
              className="top-distribution-card"
            >
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                {displayStats.topAssetTypes.map((item, index) => (
                  <div key={item.type} className="top-item">
                    <div className="top-rank">#{index + 1}</div>
                    <div className="top-content">
                      <div className="top-name">{item.type}</div>
                      <div className="top-value">
                        {item.value.toLocaleString()} {baseCurrency}
                      </div>
                    </div>
                    <div className="top-percentage">
                      <Progress 
                        percent={parseFloat(item.percentage)} 
                        size="small" 
                        showInfo={false}
                        strokeColor={['#1890ff', '#52c41a', '#faad14', '#722ed1', '#eb2f96'][index]}
                      />
                      <span className="percentage-text">{item.percentage}%</span>
                    </div>
                  </div>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      )}

      {/* 数据表格 */}
      <Card 
        title={<span style={{fontWeight:600, color:'#1d39c4', fontSize:16}}>📋 资产快照明细</span>} 
        bordered={false}
        style={{ 
          background: 'linear-gradient(135deg, #fafcff 0%, #f0f5ff 100%)',
          borderRadius: 12,
          boxShadow: '0 2px 8px #f0f1f2'
        }}
        bodyStyle={{ padding: 16 }}
      >
        <Table
          columns={[
            {
              title: '平台',
              dataIndex: 'platform',
              key: 'platform',
              render: (text: string) => <Tag color="blue">{text}</Tag>,
            },
            {
              title: '资产类型',
              dataIndex: 'asset_type',
              key: 'asset_type',
              render: (text: string) => <Tag color="green">{text}</Tag>,
            },
            {
              title: '资产代码',
              dataIndex: 'asset_code',
              key: 'asset_code',
            },
            {
              title: '资产名称',
              dataIndex: 'asset_name',
              key: 'asset_name',
              ellipsis: true,
            },
            {
              title: '币种',
              dataIndex: 'currency',
              key: 'currency',
              render: (text: string) => <Tag color="orange">{text}</Tag>,
            },
            {
              title: '余额',
              dataIndex: 'balance',
              key: 'balance',
              render: (value: number) => value.toLocaleString(),
            },
            {
              title: '基准价值',
              dataIndex: 'base_value',
              key: 'base_value',
              render: (value: number) => (
                <span style={{ color: '#3f8600', fontWeight: 600 }}>
                  {value?.toLocaleString()} {baseCurrency}
                </span>
              ),
            },
            {
              title: '快照时间',
              dataIndex: 'snapshot_time',
              key: 'snapshot_time',
              render: (text: string) => new Date(text).toLocaleString(),
            },
          ]}
          dataSource={filteredData}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            pageSize: 10,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </Card>
  );
};

export default AssetSnapshotOverview;