import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Space, message, Row, Col, Statistic, Tag, Descriptions, Tabs, Select, Switch } from 'antd';
import { ReloadOutlined, CheckCircleOutlined, ExclamationCircleOutlined, SettingOutlined, DollarCircleOutlined } from '@ant-design/icons';
import { okxAPI } from '../services/api';

const { TabPane } = Tabs;
const { Option } = Select;

interface OKXConfig {
    api_configured: boolean;
    sandbox_mode: boolean;
    base_url: string;
    api_key_prefix: string;
}

interface OKXConnectionTest {
    public_api: boolean;
    private_api: boolean;
    private_error?: string;
    error?: string;
    timestamp: number;
}



export const OKXManagement: React.FC = () => {
    // 概览/汇总区块
    const [summary, setSummary] = useState<any>(null);

    // API配置区块
    const [config, setConfig] = useState<OKXConfig | null>(null);

    // 连接状态区块
    const [connectionTest, setConnectionTest] = useState<OKXConnectionTest | null>(null);
    const [testLoading, setTestLoading] = useState(true);



    // 持仓数据区块独立状态（暂时注释，避免TypeScript错误）
    // const [positionsData, setPositionsData] = useState<any[]>([]);
    // const [positionsLoading, setPositionsLoading] = useState(false);
    // const [positionsError, setPositionsError] = useState<string | null>(null);
    // const [positionsLoadTime, setPositionsLoadTime] = useState<number | null>(null);

    // 交易记录区块独立状态
    const [transactionsData, setTransactionsData] = useState<any[]>([]);
    const [transactionsLoading, setTransactionsLoading] = useState(false);
    const [transactionsError, setTransactionsError] = useState<string | null>(null);
    const [transactionsLoadTime, setTransactionsLoadTime] = useState<number | null>(null);

    // 交易账户余额区块独立状态
    const [tradingBalances, setTradingBalances] = useState<any[]>([]);
    const [tradingBalancesLoading, setTradingBalancesLoading] = useState(false);
    const [tradingBalancesError, setTradingBalancesError] = useState<string | null>(null);
    const [tradingBalancesLoadTime, setTradingBalancesLoadTime] = useState<number | null>(null);

    // 资金账户余额区块独立状态
    const [fundingBalances, setFundingBalances] = useState<any[]>([]);
    const [fundingBalancesLoading, setFundingBalancesLoading] = useState(false);
    const [fundingBalancesError, setFundingBalancesError] = useState<string | null>(null);
    const [fundingBalancesLoadTime, setFundingBalancesLoadTime] = useState<number | null>(null);

    // 储蓄账户余额区块独立状态
    const [savingsBalances, setSavingsBalances] = useState<any[]>([]);
    const [savingsBalancesLoading, setSavingsBalancesLoading] = useState(false);
    const [savingsBalancesError, setSavingsBalancesError] = useState<string | null>(null);
    const [savingsBalancesLoadTime, setSavingsBalancesLoadTime] = useState<number | null>(null);

    // Web3总额状态
    const [web3TotalBalance, setWeb3TotalBalance] = useState<any>(null);
    const [web3TotalBalanceError, setWeb3TotalBalanceError] = useState<string | null>(null);
    const [syncing, setSyncing] = useState(false); // 新增本地loading状态

    // 汇率数据状态
    const [exchangeRates, setExchangeRates] = useState<{ [key: string]: number }>({});

    // 行情数据区块独立状态
    const [tickerData, setTickerData] = useState<any>(null);
    const [tickerLoading, setTickerLoading] = useState(false);
    const [tickerError, setTickerError] = useState<string | null>(null);
    const [selectedInstrument, setSelectedInstrument] = useState('BTC-USDT');

    // 交易产品信息区块独立状态
    const [instrumentsData, setInstrumentsData] = useState<any>(null);
    const [instrumentsLoading, setInstrumentsLoading] = useState(false);
    const [instrumentsError, setInstrumentsError] = useState<string | null>(null);

    // 账单流水区块独立状态（暂时注释，避免TypeScript错误）
    // const [billsData, setBillsData] = useState<any>(null);
    // const [billsLoading, setBillsLoading] = useState(false);
    // const [billsError, setBillsError] = useState<string | null>(null);

    const [activeTab, setActiveTab] = useState('1');

    // 小额币种隐藏开关
    const [hideSmall, setHideSmall] = useState(true);

    // 数字精度开关
    const [showPreciseNumbers, setShowPreciseNumbers] = useState(true);

    // 概览/汇总独立加载
    useEffect(() => {
        okxAPI.getSummary()
            .then(res => setSummary(res.data))
            .catch(e => console.error('账户汇总获取失败:', e));
    }, []);

    // API配置独立加载
    useEffect(() => {
        okxAPI.getConfig()
            .then(res => setConfig(res.data))
            .catch(e => console.error('API配置获取失败:', e));
    }, []);

    // 连接状态独立加载
    useEffect(() => {
        setTestLoading(true);
        okxAPI.testConnection()
            .then(res => setConnectionTest(res.data))
            .catch(e => console.error('连接状态获取失败:', e))
            .finally(() => setTestLoading(false));
    }, []);



    // 从数据库获取持仓数据（暂时注释，避免TypeScript错误）
    // const fetchPositionsData = async () => {
    //     setPositionsLoading(true);
    //     setPositionsError(null);
    //     const start = Date.now();
    //     try {
    //         const response = await okxAPI.getStoredPositions();
    //         if (response.success) {
    //             setPositionsData(response.data || []);
    //             setPositionsLoadTime(Date.now() - start);
    //             message.success('持仓数据获取成功');
    //         } else {
    //             setPositionsError(response.message || '持仓数据获取失败');
    //             message.error(response.message || '持仓数据获取失败');
    //         }
    //     } catch (error: any) {
    //         setPositionsError(error.response?.data?.detail || '持仓数据获取失败');
    //         message.error('持仓数据获取失败');
    //     } finally {
    //         setPositionsLoading(false);
    //     }
    // };

    // 从数据库获取交易记录
    const fetchTransactionsData = async () => {
        setTransactionsLoading(true);
        setTransactionsError(null);
        const start = Date.now();
        try {
            const response = await okxAPI.getStoredTransactions({ limit: 100 });
            if (response.success) {
                setTransactionsData(response.data || []);
                setTransactionsLoadTime(Date.now() - start);
                message.success('交易记录获取成功');
            } else {
                setTransactionsError(response.message || '交易记录获取失败');
                message.error(response.message || '交易记录获取失败');
            }
        } catch (error: any) {
            setTransactionsError(error.response?.data?.detail || '交易记录获取失败');
            message.error('交易记录获取失败');
        } finally {
            setTransactionsLoading(false);
        }
    };

    // 从数据库获取交易账户余额
    const fetchTradingBalances = async () => {
        setTradingBalancesLoading(true);
        setTradingBalancesError(null);
        const start = Date.now();
        try {
            const response = await okxAPI.getStoredBalances();
            if (response.success) {
                // 过滤出交易账户余额
                const tradingData = (response.data || []).filter((item: any) => item.account_type === 'trading');
                setTradingBalances(tradingData);
                setTradingBalancesLoadTime(Date.now() - start);
                message.success('交易账户余额获取成功');
            } else {
                setTradingBalancesError(response.message || '交易账户余额获取失败');
                message.error(response.message || '交易账户余额获取失败');
            }
        } catch (error: any) {
            setTradingBalancesError(error.response?.data?.detail || '交易账户余额获取失败');
            message.error('交易账户余额获取失败');
        } finally {
            setTradingBalancesLoading(false);
        }
    };

    // 从数据库获取资金账户余额
    const fetchFundingBalances = async () => {
        setFundingBalancesLoading(true);
        setFundingBalancesError(null);
        const start = Date.now();
        try {
            const response = await okxAPI.getStoredBalances();
            if (response.success) {
                // 过滤出资金账户余额
                const fundingData = (response.data || []).filter((item: any) => item.account_type === 'funding');
                setFundingBalances(fundingData);
                setFundingBalancesLoadTime(Date.now() - start);
                message.success('资金账户余额获取成功');
            } else {
                setFundingBalancesError(response.message || '资金账户余额获取失败');
                message.error(response.message || '资金账户余额获取失败');
            }
        } catch (error: any) {
            setFundingBalancesError(error.response?.data?.detail || '资金账户余额获取失败');
            message.error('资金账户余额获取失败');
        } finally {
            setFundingBalancesLoading(false);
        }
    };

    // 从数据库获取储蓄账户余额
    const fetchSavingsBalances = async () => {
        setSavingsBalancesLoading(true);
        setSavingsBalancesError(null);
        const start = Date.now();
        try {
            const response = await okxAPI.getStoredBalances();
            if (response.success) {
                // 过滤出储蓄账户余额
                const savingsData = (response.data || []).filter((item: any) => item.account_type === 'savings');
                setSavingsBalances(savingsData);
                setSavingsBalancesLoadTime(Date.now() - start);
                message.success('储蓄账户余额获取成功');
            } else {
                setSavingsBalancesError(response.message || '储蓄账户余额获取失败');
                message.error(response.message || '储蓄账户余额获取失败');
            }
        } catch (error: any) {
            setSavingsBalancesError(error.response?.data?.detail || '储蓄账户余额获取失败');
            message.error('储蓄账户余额获取失败');
        } finally {
            setSavingsBalancesLoading(false);
        }
    };

    // 获取Web3总额（从数据库）
    const fetchWeb3TotalBalance = async () => {
        setWeb3TotalBalanceError(null);
        try {
            const response = await okxAPI.getStoredWeb3Balance();
            if (response.success) {
                setWeb3TotalBalance(response.data);
                message.success('Web3总额获取成功');
            } else {
                setWeb3TotalBalanceError(response.message || 'Web3总额获取失败');
                message.error(response.message || 'Web3总额获取失败');
            }
        } catch (error: any) {
            setWeb3TotalBalanceError(error.response?.data?.detail || 'Web3总额获取失败');
            message.error('Web3总额获取失败');
        }
    };

    // 获取汇率数据
    const fetchExchangeRates = async () => {
        try {
            const response = await okxAPI.getStoredMarketData();
            if (response.success) {
                const rates: { [key: string]: number } = {};
                (response.data || []).forEach((item: any) => {
                    if (item.inst_id && item.last_price) {
                        // 提取币种名称（去掉-USDT后缀）
                        const currency = item.inst_id.replace('-USDT', '');
                        rates[currency] = Number(item.last_price);
                    }
                });
                setExchangeRates(rates);
                console.log('获取到汇率数据:', rates);
            } else {
                console.warn('获取汇率数据失败:', response.message);
            }
        } catch (error: any) {
            console.error('获取汇率数据异常:', error);
        }
    };

    // 计算USDT估值
    const calculateUSDTValue = (currency: string, amount: number): number => {
        if (currency === 'USDT' || currency === 'USD') {
            return amount;
        }
        const rate = exchangeRates[currency];
        return rate ? amount * rate : 0;
    };

    // 获取行情数据（实时数据）
    const fetchTickerData = async () => {
        setTickerLoading(true);
        setTickerError(null);
        try {
            const response = await okxAPI.getTicker(selectedInstrument);
            if (response.success) {
                setTickerData(response.data);
                message.success('行情数据获取成功');
            } else {
                setTickerError(response.message || '行情数据获取失败');
                message.error(response.message || '行情数据获取失败');
            }
        } catch (error: any) {
            setTickerError(error.response?.data?.detail || '行情数据获取失败');
            message.error('行情数据获取失败');
        } finally {
            setTickerLoading(false);
        }
    };

    // 获取交易产品信息（实时数据）
    const fetchInstruments = async () => {
        setInstrumentsLoading(true);
        setInstrumentsError(null);
        try {
            const response = await okxAPI.getInstruments('SPOT');
            if (response.success) {
                setInstrumentsData(response.data);
                message.success('交易产品信息获取成功');
            } else {
                setInstrumentsError(response.message || '交易产品信息获取失败');
                message.error(response.message || '交易产品信息获取失败');
            }
        } catch (error: any) {
            setInstrumentsError(error.response?.data?.detail || '交易产品信息获取失败');
            message.error('交易产品信息获取失败');
        } finally {
            setInstrumentsLoading(false);
        }
    };

    // 获取账单流水（实时数据）（暂时注释，避免TypeScript错误）
    // const fetchBills = async () => {
    //     setBillsLoading(true);
    //     setBillsError(null);
    //     try {
    //         const response = await okxAPI.getBills({ limit: 50 });
    //         if (response.success) {
    //             setBillsData(response.data);
    //             message.success('账单流水获取成功');
    //         } else {
    //             setBillsError(response.message || '账单流水获取失败');
    //             message.error(response.message || '账单流水获取失败');
    //         }
    //     } catch (error: any) {
    //         setBillsError(error.response?.data?.detail || '账单流水获取失败');
    //         message.error('账单流水获取失败');
    //     } finally {
    //         setBillsLoading(false);
    //     }
    // };

    // 同步余额数据
    const syncBalances = async () => {
        setTradingBalancesLoading(true);
        setFundingBalancesLoading(true);
        setSavingsBalancesLoading(true);
        try {
            const response = await okxAPI.syncBalances();
            if (response.success) {
                message.success(response.message || '余额同步成功');
                // 重新获取所有余额数据
                fetchTradingBalances();
                fetchFundingBalances();
                fetchSavingsBalances();
            } else {
                message.error(response.message || '余额同步失败');
            }
        } catch (error: any) {
            message.error('余额同步失败');
        } finally {
            setTradingBalancesLoading(false);
            setFundingBalancesLoading(false);
            setSavingsBalancesLoading(false);
        }
    };

    // 同步交易记录
    const syncTransactions = async () => {
        setTransactionsLoading(true);
        try {
            const response = await okxAPI.syncTransactions(30);
            if (response.success) {
                message.success(response.message || '交易记录同步成功');
                // 重新获取交易数据
                fetchTransactionsData();
            } else {
                message.error(response.message || '交易记录同步失败');
            }
        } catch (error: any) {
            message.error('交易记录同步失败');
        } finally {
            setTransactionsLoading(false);
        }
    };

    // 同步持仓数据（暂时注释，避免TypeScript错误）
    // const syncPositions = async () => {
    //     setPositionsLoading(true);
    //     try {
    //         const response = await okxAPI.syncPositions();
    //         if (response.success) {
    //             message.success(response.message || '持仓数据同步成功');
    //             // 重新获取持仓数据
    //             fetchPositionsData();
    //         } else {
    //             message.error(response.message || '持仓数据同步失败');
    //         }
    //     } catch (error: any) {
    //         message.error('持仓数据同步失败');
    //     } finally {
    //         setPositionsLoading(false);
    //     }
    // };

    // 从API获取最新持仓数据并写入数据库（暂时注释，避免TypeScript错误）
    // const fetchLatestPositionsData = async () => {
    //     setPositionsLoading(true);
    //     setPositionsError(null);
    //     const start = Date.now();
    //     try {
    //         // 先同步到数据库
    //         const syncRes = await okxAPI.syncPositions();
    //         if (!syncRes.success) {
    //             message.error(syncRes.message || '同步持仓数据到数据库失败');
    //             setPositionsLoading(false);
    //             return;
    //         }
    //         // 再查数据库最新数据
    //         const res = await okxAPI.getStoredPositions();
    //         setPositionsData(res.data || []);
    //         setPositionsLoadTime(Date.now() - start);
    //         message.success(`同步并获取到 ${res.data?.length || 0} 条持仓记录`);
    //     } catch (e: any) {
    //         setPositionsError(e.response?.data?.detail || '获取持仓数据失败');
    //         message.error(`同步或获取持仓数据失败: ${e.response?.data?.detail || e.message}`);
    //     } finally {
    //         setPositionsLoading(false);
    //     }
    // };

    // 从API获取最新交易数据并写入数据库
    const fetchLatestTransactionsData = async () => {
        setTransactionsLoading(true);
        setTransactionsError(null);
        const start = Date.now();
        try {
            // 先同步到数据库
            const syncRes = await okxAPI.syncTransactions(30);
            if (!syncRes.success) {
                message.error(syncRes.message || '同步交易记录到数据库失败');
                setTransactionsLoading(false);
                return;
            }
            // 再查数据库最新数据
            const res = await okxAPI.getStoredTransactions({ limit: 100 });
            setTransactionsData(res.data || []);
            setTransactionsLoadTime(Date.now() - start);
            message.success(`同步并获取到 ${res.data?.length || 0} 条交易记录`);
        } catch (e: any) {
            setTransactionsError(e.response?.data?.detail || '获取交易记录失败');
            message.error(`同步或获取交易记录失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setTransactionsLoading(false);
        }
    };

    // 从API获取最新余额数据并写入数据库
    const fetchLatestBalances = async () => {
        setTradingBalancesLoading(true);
        setFundingBalancesLoading(true);
        setSavingsBalancesLoading(true);
        setTradingBalancesError(null);
        setFundingBalancesError(null);
        setSavingsBalancesError(null);
        const start = Date.now();
        try {
            // 先同步到数据库
            const syncRes = await okxAPI.syncBalances();
            if (!syncRes.success) {
                message.error(syncRes.message || '同步数据库失败');
                setTradingBalancesLoading(false);
                setFundingBalancesLoading(false);
                setSavingsBalancesLoading(false);
                return;
            }
            // 再查数据库最新数据
            const res = await okxAPI.getStoredBalances();
            const allBalances = res.data || [];

            // 按账户类型分类
            const tradingData = allBalances.filter((item: any) => item.account_type === 'trading');
            const fundingData = allBalances.filter((item: any) => item.account_type === 'funding');
            const savingsData = allBalances.filter((item: any) => item.account_type === 'savings');

            setTradingBalances(tradingData);
            setFundingBalances(fundingData);
            setSavingsBalances(savingsData);

            // 同步汇率数据
            await fetchExchangeRates();

            const totalTime = Date.now() - start;
            setTradingBalancesLoadTime(totalTime);
            setFundingBalancesLoadTime(totalTime);
            setSavingsBalancesLoadTime(totalTime);

            message.success(`同步并获取到 ${allBalances.length} 条余额记录，汇率数据已更新`);
        } catch (e: any) {
            setTradingBalancesError(e.response?.data?.detail || '获取余额失败');
            setFundingBalancesError(e.response?.data?.detail || '获取余额失败');
            setSavingsBalancesError(e.response?.data?.detail || '获取余额失败');
            message.error(`同步或获取余额失败: ${e.response?.data?.detail || e.message}`);
        } finally {
            setTradingBalancesLoading(false);
            setFundingBalancesLoading(false);
            setSavingsBalancesLoading(false);
        }
    };

    // 页面加载时自动从数据库获取数据
    useEffect(() => {
        // fetchPositionsData(); // 暂时注释，避免TypeScript错误
        fetchTransactionsData();
        fetchTradingBalances();
        fetchFundingBalances();
        fetchSavingsBalances();
        
        // 🔑 关键修复：页面初始化时获取汇率数据
        fetchExchangeRates();
    }, []);

    // 页面加载时自动获取Web3总额
    useEffect(() => {
        fetchWeb3TotalBalance();
    }, []);

    // 主动同步Web3余额到数据库
    const syncWeb3Balance = async () => {
        setSyncing(true);
        try {
            const response = await okxAPI.syncWeb3Balance();
            if (response.success && response.data?.success) {
                message.success(response.data.message || 'Web3余额同步成功');
                // 重新获取总额数据
                fetchWeb3TotalBalance();
            } else {
                message.error(response.data?.error || 'Web3余额同步失败');
            }
        } catch (error: any) {
            message.error('Web3余额同步失败');
        } finally {
            setSyncing(false);
        }
    };

    // 对余额数据按USDT估值排序，并根据小额开关过滤
    const filterAndSortByUSDTValue = (arr: any[]) => {
        let filtered = arr;
        if (hideSmall) {
            filtered = arr.filter(item => calculateUSDTValue(item.currency, Number(item.total_balance)) >= 1);
        }
        return filtered.slice().sort((a, b) => {
            const aVal = calculateUSDTValue(a.currency, Number(a.total_balance));
            const bVal = calculateUSDTValue(b.currency, Number(b.total_balance));
            return bVal - aVal;
        });
    };

    // 数字格式化函数
    const formatNumber = (val: any) => {
        if (val === undefined || val === null) return '-';

        if (showPreciseNumbers) {
            // 开启时：保留8位小数，只显示有效数字
            const num = Number(val).toFixed(8).replace(/\.?0+$/, '');
            return num;
        } else {
            // 关闭时：显示所有位数
            const num = Number(val).toFixed(20).replace(/\.?0+$/, '');
            return num;
        }
    };

    const renderConfigCard = () => (
        <Card title={<><SettingOutlined /> OKX API 配置</>} style={{ marginBottom: 16 }}>
            <Row gutter={16}>
                <Col span={6}>
                    <Statistic
                        title="API状态"
                        value={config?.api_configured ? "已配置" : "未配置"}
                        valueStyle={{ color: config?.api_configured ? '#3f8600' : '#cf1322' }}
                    />
                </Col>
                <Col span={6}>
                    <Statistic
                        title="环境模式"
                        value={config?.sandbox_mode ? "沙盒" : "正式"}
                        valueStyle={{ color: config?.sandbox_mode ? '#fa8c16' : '#3f8600' }}
                    />
                </Col>
                <Col span={6}>
                    <Statistic
                        title="API Key"
                        value={config?.api_key_prefix || "未配置"}
                    />
                </Col>
                <Col span={6}>
                    <Button type="primary" onClick={() => {
                        setTestLoading(true);
                        okxAPI.testConnection()
                            .then(res => setConnectionTest(res.data))
                            .catch(e => console.error('连接状态获取失败:', e))
                            .finally(() => setTestLoading(false));
                    }} loading={testLoading} icon={<ReloadOutlined />}>
                        测试连接
                    </Button>
                </Col>
            </Row>
            {connectionTest && (
                <div style={{ marginTop: 16 }}>
                    <Descriptions title="连接测试结果" size="small" column={3}>
                        <Descriptions.Item label="公共接口">
                            <Tag color={connectionTest.public_api ? 'success' : 'error'}>
                                {connectionTest.public_api ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                                {connectionTest.public_api ? ' 正常' : ' 异常'}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="私有接口">
                            <Tag color={connectionTest.private_api ? 'success' : 'error'}>
                                {connectionTest.private_api ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                                {connectionTest.private_api ? ' 正常' : ' 异常'}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="测试时间">
                            {new Date(connectionTest.timestamp * 1000).toLocaleString()}
                        </Descriptions.Item>
                        {connectionTest.private_error && (
                            <Descriptions.Item label="错误信息" span={3}>
                                <Tag color="error">{connectionTest.private_error}</Tag>
                            </Descriptions.Item>
                        )}
                    </Descriptions>
                </div>
            )}
        </Card>
    );

    const renderSummaryCard = () => {
        // 计算OKX三账户USDT估值合计
        const getOKXTotalUSDT = () => {
            let tradingUSDT = 0;
            tradingBalances.forEach((item: any) => {
                tradingUSDT += calculateUSDTValue(item.currency, Number(item.total_balance));
            });
            let fundingUSDT = 0;
            fundingBalances.forEach((item: any) => {
                fundingUSDT += calculateUSDTValue(item.currency, Number(item.total_balance));
            });
            let savingsUSDT = 0;
            savingsBalances.forEach((item: any) => {
                savingsUSDT += calculateUSDTValue(item.currency, Number(item.total_balance));
            });
            return tradingUSDT + fundingUSDT + savingsUSDT;
        };

        // 统计币种
        const allCoins: { currency: string, usdtValue: number }[] = [];
        tradingBalances.forEach((item: any) => {
            allCoins.push({ currency: item.currency, usdtValue: calculateUSDTValue(item.currency, Number(item.total_balance)) });
        });
        fundingBalances.forEach((item: any) => {
            allCoins.push({ currency: item.currency, usdtValue: calculateUSDTValue(item.currency, Number(item.total_balance)) });
        });
        savingsBalances.forEach((item: any) => {
            allCoins.push({ currency: item.currency, usdtValue: calculateUSDTValue(item.currency, Number(item.total_balance)) });
        });
        // 主持仓数量：USDT估值>=1的币种（去重）
        const mainCoinSet = new Set(
            allCoins.filter(c => c.usdtValue >= 1).map(c => c.currency)
        );
        // 总持仓数量：所有币种（去重）
        const allCoinSet = new Set(allCoins.map(c => c.currency));

        const okxTotalUSDT = getOKXTotalUSDT();
        const web3USD = web3TotalBalance?.total_value ? Number(web3TotalBalance.total_value) : 0;
        const totalAssets = okxTotalUSDT + web3USD;

        return (
            <Card title={<><DollarCircleOutlined /> OKX 账户汇总</>} style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                    <Col span={6}>
                        <Statistic
                            title="总资产 (USD)"
                            value={totalAssets.toFixed(2)}
                            precision={2}
                            valueStyle={{ color: '#3f8600' }}
                            prefix="$"
                        />
                    </Col>
                    <Col span={6}>
                        <Statistic
                            title="总资产 (CNY)"
                            value={summary?.total_balance_cny?.toFixed(2) || 0}
                            precision={2}
                            valueStyle={{ color: '#3f8600' }}
                            prefix="¥"
                        />
                    </Col>
                    <Col span={6}>
                        <Statistic
                            title="持仓数量"
                            value={mainCoinSet.size}
                            valueStyle={{ color: '#1890ff' }}
                        />
                        <div style={{ color: '#888', fontSize: 12, marginTop: 2 }}>
                            包含所有小额币种后总持仓数量：{allCoinSet.size}
                        </div>
                    </Col>
                    <Col span={6}>
                        <Statistic
                            title="24h交易数"
                            value={summary?.transaction_count_24h || 0}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Col>
                </Row>
                <div style={{ marginTop: 8, color: '#888', fontSize: 12 }}>
                    账户余额 {okxTotalUSDT.toFixed(2)} + web3余额 {web3USD.toFixed(2)}
                </div>
                <div style={{ marginTop: 16 }}>
                    <Space>
                        <Button type="primary" onClick={syncBalances} loading={tradingBalancesLoading || fundingBalancesLoading || savingsBalancesLoading}>
                            <ReloadOutlined /> 同步余额
                        </Button>
                        <Button onClick={syncTransactions} loading={transactionsLoading}>
                            <ReloadOutlined /> 同步交易
                        </Button>
                        {/* <Button onClick={syncPositions} loading={positionsLoading}>
                            <ReloadOutlined /> 同步持仓
                        </Button> */}
                    </Space>
                </div>
            </Card>
        );
    };



    const renderTickerInfo = () => {
        if (!tickerData?.data?.[0]) return null;

        const ticker = tickerData.data[0];
        return (
            <Descriptions column={2} size="small">
                <Descriptions.Item label="交易对">{ticker.instId}</Descriptions.Item>
                <Descriptions.Item label="最新价">{ticker.last}</Descriptions.Item>
                <Descriptions.Item label="24h最高">{ticker.high24h}</Descriptions.Item>
                <Descriptions.Item label="24h最低">{ticker.low24h}</Descriptions.Item>
                <Descriptions.Item label="24h成交量">{ticker.vol24h}</Descriptions.Item>
                <Descriptions.Item label="24h涨跌幅">{(parseFloat(ticker.last) - parseFloat(ticker.open24h)).toFixed(4)}</Descriptions.Item>
            </Descriptions>
        );
    };

    // const renderBillsTable = () => {
    //     const bills = billsData?.data?.data || [];
    //     console.log('[OKX] bills:', bills);
    //     if (!bills.length) return <div>No data</div>;
    //     const columns = [
    //         { title: '币种', dataIndex: 'ccy', key: 'ccy' },
    //         { title: '类型', dataIndex: 'type', key: 'type' },
    //         { title: '数量', dataIndex: 'sz', key: 'sz' },
    //         { title: '余额', dataIndex: 'bal', key: 'bal' },
    //         { title: '时间', dataIndex: 'ts', key: 'ts', render: (val: string) => val ? new Date(Number(val)).toLocaleString() : '-' },
    //         { title: '备注', dataIndex: 'notes', key: 'notes' },
    //     ];
    //     return (
    //         <Table
    //             columns={columns}
    //             dataSource={bills}
    //             rowKey={(row) => (row as any).billId || (row as any).ts || Math.random()}
    //             pagination={false}
    //             size="small"
    //         />
    //     );
    // };

    const renderTradingBalancesTable = () => {
        if (!tradingBalances.length) return <div>暂无交易账户余额数据</div>;
        const sorted = filterAndSortByUSDTValue(tradingBalances);
        const columns = [
            { title: '币种', dataIndex: 'currency', key: 'currency' },
            {
                title: '总余额',
                dataIndex: 'total_balance',
                key: 'total_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '可用余额',
                dataIndex: 'available_balance',
                key: 'available_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '冻结余额',
                dataIndex: 'frozen_balance',
                key: 'frozen_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: 'USDT估值',
                key: 'usdt_value',
                render: (record: any) => {
                    const amount = Number(record.total_balance);
                    const currency = record.currency;
                    const usdtValue = calculateUSDTValue(currency, amount);
                    return (
                        <span style={{ color: usdtValue > 0 ? '#3f8600' : '#999' }}>
                            {usdtValue > 0 ? `$${usdtValue.toFixed(2)}` : '-'}
                        </span>
                    );
                }
            },
            {
                title: '更新时间',
                dataIndex: 'update_time',
                key: 'update_time',
                render: (val: string) => val ? new Date(val).toLocaleString() : '-'
            },
        ];
        return (
            <div>
                <div style={{ marginBottom: 8 }}>
                    <Switch checked={hideSmall} onChange={setHideSmall} size="small" /> 隐藏小额币种（{'<'}1 USDT）
                </div>
                <Table
                    columns={columns}
                    dataSource={sorted}
                    rowKey={(row) => row.currency + (row.update_time || Math.random())}
                    pagination={false}
                    size="small"
                />
            </div>
        );
    };

    const renderFundingBalancesTable = () => {
        if (!fundingBalances.length) return <div>暂无资金账户余额数据</div>;
        const sorted = filterAndSortByUSDTValue(fundingBalances);
        const columns = [
            { title: '币种', dataIndex: 'currency', key: 'currency' },
            {
                title: '总余额',
                dataIndex: 'total_balance',
                key: 'total_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '可用余额',
                dataIndex: 'available_balance',
                key: 'available_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '冻结余额',
                dataIndex: 'frozen_balance',
                key: 'frozen_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: 'USDT估值',
                key: 'usdt_value',
                render: (record: any) => {
                    const amount = Number(record.total_balance);
                    const currency = record.currency;
                    const usdtValue = calculateUSDTValue(currency, amount);
                    return (
                        <span style={{ color: usdtValue > 0 ? '#3f8600' : '#999' }}>
                            {usdtValue > 0 ? `$${usdtValue.toFixed(2)}` : '-'}
                        </span>
                    );
                }
            },
            {
                title: '更新时间',
                dataIndex: 'update_time',
                key: 'update_time',
                render: (val: string) => val ? new Date(val).toLocaleString() : '-'
            },
        ];
        return (
            <div>
                <div style={{ marginBottom: 8 }}>
                    <Switch checked={hideSmall} onChange={setHideSmall} size="small" /> 隐藏小额币种（{'<'}1 USDT）
                </div>
                <Table
                    columns={columns}
                    dataSource={sorted}
                    rowKey={(row) => row.currency + (row.update_time || Math.random())}
                    pagination={false}
                    size="small"
                />
            </div>
        );
    };

    const renderSavingsBalancesTable = () => {
        if (!savingsBalances.length) return <div>暂无储蓄账户余额数据</div>;
        const sorted = filterAndSortByUSDTValue(savingsBalances);
        const columns = [
            { title: '币种', dataIndex: 'currency', key: 'currency' },
            {
                title: '总余额', dataIndex: 'total_balance', key: 'total_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '可用余额', dataIndex: 'available_balance', key: 'available_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '冻结余额', dataIndex: 'frozen_balance', key: 'frozen_balance',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: 'USDT估值',
                key: 'usdt_value',
                render: (record: any) => {
                    const amount = Number(record.total_balance);
                    const currency = record.currency;
                    const usdtValue = calculateUSDTValue(currency, amount);
                    return (
                        <span style={{ color: usdtValue > 0 ? '#3f8600' : '#999' }}>
                            {usdtValue > 0 ? `$${usdtValue.toFixed(2)}` : '-'}
                        </span>
                    );
                }
            },
            {
                title: '更新时间', dataIndex: 'update_time', key: 'update_time',
                render: (val: string) => val ? new Date(val).toLocaleString() : '-'
            },
        ];
        return (
            <div>
                <div style={{ marginBottom: 8 }}>
                    <Switch checked={hideSmall} onChange={setHideSmall} size="small" /> 隐藏小额币种（{'<'}1 USDT）
                </div>
                <Table
                    columns={columns}
                    dataSource={sorted}
                    rowKey={(row) => row.currency + (row.update_time || Math.random())}
                    pagination={false}
                    size="small"
                />
            </div>
        );
    };

    const renderWeb3TotalBalance = () => {
        if (!web3TotalBalance) return <div>暂无Web3总额数据</div>;

        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <Row gutter={16}>
                    <Col span={12}>
                        <Card>
                            <Statistic
                                title="Web3账户总价值"
                                value={web3TotalBalance.total_value}
                                precision={2}
                                valueStyle={{ color: '#3f8600', fontSize: '24px' }}
                                suffix="USD"
                            />
                            <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
                                货币: {web3TotalBalance.currency}
                            </div>
                        </Card>
                    </Col>
                    <Col span={12}>
                        <Card>
                            <Statistic
                                title="最后更新时间"
                                value={web3TotalBalance.update_time ? new Date(web3TotalBalance.update_time).toLocaleString() : '未知'}
                                valueStyle={{ fontSize: '14px', color: '#666' }}
                            />
                            <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
                                数据来源: {web3TotalBalance.source}
                            </div>
                        </Card>
                    </Col>
                </Row>
            </div>
        );
    };

    return (
        <div>
            {renderConfigCard()}
            {renderSummaryCard()}

            <Card>
                <Tabs activeKey={activeTab} onChange={setActiveTab}>
                    <TabPane tab="交易账户余额" key="1">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchTradingBalances} loading={tradingBalancesLoading}>
                                从数据库获取
                            </Button>
                            <Button onClick={fetchLatestBalances} loading={tradingBalancesLoading}>
                                从API同步并获取
                            </Button>
                        </Space>
                        {tradingBalancesError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {tradingBalancesError}</div>}
                        {tradingBalancesLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {tradingBalancesLoadTime}ms</div>}
                        {tradingBalances.length > 0 && renderTradingBalancesTable()}
                    </TabPane>

                    <TabPane tab="资金账户余额" key="2">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchFundingBalances} loading={fundingBalancesLoading}>
                                从数据库获取
                            </Button>
                            <Button onClick={fetchLatestBalances} loading={fundingBalancesLoading}>
                                从API同步并获取
                            </Button>
                        </Space>
                        {fundingBalancesError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {fundingBalancesError}</div>}
                        {fundingBalancesLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {fundingBalancesLoadTime}ms</div>}
                        {fundingBalances.length > 0 && renderFundingBalancesTable()}
                    </TabPane>

                    <TabPane tab="储蓄账户余额" key="3">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchSavingsBalances} loading={savingsBalancesLoading}>
                                从数据库获取
                            </Button>
                            <Button onClick={fetchLatestBalances} loading={savingsBalancesLoading}>
                                从API同步并获取
                            </Button>
                        </Space>
                        {savingsBalancesError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {savingsBalancesError}</div>}
                        {savingsBalancesLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {savingsBalancesLoadTime}ms</div>}
                        {savingsBalances.length > 0 && renderSavingsBalancesTable()}
                    </TabPane>

                    <TabPane tab="Web3总额" key="4">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={syncWeb3Balance} loading={syncing}>
                                同步并获取
                            </Button>
                        </Space>
                        {web3TotalBalanceError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {web3TotalBalanceError}</div>}
                        {renderWeb3TotalBalance()}
                    </TabPane>

                    {/* <TabPane tab="Web3账户余额" key="5">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchWeb3Balances} loading={web3BalancesLoading}>
                                获取账户余额
                            </Button>
                        </Space>
                        {web3BalancesError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {web3BalancesError}</div>}
                        {web3BalancesLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {web3BalancesLoadTime}ms</div>}
                        {web3Balances.length > 0 && renderWeb3BalancesTable()}
                    </TabPane> */}

                    {/* <TabPane tab="Web3代币列表" key="6">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchWeb3Tokens} loading={web3TokensLoading}>
                                获取代币列表
                            </Button>
                        </Space>
                        {web3TokensError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {web3TokensError}</div>}
                        {web3TokensLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {web3TokensLoadTime}ms</div>}
                        {web3Tokens.length > 0 && renderWeb3TokensTable()}
                    </TabPane>

                    <TabPane tab="Web3交易记录" key="7">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchWeb3Transactions} loading={web3TransactionsLoading}>
                                获取交易记录
                            </Button>
                        </Space>
                        {web3TransactionsError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {web3TransactionsError}</div>}
                        {web3TransactionsLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {web3TransactionsLoadTime}ms</div>}
                        {web3Transactions.length > 0 && renderWeb3TransactionsTable()}
                    </TabPane> */}

                    {/* <TabPane tab="持仓数据" key="8">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchPositionsData} loading={positionsLoading}>
                                从数据库获取
                            </Button>
                            <Button onClick={fetchLatestPositionsData} loading={positionsLoading}>
                                从API同步并获取
                            </Button>
                        </Space>
                        {positionsError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {positionsError}</div>}
                        {positionsLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {positionsLoadTime}ms</div>}
                        {positionsData.length > 0 && (
                            <Table
                                columns={[
                                    { title: '交易对', dataIndex: 'instId', key: 'instId' },
                                    { title: '持仓方向', dataIndex: 'posSide', key: 'posSide' },
                                    { title: '持仓数量', dataIndex: 'pos', key: 'pos' },
                                    { title: '开仓均价', dataIndex: 'avgPx', key: 'avgPx' },
                                    { title: '未实现盈亏', dataIndex: 'upl', key: 'upl' },
                                    { title: '杠杆倍数', dataIndex: 'lever', key: 'lever' },
                                    { title: '保证金模式', dataIndex: 'mgnMode', key: 'mgnMode' },
                                    { title: '更新时间', dataIndex: 'uTime', key: 'uTime', render: (val: string) => val ? new Date(Number(val)).toLocaleString() : '-' },
                                ]}
                                dataSource={positionsData}
                                rowKey="posId"
                                pagination={false}
                                size="small"
                            />
                        )}
                    </TabPane> */}

                    <TabPane tab="交易记录" key="9">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchTransactionsData} loading={transactionsLoading}>
                                从数据库获取
                            </Button>
                            <Button onClick={fetchLatestTransactionsData} loading={transactionsLoading}>
                                从API同步并获取
                            </Button>
                        </Space>
                        <div style={{ marginBottom: 16 }}>
                            <Switch
                                checked={showPreciseNumbers}
                                onChange={setShowPreciseNumbers}
                                checkedChildren="8位小数"
                                unCheckedChildren="全部位数"
                            />
                            <span style={{ marginLeft: 8 }}>数字精度</span>
                        </div>
                        {transactionsError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {transactionsError}</div>}
                        {transactionsLoadTime && <div style={{ color: 'green', marginBottom: 16 }}>加载时间: {transactionsLoadTime}ms</div>}
                        {transactionsData.length > 0 && (
                            <Table
                                columns={[
                                    { title: '账单类型', dataIndex: 'type_desc', key: 'type_desc' },
                                    { title: '子类型', dataIndex: 'sub_type_desc', key: 'sub_type_desc' },
                                    { title: '交易对', dataIndex: 'inst_id', key: 'inst_id' },
                                    {
                                        title: '交易数量', dataIndex: 'quantity', key: 'quantity', render: formatNumber
                                    },
                                    {
                                        title: '交易价格', dataIndex: 'price', key: 'price', render: formatNumber
                                    },
                                    {
                                        title: '手续费', dataIndex: 'fee', key: 'fee', render: formatNumber
                                    },
                                    {
                                        title: '余额', dataIndex: 'bal', key: 'bal', render: formatNumber
                                    },
                                    {
                                        title: '余额变化', dataIndex: 'bal_chg', key: 'bal_chg', render: formatNumber
                                    },
                                    { title: '货币', dataIndex: 'currency', key: 'currency' },
                                    {
                                        title: '持仓余额', dataIndex: 'pos_bal', key: 'pos_bal', render: formatNumber
                                    },
                                    { title: '交易时间', dataIndex: 'timestamp', key: 'timestamp', render: (val: string) => val ? new Date(val).toLocaleString() : '-' },
                                ]}
                                dataSource={transactionsData}
                                rowKey="transaction_id"
                                pagination={false}
                                size="small"
                            />
                        )}
                    </TabPane>

                    <TabPane tab="行情数据" key="10">
                        <Space style={{ marginBottom: 16 }}>
                            <Select
                                value={selectedInstrument}
                                onChange={setSelectedInstrument}
                                style={{ width: 120 }}
                            >
                                <Option value="BTC-USDT">BTC-USDT</Option>
                                <Option value="ETH-USDT">ETH-USDT</Option>
                                <Option value="SOL-USDT">SOL-USDT</Option>
                                <Option value="ADA-USDT">ADA-USDT</Option>
                            </Select>
                            <Button type="primary" onClick={fetchTickerData} loading={tickerLoading}>
                                获取行情
                            </Button>
                        </Space>
                        {tickerError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {tickerError}</div>}
                        {tickerData && renderTickerInfo()}
                    </TabPane>

                    <TabPane tab="交易产品" key="11">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchInstruments} loading={instrumentsLoading}>
                                获取交易产品
                            </Button>
                        </Space>
                        {instrumentsError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {instrumentsError}</div>}
                        {instrumentsData && (
                            <div>共找到 {instrumentsData.data?.length || 0} 个交易对</div>
                        )}
                    </TabPane>

                    {/* <TabPane tab="账单流水" key="12">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchBills} loading={billsLoading}>
                                获取账单流水
                            </Button>
                        </Space>
                        {billsError && <div style={{ color: 'red', marginBottom: 16 }}>错误: {billsError}</div>}
                        {billsData && renderBillsTable()}
                    </TabPane> */}
                </Tabs>
            </Card>
        </div>
    );
}; 