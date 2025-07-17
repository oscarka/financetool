import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tabs, Badge, Alert, Select, Row, Col, Statistic, Tag, Tooltip, DatePicker, message } from 'antd';
import { ReloadOutlined, BankOutlined, DollarCircleOutlined } from '@ant-design/icons';
import api from '../services/api';
import { Line } from '@ant-design/charts';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';

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
    // 概览/汇总区块
    const [summary, setSummary] = useState<any>(null);
    const [summaryLoading, setSummaryLoading] = useState(true);
    const [summaryError, setSummaryError] = useState<string | null>(null);
    // API配置区块
    const [config, setConfig] = useState<any>(null);
    const [configLoading, setConfigLoading] = useState(true);
    const [configError, setConfigError] = useState<string | null>(null);
    // 连接状态区块
    const [connectionStatus, setConnectionStatus] = useState<any>(null);
    const [testLoading, setTestLoading] = useState(true);
    const [testError, setTestError] = useState<string | null>(null);

    // 余额区块独立状态
    const [balances, setBalances] = useState<any[]>([]);
    const [balancesLoading, setBalancesLoading] = useState(false);
    const [balancesError, setBalancesError] = useState<string | null>(null);
    const [balanceLoadTime, setBalanceLoadTime] = useState<number | null>(null);
    // 交易区块独立状态
    const [transactions, setTransactions] = useState<any[]>([]);
    const [transactionsLoading, setTransactionsLoading] = useState(false);
    const [transactionsError, setTransactionsError] = useState<string | null>(null);
    const [transactionsLoadTime, setTransactionsLoadTime] = useState<number | null>(null);
    // 汇率区块独立状态
    const [exchangeRates, setExchangeRates] = useState<any>(null);
    const [exchangeRatesLoading, setExchangeRatesLoading] = useState(false);
    const [exchangeRatesError, setExchangeRatesError] = useState<string | null>(null);
    const [exchangeRatesLoadTime, setExchangeRatesLoadTime] = useState<number | null>(null);

    const [sourceCurrency, setSourceCurrency] = useState('USD');
    const [targetCurrency, setTargetCurrency] = useState('CNY');
    const [transactionDays, setTransactionDays] = useState(90); // 默认90天
    const [ratePairs, setRatePairs] = useState<{ source: string, target: string }[]>([]);
    const [selectedPair, setSelectedPair] = useState<{ source: string, target: string } | null>(null);
    const [rateHistory, setRateHistory] = useState<any[]>([]);
    const [rateLoading, setRateLoading] = useState(false);
    const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([dayjs().subtract(30, 'days'), dayjs()]);
    const [latestRate, setLatestRate] = useState<number | null>(null);

    // 调试区域显示状态


    // 删除fetchData、fetchCardData相关的setLoading、setError、setTestLoading、setTestError等调用（如setLoading(true)、setError(null)等），只保留Tabs和下方区块原有逻辑，后续分步解耦。

    // 余额区块独立加载
    const fetchBalances = async () => {
        setBalancesLoading(true);
        setBalancesError(null);
        const start = Date.now();
        try {
            const res = await api.get('/wise/stored-balances');
            setBalances(res.data?.data || res.data || []);
            setBalanceLoadTime(Date.now() - start);
        } catch (e: any) {
            setBalancesError(e.response?.data?.detail || '获取余额失败');
        } finally {
            setBalancesLoading(false);
        }
    };
    useEffect(() => { fetchBalances(); }, []);

    // 交易区块独立加载
    const fetchTransactions = async () => {
        setTransactionsLoading(true);
        setTransactionsError(null);
        const start = Date.now();
        try {
            const params: any = { limit: 100 };
            if (transactionDays) {
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - transactionDays);
                params.from_date = startDate.toISOString().split('T')[0];
                params.to_date = endDate.toISOString().split('T')[0];
            }
            const res = await api.get('/wise/stored-transactions', { params });
            setTransactions(res.data?.data || res.data || []);
            setTransactionsLoadTime(Date.now() - start);
        } catch (e: any) {
            setTransactionsError(e.response?.data?.detail || '获取交易失败');
        } finally {
            setTransactionsLoading(false);
        }
    };
    useEffect(() => { fetchTransactions(); }, [transactionDays]);

    // 汇率区块独立加载
    const fetchExchangeRate = async () => {
        console.log('fetchExchangeRate被调用');
        setExchangeRatesLoading(true);
        setExchangeRatesError(null);
        const start = Date.now();
        try {
            const response = await api.get(`/wise/exchange-rates?source=${sourceCurrency}&target=${targetCurrency}`);
            console.log('API响应:', response.data);
            setExchangeRates(response.data);
            setExchangeRatesLoadTime(Date.now() - start);
        } catch (err: any) {
            setExchangeRatesError(err.response?.data?.detail || '获取汇率失败');
        } finally {
            setExchangeRatesLoading(false);
        }
    };
    useEffect(() => { fetchExchangeRate(); }, [sourceCurrency, targetCurrency]);

    // 概览/汇总独立加载
    useEffect(() => {
        setSummaryLoading(true);
        setSummaryError(null);
        api.get('/wise/summary')
            .then(res => setSummary(res.data?.data || res.data))
            .catch(e => setSummaryError(e.response?.data?.detail || '账户汇总获取失败'))
            .finally(() => setSummaryLoading(false));
    }, []);
    // API配置独立加载
    useEffect(() => {
        setConfigLoading(true);
        setConfigError(null);
        api.get('/wise/config')
            .then(res => setConfig(res.data?.data || res.data))
            .catch(e => setConfigError(e.response?.data?.detail || 'API配置获取失败'))
            .finally(() => setConfigLoading(false));
    }, []);
    // 连接状态独立加载
    useEffect(() => {
        setTestLoading(true);
        setTestError(null);
        api.get('/wise/test')
            .then(res => setConnectionStatus(res.data?.data || res.data))
            .catch(e => setTestError(e.response?.data?.detail || '连接状态获取失败'))
            .finally(() => setTestLoading(false));
    }, []);

    // 自动识别持有币种组合
    useEffect(() => {
        console.log('summary状态:', summary);
        console.log('summary.balance_by_currency:', summary?.balance_by_currency);

        if (summary && summary.balance_by_currency) {
            const currencies = Object.keys(summary.balance_by_currency);
            console.log('识别到的币种:', currencies);

            const pairs: { source: string, target: string }[] = [];
            for (let i = 0; i < currencies.length; i++) {
                for (let j = 0; j < currencies.length; j++) {
                    if (i !== j) pairs.push({ source: currencies[i], target: currencies[j] });
                }
            }
            console.log('生成的币种对:', pairs);

            setRatePairs(pairs);
            if (!selectedPair && pairs.length > 0) {
                console.log('设置selectedPair为:', pairs[0]);
                setSelectedPair(pairs[0]);
            }
            // 立即加载第一个币种对的历史汇率数据
            setTimeout(() => {
                if (pairs[0]) {
                    const tempSelectedPair = pairs[0];
                    const from = dateRange[0].format('YYYY-MM-DD');
                    const to = dateRange[1].format('YYYY-MM-DD');

                    // 尝试从数据库获取数据
                    api.get('/wise/exchange-rates/history', {
                        params: {
                            source: tempSelectedPair.source,
                            target: tempSelectedPair.target,
                            from_time: from,
                            to_time: to,
                            group: 'day',
                        },
                    }).then(res => {
                        if (res.data.data && res.data.data.length > 0) {
                            setRateHistory(res.data.data);
                            setLatestRate(res.data.data[res.data.data.length - 1].rate);
                        }
                    }).catch(() => {
                        // 如果数据库没有数据，静默失败，用户可以通过按钮手动获取
                    });
                }
            }, 100);
        }
    }, [summary]);

    // 拉取历史汇率
    const fetchRateHistory = async () => {
        if (!selectedPair) return;
        setRateLoading(true);
        const from = dateRange[0].format('YYYY-MM-DD');
        const to = dateRange[1].format('YYYY-MM-DD');
        try {
            // 优先从数据库获取汇率历史数据
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
            console.log('从数据库获取汇率历史失败，尝试从API获取:', e);
            // 如果数据库没有数据，尝试从API获取
            try {
                const res = await api.get('/wise/historical-rates', {
                    params: {
                        source: selectedPair.source,
                        target: selectedPair.target,
                        from_date: from,
                        to_date: to,
                        interval: 24,
                    },
                });
                setRateHistory(res.data.data || []);
                if (res.data.data && res.data.data.length > 0) {
                    setLatestRate(res.data.data[res.data.data.length - 1].rate);
                } else {
                    setLatestRate(null);
                }
            } catch (apiError) {
                console.error('从API获取汇率历史也失败:', apiError);
                setRateHistory([]);
                setLatestRate(null);
            }
        }
        setRateLoading(false);
    };

    useEffect(() => {
        if (selectedPair) fetchRateHistory();
        // eslint-disable-next-line
    }, [selectedPair, dateRange]);

    // 智能获取历史汇率数据
    const fetchHistoryRates = async () => {
        console.log('fetchHistoryRates被调用，selectedPair:', selectedPair);
        if (!selectedPair) {
            console.log('selectedPair为null，显示警告');
            message.warning('请先选择币种对');
            return;
        }
        setRateLoading(true);
        const from = dateRange[0].format('YYYY-MM-DD');
        const to = dateRange[1].format('YYYY-MM-DD');
        console.log('请求参数:', { from, to, source: selectedPair.source, target: selectedPair.target });
        try {
            // 首先尝试从数据库获取数据
            console.log('正在从数据库获取历史汇率数据...');
            const dbRes = await api.get('/wise/exchange-rates/history', {
                params: {
                    source: selectedPair.source,
                    target: selectedPair.target,
                    from_time: from,
                    to_time: to,
                    group: 'day',
                },
            });
            console.log('数据库响应:', dbRes.data);
            console.log('dbRes.data类型:', typeof dbRes.data, '是否为数组:', Array.isArray(dbRes.data));
            console.log('dbRes.data.data:', dbRes.data.data, '类型:', typeof dbRes.data.data, '是否为数组:', Array.isArray(dbRes.data.data));
            console.log('dbRes.data.data长度:', dbRes.data.data?.length);
            // 修正数据访问路径：直接使用 dbRes.data 而不是 dbRes.data.data
            const dbData = Array.isArray(dbRes.data) ? dbRes.data : (dbRes.data?.data || []);
            console.log('修正后的数据库数据:', dbData, '长度:', dbData.length);

            if (dbData && dbData.length > 0) {
                // 数据库有数据，直接显示
                console.log('数据库有数据，设置rateHistory:', dbData);

                // 数据清理：过滤掉无效的汇率数据
                const validData = dbData.filter((item: any) =>
                    item &&
                    typeof item.rate === 'number' &&
                    !isNaN(item.rate) &&
                    item.rate > 0 &&
                    item.time
                );

                console.log('数据清理后有效数据条数:', validData.length, '原始数据条数:', dbData.length);
                if (validData.length < dbData.length) {
                    console.log('过滤掉的无效数据:', dbData.filter((item: any) =>
                        !item ||
                        typeof item.rate !== 'number' ||
                        isNaN(item.rate) ||
                        item.rate <= 0 ||
                        !item.time
                    ));
                }

                setRateHistory(validData);
                if (validData.length > 0) {
                    setLatestRate(validData[validData.length - 1].rate);
                }
                message.success(`从数据库获取到 ${validData.length} 条有效历史汇率数据`);
            } else {
                // 数据库没有数据，从API获取
                console.log('数据库无数据，从API获取...');
                message.info('数据库中无数据，正在从API获取...');
                const apiRes = await api.get('/wise/historical-rates', {
                    params: {
                        source: selectedPair.source,
                        target: selectedPair.target,
                        from_date: from,
                        to_date: to,
                        interval: 24,
                    },
                });
                console.log('API响应:', apiRes.data);

                // 修正API数据访问路径
                const apiData = Array.isArray(apiRes.data) ? apiRes.data : (apiRes.data?.data || []);
                console.log('修正后的API数据:', apiData, '长度:', apiData.length);

                if (apiData && apiData.length > 0) {
                    console.log('API有数据，设置rateHistory:', apiData);

                    // 数据清理：过滤掉无效的汇率数据
                    const validApiData = apiData.filter((item: any) =>
                        item &&
                        typeof item.rate === 'number' &&
                        !isNaN(item.rate) &&
                        item.rate > 0 &&
                        item.time
                    );

                    console.log('API数据清理后有效数据条数:', validApiData.length, '原始数据条数:', apiData.length);

                    setRateHistory(validApiData);
                    setLatestRate(validApiData[validApiData.length - 1].rate);
                    message.success(`从API获取到 ${validApiData.length} 条有效历史汇率数据`);
                } else {
                    console.log('API也无数据，设置空数组');
                    setRateHistory([]);
                    setLatestRate(null);
                    message.info('API中也没有找到汇率历史数据');
                }
            }
        } catch (e: any) {
            console.error('获取汇率历史失败:', e);
            message.error(`获取汇率历史失败: ${e.response?.data?.detail || e.message}`);
            setRateHistory([]);
            setLatestRate(null);
        } finally {
            setRateLoading(false);
        }
    };

    // 从API获取最新余额数据并写入数据库
    const fetchLatestBalances = async () => {
        setBalancesLoading(true);
        setBalancesError(null);
        const start = Date.now();
        try {
            // 先同步到数据库
            const syncRes = await api.post('/wise/sync-balances');
            if (!syncRes.data.success) {
                message.error(syncRes.data.message || '同步数据库失败');
                setBalancesLoading(false);
                return;
            }
            // 再查数据库最新数据
            const res = await api.get('/wise/stored-balances');
            setBalances(res.data?.data || res.data || []);
            setBalanceLoadTime(Date.now() - start);
            message.success(`同步并获取到 ${res.data.count || 0} 条余额记录`);
        } catch (e: any) {
            setBalancesError(e.response?.data?.detail || '获取余额失败');
            message.error(`同步或获取余额失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setBalancesLoading(false);
        }
    };

    // 从API获取最新交易数据并写入数据库
    const fetchLatestTransactions = async () => {
        setTransactionsLoading(true);
        setTransactionsError(null);
        const start = Date.now();
        try {
            // 先同步到数据库
            const syncRes = await api.post('/wise/sync-transactions');
            if (!syncRes.data.success) {
                message.error(syncRes.data.message || '同步交易记录到数据库失败');
                setTransactionsLoading(false);
                return;
            }
            // 再查数据库最新数据
            const params: any = { limit: 100 };
            if (transactionDays) {
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - transactionDays);
                params.from_date = startDate.toISOString().split('T')[0];
                params.to_date = endDate.toISOString().split('T')[0];
            }
            const res = await api.get('/wise/stored-transactions', { params });
            setTransactions(res.data?.data || res.data || []);
            setTransactionsLoadTime(Date.now() - start);
            message.success(`同步并获取到 ${res.data.count || 0} 条交易记录`);
        } catch (e: any) {
            setTransactionsError(e.response?.data?.detail || '获取交易记录失败');
            message.error(`同步或获取交易记录失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setTransactionsLoading(false);
        }
    };

    // 页面加载后自动拉取一次历史汇率
    useEffect(() => {
        if (selectedPair) {
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
                <div>
                    <h1 style={{ fontSize: 24, fontWeight: 700 }}>Wise多币种账户管理</h1>
                    <p style={{ color: '#666', marginTop: 4 }}>当前显示数据库中的缓存数据，点击"从API获取最新"可获取实时数据，汇率历史优先从数据库获取</p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    <Button icon={<ReloadOutlined />} onClick={fetchBalances} loading={balancesLoading} type="primary">刷新数据</Button>
                </div>
            </div>

            {balancesError && <Alert type="error" message={balancesError} showIcon style={{ marginBottom: 16 }} />}

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
                    <Card loading={testLoading}>
                        <div>连接状态：{testError ? <span style={{ color: 'red' }}>{testError}</span> : (connectionStatus ? (
                            connectionStatus.private_api ? <span style={{ color: 'green' }}>连接正常</span> : <span style={{ color: 'red' }}>连接异常 {connectionStatus.private_error || ''}</span>
                        ) : '未知')}</div>
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
                    <Card loading={summaryLoading}>
                        <div>账户汇总：{summaryError ? <span style={{ color: 'red' }}>{summaryError}</span> : (summary ? (
                            <span>总账户数: {typeof summary.total_accounts === 'number' ? summary.total_accounts : '-'}，支持货币: {typeof summary.total_currencies === 'number' ? summary.total_currencies : '-'}，总资产: ${getTotalWorth().toFixed(2)}，最近交易: {typeof summary.recent_transactions_count === 'number' ? summary.recent_transactions_count : '-'}</span>
                        ) : '-')}</div>
                    </Card>
                </Col>
            </Row>

            <Tabs defaultActiveKey="balances">
                <TabPane tab="账户余额" key="balances">
                    <div style={{ color: '#888', fontSize: 12, marginBottom: 8 }}>
                        {balanceLoadTime !== null ? `本次数据加载耗时：${balanceLoadTime} ms` : ''}
                    </div>
                    {balancesError && <Alert type="error" message={balancesError} showIcon style={{ marginBottom: 8 }} />}
                    <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
                        <Button onClick={fetchLatestBalances} loading={balancesLoading} type="default">同步API并写入数据库</Button>
                    </div>
                    {/* Debug: 展示原始balances数据 */}
                    <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f6f6f6', fontSize: 12, marginBottom: 8 }}>{JSON.stringify(balances, null, 2)}</pre>
                    <Table
                        dataSource={Array.isArray(balances) ? balances : []}
                        columns={columnsBalances}
                        rowKey={(r) => r.account_id + r.currency}
                        loading={balancesLoading}
                        pagination={{ pageSize: 10 }}
                        scroll={{ x: 1200 }}
                        size="small"
                    />
                </TabPane>
                <TabPane tab="交易记录" key="transactions">
                    <div style={{ color: '#888', fontSize: 12, marginBottom: 8 }}>
                        {transactionsLoadTime !== null ? `本次数据加载耗时：${transactionsLoadTime} ms` : ''}
                    </div>
                    {transactionsError && <Alert type="error" message={transactionsError} showIcon style={{ marginBottom: 8 }} />}
                    <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
                        <Button onClick={fetchLatestTransactions} loading={transactionsLoading} type="default">同步API并写入数据库</Button>
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
                            loading={transactionsLoading}
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
                    <div style={{ color: '#888', fontSize: 12, marginBottom: 8 }}>
                        {exchangeRatesLoadTime !== null ? `本次数据加载耗时：${exchangeRatesLoadTime} ms` : ''}
                    </div>
                    {exchangeRatesError && <Alert type="error" message={exchangeRatesError} showIcon style={{ marginBottom: 8 }} />}

                    {/* 实时汇率查询区域 */}
                    <Card style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
                            <span>源货币:</span>
                            <Select style={{ width: 120 }} value={sourceCurrency} onChange={setSourceCurrency}>
                                {currencyOptions.map(opt => <Option key={opt.value} value={opt.value}>{opt.label}</Option>)}
                            </Select>
                            <span>目标货币:</span>
                            <Select style={{ width: 120 }} value={targetCurrency} onChange={setTargetCurrency}>
                                {currencyOptions.map(opt => <Option key={opt.value} value={opt.value}>{opt.label}</Option>)}
                            </Select>
                            <Button onClick={fetchExchangeRate} loading={exchangeRatesLoading} icon={<ReloadOutlined />}>刷新汇率</Button>
                        </div>



                        {Array.isArray(exchangeRates) && exchangeRates.length > 0 && (
                            <Alert
                                type="info"
                                message={`1 ${sourceCurrency} = ${exchangeRates[0].rate} ${targetCurrency}`}
                                description={`更新时间: ${exchangeRates[0].time ? formatDate(exchangeRates[0].time) : ''}`}
                                showIcon
                            />
                        )}
                    </Card>

                    {/* 历史汇率图表区域 */}
                    <Card>
                        <div style={{ color: '#888', fontSize: 12, marginBottom: 8 }}>
                            汇率历史最后同步时间：{
                                Array.isArray(rateHistory) && rateHistory.length > 0
                                    ? (rateHistory[rateHistory.length - 1]?.time || '-')
                                    : '-'
                            }
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                            <div style={{ marginRight: 16, padding: 4, background: '#f0f0f0', borderRadius: 4 }}>
                                selectedPair: {selectedPair ? JSON.stringify(selectedPair) : 'null'}
                            </div>
                            <Button
                                type="primary"
                                onClick={fetchHistoryRates}
                                loading={rateLoading}
                                style={{ marginRight: 16 }}
                            >
                                智能获取汇率
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
                                value={dateRange}
                                onChange={(dates) => {
                                    if (dates && dates[0] && dates[1]) {
                                        setDateRange([dates[0], dates[1]]);
                                    }
                                }}
                                style={{ marginRight: 16 }}
                                format="YYYY-MM-DD"
                                placeholder={['开始日期', '结束日期']}
                            />
                            <span>当前汇率：{latestRate !== null ? latestRate : '-'}</span>
                        </div>

                        {rateHistory.length === 0 ? (
                            <div style={{ textAlign: 'center', color: '#aaa', padding: 32 }}>暂无数据</div>
                        ) : (
                            <Line
                                loading={rateLoading}
                                data={rateHistory}
                                xField="time"
                                yField="rate"
                                point={{ size: 3 }}
                                smooth
                                height={320}
                            />
                        )}
                    </Card>
                </TabPane>
            </Tabs>
        </div>
    );
};

export default WiseManagement; 