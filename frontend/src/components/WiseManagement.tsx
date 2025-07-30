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
    { value: 'CNY', label: 'CNY - 人民币' },
    { value: 'EUR', label: 'EUR - 欧元' },
    { value: 'AUD', label: 'AUD - 澳元' },
    { value: 'JPY', label: 'JPY - 日元' },
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

    // 新增：基准币种
    const [baseCurrency, setBaseCurrency] = useState<string>('CNY');
    // 新增：币种=>基准币种汇率映射
    const [ratesMap, setRatesMap] = useState<Record<string, number>>({});
    const [ratesLoading, setRatesLoading] = useState(false);

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
            setBalancesError(e.response?.data?.detail || e.response?.data?.message || '获取余额失败');
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
            setTransactionsError(e.response?.data?.detail || e.response?.data?.message || '获取交易失败');
        } finally {
            setTransactionsLoading(false);
        }
    };
    useEffect(() => { fetchTransactions(); }, [transactionDays]);

    // 汇率区块独立加载
    const fetchExchangeRate = async () => {
        setExchangeRatesLoading(true);
        setExchangeRatesError(null);
        const start = Date.now();
        try {
            const response = await api.get(`/wise/exchange-rates?source=${sourceCurrency}&target=${targetCurrency}`);
            setExchangeRates(response.data);
            setExchangeRatesLoadTime(Date.now() - start);
        } catch (err: any) {
            setExchangeRatesError(err.response?.data?.detail || err.response?.data?.message || '获取汇率失败');
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
            .catch(e => setSummaryError(e.response?.data?.detail || e.response?.data?.message || '账户汇总获取失败'))
            .finally(() => setSummaryLoading(false));
    }, []);
    // API配置独立加载
    useEffect(() => {
        setConfigLoading(true);
        setConfigError(null);
        api.get('/wise/config')
            .then(res => setConfig(res.data?.data || res.data))
            .catch(e => setConfigError(e.response?.data?.detail || e.response?.data?.message || 'API配置获取失败'))
            .finally(() => setConfigLoading(false));
    }, []);
    // 连接状态独立加载
    useEffect(() => {
        setTestLoading(true);
        setTestError(null);
        api.get('/wise/test')
            .then(res => setConnectionStatus(res.data?.data || res.data))
            .catch(e => setTestError(e.response?.data?.detail || e.response?.data?.message || '连接状态获取失败'))
            .finally(() => setTestLoading(false));
    }, []);

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
            if (!selectedPair && pairs.length > 0) {
                setSelectedPair(pairs[0]);
            }
            // 立即加载第一个币种对的历史汇率数据
            setTimeout(() => {
                if (pairs[0]) {
                    const tempSelectedPair = pairs[0];
                    const from = dateRange[0].format('YYYY-MM-DD');
                    const to = dateRange[1].format('YYYY-MM-DD');

                    // 使用智能同步API获取数据
                    api.post('/wise/exchange-rates/smart-sync', null, {
                        params: {
                            source: tempSelectedPair.source,
                            target: tempSelectedPair.target,
                            from_date: from,
                            to_date: to,
                            group: 'day',
                        },
                    }).then(res => {
                        // 判断响应格式：如果success字段存在且为true，或者data是数组且success字段不存在，都认为是成功
                        const isSuccess = res.data.success === true ||
                            (Array.isArray(res.data) && res.data.length > 0);

                        if (isSuccess) {
                            // 如果响应直接是数组，使用响应本身；否则使用data字段
                            const rateData = Array.isArray(res.data) ? res.data : (res.data.data || []);
                            if (rateData && rateData.length > 0) {
                                setRateHistory(rateData);
                                setLatestRate(rateData[rateData.length - 1].rate);
                            }
                        }
                    }).catch(() => {
                        // 如果智能同步失败，静默失败，用户可以通过按钮手动获取
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
            // 使用智能同步API获取汇率历史数据
            const res = await api.post('/wise/exchange-rates/smart-sync', null, {
                params: {
                    source: selectedPair.source,
                    target: selectedPair.target,
                    from_date: from,
                    to_date: to,
                    group: 'day',
                },
            });

            // 判断响应格式：如果success字段存在且为true，或者data是数组且success字段不存在，都认为是成功
            const isSuccess = res.data.success === true ||
                (Array.isArray(res.data) && res.data.length > 0);

            if (isSuccess) {
                // 如果响应直接是数组，使用响应本身；否则使用data字段
                const rateData = Array.isArray(res.data) ? res.data : (res.data.data || []);
                setRateHistory(rateData);
                if (rateData && rateData.length > 0) {
                    setLatestRate(rateData[rateData.length - 1].rate);
                } else {
                    setLatestRate(null);
                }
            } else {
                const errorMsg = res.data.message || res.data.detail || '未知错误';
                console.log('智能同步失败:', errorMsg);
                setRateHistory([]);
                setLatestRate(null);
            }
        } catch (e: any) {
            const errorMsg = e.response?.data?.detail || e.response?.data?.message || e.message || '未知错误';
            console.log('智能同步获取汇率历史失败:', errorMsg);
            setRateHistory([]);
            setLatestRate(null);
        }
        setRateLoading(false);
    };

    useEffect(() => {
        if (selectedPair) fetchRateHistory();
        // eslint-disable-next-line
    }, [selectedPair, dateRange]);

    // 智能获取历史汇率数据
    const fetchHistoryRates = async () => {
        if (!selectedPair) {
            message.warning('请先选择币种对');
            return;
        }

        // 防止重复调用
        if (rateLoading) {
            return;
        }

        setRateLoading(true);
        const from = dateRange[0].format('YYYY-MM-DD');
        const to = dateRange[1].format('YYYY-MM-DD');

        try {
            // 调用智能同步API
            const smartSyncRes = await api.post('/wise/exchange-rates/smart-sync', null, {
                params: {
                    source: selectedPair.source,
                    target: selectedPair.target,
                    from_date: from,
                    to_date: to,
                    group: 'day',
                },
            });

            // 检查响应结构
            if (!smartSyncRes.data) {
                throw new Error('API响应为空');
            }

            // 判断响应格式：如果success字段存在且为true，或者data是数组且success字段不存在，都认为是成功
            const isSuccess = smartSyncRes.data.success === true ||
                (Array.isArray(smartSyncRes.data) && smartSyncRes.data.length > 0);

            if (isSuccess) {
                // 如果响应直接是数组，使用响应本身；否则使用data字段
                const syncData = Array.isArray(smartSyncRes.data) ? smartSyncRes.data : (smartSyncRes.data.data || []);

                // 数据清理：过滤掉无效的汇率数据
                const validData = syncData.filter((item: any) =>
                    item &&
                    typeof item.rate === 'number' &&
                    !isNaN(item.rate) &&
                    item.rate > 0 &&
                    item.time
                );

                // 数据格式转换：确保time字段正确
                const formattedData = validData.map((item: any) => ({
                    ...item,
                    time: item.time ? new Date(item.time).toISOString().split('T')[0] : item.time
                }));

                setRateHistory(formattedData);
                if (formattedData.length > 0) {
                    setLatestRate(formattedData[formattedData.length - 1].rate);
                }

                // 显示同步结果信息
                const syncInfo = smartSyncRes.data;
                if (syncInfo.synced_from_api) {
                    message.success(`智能同步完成！从API获取了 ${syncInfo.missing_dates_count} 天的缺失数据，共 ${formattedData.length} 条有效汇率数据`);
                } else {
                    message.success(`从数据库获取到 ${formattedData.length} 条有效历史汇率数据`);
                }
            } else {
                const errorMsg = smartSyncRes.data.message || smartSyncRes.data.detail || '未知错误';
                message.error(`智能同步失败: ${errorMsg}`);
                setRateHistory([]);
                setLatestRate(null);
            }
        } catch (e: any) {
            console.error('智能获取汇率历史失败:', e);
            const errorMsg = e.response?.data?.detail || e.response?.data?.message || e.message || '未知错误';
            message.error(`智能获取汇率历史失败: ${errorMsg}`);
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
                const errorMsg = syncRes.data.message || syncRes.data.detail || '同步数据库失败';
                message.error(errorMsg);
                setBalancesLoading(false);
                return;
            }
            // 再查数据库最新数据
            const res = await api.get('/wise/stored-balances');
            setBalances(res.data?.data || res.data || []);
            setBalanceLoadTime(Date.now() - start);
            message.success(`同步并获取到 ${res.data.count || 0} 条余额记录`);
        } catch (e: any) {
            setBalancesError(e.response?.data?.detail || e.response?.data?.message || '获取余额失败');
            message.error(`同步或获取余额失败: ${e.response?.data?.detail || e.response?.data?.message || e.message}`);
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
            // 先同步到数据库，带上天数参数
            const syncRes = await api.post('/wise/sync-transactions', { days: transactionDays });
            if (!syncRes.data.success) {
                const errorMsg = syncRes.data.message || syncRes.data.detail || '同步交易记录到数据库失败';
                message.error(errorMsg);
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
            setTransactionsError(e.response?.data?.detail || e.response?.data?.message || '获取交易记录失败');
            message.error(`同步或获取交易记录失败: ${e.response?.data?.detail || e.response?.data?.message || e.message}`);
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

    // 获取所有币种到基准币种的汇率
    const fetchAllRates = async (target: string) => {
        if (!summary?.balance_by_currency) return;
        setRatesLoading(true);
        const currencies = Object.keys(summary.balance_by_currency);
        const newRates: Record<string, number> = {};
        try {
            await Promise.all(currencies.map(async (cur) => {
                if (cur === target) {
                    newRates[cur] = 1;
                } else {
                    const res: any = await api.get(`/wise/exchange-rates?source=${cur}&target=${target}`);
                    // 兼容返回数组或对象
                    let rate = 1;
                    if (Array.isArray(res.data) && res.data.length > 0) {
                        rate = res.data[0].rate;
                    } else if (res.data?.rate) {
                        rate = res.data.rate;
                    }
                    newRates[cur] = rate;
                }
            }));
            setRatesMap(newRates);
        } catch (e: any) {
            // setRatesError(e.response?.data?.detail || '获取汇率失败'); // 已删除
        } finally {
            setRatesLoading(false);
        }
    };

    // 监听基准币种或summary变化时刷新汇率
    useEffect(() => {
        fetchAllRates(baseCurrency);
        // eslint-disable-next-line
    }, [baseCurrency, summary]);

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

    // 计算折算后的总资产
    const getTotalWorthInBase = (): number => {
        if (!summary || !summary.balance_by_currency) return 0;
        let total = 0;
        Object.entries(summary.balance_by_currency).forEach(([cur, amount]) => {
            const rate = ratesMap[cur] || 0;
            total += (typeof amount === 'number' ? amount : 0) * rate;
        });
        return total;
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
            width: 140,
            render: (v: number, r: any) => {
                const rate = ratesMap[r.currency] || 0;
                const baseValue = v * rate;
                return (
                    <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
                        {ratesLoading ? '...' : `≈${formatCurrency(baseValue, baseCurrency)}`}
                    </span>
                );
            }
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

    // 优化交易记录表格列
    const columnsTransactions = [
        {
            title: '日期',
            dataIndex: 'createdOn',
            key: 'createdOn',
            render: (v: string, r: any) => {
                const date = v || r.date || r.created_at || r.created_at;
                return date ? new Date(date).toLocaleString('zh-CN') : '-';
            }
        },
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
            render: (v: string) => {
                if (v === 'INTERBALANCE') return '币种互转';
                if (v === 'TRANSFER') return '外部转账';
                return v || '-';
            }
        },
        {
            title: '金额',
            key: 'amount',
            render: (_: any, r: any) => {
                if (r.amount && r.currency) {
                    return `${r.amount} ${r.currency}`;
                }
                return '-';
            }
        },
        {
            title: '转出金额',
            key: 'secondaryAmount',
            render: (_: any, r: any) => {
                // 优先新字段
                if (r.secondary_amount_value && r.secondary_amount_currency) {
                    return `${r.secondary_amount_value} ${r.secondary_amount_currency}`;
                }
                // 兼容老字段
                if (r.secondaryAmount) {
                    return r.secondaryAmount.replace('<positive>', '').replace('</positive>', '').trim();
                }
                return '-';
            }
        },
        {
            title: '转入金额',
            key: 'primaryAmount',
            render: (_: any, r: any) => {
                if (r.primary_amount_value && r.primary_amount_currency) {
                    return `${r.primary_amount_value} ${r.primary_amount_currency}`;
                }
                if (r.primaryAmount) {
                    return r.primaryAmount.replace('<positive>', '').replace('</positive>', '').trim();
                }
                return '-';
            }
        },
        {
            title: '目标账户/方向',
            key: 'target',
            render: (_: any, r: any) => {
                // INTERBALANCE类型优先解析title
                if (r.type === 'INTERBALANCE') {
                    // title如“To your JPY balance”或“To your AUD balance”
                    return r.title ? r.title.replace(/<[^>]+>/g, '').replace('To ', '').trim() : '-';
                }
                // TRANSFER类型显示title（如“PAYPAL AUSTRALIA”）
                if (r.type === 'TRANSFER') {
                    return r.title ? r.title.replace(/<[^>]+>/g, '').trim() : '-';
                }
                return '-';
            }
        },
        {
            title: '备注',
            key: 'remark',
            render: (_: any, r: any) => {
                // INTERBALANCE类型备注优先显示description，有title时补充显示币种方向
                if (r.type === 'INTERBALANCE') {
                    let remark = r.description || '';
                    // 补充币种方向
                    if (r.secondary_amount_currency && r.primary_amount_currency) {
                        remark += (remark ? ' ' : '') + `${r.secondary_amount_currency}→${r.primary_amount_currency}`;
                    }
                    return remark || '-';
                }
                // TRANSFER类型备注优先显示title+description
                if (r.type === 'TRANSFER') {
                    let remark = '';
                    if (r.title) remark += r.title.replace(/<[^>]+>/g, '').trim();
                    if (r.description) remark += (remark ? ' ' : '') + r.description;
                    return remark || '-';
                }
                // 其他类型兼容老逻辑
                let remark = '';
                if (r.description) remark += r.description;
                if (r.title) remark += (remark ? ' ' : '') + r.title.replace(/<[^>]+>/g, '').trim();
                return remark || '-';
            }
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (v: string) => v || '-'
        },
        {
            title: '参考号',
            key: 'reference',
            render: (_: any, r: any) => {
                // INTERBALANCE类型resource.id，TRANSFER类型resource.id
                if (r.resource && r.resource.id) return r.resource.id;
                if (r.reference_number) return r.reference_number;
                return '-';
            }
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontWeight: 700 }}>Wise多币种账户管理</h1>
                    <p style={{ color: '#666', marginTop: 4 }}>当前显示数据库中的缓存数据，点击"从API获取最新"可获取实时数据，汇率历史优先从数据库获取</p>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span>基准币种：</span>
                    <Select
                        style={{ width: 120 }}
                        value={baseCurrency}
                        onChange={setBaseCurrency}
                        options={currencyOptions}
                        loading={ratesLoading}
                    />
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
                        <Statistic
                            title={`总资产价值（${baseCurrency}）`}
                            value={ratesLoading ? '...' : getTotalWorthInBase().toFixed(2)}
                            prefix={baseCurrency === 'CNY' ? '￥' : baseCurrency === 'USD' ? '$' : baseCurrency === 'EUR' ? '€' : baseCurrency === 'JPY' ? '¥' : baseCurrency === 'AUD' ? 'A$' : ''}
                            loading={summaryLoading}
                        />
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
                        loading={balancesLoading || ratesLoading}
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
