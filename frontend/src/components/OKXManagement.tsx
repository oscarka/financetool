import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Space, message, Row, Col, Statistic, Tag, Descriptions, Tabs, Select } from 'antd';
import { ReloadOutlined, CheckCircleOutlined, ExclamationCircleOutlined, SettingOutlined } from '@ant-design/icons';
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

interface OKXAccount {
    code: string;
    msg: string;
    data: Array<{
        adjEq: string;
        details: Array<{
            availBal: string;
            bal: string;
            ccy: string;
            cashBal: string;
            uTime: string;
        }>;
    }>;
}

export const OKXManagement: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [config, setConfig] = useState<OKXConfig | null>(null);
    const [connectionTest, setConnectionTest] = useState<OKXConnectionTest | null>(null);
    const [accountData, setAccountData] = useState<OKXAccount | null>(null);
    const [tickerData, setTickerData] = useState<any>(null);
    const [instrumentsData, setInstrumentsData] = useState<any>(null);
    const [billsData, setBillsData] = useState<any>(null);
    const [selectedInstrument, setSelectedInstrument] = useState('BTC-USDT');
    const [activeTab, setActiveTab] = useState('1');
    const [assetBalances, setAssetBalances] = useState<any[]>([]);
    const [savingsBalances, setSavingsBalances] = useState<any[]>([]);

    // 获取配置信息
    const fetchConfig = async () => {
        try {
            const response = await okxAPI.getConfig();
            if (response.success) {
                setConfig(response.data);
            }
        } catch (error) {
            message.error('获取配置信息失败');
        }
    };

    // 测试连接
    const testConnection = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.testConnection();
            setConnectionTest(response.data);
            if (response.success) {
                message.success('连接测试完成');
            } else {
                message.warning('连接测试有问题');
            }
        } catch (error) {
            message.error('连接测试失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取账户信息
    const fetchAccountData = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.getAccount();
            console.log('[OKX] 获取账户信息接口返回：', response);
            if (response.success) {
                setAccountData(response.data);
                message.success('账户信息获取成功');
            } else {
                message.error(response.message || '账户信息获取失败');
            }
        } catch (error) {
            message.error('账户信息获取失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取行情数据
    const fetchTickerData = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.getTicker(selectedInstrument);
            if (response.success) {
                setTickerData(response.data);
                message.success('行情数据获取成功');
            } else {
                message.error('行情数据获取失败');
            }
        } catch (error) {
            message.error('行情数据获取失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取交易产品信息
    const fetchInstruments = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.getInstruments('SPOT');
            if (response.success) {
                setInstrumentsData(response.data);
                message.success('交易产品信息获取成功');
            } else {
                message.error('交易产品信息获取失败');
            }
        } catch (error) {
            message.error('交易产品信息获取失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取账单流水
    const fetchBills = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.getBills({ limit: 50 });
            if (response.success) {
                setBillsData(response.data);
                message.success('账单流水获取成功');
            } else {
                message.error(response.message || '账单流水获取失败');
            }
        } catch (error) {
            message.error('账单流水获取失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取资金账户余额
    const fetchAssetBalances = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.getAssetBalances();
            console.log('[OKX] 资金账户余额接口返回：', response);
            setAssetBalances(response.data?.data || []);
            message.success('资金账户余额获取成功');
        } catch (error) {
            message.error('资金账户余额获取失败');
        } finally {
            setLoading(false);
        }
    };

    // 获取储蓄账户余额
    const fetchSavingsBalances = async () => {
        setLoading(true);
        try {
            const response = await okxAPI.getSavingsBalance();
            console.log('[OKX] 储蓄账户余额接口返回：', response);
            setSavingsBalances(response.data?.data || []);
            message.success('储蓄账户余额获取成功');
        } catch (error) {
            message.error('储蓄账户余额获取失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConfig();
        testConnection();
    }, []);

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
                    <Button type="primary" onClick={testConnection} loading={loading} icon={<ReloadOutlined />}>
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

    const renderAccountTable = () => {
        // 兼容后端返回结构
        console.log('[OKX] accountData:', accountData);
        const details = accountData?.data?.[0]?.details || [];
        console.log('[OKX] account details:', details);
        const data = details; // 不做过滤，全部显示
        console.log('[OKX] table data:', data);

        const columns = [
            { title: '币种', dataIndex: 'ccy', key: 'ccy' },
            {
                title: '余额',
                dataIndex: 'bal',
                key: 'bal',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '可用余额',
                dataIndex: 'availBal',
                key: 'availBal',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '现金余额',
                dataIndex: 'cashBal',
                key: 'cashBal',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            { title: '更新时间', dataIndex: 'uTime', key: 'uTime', render: (val: string) => val ? new Date(parseInt(val)).toLocaleString() : '-' },
        ];

        return (
            <Table
                columns={columns}
                dataSource={data}
                rowKey="ccy"
                pagination={false}
                size="small"
            />
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

    const renderBillsTable = () => {
        const bills = billsData?.data?.data || [];
        console.log('[OKX] bills:', bills);
        if (!bills.length) return <div>No data</div>;
        const columns = [
            { title: '币种', dataIndex: 'ccy', key: 'ccy' },
            { title: '类型', dataIndex: 'type', key: 'type' },
            { title: '数量', dataIndex: 'sz', key: 'sz' },
            { title: '余额', dataIndex: 'bal', key: 'bal' },
            { title: '时间', dataIndex: 'ts', key: 'ts', render: (val: string) => val ? new Date(Number(val)).toLocaleString() : '-' },
            { title: '备注', dataIndex: 'notes', key: 'notes' },
        ];
        return (
            <Table
                columns={columns}
                dataSource={bills}
                rowKey={(row) => (row as any).billId || (row as any).ts || Math.random()}
                pagination={false}
                size="small"
            />
        );
    };

    const renderAssetBalancesTable = () => {
        if (!assetBalances.length) return <div>No data</div>;
        const columns = [
            { title: '币种', dataIndex: 'ccy', key: 'ccy' },
            { title: '余额', dataIndex: 'bal', key: 'bal' },
            { title: '可用余额', dataIndex: 'availBal', key: 'availBal' },
            { title: '冻结余额', dataIndex: 'frozenBal', key: 'frozenBal' },
            { title: '更新时间', dataIndex: 'uTime', key: 'uTime', render: (val: string) => val ? new Date(Number(val)).toLocaleString() : '-' },
        ];
        return (
            <Table
                columns={columns}
                dataSource={assetBalances}
                rowKey={(row) => row.ccy + (row.uTime || Math.random())}
                pagination={false}
                size="small"
            />
        );
    };

    const renderSavingsBalancesTable = () => {
        if (!savingsBalances.length) return <div>No data</div>;
        const columns = [
            { title: '币种', dataIndex: 'ccy', key: 'ccy' },
            {
                title: '余额', dataIndex: 'amt', key: 'amt',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
            {
                title: '收益', dataIndex: 'earnings', key: 'earnings',
                render: (val: any) => {
                    const num = Number(val);
                    return isNaN(num) ? '0' : num.toFixed(8);
                }
            },
        ];
        return (
            <Table
                columns={columns}
                dataSource={savingsBalances}
                rowKey={(row) => row.ccy + (row.amt || Math.random())}
                pagination={false}
                size="small"
            />
        );
    };

    return (
        <div>
            {renderConfigCard()}

            <Card>
                <Tabs activeKey={activeTab} onChange={setActiveTab}>
                    <TabPane tab="账户信息" key="1">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchAccountData} loading={loading}>
                                获取账户信息
                            </Button>
                        </Space>
                        {accountData && renderAccountTable()}
                    </TabPane>

                    <TabPane tab="行情数据" key="2">
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
                            <Button type="primary" onClick={fetchTickerData} loading={loading}>
                                获取行情
                            </Button>
                        </Space>
                        {tickerData && renderTickerInfo()}
                    </TabPane>

                    <TabPane tab="交易产品" key="3">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchInstruments} loading={loading}>
                                获取交易产品
                            </Button>
                        </Space>
                        {instrumentsData && (
                            <div>共找到 {instrumentsData.data?.length || 0} 个交易对</div>
                        )}
                    </TabPane>

                    <TabPane tab="账单流水" key="4">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchBills} loading={loading}>
                                获取账单流水
                            </Button>
                        </Space>
                        {billsData && renderBillsTable()}
                    </TabPane>

                    <TabPane tab="资金账户余额" key="5">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchAssetBalances} loading={loading}>
                                获取资金账户余额
                            </Button>
                        </Space>
                        {assetBalances.length > 0 && renderAssetBalancesTable()}
                    </TabPane>

                    <TabPane tab="储蓄账户余额" key="6">
                        <Space style={{ marginBottom: 16 }}>
                            <Button type="primary" onClick={fetchSavingsBalances} loading={loading}>
                                获取储蓄账户余额
                            </Button>
                        </Space>
                        {savingsBalances.length > 0 && renderSavingsBalancesTable()}
                    </TabPane>
                </Tabs>
            </Card>
        </div>
    );
}; 