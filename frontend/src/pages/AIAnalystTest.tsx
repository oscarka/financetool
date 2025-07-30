import React, { useState } from 'react';
import { Card, Button, Input, Select, Checkbox, DatePicker, Space, Typography, Row, Col, Alert, Spin } from 'antd';
import { PlayCircleOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface ApiResult {
  success: boolean;
  data: any;
  status: number;
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
  const [responses, setResponses] = useState<{[key: string]: ApiResult | null}>({});
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});

  const apiCall = async (endpoint: string, params: any = {}) => {
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
      return { success: response.ok, data, status: response.status };
    } catch (error: any) {
      return { success: false, data: { error: error.message }, status: 0 };
    }
  };

  const handleApiTest = async (testType: string, endpoint: string, params: any = {}) => {
    setLoading(prev => ({ ...prev, [testType]: true }));
    
    try {
      const result = await apiCall(endpoint, params);
      setResponses(prev => ({ ...prev, [testType]: result }));
    } catch (error) {
      setResponses(prev => ({ 
        ...prev, 
        [testType]: { success: false, data: { error: 'Network error' }, status: 0 } 
      }));
    } finally {
      setLoading(prev => ({ ...prev, [testType]: false }));
    }
  };

  const testAssetData = () => {
    handleApiTest('asset', '/asset-data', {
      base_currency: baseCurrency,
      include_small_amounts: includeSmall
    });
  };

  const testTransactionData = () => {
    handleApiTest('transaction', '/transaction-data', {
      start_date: startDate.format('YYYY-MM-DD'),
      end_date: endDate.format('YYYY-MM-DD'),
      platform: platform,
      limit: limit
    });
  };

  const testHistoricalData = () => {
    handleApiTest('historical', '/historical-data', {
      days: days,
      asset_codes: assetCodes
    });
  };

  const testMarketData = () => {
    handleApiTest('market', '/market-data');
  };

  const testDCAData = () => {
    handleApiTest('dca', '/dca-data');
  };

  const testHealth = () => {
    handleApiTest('health', '/health');
  };

  const ResponseDisplay = ({ result, type }: { result: ApiResult | null, type: string }) => {
    if (!result) return null;

    return (
      <div style={{ marginTop: 16 }}>
        {result.success ? (
          <Alert
            type="success"
            message={`✅ 成功 (Status: ${result.status})`}
            description={
              <TextArea
                value={JSON.stringify(result.data, null, 2)}
                rows={8}
                readOnly
                style={{ fontFamily: 'monospace', fontSize: '12px' }}
              />
            }
          />
        ) : (
          <Alert
            type="error"
            message={`❌ 错误 (Status: ${result.status})`}
            description={
              <TextArea
                value={JSON.stringify(result.data, null, 2)}
                rows={4}
                readOnly
                style={{ fontFamily: 'monospace', fontSize: '12px' }}
              />
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
        <Title level={1} style={{ color: 'white', margin: 0 }}>
          🤖 AI分析师数据API测试
        </Title>
        <Paragraph style={{ color: 'white', margin: '8px 0 0 0', fontSize: '16px' }}>
          内部测试工具 - 快速验证API接口和数据结构
        </Paragraph>
      </div>

      {/* API Key配置 */}
      <Card style={{ marginBottom: '24px', background: '#fff3cd', borderColor: '#ffeaa7' }}>
        <Space>
          <Text strong>API Key:</Text>
          <Input
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            style={{ width: 200 }}
            placeholder="输入API密钥"
          />
          <Text type="secondary">测试用: ai_analyst_key_2024 或 demo_key_12345</Text>
        </Space>
      </Card>

      {/* API测试卡片 */}
      <Row gutter={[16, 16]}>
        {/* 资产数据 */}
        <Col xs={24} md={12} lg={8}>
          <Card title="📊 资产数据" style={{ height: '100%' }}>
            <Paragraph>获取当前持仓快照和汇总信息</Paragraph>
            
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>基准货币:</Text>
                <Select value={baseCurrency} onChange={setBaseCurrency} style={{ width: 100, marginLeft: 8 }}>
                  <Option value="CNY">CNY</Option>
                  <Option value="USD">USD</Option>
                  <Option value="EUR">EUR</Option>
                </Select>
              </div>
              
              <Checkbox checked={includeSmall} onChange={(e) => setIncludeSmall(e.target.checked)}>
                包含小额资产
              </Checkbox>
            </Space>

            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={testAssetData}
              loading={loading.asset}
              style={{ marginTop: 16 }}
            >
              测试接口
            </Button>

            <ResponseDisplay result={responses.asset} type="asset" />
          </Card>
        </Col>

        {/* 交易数据 */}
        <Col xs={24} md={12} lg={8}>
          <Card title="💰 交易数据" style={{ height: '100%' }}>
            <Paragraph>获取交易历史记录和统计</Paragraph>
            
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>开始日期:</Text>
                <DatePicker 
                  value={startDate} 
                  onChange={(date) => setStartDate(date || dayjs())}
                  style={{ width: '100%' }}
                />
              </div>
              
              <div>
                <Text>结束日期:</Text>
                <DatePicker 
                  value={endDate} 
                  onChange={(date) => setEndDate(date || dayjs())}
                  style={{ width: '100%' }}
                />
              </div>
              
              <Input
                placeholder="平台 (可选)"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
              />
              
              <div>
                <Text>限制条数:</Text>
                <Input
                  type="number"
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  style={{ width: 80, marginLeft: 8 }}
                />
              </div>
            </Space>

            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={testTransactionData}
              loading={loading.transaction}
              style={{ marginTop: 16 }}
            >
              测试接口
            </Button>

            <ResponseDisplay result={responses.transaction} type="transaction" />
          </Card>
        </Col>

        {/* 历史数据 */}
        <Col xs={24} md={12} lg={8}>
          <Card title="📈 历史数据" style={{ height: '100%' }}>
            <Paragraph>获取资产价值和净值历史</Paragraph>
            
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>天数:</Text>
                <Input
                  type="number"
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  style={{ width: 80, marginLeft: 8 }}
                />
              </div>
              
              <Input
                placeholder="资产代码 (逗号分隔)"
                value={assetCodes}
                onChange={(e) => setAssetCodes(e.target.value)}
              />
            </Space>

            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={testHistoricalData}
              loading={loading.historical}
              style={{ marginTop: 16 }}
            >
              测试接口
            </Button>

            <ResponseDisplay result={responses.historical} type="historical" />
          </Card>
        </Col>

        {/* 市场数据 */}
        <Col xs={24} md={12} lg={8}>
          <Card title="🌍 市场数据" style={{ height: '100%' }}>
            <Paragraph>获取汇率和市场环境信息</Paragraph>

            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={testMarketData}
              loading={loading.market}
              style={{ marginTop: 16 }}
            >
              测试接口
            </Button>

            <ResponseDisplay result={responses.market} type="market" />
          </Card>
        </Col>

        {/* 定投数据 */}
        <Col xs={24} md={12} lg={8}>
          <Card title="🔄 定投数据" style={{ height: '100%' }}>
            <Paragraph>获取定投计划和执行历史</Paragraph>

            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={testDCAData}
              loading={loading.dca}
              style={{ marginTop: 16 }}
            >
              测试接口
            </Button>

            <ResponseDisplay result={responses.dca} type="dca" />
          </Card>
        </Col>

        {/* 健康检查 */}
        <Col xs={24} md={12} lg={8}>
          <Card title="🏥 健康检查" style={{ height: '100%' }}>
            <Paragraph>验证API服务状态</Paragraph>

            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={testHealth}
              loading={loading.health}
              style={{ marginTop: 16 }}
            >
              测试接口
            </Button>

            <ResponseDisplay result={responses.health} type="health" />
          </Card>
        </Col>
      </Row>

      {/* 说明文档 */}
      <Card style={{ marginTop: '24px' }} title="📚 使用说明">
        <Row gutter={16}>
          <Col span={12}>
            <Title level={4}>🎯 测试流程</Title>
            <ol>
              <li>确认API Key正确</li>
              <li>选择要测试的接口</li>
              <li>调整相关参数</li>
              <li>点击"测试接口"按钮</li>
              <li>查看返回的数据结构</li>
            </ol>
          </Col>
          <Col span={12}>
            <Title level={4}>🔍 数据说明</Title>
            <ul>
              <li><strong>资产数据</strong>: 当前持仓快照和汇总</li>
              <li><strong>交易数据</strong>: 历史交易记录和统计</li>
              <li><strong>历史数据</strong>: 资产价值时间序列</li>
              <li><strong>市场数据</strong>: 汇率和基金净值</li>
              <li><strong>定投数据</strong>: 定投计划和执行历史</li>
            </ul>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default AIAnalystTest;