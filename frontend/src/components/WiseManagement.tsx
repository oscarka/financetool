import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tabs, Badge, Alert, Select, Row, Col, Statistic, Tag, Tooltip, DatePicker, message } from 'antd';
import { ReloadOutlined, BankOutlined, ClockCircleOutlined, DollarCircleOutlined } from '@ant-design/icons';
import api from '../services/api';
import { Line } from '@ant-design/charts';
import dayjs from 'dayjs';
import moment from 'moment';

const { TabPane } = Tabs;
const { Option } = Select;

const currencyOptions = [
    { value: 'USD', label: 'USD - 美元' },
    { value: 'EUR', label: 'EUR - 欧元' },
    { value: 'GBP', label: 'GBP - 英镑' },
    { value: 'CNY', label: 'CNY - 人民币' },
    { value: 'JPY', label: 'JPY - 日元' },
    { value: 'AUD', label: 'AUD - 澳元' },
];

const WiseManagement: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [balances, setBalances] = useState<any[]>([]);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [exchangeRates, setExchangeRates] = useState<any>(null);
    const [summary, setSummary] = useState<any>(null);
    const [config, setConfig] = useState<any>(null);
    const [connectionStatus, setConnectionStatus] = useState<any>(null);
    const [sourceCurrency, setSourceCurrency] = useState('USD');
    const [targetCurrency, setTargetCurrency] = useState('CNY');

    const [transactionDays, setTransactionDays] = useState(90); // 默认90天
    const [configLoading, setConfigLoading] = useState(true);
    const [testLoading, setTestLoading] = useState(true);
    const [summaryLoading, setSummaryLoading] = useState(true);
    const [configError, setConfigError] = useState<string | null>(null);
    const [testError, setTestError] = useState<string | null>(null);
    const [summaryError, setSummaryError] = useState<string | null>(null);
    const [ratePairs, setRatePairs] = useState<{ source: string, target: string }[]>([]);
    const [selectedPair, setSelectedPair] = useState<{ source: string, target: string } | null>(null);
    const [rateHistory, setRateHistory] = useState<any[]>([]);
    const [rateLoading, setRateLoading] = useState(false);
    const [dateRange, setDateRange] = useState<[moment.Moment, moment.Moment]>([moment().subtract(30, 'days'), moment()]);
    const [latestRate, setLatestRate] = useState<number | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [configRes, statusRes, summaryRes, balancesRes, transactionsRes, ratesRes] = await Promise.all([
                api.get('/wise/config'),
                api.get('/wise/test'),
                api.get('/wise/summary'),
                api.get('/wise/all-balances'),
                api.get(`/wise/recent-transactions?days=${transactionDays}`),
                api.get(`/wise/exchange-rates?source=${sourceCurrency}&target=${targetCurrency}`),
            ]);
            setConfig(configRes.data.data);
            setConnectionStatus(statusRes.data.data);
            setSummary(summaryRes.data.data);
            setBalances((balancesRes.data && balancesRes.data.data) ? balancesRes.data.data : (balancesRes.data || []));
            setTransactions((transactionsRes.data && transactionsRes.data.data) ? transactionsRes.data.data : (transactionsRes.data || []));
            setExchangeRates(ratesRes.data.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || '获取数据失败');
        } finally {
            setLoading(false);
        }
    };

    const fetchExchangeRate = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/wise/exchange-rates?source=${sourceCurrency}&target=${targetCurrency}`);
            setExchangeRates(response.data.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || '获取汇率失败');
        } finally {
            setLoading(false);
        }
    };

    const fetchCardData = async () => {
        setConfigLoading(true); setTestLoading(true); setSummaryLoading(true);
        setConfigError(null); setTestError(null); setSummaryError(null);
        try {
            const configRes = await api.get('/wise/config');
            setConfig(configRes.data?.data || configRes.data);
        } catch (e: any) {
            setConfigError(e.response?.data?.detail || 'API配置获取失败');
        } finally { setConfigLoading(false); }
        try {
            const testRes = await api.get('/wise/test');
            setConnectionStatus(testRes.data?.data || testRes.data);
        } catch (e: any) {
            setTestError(e.response?.data?.detail || '连接状态获取失败');
        } finally { setTestLoading(false); }
        try {
            const summaryRes = await api.get('/wise/summary');
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
        if (sourceCurrency && targetCurrency) {
            fetchExchangeRate();
        }
        // eslint-disable-next-line
    }, [sourceCurrency, targetCurrency]);

    // 自动识别持有币种组合
    useEffect(() => {
        if (summary && summary.balance_by_currency) {
            const currencies = Object.keys(summary.balance_by_currency);
            const pairs: { source: string, target: string }[] = [];
            for (let i = 0; i < currencies.length; i++) {
                for (let j = 0; j < currencies.length; j++) {
                    if (i !== j) pairs.push({ source: currencies[i], target: currencies[j] });
                }
            }
            setRatePairs(pairs);
            if (!selectedPair && pairs.length > 0) setSelectedPair(pairs[0]);
        }
    }, [summary]);

    // 拉取历史汇率
    const fetchRateHistory = async () => {
        if (!selectedPair) return;
        setRateLoading(true);
        const from = dateRange[0].format('YYYY-MM-DD');
        const to = dateRange[1].format('YYYY-MM-DD');
        try {
            const res = await api.get('/wise/exchange-rates/history', {
                params: {
                    source: selectedPair.source,
                    target: selectedPair.target,
                    from_time: from,
                    to_time: to,
                    group: 'day',
                },
            });
            setRateHistory(res.data.data || []);
            if (res.data.data && res.data.data.length > 0) {
                setLatestRate(res.data.data[res.data.data.length - 1].rate);
            } else {
                setLatestRate(null);
            }
        } catch (e) {
            setRateHistory([]);
            setLatestRate(null);
        }
        setRateLoading(false);
    };

    useEffect(() => {
        if (selectedPair) fetchRateHistory();
        // eslint-disable-next-line
    }, [selectedPair, dateRange]);

    // 拉取历史汇率数据
    const fetchHistoryRates = async () => {
        try {
            await api.post('/wise/exchange-rates/fetch-history', {
                days: 30,
                group: 'day'
            });
            message.success('历史汇率数据拉取成功');
            // 重新获取当前选中的汇率历史
            if (selectedPair) fetchRateHistory();
        } catch (e) {
            message.error('历史汇率数据拉取失败');
        }
    };

    // 同步余额数据到数据库
    const syncBalancesToDb = async () => {
        try {
            setLoading(true);
            const response = await api.post('/wise/sync-balances');
            if (response.data.success) {
                message.success(`余额同步成功: ${response.data.message}`);
                // 重新获取数据
                fetchData();
            } else {
                message.error(`余额同步失败: ${response.data.message}`);
            }
        } catch (e: any) {
            message.error(`余额同步失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setLoading(false);
        }
    };

    // 同步交易数据到数据库
    const syncTransactionsToDb = async () => {
        try {
            setLoading(true);
            const response = await api.post('/wise/sync-transactions');
            if (response.data.success) {
                message.success(`交易同步成功: ${response.data.message}`);
                // 重新获取数据
                fetchData();
            } else {
                message.error(`交易同步失败: ${response.data.message}`);
            }
        } catch (e: any) {
            message.error(`交易同步失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setLoading(false);
        }
    };

    // 获取存储的余额数据
    const fetchStoredBalances = async () => {
        try {
            setLoading(true);
            const response = await api.get('/wise/stored-balances');
            if (response.data.success) {
                setBalances(response.data.data);
                message.success(`从数据库获取到 ${response.data.count} 条余额记录`);
            } else {
                message.error('获取存储的余额数据失败');
            }
        } catch (e: any) {
            message.error(`获取存储的余额数据失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setLoading(false);
        }
    };

    // 获取存储的交易数据
    const fetchStoredTransactions = async () => {
        try {
            setLoading(true);
            const response = await api.get('/wise/stored-transactions', {
                params: { limit: 100 }
            });
            if (response.data.success) {
                setTransactions(response.data.data);
                message.success(`从数据库获取到 ${response.data.count} 条交易记录`);
            } else {
                message.error('获取存储的交易数据失败');
            }
        } catch (e: any) {
            message.error(`获取存储的交易数据失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setLoading(false);
        }
    };

    // 页面加载后自动拉取一次历史汇率
    useEffect(() => {
        if (selectedPair && rateHistory.length === 0) {
            fetchRateHistory();
        }
        // eslint-disable-next-line
    }, [selectedPair]);

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

    const getInvestmentStateColor = (state: string) => {
        switch (state) {
            case 'INVESTED': return 'green';
            case 'NOT_INVESTED': return 'blue';
            case 'DIVESTING': return 'orange';
            default: return 'default';
        }
    };

    const getInvestmentStateText = (state: string) => {
        switch (state) {
            case 'INVESTED': return '已投资';
            case 'NOT_INVESTED': return '未投资';
            case 'DIVESTING': return '撤资中';
            default: return state;
        }
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
            title: '现金金额',
            dataIndex: 'cash_amount',
            key: 'cash_amount',
            width: 120,
            render: (v: number, r: any) => formatCurrency(v, r.currency)
        },
        {
            title: '冻结金额',
            dataIndex: 'reserved_balance',
            key: 'reserved_balance',
            width: 120,
            render: (v: number, r: any) => formatCurrency(v, r.currency)
        },
        {
            title: '总价值',
            dataIndex: 'total_worth',
            key: 'total_worth',
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
            width: 100,
            render: (v: string) => <Tag color={v === 'STANDARD' ? 'blue' : 'green'}>{v}</Tag>
        },
        {
            title: '投资状态',
            dataIndex: 'investment_state',
            key: 'investment_state',
            width: 100,
            render: (v: string) => (
                <Tag color={getInvestmentStateColor(v)}>
                    {getInvestmentStateText(v)}
                </Tag>
            )
        },
        {
            title: '主要账户',
            dataIndex: 'primary',
            key: 'primary',
            width: 80,
            render: (v: boolean) => v ? <Badge status="success" text="是" /> : <Badge status="default" text="否" />
        },
        {
            title: '创建时间',
            dataIndex: 'creation_time',
            key: 'creation_time',
            width: 150,
            render: (v: string) => (
                <Tooltip title={formatDate(v)}>
                    <span>{new Date(v).toLocaleDateString('zh-CN')}</span>
                </Tooltip>
            )
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
        { title: '日期', dataIndex: 'date', key: 'date', render: (v: string) => formatDate(v) },
        { title: '类型', dataIndex: 'type', key: 'type', render: (v: string) => <Badge color={v === 'credit' ? 'green' : v === 'debit' ? 'red' : 'blue'} text={v} /> },
        { title: '金额', dataIndex: 'amount', key: 'amount', render: (v: number, r: any) => formatCurrency(v, r.currency) },
        { title: '描述', dataIndex: 'description', key: 'description' },
        { title: '状态', dataIndex: 'status', key: 'status', render: (v: string) => <Badge color={v === 'completed' ? 'green' : v === 'pending' ? 'gold' : 'red'} text={v} /> },
        { title: '参考号', dataIndex: 'reference_number', key: 'reference_number' },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ fontSize: 24, fontWeight: 700 }}>Wise多币种账户管理</h1>
                <div style={{ display: 'flex', gap: 8 }}>
                    <Button onClick={syncBalancesToDb} loading={loading} type="default">同步余额到数据库</Button>
                    <Button onClick={syncTransactionsToDb} loading={loading} type="default">同步交易到数据库</Button>
                    <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading} type="primary">刷新数据</Button>
                </div>
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
            {/* 下方三张卡片 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                    <Card loading={configLoading}>
                        <div>API配置：{configError ? <span style={{ color: 'red' }}>{configError}</span> : (config ? (
                            config.api_configured ? <span style={{ color: 'green' }}>已配置，BaseURL: {config.base_url}，Token: {config.token_prefix}</span> : <span style={{ color: 'red' }}>未配置</span>
                        ) : '未配置')}</div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card loading={testLoading}>
                        <div>连接状态：{testError ? <span style={{ color: 'red' }}>{testError}</span> : (connectionStatus ? (
                            connectionStatus.private_api ? <span style={{ color: 'green' }}>连接正常</span> : <span style={{ color: 'red' }}>连接异常 {connectionStatus.private_error || ''}</span>
                        ) : '未知')}</div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card loading={summaryLoading}>
                        <div>账户汇总：{summaryError ? <span style={{ color: 'red' }}>{summaryError}</span> : (summary ? (
                            <span>总账户数: {typeof summary.total_accounts === 'number' ? summary.total_accounts : '-'}，支持货币: {typeof summary.total_currencies === 'number' ? summary.total_currencies : '-'}，总资产: ${getTotalWorth().toFixed(2)}，最近交易: {typeof summary.recent_transactions_count === 'number' ? summary.recent_transactions_count : '-'}</span>
                        ) : '-')}</div>
                    </Card>
                </Col>
            </Row>

            <Tabs defaultActiveKey="balances">
                <TabPane tab="账户余额" key="balances">
                    <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
                        <Button onClick={fetchStoredBalances} loading={loading} type="default">查看数据库余额</Button>
                        <Button onClick={syncBalancesToDb} loading={loading} type="default">同步余额到数据库</Button>
                    </div>
                    {/* Debug: 展示原始balances数据 */}
                    <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f6f6f6', fontSize: 12, marginBottom: 8 }}>{JSON.stringify(balances, null, 2)}</pre>
                    <Table
                        dataSource={Array.isArray(balances) ? balances : []}
                        columns={columnsBalances}
                        rowKey={(r) => r.account_id + r.currency}
                        loading={loading}
                        pagination={{ pageSize: 10 }}
                        scroll={{ x: 1200 }}
                        size="small"
                    />
                </TabPane>
                <TabPane tab="交易记录" key="transactions">
                    <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
                        <Button onClick={fetchStoredTransactions} loading={loading} type="default">查看数据库交易</Button>
                        <Button onClick={syncTransactionsToDb} loading={loading} type="default">同步交易到数据库</Button>
                    </div>
                    {/* Debug: 展示原始transactions数据 */}
                    <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f6f6f6', fontSize: 12, marginBottom: 8 }}>{JSON.stringify(transactions, null, 2)}</pre>

                    {/* 时间范围选择器 */}
                    <div style={{ marginBottom: 16 }}>
                        <span style={{ marginRight: 8 }}>查询时间范围：</span>
                        <Select
                            value={transactionDays}
                            onChange={setTransactionDays}
                            style={{ width: 120 }}
                            onSelect={() => fetchData()}
                        >
                            <Option value={7}>最近7天</Option>
                            <Option value={30}>最近30天</Option>
                            <Option value={90}>最近90天</Option>
                            <Option value={180}>最近180天</Option>
                            <Option value={365}>最近1年</Option>
                        </Select>
                    </div>

                    {Array.isArray(transactions) && transactions.length > 0 ? (
                        <Table
                            dataSource={transactions}
                            columns={columnsTransactions}
                            rowKey={(r) => r.transaction_id}
                            loading={loading}
                            pagination={{ pageSize: 10 }}
                        />
                    ) : (
                        <Alert
                            type="info"
                            message="暂无交易记录"
                            description="最近7天内没有交易记录，或者账户尚未开通多币种账户功能。"
                            showIcon
                        />
                    )}
                </TabPane>
                <TabPane tab="汇率查询" key="rates">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
                        <span>源货币:</span>
                        <Select style={{ width: 120 }} value={sourceCurrency} onChange={setSourceCurrency}>
                            {currencyOptions.map(opt => <Option key={opt.value} value={opt.value}>{opt.label}</Option>)}
                        </Select>
                        <span>目标货币:</span>
                        <Select style={{ width: 120 }} value={targetCurrency} onChange={setTargetCurrency}>
                            {currencyOptions.map(opt => <Option key={opt.value} value={opt.value}>{opt.label}</Option>)}
                        </Select>
                        <Button onClick={fetchExchangeRate} loading={loading} icon={<ReloadOutlined />}>刷新汇率</Button>
                    </div>
                    {exchangeRates && (
                        <Alert
                            type="info"
                            message={`1 ${sourceCurrency} = ${exchangeRates.rate} ${targetCurrency}`}
                            description={`更新时间: ${exchangeRates.time ? formatDate(exchangeRates.time) : ''}`}
                            showIcon
                        />
                    )}
                </TabPane>
            </Tabs>

            {/* 汇率历史可视化区域 */}
            <Card style={{ marginTop: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                    <Button
                        type="primary"
                        onClick={fetchHistoryRates}
                        style={{ marginRight: 16 }}
                    >
                        拉取历史汇率
                    </Button>
                    <Select
                        style={{ width: 180, marginRight: 16 }}
                        value={selectedPair ? `${selectedPair.source}/${selectedPair.target}` : undefined}
                        onChange={val => {
                            const [source, target] = val.split('/');
                            setSelectedPair({ source, target });
                        }}
                    >
                        {ratePairs.map(pair => (
                            <Select.Option key={`${pair.source}/${pair.target}`} value={`${pair.source}/${pair.target}`}>{pair.source} / {pair.target}</Select.Option>
                        ))}
                    </Select>
                    <DatePicker.RangePicker
                        value={dateRange as any}
                        onChange={range => setDateRange(range as [moment.Moment, moment.Moment])}
                        style={{ marginRight: 16 }}
                    />
                    <span>当前汇率：{latestRate !== null ? latestRate : '-'}</span>
                </div>
                {/* 临时调试输出 */}
                <pre style={{ color: '#aaa', fontSize: 12 }}>{JSON.stringify(rateHistory, null, 2)}</pre>
                {rateHistory.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#aaa', padding: 32 }}>暂无数据</div>
                ) : (
                    <Line
                        loading={rateLoading}
                        data={rateHistory}
                        xField="time"
                        yField="rate"
                        point={{ size: 3 }}
                        tooltip={{ showMarkers: true }}
                        xAxis={{
                            type: 'time',
                            label: { formatter: (v: string) => dayjs(v).format('MM-DD') },
                        }}
                        yAxis={{
                            label: { formatter: (v: number) => v.toFixed(4) },
                        }}
                        smooth
                        height={320}
                    />
                )}
            </Card>
        </div>
    );
};

export default WiseManagement; 