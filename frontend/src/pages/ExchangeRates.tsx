import React, { useState, useEffect } from 'react';
import {
    Card,
    Table,
    Button,
    Input,
    Select,
    Space,
    Typography,
    Row,
    Col,
    Statistic,
    Alert,
    Spin,
    DatePicker,
    Divider
} from 'antd';
import { ReloadOutlined, SwapOutlined, DollarOutlined } from '@ant-design/icons';
import { exchangeRateAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

interface ExchangeRate {
    currency: string;
    currency_name: string;
    spot_buy: number;
    spot_sell: number;
    cash_buy: number;
    cash_sell: number;
    middle_rate: number;
    update_time: string;
}

interface Currency {
    code: string;
    name: string;
    symbol: string;
    rate: number;
    update_time: string;
}

const ExchangeRates: React.FC = () => {
    const [rates, setRates] = useState<ExchangeRate[]>([]);
    const [currencies, setCurrencies] = useState<Currency[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedCurrency, setSelectedCurrency] = useState<string>('USD');
    const [historicalData, setHistoricalData] = useState<any[]>([]);
    const [convertAmount, setConvertAmount] = useState<number>(100);
    const [fromCurrency, setFromCurrency] = useState<string>('USD');
    const [toCurrency, setToCurrency] = useState<string>('CNY');
    const [convertedAmount, setConvertedAmount] = useState<number | null>(null);
    const [convertLoading, setConvertLoading] = useState(false);

    // 获取所有汇率
    const fetchRates = async () => {
        setLoading(true);
        try {
            const response = await exchangeRateAPI.getAllRates();
            if (response.success) {
                setRates(response.data.rates);
            }
        } catch (error) {
            console.error('获取汇率失败:', error);
        } finally {
            setLoading(false);
        }
    };

    // 获取货币列表
    const fetchCurrencies = async () => {
        try {
            const response = await exchangeRateAPI.getCurrencyList();
            if (response.success) {
                setCurrencies(response.data.currencies);
            }
        } catch (error) {
            console.error('获取货币列表失败:', error);
        }
    };

    // 获取历史汇率
    const fetchHistoricalRates = async () => {
        try {
            const response = await exchangeRateAPI.getHistoricalRates(selectedCurrency);
            if (response.success) {
                setHistoricalData(response.data.history);
            }
        } catch (error) {
            console.error('获取历史汇率失败:', error);
        }
    };

    // 货币转换
    const handleConvert = async () => {
        setConvertLoading(true);
        try {
            const response = await exchangeRateAPI.convertCurrency(
                convertAmount,
                fromCurrency,
                toCurrency
            );
            if (response.success) {
                setConvertedAmount(response.data.converted_amount);
            }
        } catch (error) {
            console.error('货币转换失败:', error);
        } finally {
            setConvertLoading(false);
        }
    };

    useEffect(() => {
        fetchRates();
        fetchCurrencies();
    }, []);

    useEffect(() => {
        if (selectedCurrency) {
            fetchHistoricalRates();
        }
    }, [selectedCurrency]);

    const columns = [
        {
            title: '货币',
            dataIndex: 'currency',
            key: 'currency',
            width: 100,
        },
        {
            title: '现汇买入价',
            dataIndex: 'spot_buy',
            key: 'spot_buy',
            render: (value: number) => value.toFixed(4),
        },
        {
            title: '现汇卖出价',
            dataIndex: 'spot_sell',
            key: 'spot_sell',
            render: (value: number) => value.toFixed(4),
        },
        {
            title: '现钞买入价',
            dataIndex: 'cash_buy',
            key: 'cash_buy',
            render: (value: number) => value.toFixed(4),
        },
        {
            title: '现钞卖出价',
            dataIndex: 'cash_sell',
            key: 'cash_sell',
            render: (value: number) => value.toFixed(4),
        },
        {
            title: '中行折算价',
            dataIndex: 'middle_rate',
            key: 'middle_rate',
            render: (value: number) => value.toFixed(4),
        },
        {
            title: '更新时间',
            dataIndex: 'update_time',
            key: 'update_time',
            render: (value: string) => new Date(value).toLocaleString(),
        },
    ];

    const historicalColumns = [
        {
            title: '日期',
            dataIndex: 'date',
            key: 'date',
        },
        {
            title: '汇率',
            dataIndex: 'rate',
            key: 'rate',
            render: (value: number) => value.toFixed(4),
        },
        {
            title: '涨跌',
            dataIndex: 'change',
            key: 'change',
            render: (value: number) => (
                <span style={{ color: value >= 0 ? '#52c41a' : '#ff4d4f' }}>
                    {value >= 0 ? '+' : ''}{value.toFixed(4)}
                </span>
            ),
        },
        {
            title: '涨跌幅',
            dataIndex: 'change_pct',
            key: 'change_pct',
            render: (value: number) => (
                <span style={{ color: value >= 0 ? '#52c41a' : '#ff4d4f' }}>
                    {value >= 0 ? '+' : ''}{value.toFixed(2)}%
                </span>
            ),
        },
    ];

    return (
        <div>
            <Title level={2}>
                <DollarOutlined /> 汇率管理
            </Title>

            <Row gutter={[16, 16]}>
                {/* 货币转换器 */}
                <Col span={24}>
                    <Card title="货币转换器" extra={
                        <Button
                            icon={<SwapOutlined />}
                            onClick={() => {
                                const temp = fromCurrency;
                                setFromCurrency(toCurrency);
                                setToCurrency(temp);
                            }}
                        >
                            交换
                        </Button>
                    }>
                        <Row gutter={16} align="middle">
                            <Col span={6}>
                                <Input
                                    type="number"
                                    value={convertAmount}
                                    onChange={(e) => setConvertAmount(Number(e.target.value))}
                                    placeholder="输入金额"
                                    addonBefore={fromCurrency}
                                />
                            </Col>
                            <Col span={2}>
                                <SwapOutlined style={{ fontSize: '18px' }} />
                            </Col>
                            <Col span={6}>
                                <Select
                                    value={fromCurrency}
                                    onChange={setFromCurrency}
                                    style={{ width: '100%' }}
                                >
                                    {currencies.map(currency => (
                                        <Option key={currency.code} value={currency.code}>
                                            {currency.code} - {currency.name}
                                        </Option>
                                    ))}
                                </Select>
                            </Col>
                            <Col span={2}>
                                <SwapOutlined style={{ fontSize: '18px' }} />
                            </Col>
                            <Col span={6}>
                                <Select
                                    value={toCurrency}
                                    onChange={setToCurrency}
                                    style={{ width: '100%' }}
                                >
                                    {currencies.map(currency => (
                                        <Option key={currency.code} value={currency.code}>
                                            {currency.code} - {currency.name}
                                        </Option>
                                    ))}
                                </Select>
                            </Col>
                            <Col span={2}>
                                <Button
                                    type="primary"
                                    onClick={handleConvert}
                                    loading={convertLoading}
                                >
                                    转换
                                </Button>
                            </Col>
                        </Row>

                        {convertedAmount !== null && (
                            <Alert
                                message={`${convertAmount} ${fromCurrency} = ${convertedAmount.toFixed(2)} ${toCurrency}`}
                                type="success"
                                showIcon
                                style={{ marginTop: 16 }}
                            />
                        )}
                    </Card>
                </Col>

                {/* 汇率统计 */}
                <Col span={24}>
                    <Row gutter={16}>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="支持货币数量"
                                    value={currencies.length}
                                    prefix={<DollarOutlined />}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="美元汇率"
                                    value={rates.find(r => r.currency === '美元')?.middle_rate || 0}
                                    precision={4}
                                    prefix="¥"
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="欧元汇率"
                                    value={rates.find(r => r.currency === '欧元')?.middle_rate || 0}
                                    precision={4}
                                    prefix="¥"
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card>
                                <Statistic
                                    title="日元汇率"
                                    value={rates.find(r => r.currency === '日元')?.middle_rate || 0}
                                    precision={4}
                                    prefix="¥"
                                />
                            </Card>
                        </Col>
                    </Row>
                </Col>

                {/* 汇率表格 */}
                <Col span={24}>
                    <Card
                        title="实时汇率"
                        extra={
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={fetchRates}
                                loading={loading}
                            >
                                刷新
                            </Button>
                        }
                    >
                        <Table
                            columns={columns}
                            dataSource={rates}
                            rowKey="currency"
                            loading={loading}
                            pagination={{
                                pageSize: 20,
                                showSizeChanger: true,
                                showQuickJumper: true,
                            }}
                            scroll={{ x: 800 }}
                        />
                    </Card>
                </Col>

                {/* 历史汇率 */}
                <Col span={24}>
                    <Card
                        title="历史汇率走势"
                        extra={
                            <Space>
                                <Select
                                    value={selectedCurrency}
                                    onChange={setSelectedCurrency}
                                    style={{ width: 120 }}
                                >
                                    {currencies.map(currency => (
                                        <Option key={currency.code} value={currency.code}>
                                            {currency.code}
                                        </Option>
                                    ))}
                                </Select>
                                <Button
                                    icon={<ReloadOutlined />}
                                    onClick={fetchHistoricalRates}
                                >
                                    刷新
                                </Button>
                            </Space>
                        }
                    >
                        <Table
                            columns={historicalColumns}
                            dataSource={historicalData}
                            rowKey="date"
                            pagination={{
                                pageSize: 10,
                                showSizeChanger: true,
                            }}
                        />
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default ExchangeRates; 