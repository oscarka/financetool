import React, { useState } from 'react';
import { Card, Button, Input, Select, Checkbox, DatePicker, Space, Typography, Row, Col, Alert, Tag, Collapse, Tabs, Switch, Tooltip, message, List } from 'antd';
import { PlayCircleOutlined, CopyOutlined, ReloadOutlined, QuestionCircleOutlined, ClockCircleOutlined, DollarOutlined, PieChartOutlined } from '@ant-design/icons';
import { aiAnalystAPI } from '../services/api';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Panel } = Collapse;
const { TabPane } = Tabs;

interface ApiResult {
  success: boolean;
  data?: any;
  error?: string;
  status?: number;
  responseTime?: number;
  timestamp?: string;
}

interface TestScenario {
  name: string;
  description: string;
  params: any;
  expectedData: string[];
}

const AIAnalystTest: React.FC = () => {
  // API参数状态
  const [apiKey, setApiKey] = useState('ai_analyst_key_2024');
  const [baseCurrency, setBaseCurrency] = useState('CNY');
  const [includeSmall, setIncludeSmall] = useState(false);
  const [startDate, setStartDate] = useState(dayjs().subtract(30, 'day'));
  const [endDate, setEndDate] = useState(dayjs());
  const [platform, setPlatform] = useState('');
  const [limit, setLimit] = useState(50);
  const [days, setDays] = useState(30);
  const [assetCodes, setAssetCodes] = useState('');

  // 响应状态
  const [responses, setResponses] = useState<{ [key: string]: ApiResult | null }>({});
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // 预设测试场景
  const testScenarios: { [key: string]: TestScenario[] } = {
    asset: [
      {
        name: "完整资产概览",
        description: "获取所有资产信息，包括小额持仓",
        params: { base_currency: "CNY", include_small_amounts: true },
        expectedData: ["总资产价值", "平台分布", "资产类型分布", "持仓明细"]
      },
      {
        name: "主要资产(过滤小额)",
        description: "只看主要持仓，过滤掉小额资产",
        params: { base_currency: "USD", include_small_amounts: false },
        expectedData: ["核心持仓", "平台汇总", "货币换算"]
      },
      {
        name: "欧元计价视角",
        description: "以欧元为基准查看资产分布",
        params: { base_currency: "EUR", include_small_amounts: true },
        expectedData: ["EUR计价总值", "汇率影响分析"]
      }
    ],
    transaction: [
      {
        name: "近期交易活动",
        description: "查看最近7天的交易记录",
        params: {
          start_date: dayjs().subtract(7, 'day').format('YYYY-MM-DD'),
          end_date: dayjs().format('YYYY-MM-DD'),
          limit: 20
        },
        expectedData: ["买卖记录", "交易频率", "交易金额", "手续费统计"]
      },
      {
        name: "月度交易分析",
        description: "分析整个月的投资行为",
        params: {
          start_date: dayjs().startOf('month').format('YYYY-MM-DD'),
          end_date: dayjs().format('YYYY-MM-DD'),
          limit: 100
        },
        expectedData: ["月度投入", "交易模式", "平台偏好"]
      },
      {
        name: "特定平台分析",
        description: "分析某个平台的交易情况",
        params: {
          start_date: dayjs().subtract(90, 'day').format('YYYY-MM-DD'),
          end_date: dayjs().format('YYYY-MM-DD'),
          platform: "IBKR",
          limit: 50
        },
        expectedData: ["平台交易统计", "资产偏好", "交易成本"]
      }
    ],
    historical: [
      {
        name: "短期表现追踪",
        description: "查看最近7天的资产价值变化",
        params: { days: 7, asset_codes: "" },
        expectedData: ["每日净值", "波动幅度", "趋势方向"]
      },
      {
        name: "月度趋势分析",
        description: "分析过去30天的资产表现",
        params: { days: 30, asset_codes: "" },
        expectedData: ["月度收益率", "回撤分析", "波动率"]
      },
      {
        name: "特定资产追踪",
        description: "关注特定基金或股票的历史表现",
        params: { days: 60, asset_codes: "000001,110003,AAPL" },
        expectedData: ["个股表现", "基金净值", "相对强弱"]
      }
    ]
  };

  // 数据解读提示
  const dataInterpretation = {
    asset: {
      title: "📊 资产数据解读",
      tips: [
        "总资产价值反映当前财富规模",
        "平台分布显示风险分散程度",
        "资产类型分布反映投资策略",
        "小额资产可能包含分红或余额"
      ]
    },
    transaction: {
      title: "💰 交易数据解读",
      tips: [
        "交易频率反映投资风格（长期vs短期）",
        "买卖比例显示市场判断",
        "平台选择体现投资偏好",
        "手续费占比影响实际收益"
      ]
    },
    historical: {
      title: "📈 历史数据解读",
      tips: [
        "净值趋势显示投资效果",
        "波动率反映风险水平",
        "回撤幅度测试心理承受能力",
        "收益率需要年化处理才有意义"
      ]
    },
    market: {
      title: "🌍 市场数据解读",
      tips: [
        "汇率变化直接影响海外资产价值",
        "基金净值反映市场整体走势",
        "市场指标提供宏观判断依据"
      ]
    },
    dca: {
      title: "🔄 定投数据解读",
      tips: [
        "定投能平滑市场波动",
        "执行率反映计划执行情况",
        "成本均价显示定投效果",
        "收益需要长期视角评估"
      ]
    }
  };

  const apiCall = async (apiFunction: () => Promise<any>) => {
    const startTime = Date.now();

    try {
      const response = await apiFunction();
      const endTime = Date.now();
      const responseTime = endTime - startTime;

      return {
        success: true,
        data: response,
        responseTime,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误',
        responseTime,
        timestamp: new Date().toISOString()
      };
    }
  };

  const handleApiTest = async (testType: string, apiFunction: () => Promise<any>) => {
    setLoading(prev => ({ ...prev, [testType]: true }));

    try {
      const result = await apiCall(apiFunction, params);
      setResponses(prev => ({ ...prev, [testType]: result }));

      if (result.success) {
        message.success(`${testType}接口调用成功 (${result.responseTime}ms)`);
      } else {
        message.error(`${testType}接口调用失败: ${result.error || '未知错误'}`);
      }
    } catch (error) {
      setResponses(prev => ({
        ...prev,
        [testType]: { success: false, error: 'Network error', responseTime: 0 }
      }));
      message.error('网络请求失败');
    } finally {
      setLoading(prev => ({ ...prev, [testType]: false }));
    }
  };

  // 快速测试功能
  const quickTest = async (testType: string, scenario: TestScenario) => {
    // 自动设置参数
    if (testType === 'asset') {
      setBaseCurrency(scenario.params.base_currency || 'CNY');
      setIncludeSmall(scenario.params.include_small_amounts || false);
    } else if (testType === 'transaction') {
      if (scenario.params.start_date) setStartDate(dayjs(scenario.params.start_date));
      if (scenario.params.end_date) setEndDate(dayjs(scenario.params.end_date));
      setPlatform(scenario.params.platform || '');
      setLimit(scenario.params.limit || 50);
    } else if (testType === 'historical') {
      setDays(scenario.params.days || 30);
      setAssetCodes(scenario.params.asset_codes || '');
    }

    // 延迟执行以确保状态更新
    setTimeout(() => {
      const apiFunctionMap = {
        asset: () => aiAnalystAPI.getAssetData(apiKey, scenario.params),
        transaction: () => aiAnalystAPI.getTransactionData(apiKey, scenario.params),
        historical: () => aiAnalystAPI.getHistoricalData(apiKey, scenario.params)
      };
      handleApiTest(testType, apiFunctionMap[testType as keyof typeof apiFunctionMap]);
    }, 100);

    message.info(`正在执行场景: ${scenario.name}`);
  };

  // 批量测试
  const batchTest = async () => {
    message.info('开始批量测试所有接口...');
    const tests = [
      { type: 'health', apiFunction: () => aiAnalystAPI.getHealth(apiKey) },
      { type: 'market', apiFunction: () => aiAnalystAPI.getMarketData(apiKey) },
      { type: 'asset', apiFunction: () => aiAnalystAPI.getAssetData(apiKey, { base_currency: baseCurrency, include_small_amounts: includeSmall }) },
      { type: 'dca', apiFunction: () => aiAnalystAPI.getDCAData(apiKey) }
    ];

    for (const test of tests) {
      await handleApiTest(test.type, test.apiFunction);
      await new Promise(resolve => setTimeout(resolve, 500)); // 避免请求过于频繁
    }
    message.success('批量测试完成！');
  };

  // 复制功能
  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success(`${type}已复制到剪贴板`);
    });
  };

  // 导出数据
  const exportData = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${dayjs().format('YYYY-MM-DD_HH-mm-ss')}.json`;
    a.click();
    URL.revokeObjectURL(url);
    message.success('数据已导出');
  };

  // 自动刷新
  const toggleAutoRefresh = () => {
    if (autoRefresh) {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
      setAutoRefresh(false);
      message.info('自动刷新已关闭');
    } else {
      const interval = setInterval(() => {
        handleApiTest('health', '/health');
      }, 30000); // 30秒刷新一次健康检查
      setRefreshInterval(interval);
      setAutoRefresh(true);
      message.info('自动刷新已开启 (30秒间隔)');
    }
  };

  // API测试函数
  const testAssetData = () => {
    handleApiTest('asset', () => aiAnalystAPI.getAssetData(apiKey, {
      base_currency: baseCurrency,
      include_small_amounts: includeSmall
    }));
  };

  const testTransactionData = () => {
    handleApiTest('transaction', () => aiAnalystAPI.getTransactionData(apiKey, {
      start_date: startDate.format('YYYY-MM-DD'),
      end_date: endDate.format('YYYY-MM-DD'),
      platform: platform,
      limit: limit
    }));
  };

  const testHistoricalData = () => {
    handleApiTest('historical', () => aiAnalystAPI.getHistoricalData(apiKey, {
      days: days,
      asset_codes: assetCodes ? assetCodes.split(',').map(code => code.trim()) : []
    }));
  };

  const testMarketData = () => {
    handleApiTest('market', () => aiAnalystAPI.getMarketData(apiKey));
  };

  const testDCAData = () => {
    handleApiTest('dca', () => aiAnalystAPI.getDCAData(apiKey));
  };

  const testHealth = () => {
    handleApiTest('health', () => aiAnalystAPI.getHealth(apiKey));
  };

  // 增强的响应显示组件
  const ResponseDisplay = ({ result, type }: { result: ApiResult | null, type: string }) => {
    if (!result) return null;

    const interpretation = dataInterpretation[type as keyof typeof dataInterpretation];

    return (
      <div style={{ marginTop: 16 }}>
        {result.success ? (
          <Alert
            type="success"
            message={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>✅ 成功 (Status: {result.status}) {result.responseTime && `- ${result.responseTime}ms`}</span>
                <Space>
                  <Button
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(JSON.stringify(result.data, null, 2), 'API响应')}
                  >
                    复制
                  </Button>
                  <Button
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => exportData(result.data, `${type}_data`)}
                  >
                    导出
                  </Button>
                </Space>
              </div>
            }
            description={
              <Collapse size="small" style={{ marginTop: 8 }}>
                <Panel header="📋 响应数据" key="data">
                  <TextArea
                    value={JSON.stringify(result.data, null, 2)}
                    rows={8}
                    readOnly
                    style={{ fontFamily: 'monospace', fontSize: '12px' }}
                  />
                </Panel>
                {interpretation && (
                  <Panel header={interpretation.title} key="interpretation">
                    <List
                      size="small"
                      dataSource={interpretation.tips}
                      renderItem={(tip, index) => (
                        <List.Item>
                          <Text>
                            <Tag color="blue">{index + 1}</Tag>
                            {tip}
                          </Text>
                        </List.Item>
                      )}
                    />
                  </Panel>
                )}
              </Collapse>
            }
          />
        ) : (
          <Alert
            type="error"
            message={`❌ 错误 (Status: ${result.status}) ${result.responseTime && `- ${result.responseTime}ms`}`}
            description={
              <div>
                <TextArea
                  value={JSON.stringify(result.data, null, 2)}
                  rows={4}
                  readOnly
                  style={{ fontFamily: 'monospace', fontSize: '12px' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">💡 常见问题解决方法：</Text>
                  <ul style={{ marginTop: 4, fontSize: '12px' }}>
                    <li>检查API Key是否正确</li>
                    <li>确认后端服务是否启动</li>
                    <li>验证请求参数格式</li>
                    <li>查看浏览器网络面板获取详细错误</li>
                  </ul>
                </div>
              </div>
            }
          />
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 页头 */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '24px',
        borderRadius: '10px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Title level={1} style={{ color: 'white', margin: 0 }}>
              🤖 AI分析师数据API测试中心
            </Title>
            <Paragraph style={{ color: 'white', margin: '8px 0 0 0', fontSize: '16px' }}>
              专业的API测试工具 - 快速验证接口、分析数据结构、获取投资洞察
            </Paragraph>
          </div>
          <Space>
            <Tooltip title="自动刷新健康检查">
              <Switch
                checked={autoRefresh}
                onChange={toggleAutoRefresh}
                checkedChildren="自动"
                unCheckedChildren="手动"
              />
            </Tooltip>
            <Button
              type="primary"
              ghost
              icon={<ReloadOutlined />}
              onClick={batchTest}
            >
              批量测试
            </Button>
          </Space>
        </div>
      </div>

      {/* API Key配置和状态 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={16}>
          <Card style={{ background: '#fff3cd', borderColor: '#ffeaa7' }}>
            <Space size="large">
              <div>
                <Text strong>🔑 API Key:</Text>
                <Input
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  style={{ width: 200, marginLeft: 8 }}
                  placeholder="输入API密钥"
                />
              </div>
              <div>
                <Text type="secondary">测试密钥: </Text>
                <Tag color="green" style={{ cursor: 'pointer' }} onClick={() => setApiKey('ai_analyst_key_2024')}>
                  ai_analyst_key_2024
                </Tag>
                <Tag color="blue" style={{ cursor: 'pointer' }} onClick={() => setApiKey('demo_key_12345')}>
                  demo_key_12345
                </Tag>
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Text strong>🚀 快速操作</Text>
              <div style={{ marginTop: 8 }}>
                <Space>
                  <Button size="small" icon={<ClockCircleOutlined />} onClick={testHealth}>
                    健康检查
                  </Button>
                  <Button size="small" icon={<DollarOutlined />} onClick={testMarketData}>
                    市场数据
                  </Button>
                </Space>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* API测试卡片 */}
      <Row gutter={[16, 16]}>
        {/* 资产数据 */}
        <Col xs={24} lg={12}>
          <Card
            title={<><PieChartOutlined /> 资产数据</>}
            style={{ height: '100%' }}
            extra={
              <Tooltip title="查看测试场景">
                <QuestionCircleOutlined style={{ color: '#1890ff' }} />
              </Tooltip>
            }
          >
            <Tabs size="small" defaultActiveKey="params">
              <TabPane tab="参数设置" key="params">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text>基准货币:</Text>
                    <Select value={baseCurrency} onChange={setBaseCurrency} style={{ width: 120, marginLeft: 8 }}>
                      <Option value="CNY">🇨🇳 CNY</Option>
                      <Option value="USD">🇺🇸 USD</Option>
                      <Option value="EUR">🇪🇺 EUR</Option>
                      <Option value="GBP">🇬🇧 GBP</Option>
                    </Select>
                  </div>

                  <Checkbox checked={includeSmall} onChange={(e) => setIncludeSmall(e.target.checked)}>
                    📊 包含小额资产 (&lt; 100元等值)
                  </Checkbox>
                </Space>

                <div style={{ marginTop: 16 }}>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={testAssetData}
                    loading={loading.asset}
                    size="large"
                    style={{ width: '100%' }}
                  >
                    测试资产接口
                  </Button>
                </div>
              </TabPane>

              <TabPane tab="测试场景" key="scenarios">
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {testScenarios.asset.map((scenario, index) => (
                    <Card
                      key={index}
                      size="small"
                      style={{ marginBottom: 8 }}
                      hoverable
                      onClick={() => quickTest('asset', scenario)}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text strong>{scenario.name}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>{scenario.description}</Text>
                        </div>
                        <Button size="small" type="primary" ghost>运行</Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabPane>
            </Tabs>

            <ResponseDisplay result={responses.asset} type="asset" />
          </Card>
        </Col>

        {/* 交易数据 */}
        <Col xs={24} lg={12}>
          <Card
            title={<><DollarOutlined /> 交易数据</>}
            style={{ height: '100%' }}
            extra={
              <Space>
                <Tag color="processing">实时</Tag>
                <Tooltip title="查看测试场景">
                  <QuestionCircleOutlined style={{ color: '#1890ff' }} />
                </Tooltip>
              </Space>
            }
          >
            <Tabs size="small" defaultActiveKey="params">
              <TabPane tab="参数设置" key="params">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Row gutter={8}>
                    <Col span={12}>
                      <Text>开始日期:</Text>
                      <DatePicker
                        value={startDate}
                        onChange={(date) => setStartDate(date || dayjs())}
                        style={{ width: '100%', marginTop: 4 }}
                        size="small"
                      />
                    </Col>
                    <Col span={12}>
                      <Text>结束日期:</Text>
                      <DatePicker
                        value={endDate}
                        onChange={(date) => setEndDate(date || dayjs())}
                        style={{ width: '100%', marginTop: 4 }}
                        size="small"
                      />
                    </Col>
                  </Row>

                  <div>
                    <Text>交易平台:</Text>
                    <Select
                      value={platform}
                      onChange={setPlatform}
                      style={{ width: '100%', marginTop: 4 }}
                      placeholder="选择平台 (可选)"
                      allowClear
                      size="small"
                    >
                      <Option value="IBKR">📈 IBKR (盈透证券)</Option>
                      <Option value="Wise">💳 Wise</Option>
                      <Option value="PayPal">💰 PayPal</Option>
                      <Option value="OKX">🪙 OKX</Option>
                    </Select>
                  </div>

                  <div>
                    <Text>记录数量:</Text>
                    <Select value={limit} onChange={setLimit} style={{ width: '100%', marginTop: 4 }} size="small">
                      <Option value={10}>10条 (快速预览)</Option>
                      <Option value={50}>50条 (标准)</Option>
                      <Option value={100}>100条 (详细)</Option>
                      <Option value={500}>500条 (完整)</Option>
                    </Select>
                  </div>
                </Space>

                <div style={{ marginTop: 16 }}>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={testTransactionData}
                    loading={loading.transaction}
                    size="large"
                    style={{ width: '100%' }}
                  >
                    测试交易接口
                  </Button>
                </div>
              </TabPane>

              <TabPane tab="测试场景" key="scenarios">
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {testScenarios.transaction.map((scenario, index) => (
                    <Card
                      key={index}
                      size="small"
                      style={{ marginBottom: 8 }}
                      hoverable
                      onClick={() => quickTest('transaction', scenario)}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text strong>{scenario.name}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>{scenario.description}</Text>
                        </div>
                        <Button size="small" type="primary" ghost>运行</Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabPane>
            </Tabs>

            <ResponseDisplay result={responses.transaction} type="transaction" />
          </Card>
        </Col>

        {/* 历史数据 */}
        <Col xs={24} lg={12}>
          <Card
            title={<><PieChartOutlined /> 历史数据</>}
            style={{ height: '100%' }}
            extra={
              <Tag color="warning">趋势分析</Tag>
            }
          >
            <Tabs size="small" defaultActiveKey="params">
              <TabPane tab="参数设置" key="params">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text>查询天数:</Text>
                    <Select value={days} onChange={setDays} style={{ width: '100%', marginTop: 4 }} size="small">
                      <Option value={7}>📅 7天 (短期波动)</Option>
                      <Option value={30}>📆 30天 (月度趋势)</Option>
                      <Option value={90}>🗓️ 90天 (季度分析)</Option>
                      <Option value={365}>📋 365天 (年度回顾)</Option>
                    </Select>
                  </div>

                  <div>
                    <Text>资产代码:</Text>
                    <Input
                      placeholder="例如: 000001,110003,AAPL (用逗号分隔)"
                      value={assetCodes}
                      onChange={(e) => setAssetCodes(e.target.value)}
                      style={{ marginTop: 4 }}
                      size="small"
                    />
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        💡 留空获取所有资产，填入代码获取特定资产
                      </Text>
                    </div>
                  </div>
                </Space>

                <div style={{ marginTop: 16 }}>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={testHistoricalData}
                    loading={loading.historical}
                    size="large"
                    style={{ width: '100%' }}
                  >
                    测试历史接口
                  </Button>
                </div>
              </TabPane>

              <TabPane tab="测试场景" key="scenarios">
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {testScenarios.historical.map((scenario, index) => (
                    <Card
                      key={index}
                      size="small"
                      style={{ marginBottom: 8 }}
                      hoverable
                      onClick={() => quickTest('historical', scenario)}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text strong>{scenario.name}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>{scenario.description}</Text>
                        </div>
                        <Button size="small" type="primary" ghost>运行</Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabPane>
            </Tabs>

            <ResponseDisplay result={responses.historical} type="historical" />
          </Card>
        </Col>

        {/* 其他三个接口 */}
        <Col xs={24} lg={12}>
          <Row gutter={[8, 8]}>
            {/* 市场数据 */}
            <Col span={24}>
              <Card title="🌍 市场数据" size="small">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text>汇率、基金净值、市场指标</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>无需参数，实时获取市场环境数据</Text>
                  </div>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={testMarketData}
                    loading={loading.market}
                  >
                    测试
                  </Button>
                </div>
                <ResponseDisplay result={responses.market} type="market" />
              </Card>
            </Col>

            {/* 定投数据 */}
            <Col span={24}>
              <Card title="🔄 定投数据" size="small">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text>定投计划执行情况和效果分析</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>DCA策略数据，包含成本均价和收益统计</Text>
                  </div>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={testDCAData}
                    loading={loading.dca}
                  >
                    测试
                  </Button>
                </div>
                <ResponseDisplay result={responses.dca} type="dca" />
              </Card>
            </Col>

            {/* 健康检查 */}
            <Col span={24}>
              <Card title="🏥 健康检查" size="small">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text>API服务状态监控</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>验证服务可用性和响应时间 {autoRefresh && <Tag color="green">自动刷新</Tag>}</Text>
                  </div>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={testHealth}
                    loading={loading.health}
                  >
                    测试
                  </Button>
                </div>
                <ResponseDisplay result={responses.health} type="health" />
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      {/* 使用指南 */}
      <Card style={{ marginTop: '24px' }} title="📚 使用指南和提示">
        <Tabs defaultActiveKey="guide">
          <TabPane tab="🎯 测试流程" key="guide">
            <Row gutter={16}>
              <Col span={12}>
                <Title level={4}>⚡ 快速开始</Title>
                <ol style={{ lineHeight: '1.8' }}>
                  <li>🔑 确认API Key正确 (推荐使用测试密钥)</li>
                  <li>💡 点击"测试场景"查看预设参数组合</li>
                  <li>🚀 使用"批量测试"快速验证所有接口</li>
                  <li>📊 查看响应数据和解读提示</li>
                  <li>📋 使用复制/导出功能保存测试结果</li>
                </ol>
              </Col>
              <Col span={12}>
                <Title level={4}>🔧 高级功能</Title>
                <ul style={{ lineHeight: '1.8' }}>
                  <li>🔄 <strong>自动刷新</strong>: 监控API健康状态</li>
                  <li>📈 <strong>场景测试</strong>: 一键应用预设参数</li>
                  <li>⏱️ <strong>响应时间</strong>: 监控API性能</li>
                  <li>💾 <strong>数据导出</strong>: JSON格式保存结果</li>
                  <li>📋 <strong>数据解读</strong>: 理解API返回的业务含义</li>
                </ul>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="🔍 数据说明" key="data">
            <Row gutter={16}>
              <Col span={8}>
                <Title level={4}>📊 资产类数据</Title>
                <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <li><strong>资产数据</strong>: 当前持仓快照和汇总</li>
                  <li><strong>历史数据</strong>: 资产价值时间序列</li>
                  <li><strong>基准货币</strong>: 影响汇率换算</li>
                  <li><strong>小额资产</strong>: 通常指&lt;100元等值</li>
                </ul>
              </Col>
              <Col span={8}>
                <Title level={4}>💰 交易类数据</Title>
                <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <li><strong>交易数据</strong>: 买卖记录和统计</li>
                  <li><strong>定投数据</strong>: DCA计划和执行历史</li>
                  <li><strong>平台筛选</strong>: 分析特定平台行为</li>
                  <li><strong>时间范围</strong>: 控制数据查询范围</li>
                </ul>
              </Col>
              <Col span={8}>
                <Title level={4}>🌍 市场类数据</Title>
                <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <li><strong>市场数据</strong>: 汇率和基金净值</li>
                  <li><strong>健康检查</strong>: API服务状态</li>
                  <li><strong>实时性</strong>: 数据更新频率</li>
                  <li><strong>依赖关系</strong>: 外部数据源影响</li>
                </ul>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="❓ 常见问题" key="faq">
            <Collapse>
              <Panel header="🔑 API Key验证失败怎么办？" key="1">
                <p>1. 检查API Key是否正确输入，注意大小写</p>
                <p>2. 确认使用测试密钥: <code>ai_analyst_key_2024</code> 或 <code>demo_key_12345</code></p>
                <p>3. 联系后端开发者确认密钥配置</p>
              </Panel>
              <Panel header="🌐 网络连接错误怎么解决？" key="2">
                <p>1. 确认后端服务已启动 (默认端口8000)</p>
                <p>2. 检查防火墙和网络设置</p>
                <p>3. 验证API基础URL配置: <code>http://localhost:8000</code></p>
              </Panel>
              <Panel header="📊 数据为空是什么原因？" key="3">
                <p>1. 数据库可能没有相关记录</p>
                <p>2. 查询条件过于严格 (如时间范围太小)</p>
                <p>3. 尝试调整参数或使用测试场景</p>
              </Panel>
              <Panel header="⚡ 如何提高测试效率？" key="4">
                <p>1. 使用"测试场景"功能快速设置参数</p>
                <p>2. 开启自动刷新监控服务状态</p>
                <p>3. 使用批量测试验证多个接口</p>
                <p>4. 导出测试结果用于分析对比</p>
              </Panel>
            </Collapse>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default AIAnalystTest;