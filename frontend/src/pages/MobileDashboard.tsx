import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Typography, Space, Progress, Tabs } from 'antd'
import {
    PlusCircleOutlined,
    BarChartOutlined,
    PieChartOutlined,
    LineChartOutlined,
    RightOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { fundAPI } from '../services/api'
import AssetTrendChart from '../components/AssetTrendChart';
import AssetPieChart from '../components/AssetPieChart';

const { Title, Text } = Typography

interface DashboardStats {
    total_value: number | string
    total_invested: number | string
    total_profit: number | string
    total_profit_rate: number | string
    asset_count: number
    profitable_count: number
    loss_count: number
}

const MobileDashboard: React.FC = () => {
    const navigate = useNavigate()
    const [stats, setStats] = useState<DashboardStats | null>(null)
    
    // 获取持仓汇总数据
    const fetchStats = async () => {
        try {
            const response = await fundAPI.getPositionSummary()
            if (response.success && response.data) {
                setStats(response.data)
            }
        } catch (error) {
            console.error('获取统计数据失败:', error)
        }
    }

    useEffect(() => {
        fetchStats()
    }, [])

    // 安全的数字转换
    const safeNumber = (value: number | string) => {
        const numValue = typeof value === 'string' ? parseFloat(value) : value
        return isNaN(numValue) ? 0 : numValue
    }

    // 移除未使用的formatAmount和formatPercent

    const quickActions = [
        {
            title: '添加操作',
            description: '记录新的投资操作',
            icon: PlusCircleOutlined,
            color: '#1890ff',
            path: '/operations'
        },
        {
            title: '查看持仓',
            description: '查看当前投资持仓',
            icon: BarChartOutlined,
            color: '#52c41a',
            path: '/positions'
        },
        {
            title: '收益分析',
            description: '分析投资收益情况',
            icon: PieChartOutlined,
            color: '#faad14',
            path: '/analysis'
        },
        {
            title: '基金管理',
            description: '管理基金投资',
            icon: LineChartOutlined,
            color: '#722ed1',
            path: '/funds'
        }
    ]

    // 统计信息
    const totalAsset = stats ? safeNumber(stats.total_value) : 0;
    const assetTypesCount = stats ? stats.asset_count : 0;
    const change24h = stats ? safeNumber(stats.total_profit_rate) * 100 : 0;
    const accountCount = 1; // TODO: 如有多账户可补充

    const mockAssets = [
      { asset: 'BTC', amount: 2.5, cny: 432000, usd: 60000, change: 5 },
      { asset: 'ETH', amount: 10, cny: 144000, usd: 20000, change: 2 },
      { asset: 'USDT', amount: 5000, cny: 36000, usd: 5000, change: -1 },
    ];

    return (
        <div style={{ paddingBottom: '20px' }}>
            {/* 欢迎区域 */}
            <Card 
                bordered={false}
                style={{ 
                    marginBottom: 16,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white'
                }}
            >
                <Space direction="vertical" size={8}>
                    <Title level={4} style={{ color: 'white', margin: 0 }}>
                        欢迎回来！
                    </Title>
                    <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
                        {stats ? '查看您的投资概况' : '正在加载投资数据...'}
                    </Text>
                </Space>
            </Card>

            {/* Summary 卡片区 */}
            <Row gutter={8} style={{ marginBottom: 16 }}>
                <Col span={12}>
                    <Card bordered={false} style={{ background: '#f0f5ff' }}>
                        <Statistic
                            title="总资产"
                            value={totalAsset}
                            precision={2}
                            valueStyle={{ color: '#1890ff', fontWeight: 'bold', fontSize: 18 }}
                            prefix="¥"
                        />
                    </Card>
                </Col>
                <Col span={12}>
                    <Card bordered={false} style={{ background: '#f6ffed' }}>
                        <Statistic
                            title="24h涨跌"
                            value={change24h}
                            precision={2}
                            valueStyle={{ color: '#52c41a', fontWeight: 'bold', fontSize: 18 }}
                            suffix="%"
                        />
                    </Card>
                </Col>
            </Row>
            <Row gutter={8} style={{ marginBottom: 16 }}>
                <Col span={12}>
                    <Card bordered={false} style={{ background: '#fffbe6' }}>
                        <Statistic
                            title="资产种类"
                            value={assetTypesCount}
                            valueStyle={{ color: '#faad14', fontWeight: 'bold', fontSize: 18 }}
                        />
                    </Card>
                </Col>
                <Col span={12}>
                    <Card bordered={false} style={{ background: '#fff0f6' }}>
                        <Statistic
                            title="账户数"
                            value={accountCount}
                            valueStyle={{ color: '#eb2f96', fontWeight: 'bold', fontSize: 18 }}
                        />
                    </Card>
                </Col>
            </Row>
            {/* Tab分区展示资产分布、趋势、主要资产 */}
            <Tabs defaultActiveKey="pie" style={{ marginBottom: 16 }}>
                <Tabs.TabPane tab="资产分布" key="pie">
                    <AssetPieChart baseCurrency="CNY" />
                </Tabs.TabPane>
                <Tabs.TabPane tab="资产趋势" key="trend">
                    <AssetTrendChart baseCurrency="CNY" days={30} />
                </Tabs.TabPane>
                <Tabs.TabPane tab="主要资产" key="table">
                    <Card bordered={false} style={{ margin: 0, padding: 0 }}>
                        {mockAssets.map(item => (
                            <div key={item.asset} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '12px 0', borderBottom: '1px solid #f0f0f0'
                            }}>
                                <span style={{ fontWeight: 600 }}>{item.asset}</span>
                                <span>{item.amount}</span>
                                <span style={{ color: '#1890ff' }}>￥{item.cny.toLocaleString()}</span>
                                <span style={{ color: '#52c41a' }}>${item.usd.toLocaleString()}</span>
                                <span style={{ color: item.change >= 0 ? '#3f8600' : '#cf1322' }}>
                                    {item.change >= 0 ? '+' : ''}{item.change}%
                                </span>
                            </div>
                        ))}
                    </Card>
                </Tabs.TabPane>
            </Tabs>

            {/* 快速操作 */}
            <Card 
                title="快速操作" 
                bordered={false}
                style={{ marginBottom: 16 }}
            >
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                    {quickActions.map((action) => {
                        const IconComponent = action.icon
                        return (
                            <Card
                                key={action.title}
                                size="small"
                                hoverable
                                onClick={() => navigate(action.path)}
                                style={{ 
                                    cursor: 'pointer',
                                    border: `1px solid ${action.color}20`,
                                    background: `${action.color}05`
                                }}
                            >
                                <div style={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    justifyContent: 'space-between' 
                                }}>
                                    <Space>
                                        <div style={{
                                            width: '40px',
                                            height: '40px',
                                            borderRadius: '8px',
                                            background: action.color,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            <IconComponent style={{ color: 'white', fontSize: '18px' }} />
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: 'bold', marginBottom: '2px' }}>
                                                {action.title}
                                            </div>
                                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                                {action.description}
                                            </Text>
                                        </div>
                                    </Space>
                                    <RightOutlined style={{ color: '#999' }} />
                                </div>
                            </Card>
                        )
                    })}
                </Space>
            </Card>

            {/* 基金分布 */}
            {stats && (
                <Card 
                    title="基金分布" 
                    bordered={false}
                    size="small"
                >
                    <Space direction="vertical" size={8} style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text type="secondary">总基金数</Text>
                            <Text style={{ fontWeight: 'bold' }}>{stats.asset_count} 个</Text>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text type="secondary">盈利基金</Text>
                            <Text style={{ color: '#3f8600', fontWeight: 'bold' }}>{stats.profitable_count} 个</Text>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text type="secondary">亏损基金</Text>
                            <Text style={{ color: '#cf1322', fontWeight: 'bold' }}>{stats.loss_count} 个</Text>
                        </div>
                        {stats.asset_count > 0 && (
                            <div style={{ marginTop: 12 }}>
                                <Progress 
                                    percent={(stats.profitable_count / stats.asset_count) * 100}
                                    showInfo={false}
                                    strokeColor="#3f8600"
                                    trailColor="#cf1322"
                                />
                                <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    marginTop: 4,
                                    fontSize: '12px'
                                }}>
                                    <Text style={{ color: '#3f8600' }}>
                                        盈利 {((stats.profitable_count / stats.asset_count) * 100).toFixed(1)}%
                                    </Text>
                                    <Text style={{ color: '#cf1322' }}>
                                        亏损 {((stats.loss_count / stats.asset_count) * 100).toFixed(1)}%
                                    </Text>
                                </div>
                            </div>
                        )}
                    </Space>
                </Card>
            )}
        </div>
    )
}

export default MobileDashboard