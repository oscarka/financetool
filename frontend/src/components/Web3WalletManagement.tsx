import React, { useState, useEffect } from 'react';
import {
    Card, 
    Button, 
    Table, 
    message, 
    Row, 
    Col, 
    Statistic, 
    Space, 
    Input, 
    Select, 
    Modal, 
    Typography,
    Tag,
    Popconfirm,
    Tooltip,
    Alert
} from 'antd';
import {
    WalletOutlined,
    SyncOutlined,
    PlusOutlined,
    DeleteOutlined,
    InfoCircleOutlined,
    DollarOutlined
} from '@ant-design/icons';
import { web3WalletAPI } from '../services/api';

const { Text, Title } = Typography;
const { Option } = Select;

interface Wallet {
    id: number;
    wallet_address: string;
    wallet_name: string;
    chain_type: string;
    connection_type: string;
    last_sync_time: string | null;
    created_at: string;
}

interface Asset {
    chain: string;
    token_symbol: string;
    token_name: string;
    token_address: string | null;
    balance: string;
    balance_formatted: string;
    usdt_price: number;
    usdt_value: number;
    is_native_token: boolean;
    sync_time: string;
    wallet_info?: {
        wallet_id: number;
        wallet_name: string;
        wallet_address: string;
        chain_type: string;
    };
}

interface Portfolio {
    total_value_usdt: number;
    wallet_count: number;
    token_count: number;
    last_update: string;
}

export const Web3WalletManagement: React.FC = () => {
    const [wallets, setWallets] = useState<Wallet[]>([]);
    const [assets, setAssets] = useState<Asset[]>([]);
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const [loading, setLoading] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [addWalletVisible, setAddWalletVisible] = useState(false);
    
    // 添加钱包表单状态
    const [newWalletAddress, setNewWalletAddress] = useState('');
    const [newWalletChain, setNewWalletChain] = useState('ethereum');
    const [newWalletName, setNewWalletName] = useState('');

    const supportedChains = [
        { value: 'ethereum', label: '以太坊 (Ethereum)' },
        { value: 'bsc', label: '币安智能链 (BSC)' },
        { value: 'polygon', label: '多边形 (Polygon)' },
        { value: 'arbitrum', label: 'Arbitrum' }
    ];

    // 获取钱包列表
    const fetchWallets = async () => {
        try {
            setLoading(true);
            const response = await web3WalletAPI.getWallets();
            if (response.success) {
                setWallets(response.data || []);
            } else {
                message.error(response.message || '获取钱包列表失败');
            }
        } catch (error: any) {
            message.error('获取钱包列表失败');
            console.error('获取钱包列表失败:', error);
        } finally {
            setLoading(false);
        }
    };

    // 获取投资组合总览
    const fetchPortfolio = async () => {
        try {
            const response = await web3WalletAPI.getPortfolio();
            if (response.success) {
                setPortfolio(response.data);
            }
        } catch (error: any) {
            console.error('获取投资组合失败:', error);
        }
    };

    // 获取所有资产
    const fetchAllAssets = async () => {
        try {
            const response = await web3WalletAPI.getAllAssets();
            if (response.success) {
                setAssets(response.data || []);
            } else {
                message.error(response.message || '获取资产列表失败');
            }
        } catch (error: any) {
            message.error('获取资产列表失败');
            console.error('获取资产列表失败:', error);
        }
    };

    // 同步所有钱包
    const syncAllWallets = async () => {
        try {
            setSyncing(true);
            message.loading('正在同步所有钱包...', 0);
            
            const response = await web3WalletAPI.syncAllWallets();
            message.destroy();
            
            if (response.success) {
                message.success(response.message);
                await Promise.all([
                    fetchWallets(),
                    fetchPortfolio(),
                    fetchAllAssets()
                ]);
            } else {
                message.error(response.message || '同步失败');
            }
        } catch (error: any) {
            message.destroy();
            message.error('同步钱包失败');
            console.error('同步钱包失败:', error);
        } finally {
            setSyncing(false);
        }
    };

    // 添加钱包
    const addWallet = async () => {
        if (!newWalletAddress.trim()) {
            message.error('请输入钱包地址');
            return;
        }

        try {
            setLoading(true);
            const response = await web3WalletAPI.addWallet({
                wallet_address: newWalletAddress.trim(),
                chain_type: newWalletChain,
                wallet_name: newWalletName.trim() || undefined
            });

            if (response.success) {
                message.success('钱包添加成功');
                setAddWalletVisible(false);
                setNewWalletAddress('');
                setNewWalletName('');
                setNewWalletChain('ethereum');
                
                // 刷新数据
                await Promise.all([
                    fetchWallets(),
                    fetchPortfolio(),
                    fetchAllAssets()
                ]);
            } else {
                message.error(response.message || '添加钱包失败');
            }
        } catch (error: any) {
            message.error('添加钱包失败');
            console.error('添加钱包失败:', error);
        } finally {
            setLoading(false);
        }
    };

    // 移除钱包
    const removeWallet = async (walletId: number) => {
        try {
            const response = await web3WalletAPI.removeWallet(walletId);
            if (response.success) {
                message.success('钱包已移除');
                await Promise.all([
                    fetchWallets(),
                    fetchPortfolio(),
                    fetchAllAssets()
                ]);
            } else {
                message.error(response.message || '移除钱包失败');
            }
        } catch (error: any) {
            message.error('移除钱包失败');
            console.error('移除钱包失败:', error);
        }
    };

    // 同步单个钱包
    const syncSingleWallet = async (walletId: number) => {
        try {
            setSyncing(true);
            const response = await web3WalletAPI.syncWallet(walletId);
            
            if (response.success) {
                message.success('钱包同步成功');
                await Promise.all([
                    fetchWallets(),
                    fetchPortfolio(),
                    fetchAllAssets()
                ]);
            } else {
                message.error(response.message || '同步失败');
            }
        } catch (error: any) {
            message.error('同步钱包失败');
            console.error('同步钱包失败:', error);
        } finally {
            setSyncing(false);
        }
    };

    // 格式化地址显示
    const formatAddress = (address: string) => {
        if (!address) return '';
        return `${address.slice(0, 6)}...${address.slice(-4)}`;
    };

    // 获取链的颜色
    const getChainColor = (chain: string) => {
        const colors: { [key: string]: string } = {
            ethereum: 'blue',
            bsc: 'gold',
            polygon: 'purple',
            arbitrum: 'cyan'
        };
        return colors[chain] || 'default';
    };

    // 钱包表格列定义
    const walletColumns = [
        {
            title: '钱包名称',
            dataIndex: 'wallet_name',
            key: 'wallet_name',
            render: (name: string, record: Wallet) => (
                <div>
                    <Text strong>{name}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                        {formatAddress(record.wallet_address)}
                    </Text>
                </div>
            ),
        },
        {
            title: '网络',
            dataIndex: 'chain_type',
            key: 'chain_type',
            render: (chain: string) => (
                <Tag color={getChainColor(chain)}>
                    {chain.toUpperCase()}
                </Tag>
            ),
        },
        {
            title: '最后同步',
            dataIndex: 'last_sync_time',
            key: 'last_sync_time',
            render: (time: string | null) => (
                time ? new Date(time).toLocaleString() : '未同步'
            ),
        },
        {
            title: '操作',
            key: 'actions',
            render: (_, record: Wallet) => (
                <Space>
                    <Tooltip title="同步钱包">
                        <Button
                            type="primary"
                            size="small"
                            icon={<SyncOutlined />}
                            loading={syncing}
                            onClick={() => syncSingleWallet(record.id)}
                        />
                    </Tooltip>
                    <Popconfirm
                        title="确定要移除这个钱包吗？"
                        onConfirm={() => removeWallet(record.id)}
                        okText="确定"
                        cancelText="取消"
                    >
                        <Button
                            type="primary"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                        />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    // 资产表格列定义
    const assetColumns = [
        {
            title: '钱包',
            key: 'wallet',
            render: (_, record: Asset) => (
                <div>
                    <Text strong>{record.wallet_info?.wallet_name}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                        {formatAddress(record.wallet_info?.wallet_address || '')}
                    </Text>
                </div>
            ),
        },
        {
            title: '网络',
            dataIndex: 'chain',
            key: 'chain',
            render: (chain: string) => (
                <Tag color={getChainColor(chain)}>
                    {chain.toUpperCase()}
                </Tag>
            ),
        },
        {
            title: '代币',
            key: 'token',
            render: (_, record: Asset) => (
                <div>
                    <Text strong>{record.token_symbol}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                        {record.token_name}
                    </Text>
                </div>
            ),
        },
        {
            title: '余额',
            dataIndex: 'balance_formatted',
            key: 'balance',
            align: 'right' as const,
            render: (balance: string) => (
                <Text strong>{balance}</Text>
            ),
        },
        {
            title: 'USDT价格',
            dataIndex: 'usdt_price',
            key: 'usdt_price',
            align: 'right' as const,
            render: (price: number) => (
                <Text>${price.toFixed(4)}</Text>
            ),
        },
        {
            title: 'USDT价值',
            dataIndex: 'usdt_value',
            key: 'usdt_value',
            align: 'right' as const,
            render: (value: number) => (
                <Text strong style={{ color: '#52c41a' }}>
                    ${value.toFixed(2)}
                </Text>
            ),
        },
    ];

    // 初始化数据
    useEffect(() => {
        const initData = async () => {
            await Promise.all([
                fetchWallets(),
                fetchPortfolio(),
                fetchAllAssets()
            ]);
        };
        
        initData();
    }, []);

    return (
        <div>
            {/* 总览卡片 */}
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="总资产价值"
                            value={portfolio?.total_value_usdt || 0}
                            precision={2}
                            prefix={<DollarOutlined />}
                            suffix="USDT"
                            valueStyle={{ color: '#3f8600' }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="钱包数量"
                            value={portfolio?.wallet_count || 0}
                            prefix={<WalletOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="代币种类"
                            value={portfolio?.token_count || 0}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="最后更新"
                            value={portfolio ? new Date(portfolio.last_update).toLocaleTimeString() : '--'}
                            valueStyle={{ fontSize: '16px', color: '#666' }}
                        />
                    </Card>
                </Col>
            </Row>

            {/* 操作按钮区域 */}
            <Card title="钱包管理" style={{ marginBottom: 24 }}>
                <Space size="large" wrap>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => setAddWalletVisible(true)}
                    >
                        添加钱包
                    </Button>
                    <Button
                        type="primary"
                        icon={<SyncOutlined />}
                        loading={syncing}
                        onClick={syncAllWallets}
                    >
                        同步所有钱包
                    </Button>
                </Space>

                <Alert
                    message="使用说明"
                    description="添加钱包地址后，系统会自动查询该地址在对应区块链上的代币余额。支持以太坊、BSC、Polygon等主流网络。"
                    type="info"
                    showIcon
                    style={{ marginTop: 16 }}
                />
            </Card>

            {/* 钱包列表 */}
            <Card title="已连接钱包" style={{ marginBottom: 24 }}>
                <Table
                    columns={walletColumns}
                    dataSource={wallets}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                    locale={{ emptyText: '暂无钱包，请先添加钱包地址' }}
                />
            </Card>

            {/* 资产列表 */}
            <Card title="资产详情">
                <Table
                    columns={assetColumns}
                    dataSource={assets}
                    rowKey={(record) => `${record.wallet_info?.wallet_id}-${record.chain}-${record.token_symbol}`}
                    loading={loading}
                    pagination={{ pageSize: 20 }}
                    locale={{ emptyText: '暂无资产数据' }}
                    scroll={{ x: 1000 }}
                />
            </Card>

            {/* 添加钱包弹窗 */}
            <Modal
                title="添加钱包"
                open={addWalletVisible}
                onOk={addWallet}
                onCancel={() => {
                    setAddWalletVisible(false);
                    setNewWalletAddress('');
                    setNewWalletName('');
                    setNewWalletChain('ethereum');
                }}
                confirmLoading={loading}
                okText="添加"
                cancelText="取消"
            >
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <div>
                        <Text strong>钱包地址 *</Text>
                        <Input
                            placeholder="请输入钱包地址，如：0x1234..."
                            value={newWalletAddress}
                            onChange={(e) => setNewWalletAddress(e.target.value)}
                            style={{ marginTop: 8 }}
                        />
                    </div>
                    
                    <div>
                        <Text strong>区块链网络 *</Text>
                        <Select
                            value={newWalletChain}
                            onChange={setNewWalletChain}
                            style={{ width: '100%', marginTop: 8 }}
                        >
                            {supportedChains.map(chain => (
                                <Option key={chain.value} value={chain.value}>
                                    {chain.label}
                                </Option>
                            ))}
                        </Select>
                    </div>
                    
                    <div>
                        <Text strong>钱包名称</Text>
                        <Input
                            placeholder="给钱包起个名字（可选）"
                            value={newWalletName}
                            onChange={(e) => setNewWalletName(e.target.value)}
                            style={{ marginTop: 8 }}
                        />
                    </div>
                </Space>
            </Modal>
        </div>
    );
};