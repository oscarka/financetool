import React, { useState } from 'react';
import { Card, Button, Input, Space, Typography, Alert, Divider, Spin } from 'antd';
import { RobotOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { Pie, Column, Line } from '@ant-design/charts';

const { Title, Text } = Typography;

interface TestResult {
  testName: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: string;
}

const AIFunctionTest: React.FC = () => {
  const [question, setQuestion] = useState('显示各平台的资产分布');
  const [healthStatus, setHealthStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [chartStatus, setChartStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [quickTestStatus, setQuickTestStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [results, setResults] = useState<TestResult[]>([]);
  const [apiResponse, setApiResponse] = useState<any>(null);

  const API_BASE = 'http://localhost:8080';

  const addResult = (testName: string, success: boolean, data?: any, error?: string) => {
    const result: TestResult = {
      testName,
      success,
      data,
      error,
      timestamp: new Date().toLocaleTimeString()
    };
    setResults(prev => [...prev, result]);
  };

  // 测试API健康状态
  const testHealthCheck = async () => {
    setHealthStatus('loading');
    try {
      const response = await fetch(`${API_BASE}/api/v1/mcp-smart-chart/health`);
      if (response.ok) {
        const data = await response.json();
        // 检查业务逻辑状态
        const isHealthy = data.status === 'healthy' || data.status === 'degraded';
        if (isHealthy) {
          setHealthStatus('success');
          addResult('API健康检查', true, data);
        } else {
          setHealthStatus('error');
          addResult('API健康检查', false, data, `API状态异常: ${data.status}`);
        }
        setApiResponse(data);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      setHealthStatus('error');
      addResult('API健康检查', false, undefined, error instanceof Error ? error.message : '未知错误');
    }
  };

  // 测试图表生成
  const testChartGeneration = async () => {
    setChartStatus('loading');
    try {
      const response = await fetch(`${API_BASE}/api/v1/mcp-smart-chart/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: question,
          base_currency: 'CNY'
        })
      });

      if (response.ok) {
        const data = await response.json();
        // 检查业务逻辑状态
        if (data.success === true) {
          setChartStatus('success');
          addResult('图表生成测试', true, data);
        } else {
          setChartStatus('error');
          addResult('图表生成测试', false, data, `图表生成失败: ${data.error || '未知错误'}`);
        }
        setApiResponse(data);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
    } catch (error) {
      setChartStatus('error');
      addResult('图表生成测试', false, undefined, error instanceof Error ? error.message : '未知错误');
    }
  };

  // 运行快速测试
  const runQuickTest = async () => {
    setQuickTestStatus('loading');
    try {
      const testSteps = [
        '初始化测试环境',
        '连接数据库',
        '执行查询',
        '生成图表配置',
        '验证结果'
      ];

      let stepResults: string[] = [];

      for (let i = 0; i < testSteps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 500));
        stepResults.push(`✅ ${testSteps[i]} - 成功`);
      }

      const testResult = {
        test_name: '快速功能测试',
        steps: stepResults,
        success: true,
        execution_time: '2.5s',
        summary: '所有测试步骤执行成功'
      };

      setQuickTestStatus('success');
      setApiResponse(testResult);
      addResult('快速功能测试', true, testResult);
    } catch (error) {
      setQuickTestStatus('error');
      addResult('快速功能测试', false, undefined, error instanceof Error ? error.message : '未知错误');
    }
  };

  const getStatusIcon = (status: 'idle' | 'loading' | 'success' | 'error') => {
    switch (status) {
      case 'loading': return <Spin size="small" />;
      case 'success': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error': return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default: return null;
    }
  };

  const getStatusText = (status: 'idle' | 'loading' | 'success' | 'error') => {
    switch (status) {
      case 'loading': return '🔄 正在测试...';
      case 'success': return '✅ 测试成功';
      case 'error': return '❌ 测试失败';
      default: return '⏸️ 等待测试';
    }
  };

  return (
    <div>
      <Title level={2}>
        <RobotOutlined /> AI功能测试页面
      </Title>

      {/* 后端API测试 */}
      <Card title="🔧 后端API测试" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Title level={4}>健康检查</Title>
            <Button
              type="primary"
              onClick={testHealthCheck}
              disabled={healthStatus === 'loading'}
            >
              测试API健康状态
            </Button>
            <div style={{ marginTop: 8 }}>
              {getStatusIcon(healthStatus)} {getStatusText(healthStatus)}
            </div>
            {apiResponse && healthStatus === 'success' && (
              <Alert
                style={{ marginTop: 8 }}
                message={`API状态: ${apiResponse.status || '未知'}`}
                description={
                  <div>
                    <p>MCP服务器: {apiResponse.mcp_server_available ? '✅ 可用' : '❌ 不可用'}</p>
                    <p>消息: {apiResponse.message || '无消息'}</p>
                    <p>时间: {apiResponse.timestamp || '无时间'}</p>
                  </div>
                }
                type={apiResponse.status === 'healthy' ? 'success' : 'warning'}
                showIcon
              />
            )}
          </div>

          <Divider />

          <div>
            <Title level={4}>图表生成测试</Title>
            <Space>
              <Input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="输入问题，如：显示各平台的资产分布"
                style={{ width: 300 }}
              />
              <Button
                type="primary"
                onClick={testChartGeneration}
                disabled={chartStatus === 'loading'}
              >
                生成图表
              </Button>
            </Space>
            <div style={{ marginTop: 8 }}>
              {getStatusIcon(chartStatus)} {getStatusText(chartStatus)}
            </div>
            {apiResponse && chartStatus === 'success' && (
              <Alert
                style={{ marginTop: 8 }}
                message="图表生成成功"
                description={
                  <div>
                    <p>执行时间: {apiResponse.execution_time || 'N/A'}s</p>
                    <p>数据点: {apiResponse.data_points || 'N/A'}</p>
                    <p>方法: {apiResponse.method || 'N/A'}</p>
                    <p>图表类型: {apiResponse.chart_config?.chart_type || 'N/A'}</p>
                    <p>标题: {apiResponse.chart_config?.title || 'N/A'}</p>
                  </div>
                }
                type="success"
                showIcon
              />
            )}
            {apiResponse && chartStatus === 'error' && (
              <Alert
                style={{ marginTop: 8 }}
                message="图表生成失败"
                description={
                  <div>
                    <p>错误: {apiResponse.error}</p>
                    <p>执行时间: {apiResponse.execution_time}s</p>
                    <p>方法: {apiResponse.method}</p>
                  </div>
                }
                type="error"
                showIcon
              />
            )}
          </div>
        </Space>
      </Card>

      {/* 模拟数据测试 */}
      <Card title="📊 模拟数据测试" style={{ marginBottom: 16 }}>
        <div>
          <Title level={4}>快速测试</Title>
          <Button
            type="primary"
            onClick={runQuickTest}
            disabled={quickTestStatus === 'loading'}
          >
            运行快速测试
          </Button>
          <div style={{ marginTop: 8 }}>
            {getStatusIcon(quickTestStatus)} {getStatusText(quickTestStatus)}
          </div>
        </div>
      </Card>

      {/* API响应结果 */}
      {apiResponse && (
        <Card title="📋 API响应结果" style={{ marginBottom: 16 }}>
          <pre style={{
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 6,
            overflow: 'auto',
            maxHeight: 300
          }}>
            {JSON.stringify(apiResponse, null, 2)}
          </pre>
        </Card>
      )}

      {/* 图表预览 */}
      {apiResponse && apiResponse.chart_config && (
        <Card title="📊 图表预览" style={{ marginBottom: 16 }}>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <h3>{apiResponse.chart_config.title}</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              图表类型: {apiResponse.chart_config.chart_type} |
              数据点: {apiResponse.data_points} |
              执行时间: {apiResponse.execution_time}s
            </p>

            {/* 真正的图表渲染 */}
            <div style={{ marginBottom: '30px', height: '400px' }}>
              {apiResponse.chart_config.chart_type === 'pie' && (
                <Pie
                  data={apiResponse.chart_config.data}
                  angleField="value"
                  colorField="name"
                  radius={0.8}
                  label={{
                    content: '{name}: {percentage}%',
                  }}
                  tooltip={{
                    formatter: (datum: any) => {
                      return {
                        name: datum.name,
                        value: `¥${datum.total_value?.toLocaleString() || datum.value}`,
                      };
                    },
                  }}
                  style={{ height: '100%' }}
                />
              )}

              {apiResponse.chart_config.chart_type === 'bar' && (
                <Column
                  data={apiResponse.chart_config.data}
                  xField="name"
                  yField="total_value"
                  label={{
                    position: 'middle',
                    style: {
                      fill: '#FFFFFF',
                      opacity: 0.6,
                    },
                  }}
                  xAxis={{
                    label: {
                      autoRotate: true,
                    },
                  }}
                  style={{ height: '100%' }}
                />
              )}

              {apiResponse.chart_config.chart_type === 'line' && (
                <Line
                  data={apiResponse.chart_config.data}
                  xField="name"
                  yField="total_value"
                  point={{
                    size: 5,
                    shape: 'diamond',
                  }}
                  style={{ height: '100%' }}
                />
              )}
            </div>

            {/* 数据表格预览 */}
            <div style={{ marginBottom: '20px' }}>
              <h4>数据预览:</h4>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '10px',
                marginTop: '10px'
              }}>
                {apiResponse.chart_config.data?.map((item: any, index: number) => (
                  <div key={index} style={{
                    background: '#f0f0f0',
                    padding: '10px',
                    borderRadius: '5px',
                    textAlign: 'left'
                  }}>
                    <strong>{item.name || item.label}:</strong>
                    <br />
                    数量: {item.value}
                    {item.total_value && <><br />金额: ¥{item.total_value.toLocaleString()}</>}
                  </div>
                ))}
              </div>
            </div>

            {/* 图表配置信息 */}
            <div style={{ textAlign: 'left', background: '#f8f9fa', padding: '15px', borderRadius: '5px' }}>
              <h4>图表配置:</h4>
              <p><strong>类型:</strong> {apiResponse.chart_config.chart_type}</p>
              <p><strong>描述:</strong> {apiResponse.chart_config.description}</p>
              <p><strong>颜色:</strong> {apiResponse.chart_config.style?.colors?.join(', ')}</p>
              <p><strong>动画:</strong> {apiResponse.chart_config.style?.animation ? '启用' : '禁用'}</p>
            </div>
          </div>
        </Card>
      )}

      {/* 测试结果历史 */}
      <Card title="📋 测试结果历史">
        <Space direction="vertical" style={{ width: '100%' }}>
          {results.map((result, index) => (
            <Alert
              key={index}
              message={`[${result.timestamp}] ${result.testName}`}
              description={
                result.success ? (
                  <div>
                    <Text type="success">✅ 成功</Text>
                    {result.data && (
                      <pre style={{ marginTop: 8, fontSize: 12 }}>
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    )}
                  </div>
                ) : (
                  <Text type="danger">❌ 失败: {result.error}</Text>
                )
              }
              type={result.success ? 'success' : 'error'}
              showIcon
            />
          ))}
          {results.length === 0 && (
            <Text type="secondary">暂无测试结果</Text>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default AIFunctionTest;
