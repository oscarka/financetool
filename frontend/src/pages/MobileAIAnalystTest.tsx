import React, { useState } from 'react';
import { Card, Button, Input, Select, Checkbox, DatePicker, Space, Typography, Alert, Tag, Collapse, Tabs, Switch, Tooltip, message, List, Divider } from 'antd';
import { PlayCircleOutlined, CopyOutlined, ReloadOutlined, QuestionCircleOutlined, ClockCircleOutlined, DollarOutlined, PieChartOutlined, RobotOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Panel } = Collapse;
const { TabPane } = Tabs;

interface ApiResult {
  success: boolean;
  data: any;
  status: number;
  responseTime?: number;
}

interface TestScenario {
  name: string;
  description: string;
  params: any;
}

const MobileAIAnalystTest: React.FC = () => {
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
  const [responses, setResponses] = useState<{[key: string]: ApiResult | null}>({});
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});
  const [autoRefresh, setAutoRefresh] = useState(false);

  // 移动端预设场景 (简化版)
  const mobileScenarios = {
    asset: [
      { name: "完整资产", description: "所有持仓", params: { base_currency: "CNY", include_small_amounts: true } },
      { name: "主要资产", description: "过滤小额", params: { base_currency: "USD", include_small_amounts: false } }
    ],
    transaction: [
      { name: "近7天", description: "最近交易", params: { start_date: dayjs().subtract(7, 'day').format('YYYY-MM-DD'), end_date: dayjs().format('YYYY-MM-DD'), limit: 20 } },
      { name: "本月", description: "月度交易", params: { start_date: dayjs().startOf('month').format('YYYY-MM-DD'), end_date: dayjs().format('YYYY-MM-DD'), limit: 50 } }
    ],
    historical: [
      { name: "7天趋势", description: "短期波动", params: { days: 7 } },
      { name: "30天趋势", description: "月度分析", params: { days: 30 } }
    ]
  };

  const apiCall = async (endpoint: string, params: any = {}) => {
    const startTime = Date.now();
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const url = new URL(`${baseUrl}/api/v1/ai-analyst${endpoint}`);
    
    Object.keys(params).forEach(key => {
      if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
        url.searchParams.append(key, params[key]);
      }
    });

    try {
      const response = await fetch(url.toString(), {
        headers: {
          'X-API-Key': apiKey,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      const responseTime = Date.now() - startTime;
      
      return { 
        success: response.ok, 
        data, 
        status: response.status,
        responseTime 
      };
    } catch (error: any) {
      return { 
        success: false, 
        data: { error: error.message }, 
        status: 0,
        responseTime: Date.now() - startTime
      };
    }
  };

  const handleApiTest = async (testType: string, endpoint: string, params: any = {}) => {
    setLoading(prev => ({ ...prev, [testType]: true }));
    
    try {
      const result = await apiCall(endpoint, params);
      setResponses(prev => ({ ...prev, [testType]: result }));
      
      if (result.success) {
        message.success(`${testType} 成功 (${result.responseTime}ms)`);
      } else {
        message.error(`${testType} 失败: ${result.data.error || '未知错误'}`);
      }
    } catch (error) {
      setResponses(prev => ({ 
        ...prev, 
        [testType]: { success: false, data: { error: 'Network error' }, status: 0 } 
      }));
      message.error('网络请求失败');
    } finally {
      setLoading(prev => ({ ...prev, [testType]: false }));
    }
  };

  // 快速测试
  const quickTest = (testType: string, scenario: TestScenario) => {
    if (testType === 'asset') {
      setBaseCurrency(scenario.params.base_currency || 'CNY');
      setIncludeSmall(scenario.params.include_small_amounts || false);
    } else if (testType === 'transaction') {
      if (scenario.params.start_date) setStartDate(dayjs(scenario.params.start_date));
      if (scenario.params.end_date) setEndDate(dayjs(scenario.params.end_date));
      setLimit(scenario.params.limit || 50);
    } else if (testType === 'historical') {
      setDays(scenario.params.days || 30);
    }

    setTimeout(() => {
      const endpointMap = {
        asset: '/asset-data',
        transaction: '/transaction-data', 
        historical: '/historical-data'
      };
      handleApiTest(testType, endpointMap[testType as keyof typeof endpointMap], scenario.params);
    }, 100);

    message.info(`运行: ${scenario.name}`);
  };

  // 复制功能
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success('已复制');
    });
  };

  // 移动端响应显示组件
  const MobileResponseDisplay = ({ result, type }: { result: ApiResult | null, type: string }) => {
    if (!result) return null;

    return (
      <div style={{ marginTop: 12 }}>
        {result.success ? (
          <Alert
            type="success"
            message={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px' }}>✅ 成功 ({result.responseTime}ms)</span>
                <Button 
                  size="small" 
                  icon={<CopyOutlined />}
                  onClick={() => copyToClipboard(JSON.stringify(result.data, null, 2))}
                >
                  复制
                </Button>
              </div>
            }
            description={
              <Collapse size="small" style={{ marginTop: 8 }}>
                <Panel header="📋 响应数据" key="data">
                  <TextArea
                    value={JSON.stringify(result.data, null, 2)}
                    rows={6}
                    readOnly
                    style={{ fontFamily: 'monospace', fontSize: '11px' }}
                  />
                </Panel>
              </Collapse>
            }
          />
        ) : (
          <Alert
            type="error"
            message={`❌ 错误 (${result.status})`}
            description={
              <TextArea
                value={JSON.stringify(result.data, null, 2)}
                rows={3}
                readOnly
                style={{ fontFamily: 'monospace', fontSize: '11px' }}
              />
            }
          />
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: '16px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 移动端页头 */}
      <Card style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        marginBottom: '16px',
        borderRadius: '12px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <RobotOutlined style={{ fontSize: '32px', marginBottom: '8px' }} />
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            AI分析师API测试
          </Title>
          <Text style={{ color: 'white', fontSize: '14px' }}>
            移动端专用测试工具
          </Text>
        </div>
      </Card>

      {/* API Key 快速配置 */}
      <Card style={{ marginBottom: '16px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>🔑 API Key</Text>
            <Input
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              style={{ marginTop: 4 }}
              placeholder="输入API密钥"
              size="small"
            />
          </div>
          <Space wrap>
            <Tag 
              color="green" 
              style={{ cursor: 'pointer' }} 
              onClick={() => setApiKey('ai_analyst_key_2024')}
            >
              测试密钥1
            </Tag>
            <Tag 
              color="blue" 
              style={{ cursor: 'pointer' }} 
              onClick={() => setApiKey('demo_key_12345')}
            >
              测试密钥2
            </Tag>
          </Space>
        </Space>
      </Card>

      {/* 快速操作 */}
      <Card style={{ marginBottom: '16px' }}>
        <div style={{ textAlign: 'center' }}>
          <Text strong>🚀 快速测试</Text>
          <div style={{ marginTop: 8 }}>
            <Space wrap>
              <Button 
                size="small" 
                icon={<ClockCircleOutlined />} 
                onClick={() => handleApiTest('health', '/health')}
                loading={loading.health}
              >
                健康检查
              </Button>
              <Button 
                size="small" 
                icon={<DollarOutlined />} 
                onClick={() => handleApiTest('market', '/market-data')}
                loading={loading.market}
              >
                市场数据
              </Button>
              <Button 
                size="small" 
                icon={<PieChartOutlined />} 
                onClick={() => handleApiTest('dca', '/dca-data')}
                loading={loading.dca}
              >
                定投数据
              </Button>
            </Space>
          </div>
        </div>
      </Card>

      {/* 资产数据测试 */}
      <Card style={{ marginBottom: '16px' }} title="📊 资产数据">
        <Tabs size="small" defaultActiveKey="params">
          <TabPane tab="参数" key="params">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>基准货币:</Text>
                <Select value={baseCurrency} onChange={setBaseCurrency} style={{ width: '100%', marginTop: 4 }} size="small">
                  <Option value="CNY">🇨🇳 CNY</Option>
                  <Option value="USD">🇺🇸 USD</Option>
                  <Option value="EUR">🇪🇺 EUR</Option>
                </Select>
              </div>
              
              <Checkbox 
                checked={includeSmall} 
                onChange={(e) => setIncludeSmall(e.target.checked)}
                style={{ fontSize: '14px' }}
              >
                包含小额资产
              </Checkbox>

              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />}
                onClick={() => handleApiTest('asset', '/asset-data', {
                  base_currency: baseCurrency,
                  include_small_amounts: includeSmall
                })}
                loading={loading.asset}
                style={{ width: '100%' }}
                size="small"
              >
                测试资产接口
              </Button>
            </Space>
          </TabPane>
          
          <TabPane tab="场景" key="scenarios">
            <Space direction="vertical" style={{ width: '100%' }}>
              {mobileScenarios.asset.map((scenario, index) => (
                <Card 
                  key={index} 
                  size="small" 
                  hoverable
                  onClick={() => quickTest('asset', scenario)}
                  style={{ cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong style={{ fontSize: '14px' }}>{scenario.name}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>{scenario.description}</Text>
                    </div>
                    <Button size="small" type="primary" ghost>运行</Button>
                  </div>
                </Card>
              ))}
            </Space>
          </TabPane>
        </Tabs>

        <MobileResponseDisplay result={responses.asset} type="asset" />
      </Card>

      {/* 交易数据测试 */}
      <Card style={{ marginBottom: '16px' }} title="💰 交易数据">
        <Tabs size="small" defaultActiveKey="params">
          <TabPane tab="参数" key="params">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>开始日期:</Text>
                <DatePicker 
                  value={startDate} 
                  onChange={(date) => setStartDate(date || dayjs())}
                  style={{ width: '100%', marginTop: 4 }}
                  size="small"
                />
              </div>
              
              <div>
                <Text>结束日期:</Text>
                <DatePicker 
                  value={endDate} 
                  onChange={(date) => setEndDate(date || dayjs())}
                  style={{ width: '100%', marginTop: 4 }}
                  size="small"
                />
              </div>
              
              <div>
                <Text>平台:</Text>
                <Select
                  value={platform}
                  onChange={setPlatform}
                  style={{ width: '100%', marginTop: 4 }}
                  placeholder="选择平台 (可选)"
                  allowClear
                  size="small"
                >
                  <Option value="IBKR">IBKR</Option>
                  <Option value="Wise">Wise</Option>
                  <Option value="PayPal">PayPal</Option>
                  <Option value="OKX">OKX</Option>
                </Select>
              </div>

              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />}
                onClick={() => handleApiTest('transaction', '/transaction-data', {
                  start_date: startDate.format('YYYY-MM-DD'),
                  end_date: endDate.format('YYYY-MM-DD'),
                  platform: platform,
                  limit: limit
                })}
                loading={loading.transaction}
                style={{ width: '100%' }}
                size="small"
              >
                测试交易接口
              </Button>
            </Space>
          </TabPane>
          
          <TabPane tab="场景" key="scenarios">
            <Space direction="vertical" style={{ width: '100%' }}>
              {mobileScenarios.transaction.map((scenario, index) => (
                <Card 
                  key={index} 
                  size="small" 
                  hoverable
                  onClick={() => quickTest('transaction', scenario)}
                  style={{ cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong style={{ fontSize: '14px' }}>{scenario.name}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>{scenario.description}</Text>
                    </div>
                    <Button size="small" type="primary" ghost>运行</Button>
                  </div>
                </Card>
              ))}
            </Space>
          </TabPane>
        </Tabs>

        <MobileResponseDisplay result={responses.transaction} type="transaction" />
      </Card>

      {/* 历史数据测试 */}
      <Card style={{ marginBottom: '16px' }} title="📈 历史数据">
        <Tabs size="small" defaultActiveKey="params">
          <TabPane tab="参数" key="params">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>查询天数:</Text>
                <Select value={days} onChange={setDays} style={{ width: '100%', marginTop: 4 }} size="small">
                  <Option value={7}>7天</Option>
                  <Option value={30}>30天</Option>
                  <Option value={90}>90天</Option>
                </Select>
              </div>
              
              <div>
                <Text>资产代码:</Text>
                <Input
                  placeholder="例如: 000001,AAPL (逗号分隔)"
                  value={assetCodes}
                  onChange={(e) => setAssetCodes(e.target.value)}
                  style={{ marginTop: 4 }}
                  size="small"
                />
              </div>

              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />}
                onClick={() => handleApiTest('historical', '/historical-data', {
                  days: days,
                  asset_codes: assetCodes
                })}
                loading={loading.historical}
                style={{ width: '100%' }}
                size="small"
              >
                测试历史接口
              </Button>
            </Space>
          </TabPane>
          
          <TabPane tab="场景" key="scenarios">
            <Space direction="vertical" style={{ width: '100%' }}>
              {mobileScenarios.historical.map((scenario, index) => (
                <Card 
                  key={index} 
                  size="small" 
                  hoverable
                  onClick={() => quickTest('historical', scenario)}
                  style={{ cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong style={{ fontSize: '14px' }}>{scenario.name}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>{scenario.description}</Text>
                    </div>
                    <Button size="small" type="primary" ghost>运行</Button>
                  </div>
                </Card>
              ))}
            </Space>
          </TabPane>
        </Tabs>

        <MobileResponseDisplay result={responses.historical} type="historical" />
      </Card>

      {/* 其他接口快速显示结果 */}
      {responses.health && (
        <Card style={{ marginBottom: '16px' }} title="🏥 健康检查结果">
          <MobileResponseDisplay result={responses.health} type="health" />
        </Card>
      )}

      {responses.market && (
        <Card style={{ marginBottom: '16px' }} title="🌍 市场数据结果">
          <MobileResponseDisplay result={responses.market} type="market" />
        </Card>
      )}

      {responses.dca && (
        <Card style={{ marginBottom: '16px' }} title="🔄 定投数据结果">
          <MobileResponseDisplay result={responses.dca} type="dca" />
        </Card>
      )}

      {/* 使用提示 */}
      <Card title="💡 使用提示">
        <Collapse size="small">
          <Panel header="快速开始" key="1">
            <ol style={{ fontSize: '14px', paddingLeft: '16px' }}>
              <li>选择或输入API Key</li>
              <li>点击"快速测试"验证连接</li>
              <li>使用"场景"快速设置参数</li>
              <li>查看响应数据</li>
            </ol>
          </Panel>
          <Panel header="数据说明" key="2">
            <ul style={{ fontSize: '14px', paddingLeft: '16px' }}>
              <li><strong>资产数据</strong>: 当前持仓和汇总</li>
              <li><strong>交易数据</strong>: 历史交易记录</li>
              <li><strong>历史数据</strong>: 价值时间序列</li>
              <li><strong>市场数据</strong>: 汇率和净值</li>
            </ul>
          </Panel>
        </Collapse>
      </Card>
    </div>
  );
};

export default MobileAIAnalystTest;