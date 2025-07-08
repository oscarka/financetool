import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tabs, Badge, Alert, Select, Row, Col, Statistic, Tag, Tooltip } from 'antd';
import { ReloadOutlined, BankOutlined, ClockCircleOutlined, DollarCircleOutlined, PayCircleOutlined } from '@ant-design/icons';
import api from '../services/api';

const { TabPane } = Tabs;
const { Option } = Select;

const PayPalManagement: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [balances, setBalances] = useState<any[]>([]);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [summary, setSummary] = useState<any>(null);
    const [config, setConfig] = useState<any>(null);
    const [connectionStatus, setConnectionStatus] = useState<any>(null);
    const [transactionDays, setTransactionDays] = useState(30); // 默认30天
    const [configLoading, setConfigLoading] = useState(true);
    const [testLoading, setTestLoading] = useState(true);
    const [summaryLoading, setSummaryLoading] = useState(true);
    const [configError, setConfigError] = useState<string | null>(null);
    const [testError, setTestError] = useState<string | null>(null);
    const [summaryError, setSummaryError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [configRes, statusRes, summaryRes, balancesRes, transactionsRes] = await Promise.all([
                api.get('/paypal/config'),
                api.get('/paypal/test'),
                api.get('/paypal/summary'),
                api.get('/paypal/all-balances'),
                api.get(`/paypal/recent-transactions?days=${transactionDays}`),
            ]);
            setConfig(configRes.data.data);
            setConnectionStatus(statusRes.data.data);
            setSummary(summaryRes.data.data);
            setBalances((balancesRes.data && balancesRes.data.data) ? balancesRes.data.data : (balancesRes.data || []));
            setTransactions((transactionsRes.data && transactionsRes.data.data) ? transactionsRes.data.data : (transactionsRes.data || []));
        } catch (err: any) {
            setError(err.response?.data?.detail || '获取数据失败');
        } finally {
            setLoading(false);
        }
    };

    const fetchCardData = async () => {
        setConfigLoading(true); setTestLoading(true); setSummaryLoading(true);
        setConfigError(null); setTestError(null); setSummaryError(null);
        
        try {
            const configRes = await api.get('/paypal/config');
            setConfig(configRes.data?.data || configRes.data);
        } catch (e: any) {
            setConfigError(e.response?.data?.detail || 'API配置获取失败');
        } finally { setConfigLoading(false); }
        
        try {
            const testRes = await api.get('/paypal/test');
            setConnectionStatus(testRes.data?.data || testRes.data);
        } catch (e: any) {
            setTestError(e.response?.data?.detail || '连接状态获取失败');
        } finally { setTestLoading(false); }
        
        try {
            const summaryRes = await api.get('/paypal/summary');
            setSummary(summaryRes.data?.data || summaryRes.data);
        } catch (e: any) {
            setSummaryError(e.response?.data?.detail || '账户汇总获取失败');
        } finally { setSummaryLoading(false); }
    };

    useEffect(() => {
        fetchData();
        fetchCardData();
        // eslint-disable-next-line
    }, []);

    useEffect(() => {
        if (transactionDays) {
            fetchData();
        }
        // eslint-disable-next-line
    }, [transactionDays]);

    const formatCurrency = (amount: number, currency: string) => {
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

    // 计算总资产（所有币种余额简单相加，实际可按需折算）
    const getTotalWorth = (): number => {
        if (!summary || !summary.balance_by_currency) return 0;
        return Object.values(summary.balance_by_currency as Record<string, number>).reduce((a: number, b: number) => {
            const aNum = typeof a === 'number' ? a : 0;
            const bNum = typeof b === 'number' ? b : 0;
            return aNum + bNum;
        }, 0);
    };

    const getConnectionStatusText = (status: any) => {
        if (!status) return '未知';
        if (status.token_auth && status.balance_api && status.transaction_api) {
            return '连接正常';
        } else if (status.token_auth) {
            return '认证成功，部分API异常';
        } else {
            return '连接异常';
        }
    };

    const getConnectionStatusColor = (status: any) => {
        if (!status) return 'default';
        if (status.token_auth && status.balance_api && status.transaction_api) {
            return 'green';
        } else if (status.token_auth) {
            return 'orange';
        } else {
            return 'red';
        }
    };

    const columnsBalances = [
        {
            title: '账户ID',
            dataIndex: 'account_id',
            key: 'account_id',
            width: 120,
            render: (v: string) => <code>{v}</code>
        },
        {
            title: '货币',
            dataIndex: 'currency',
            key: 'currency',
            width: 80,
            render: (v: string) => <Badge count={v} style={{ backgroundColor: '#1890ff' }} />
        },
        {
            title: '可用余额',
            dataIndex: 'available_balance',
            key: 'available_balance',
            width: 120,
            render: (v: number, r: any) => (
                <span style={{ fontWeight: 'bold', color: v > 0 ? '#52c41a' : '#d9d9d9' }}>
                    {formatCurrency(v, r.currency)}
                </span>
            )
        },
        {
            title: '冻结余额',
            dataIndex: 'reserved_balance',
            key: 'reserved_balance',
            width: 120,
            render: (v: number, r: any) => formatCurrency(v, r.currency)
        },
        {
            title: '总余额',
            dataIndex: 'total_balance',
            key: 'total_balance',
            width: 120,
            render: (v: number, r: any) => (
                <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
                    {formatCurrency(v, r.currency)}
                </span>
            )
        },
        {
            title: '账户类型',
            dataIndex: 'type',
            key: 'type',
            width: 120,
            render: (v: string) => <Tag color={v === 'PAYPAL_WALLET' ? 'blue' : v === 'TOTAL_SUMMARY' ? 'gold' : 'green'}>{v}</Tag>
        },
        {
            title: '主要账户',
            dataIndex: 'primary',
            key: 'primary',
            width: 80,
            render: (v: boolean) => v ? <Badge status="success" text="是" /> : <Badge status="default" text="否" />
        },
        {
            title: '更新时间',
            dataIndex: 'update_time',
            key: 'update_time',
            width: 150,
            render: (v: string) => (
                <Tooltip title={formatDate(v)}>
                    <span>{new Date(v).toLocaleDateString('zh-CN')}</span>
                </Tooltip>
            )
        },
    ];

    const columnsTransactions = [
        { 
            title: '日期', 
            dataIndex: 'date', 
            key: 'date', 
            width: 150,
            render: (v: string) => formatDate(v) 
        },
        { 
            title: '类型', 
            dataIndex: 'type', 
            key: 'type', 
            width: 80,
            render: (v: string) => <Badge color={v === 'credit' ? 'green' : v === 'debit' ? 'red' : 'blue'} text={v} /> 
        },
        { 
            title: '金额', 
            dataIndex: 'amount', 
            key: 'amount', 
            width: 120,
            render: (v: number, r: any) => (
                <span style={{ color: r.type === 'credit' ? '#52c41a' : '#ff4d4f' }}>
                    {r.type === 'credit' ? '+' : '-'}{formatCurrency(v, r.currency)}
                </span>
            )
        },
        { 
            title: '货币', 
            dataIndex: 'currency', 
            key: 'currency', 
            width: 80,
            render: (v: string) => <Badge count={v} style={{ backgroundColor: '#1890ff' }} />
        },
        { 
            title: '描述', 
            dataIndex: 'description', 
            key: 'description',
            width: 200,
            ellipsis: true
        },
        { 
            title: '状态', 
            dataIndex: 'status', 
            key: 'status', 
            width: 100,
            render: (v: string) => <Badge color={v === 'completed' ? 'green' : v === 'pending' ? 'gold' : 'red'} text={v} /> 
        },
        { 
            title: '手续费', 
            dataIndex: 'fee_amount', 
            key: 'fee_amount', 
            width: 100,
            render: (v: number, r: any) => v > 0 ? formatCurrency(v, r.currency) : '-'
        },
        { 
            title: '付款人', 
            dataIndex: 'payer_name', 
            key: 'payer_name',
            width: 150,
            ellipsis: true
        },
        { 
            title: '交易ID', 
            dataIndex: 'transaction_id', 
            key: 'transaction_id',
            width: 120,
            render: (v: string) => <code>{v}</code>
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ fontSize: 24, fontWeight: 700 }}>
                    <PayCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                    PayPal账户管理
                </h1>
                <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading} type="primary">刷新数据</Button>
            </div>

            {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

            {/* 顶部统计卡片区 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <Card>
                        <Statistic title="总账户数" value={typeof summary?.total_accounts === 'number' ? summary.total_accounts : '-'} prefix={<BankOutlined />} loading={summaryLoading} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic title="支持货币" value={typeof summary?.total_currencies === 'number' ? summary.total_currencies : '-'} prefix={<DollarCircleOutlined />} loading={summaryLoading} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic title="总资产价值" value={getTotalWorth().toFixed(2)} prefix="$" loading={summaryLoading} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic title="最近交易" value={typeof summary?.recent_transactions_count === 'number' ? summary.recent_transactions_count : '-'} prefix={<ClockCircleOutlined />} loading={summaryLoading} />
                    </Card>
                </Col>
            </Row>

            {/* 状态卡片 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                    <Card loading={configLoading}>
                        <div>API配置：{configError ? <span style={{ color: 'red' }}>{configError}</span> : (config ? (
                            config.api_configured ? 
                            <span style={{ color: 'green' }}>已配置，环境: {config.environment}，Client ID: {config.client_id_prefix}</span> : 
                            <span style={{ color: 'red' }}>未配置</span>
                        ) : '未配置')}</div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card loading={testLoading}>
                        <div>连接状态：{testError ? <span style={{ color: 'red' }}>{testError}</span> : (
                            <Tag color={getConnectionStatusColor(connectionStatus)}>
                                {getConnectionStatusText(connectionStatus)}
                            </Tag>
                        )}</div>
                        {connectionStatus && !connectionStatus.token_auth && (
                            <div style={{ fontSize: 12, color: '#ff4d4f' }}>
                                {connectionStatus.error}
                            </div>
                        )}
                    </Card>
                </Col>
                <Col span={8}>
                    <Card loading={summaryLoading}>
                        <div>账户汇总：{summaryError ? <span style={{ color: 'red' }}>{summaryError}</span> : (summary ? (
                            <span>总账户数: {typeof summary.total_accounts === 'number' ? summary.total_accounts : '-'}，支持货币: {typeof summary.total_currencies === 'number' ? summary.total_currencies : '-'}，总资产: ${getTotalWorth().toFixed(2)}</span>
                        ) : '-')}</div>
                    </Card>
                </Col>
            </Row>

            <Tabs defaultActiveKey="balances">
                <TabPane tab="账户余额" key="balances">
                    {/* Debug: 展示原始balances数据 */}
                    {balances.length > 0 && (
                        <pre style={{ maxHeight: 150, overflow: 'auto', background: '#f6f6f6', fontSize: 12, marginBottom: 8 }}>
                            {JSON.stringify(balances, null, 2)}
                        </pre>
                    )}
                    <Table
                        dataSource={Array.isArray(balances) ? balances : []}
                        columns={columnsBalances}
                        rowKey={(r) => r.account_id}
                        loading={loading}
                        pagination={{ pageSize: 10 }}
                        scroll={{ x: 1200 }}
                        size="small"
                        locale={{
                            emptyText: (
                                <div style={{ padding: '20px' }}>
                                    <Alert
                                        type="info"
                                        message="暂无余额数据"
                                        description="请检查API配置或账户权限设置"
                                        showIcon
                                    />
                                </div>
                            )
                        }}
                    />
                </TabPane>
                
                <TabPane tab="交易记录" key="transactions">
                    {/* 时间范围选择器 */}
                    <div style={{ marginBottom: 16 }}>
                        <span style={{ marginRight: 8 }}>查询时间范围：</span>
                        <Select
                            value={transactionDays}
                            onChange={setTransactionDays}
                            style={{ width: 120 }}
                        >
                            <Option value={7}>最近7天</Option>
                            <Option value={30}>最近30天</Option>
                            <Option value={90}>最近90天</Option>
                            <Option value={180}>最近180天</Option>
                        </Select>
                    </div>

                    {/* Debug: 展示原始transactions数据 */}
                    {transactions.length > 0 && (
                        <pre style={{ maxHeight: 150, overflow: 'auto', background: '#f6f6f6', fontSize: 12, marginBottom: 8 }}>
                            {JSON.stringify(transactions.slice(0, 3), null, 2)}
                        </pre>
                    )}

                    <Table
                        dataSource={Array.isArray(transactions) ? transactions : []}
                        columns={columnsTransactions}
                        rowKey={(r) => r.transaction_id || Math.random()}
                        loading={loading}
                        pagination={{ pageSize: 20 }}
                        scroll={{ x: 1400 }}
                        size="small"
                        locale={{
                            emptyText: (
                                <div style={{ padding: '20px' }}>
                                    <Alert
                                        type="info"
                                        message="暂无交易记录"
                                        description={`最近${transactionDays}天内没有交易记录，或者需要更多时间加载数据。`}
                                        showIcon
                                    />
                                </div>
                            )
                        }}
                    />
                </TabPane>
            </Tabs>
        </div>
    );
};

export default PayPalManagement;