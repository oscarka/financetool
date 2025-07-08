import React, { useState, useEffect } from 'react';
import { 
    Card, 
    Button, 
    Table, 
    Tabs, 
    Badge, 
    Alert, 
    Row, 
    Col, 
    Statistic, 
    Tag, 
    Tooltip, 
    message,
    Modal,
    Form,
    Input,
    DatePicker,
    InputNumber
} from 'antd';
import { 
    ReloadOutlined, 
    BankOutlined, 
    ClockCircleOutlined, 
    DollarCircleOutlined,
    LineChartOutlined,
    WarningOutlined,
    CheckCircleOutlined,
    SyncOutlined
} from '@ant-design/icons';
import { ibkrAPI } from '../services/api';
import { Line } from '@ant-design/charts';
import dayjs from 'dayjs';

const { TabPane } = Tabs;

const IBKRManagement: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [balances, setBalances] = useState<any[]>([]);
    const [positions, setPositions] = useState<any[]>([]);
    const [logs, setLogs] = useState<any[]>([]);
    const [summary, setSummary] = useState<any>(null);
    const [config, setConfig] = useState<any>(null);
    const [health, setHealth] = useState<any>(null);
    const [recentRequests, setRecentRequests] = useState<any[]>([]);

    // 各组件独立loading状态
    const [configLoading, setConfigLoading] = useState(true);
    const [healthLoading, setHealthLoading] = useState(true);
    const [summaryLoading, setSummaryLoading] = useState(true);

    // 各组件独立错误状态
    const [configError, setConfigError] = useState<string | null>(null);
    const [healthError, setHealthError] = useState<string | null>(null);
    const [summaryError, setSummaryError] = useState<string | null>(null);

    // 测试同步Modal状态
    const [syncModalVisible, setSyncModalVisible] = useState(false);
    const [syncLoading, setSyncLoading] = useState(false);
    const [form] = Form.useForm();

    // 获取所有IBKR数据
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [
                balancesRes,
                positionsRes,
                logsRes,
                summaryRes,
                recentRequestsRes
            ] = await Promise.all([
                ibkrAPI.getBalances(),
                ibkrAPI.getPositions(),
                ibkrAPI.getLogs({ limit: 50 }),
                ibkrAPI.getSummary(),
                ibkrAPI.getRecentRequests(20).catch(() => ({ data: { data: [] } }))
            ]);

            setBalances(balancesRes.data?.data || []);
            setPositions(positionsRes.data?.data || []);
            setLogs(logsRes.data?.data || []);
            setSummary(summaryRes.data?.data);
            setRecentRequests(recentRequestsRes.data?.data || []);
        } catch (err: any) {
            setError(err.response?.data?.detail || '获取IBKR数据失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取状态卡片数据
    const fetchCardData = async () => {
        setConfigLoading(true);
        setHealthLoading(true);
        setSummaryLoading(true);
        setConfigError(null);
        setHealthError(null);
        setSummaryError(null);

        // 获取配置信息
        try {
            const configRes = await ibkrAPI.getConfig();
            setConfig(configRes.data?.data || configRes.data);
        } catch (e: any) {
            setConfigError(e.response?.data?.detail || 'IBKR配置获取失败');
        } finally {
            setConfigLoading(false);
        }

        // 获取健康状态
        try {
            const healthRes = await ibkrAPI.testConnection();
            setHealth(healthRes.data?.data || healthRes.data);
        } catch (e: any) {
            setHealthError(e.response?.data?.detail || 'IBKR连接状态获取失败');
        } finally {
            setHealthLoading(false);
        }

        // 获取汇总信息
        try {
            const summaryRes = await ibkrAPI.getSummary();
            setSummary(summaryRes.data?.data || summaryRes.data);
        } catch (e: any) {
            setSummaryError(e.response?.data?.detail || 'IBKR汇总信息获取失败');
        } finally {
            setSummaryLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        fetchCardData();
    }, []);

    // 测试数据同步
    const handleTestSync = async (values: any) => {
        setSyncLoading(true);
        try {
            const syncData = {
                account_id: values.account_id,
                timestamp: values.timestamp.toISOString(),
                balances: {
                    total_cash: values.total_cash,
                    net_liquidation: values.net_liquidation,
                    buying_power: values.buying_power,
                    currency: values.currency || 'USD'
                },
                positions: values.positions ? [
                    {
                        symbol: values.symbol,
                        quantity: values.quantity,
                        market_value: values.market_value,
                        average_cost: values.average_cost,
                        currency: values.currency || 'USD'
                    }
                ] : []
            };

            const response = await ibkrAPI.syncData(syncData);
            if (response.success || response.status === 'success') {
                message.success('测试同步成功！');
                setSyncModalVisible(false);
                form.resetFields();
                // 刷新数据
                fetchData();
            } else {
                message.error('测试同步失败');
            }
        } catch (error: any) {
            message.error(error.response?.data?.detail || '测试同步失败');
        } finally {
            setSyncLoading(false);
        }
    };

    const formatCurrency = (amount: number, currency: string = 'USD') => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(amount);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('zh-CN');
    };

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'success': return 'green';
            case 'error': return 'red';
            case 'pending': return 'orange';
            default: return 'default';
        }
    };

    const getAssetClassText = (assetClass: string) => {
        switch (assetClass) {
            case 'STK': return '股票';
            case 'OPT': return '期权';
            case 'FUT': return '期货';
            case 'BOND': return '债券';
            case 'CASH': return '现金';
            default: return assetClass;
        }
    };

    // 余额表格列定义
    const balanceColumns = [
        {
            title: '账户ID',
            dataIndex: 'account_id',
            key: 'account_id',
            render: (v: string) => <code>{v}</code>
        },
        {
            title: '总现金',
            dataIndex: 'total_cash',
            key: 'total_cash',
            render: (v: number, record: any) => (
                <span style={{ fontWeight: 'bold', color: v > 0 ? '#52c41a' : '#d9d9d9' }}>
                    {formatCurrency(v, record.currency)}
                </span>
            )
        },
        {
            title: '净清算价值',
            dataIndex: 'net_liquidation',
            key: 'net_liquidation',
            render: (v: number, record: any) => (
                <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
                    {formatCurrency(v, record.currency)}
                </span>
            )
        },
        {
            title: '购买力',
            dataIndex: 'buying_power',
            key: 'buying_power',
            render: (v: number, record: any) => formatCurrency(v, record.currency)
        },
        {
            title: '货币',
            dataIndex: 'currency',
            key: 'currency',
            render: (v: string) => <Badge count={v} style={{ backgroundColor: '#1890ff' }} />
        },
        {
            title: '快照时间',
            dataIndex: 'snapshot_time',
            key: 'snapshot_time',
            render: (v: string) => (
                <Tooltip title={formatDate(v)}>
                    <span>{new Date(v).toLocaleString('zh-CN')}</span>
                </Tooltip>
            )
        },
        {
            title: '同步来源',
            dataIndex: 'sync_source',
            key: 'sync_source',
            render: (v: string) => <Tag color="blue">{v}</Tag>
        }
    ];

    // 持仓表格列定义
    const positionColumns = [
        {
            title: '账户ID',
            dataIndex: 'account_id',
            key: 'account_id',
            render: (v: string) => <code>{v}</code>
        },
        {
            title: '股票代码',
            dataIndex: 'symbol',
            key: 'symbol',
            render: (v: string) => <Tag color="green">{v}</Tag>
        },
        {
            title: '数量',
            dataIndex: 'quantity',
            key: 'quantity',
            render: (v: number) => v.toFixed(6)
        },
        {
            title: '市值',
            dataIndex: 'market_value',
            key: 'market_value',
            render: (v: number, record: any) => (
                <span style={{ fontWeight: 'bold' }}>
                    {formatCurrency(v, record.currency)}
                </span>
            )
        },
        {
            title: '平均成本',
            dataIndex: 'average_cost',
            key: 'average_cost',
            render: (v: number, record: any) => formatCurrency(v, record.currency)
        },
        {
            title: '未实现盈亏',
            dataIndex: 'unrealized_pnl',
            key: 'unrealized_pnl',
            render: (v: number, record: any) => (
                <span style={{ color: v >= 0 ? '#52c41a' : '#ff4d4f' }}>
                    {formatCurrency(v || 0, record.currency)}
                </span>
            )
        },
        {
            title: '资产类别',
            dataIndex: 'asset_class',
            key: 'asset_class',
            render: (v: string) => <Tag color="blue">{getAssetClassText(v)}</Tag>
        },
        {
            title: '快照时间',
            dataIndex: 'snapshot_time',
            key: 'snapshot_time',
            render: (v: string) => (
                <Tooltip title={formatDate(v)}>
                    <span>{new Date(v).toLocaleString('zh-CN')}</span>
                </Tooltip>
            )
        }
    ];

    // 同步日志表格列定义
    const logColumns = [
        {
            title: '时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (v: string) => formatDate(v)
        },
        {
            title: '账户ID',
            dataIndex: 'account_id',
            key: 'account_id',
            render: (v: string) => v ? <code>{v}</code> : '-'
        },
        {
            title: '同步类型',
            dataIndex: 'sync_type',
            key: 'sync_type',
            render: (v: string) => <Tag color="blue">{v}</Tag>
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (v: string) => (
                <Badge 
                    color={getStatusColor(v)} 
                    text={v} 
                />
            )
        },
        {
            title: '处理记录数',
            dataIndex: 'records_processed',
            key: 'records_processed'
        },
        {
            title: '插入记录数',
            dataIndex: 'records_inserted',
            key: 'records_inserted'
        },
        {
            title: '耗时(ms)',
            dataIndex: 'sync_duration_ms',
            key: 'sync_duration_ms',
            render: (v: number) => v ? `${v}ms` : '-'
        },
        {
            title: '来源IP',
            dataIndex: 'source_ip',
            key: 'source_ip'
        },
        {
            title: '错误信息',
            dataIndex: 'error_message',
            key: 'error_message',
            render: (v: string) => v ? (
                <Tooltip title={v}>
                    <Tag color="red">有错误</Tag>
                </Tooltip>
            ) : (
                <Tag color="green">正常</Tag>
            )
        }
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ fontSize: 24, fontWeight: 700 }}>IBKR 账户管理</h1>
                <div>
                    <Button 
                        icon={<SyncOutlined />} 
                        onClick={() => setSyncModalVisible(true)}
                        style={{ marginRight: 8 }}
                    >
                        测试同步
                    </Button>
                    <Button 
                        icon={<ReloadOutlined />} 
                        onClick={fetchData} 
                        loading={loading} 
                        type="primary"
                    >
                        刷新数据
                    </Button>
                </div>
            </div>

            {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

            {/* 顶部统计卡片区 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <Card>
                        <Statistic 
                            title="总账户数" 
                            value={summary?.total_accounts || 0} 
                            prefix={<BankOutlined />} 
                            loading={summaryLoading} 
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic 
                            title="总持仓数" 
                            value={summary?.total_positions || 0} 
                            prefix={<LineChartOutlined />} 
                            loading={summaryLoading} 
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic 
                            title="净清算价值" 
                            value={summary?.total_net_liquidation || 0} 
                            prefix="$" 
                            precision={2}
                            loading={summaryLoading} 
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic 
                            title="总现金" 
                            value={summary?.total_cash || 0} 
                            prefix={<DollarCircleOutlined />} 
                            precision={2}
                            loading={summaryLoading} 
                        />
                    </Card>
                </Col>
            </Row>

            {/* 状态卡片区 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                    <Card loading={configLoading}>
                        <div>
                            <strong>API配置：</strong>
                            {configError ? (
                                <span style={{ color: 'red' }}>
                                    <WarningOutlined /> {configError}
                                </span>
                            ) : config ? (
                                config.api_configured ? (
                                    <span style={{ color: 'green' }}>
                                        <CheckCircleOutlined /> 已配置 | 白名单: {config.allowed_ips?.length || 0}个IP
                                    </span>
                                ) : (
                                    <span style={{ color: 'red' }}>
                                        <WarningOutlined /> 未配置
                                    </span>
                                )
                            ) : (
                                '加载中...'
                            )}
                        </div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card loading={healthLoading}>
                        <div>
                            <strong>连接状态：</strong>
                            {healthError ? (
                                <span style={{ color: 'red' }}>
                                    <WarningOutlined /> {healthError}
                                </span>
                            ) : health ? (
                                health.config_valid && health.database_ok ? (
                                    <span style={{ color: 'green' }}>
                                        <CheckCircleOutlined /> 连接正常
                                    </span>
                                ) : (
                                    <span style={{ color: 'red' }}>
                                        <WarningOutlined /> 连接异常 {health.database_error || ''}
                                    </span>
                                )
                            ) : (
                                '检测中...'
                            )}
                        </div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card loading={summaryLoading}>
                        <div>
                            <strong>最近同步：</strong>
                            {summaryError ? (
                                <span style={{ color: 'red' }}>
                                    <WarningOutlined /> {summaryError}
                                </span>
                            ) : summary ? (
                                <span>
                                    状态: <Tag color={getStatusColor(summary.last_sync_status || 'unknown')}>
                                        {summary.last_sync_status || 'unknown'}
                                    </Tag>
                                    {summary.last_sync_time && (
                                        <span style={{ marginLeft: 8 }}>
                                            <ClockCircleOutlined /> {new Date(summary.last_sync_time).toLocaleString('zh-CN')}
                                        </span>
                                    )}
                                </span>
                            ) : (
                                '加载中...'
                            )}
                        </div>
                    </Card>
                </Col>
            </Row>

            <Tabs defaultActiveKey="balances">
                <TabPane tab="账户余额" key="balances">
                    <Table
                        dataSource={balances}
                        columns={balanceColumns}
                        rowKey={(record) => `${record.account_id}-${record.snapshot_time}`}
                        loading={loading}
                        pagination={{ pageSize: 10 }}
                        scroll={{ x: 1000 }}
                        size="small"
                    />
                </TabPane>
                
                <TabPane tab="持仓信息" key="positions">
                    <Table
                        dataSource={positions}
                        columns={positionColumns}
                        rowKey={(record) => `${record.account_id}-${record.symbol}-${record.snapshot_time}`}
                        loading={loading}
                        pagination={{ pageSize: 10 }}
                        scroll={{ x: 1200 }}
                        size="small"
                    />
                </TabPane>
                
                <TabPane tab="同步日志" key="logs">
                    <Table
                        dataSource={logs}
                        columns={logColumns}
                        rowKey="id"
                        loading={loading}
                        pagination={{ pageSize: 20 }}
                        scroll={{ x: 1200 }}
                        size="small"
                    />
                </TabPane>

                <TabPane tab="调试信息" key="debug">
                    <Card title="最近请求记录" style={{ marginBottom: 16 }}>
                        {recentRequests.length > 0 ? (
                            <Table
                                dataSource={recentRequests}
                                columns={[
                                    { title: 'ID', dataIndex: 'id', key: 'id' },
                                    { title: '账户ID', dataIndex: 'account_id', key: 'account_id' },
                                    { 
                                        title: '状态', 
                                        dataIndex: 'status', 
                                        key: 'status',
                                        render: (v: string) => <Badge color={getStatusColor(v)} text={v} />
                                    },
                                    { title: '处理记录', dataIndex: 'records_processed', key: 'records_processed' },
                                    { title: '插入记录', dataIndex: 'records_inserted', key: 'records_inserted' },
                                    { title: '来源IP', dataIndex: 'source_ip', key: 'source_ip' },
                                    { title: '耗时(ms)', dataIndex: 'sync_duration_ms', key: 'sync_duration_ms' },
                                    { 
                                        title: '时间', 
                                        dataIndex: 'created_at', 
                                        key: 'created_at',
                                        render: (v: string) => new Date(v).toLocaleString('zh-CN')
                                    },
                                    {
                                        title: '有错误',
                                        dataIndex: 'has_error',
                                        key: 'has_error',
                                        render: (v: boolean) => v ? <Tag color="red">是</Tag> : <Tag color="green">否</Tag>
                                    }
                                ]}
                                rowKey="id"
                                size="small"
                                pagination={false}
                            />
                        ) : (
                            <Alert type="info" message="暂无调试信息" />
                        )}
                    </Card>
                    
                    <Card title="原始数据">
                        <pre style={{ 
                            maxHeight: 400, 
                            overflow: 'auto', 
                            background: '#f6f6f6', 
                            fontSize: 12,
                            padding: 12
                        }}>
                            {JSON.stringify({ config, health, summary }, null, 2)}
                        </pre>
                    </Card>
                </TabPane>
            </Tabs>

            {/* 测试同步Modal */}
            <Modal
                title="测试IBKR数据同步"
                open={syncModalVisible}
                onCancel={() => setSyncModalVisible(false)}
                footer={null}
                width={800}
            >
                <Form
                    form={form}
                    onFinish={handleTestSync}
                    layout="vertical"
                    initialValues={{
                        account_id: 'U13638726',
                        timestamp: dayjs(),
                        currency: 'USD'
                    }}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="account_id"
                                label="账户ID"
                                rules={[{ required: true, message: '请输入账户ID' }]}
                            >
                                <Input placeholder="U13638726" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="timestamp"
                                label="时间戳"
                                rules={[{ required: true, message: '请选择时间' }]}
                            >
                                <DatePicker showTime style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Card title="余额信息" size="small" style={{ marginBottom: 16 }}>
                        <Row gutter={16}>
                            <Col span={6}>
                                <Form.Item name="total_cash" label="总现金">
                                    <InputNumber style={{ width: '100%' }} placeholder="2.74" />
                                </Form.Item>
                            </Col>
                            <Col span={6}>
                                <Form.Item name="net_liquidation" label="净清算价值">
                                    <InputNumber style={{ width: '100%' }} placeholder="5.70" />
                                </Form.Item>
                            </Col>
                            <Col span={6}>
                                <Form.Item name="buying_power" label="购买力">
                                    <InputNumber style={{ width: '100%' }} placeholder="2.74" />
                                </Form.Item>
                            </Col>
                            <Col span={6}>
                                <Form.Item name="currency" label="货币">
                                    <Input placeholder="USD" />
                                </Form.Item>
                            </Col>
                        </Row>
                    </Card>

                    <Card title="持仓信息（可选）" size="small" style={{ marginBottom: 16 }}>
                        <Row gutter={16}>
                            <Col span={8}>
                                <Form.Item name="symbol" label="股票代码">
                                    <Input placeholder="TSLA" />
                                </Form.Item>
                            </Col>
                            <Col span={8}>
                                <Form.Item name="quantity" label="数量">
                                    <InputNumber style={{ width: '100%' }} placeholder="0.01" />
                                </Form.Item>
                            </Col>
                            <Col span={8}>
                                <Form.Item name="market_value" label="市值">
                                    <InputNumber style={{ width: '100%' }} placeholder="2.96" />
                                </Form.Item>
                            </Col>
                        </Row>
                        <Row gutter={16}>
                            <Col span={12}>
                                <Form.Item name="average_cost" label="平均成本">
                                    <InputNumber style={{ width: '100%' }} placeholder="0.0" />
                                </Form.Item>
                            </Col>
                            <Col span={12}>
                                <Form.Item name="positions" label="包含持仓" valuePropName="checked">
                                    <input type="checkbox" />
                                </Form.Item>
                            </Col>
                        </Row>
                    </Card>

                    <div style={{ textAlign: 'right' }}>
                        <Button onClick={() => setSyncModalVisible(false)} style={{ marginRight: 8 }}>
                            取消
                        </Button>
                        <Button type="primary" htmlType="submit" loading={syncLoading}>
                            测试同步
                        </Button>
                    </div>
                </Form>
            </Modal>
        </div>
    );
};

export default IBKRManagement;