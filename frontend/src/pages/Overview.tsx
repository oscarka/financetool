import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Button, Table, Tag, Spin, Alert, Progress } from 'antd'
import { 
    ArrowUpOutlined, ArrowDownOutlined, 
    BarChartOutlined, FundOutlined, PieChartOutlined,
    ReloadOutlined, TrophyOutlined
} from '@ant-design/icons'

interface OverviewData {
    total_assets: number
    total_invested: number
    total_profit: number
    total_profit_rate: number
    month_profit: number
    total_positions: number
    asset_allocation: Array<{
        platform: string
        value: number
        percentage: number
    }>
    last_updated: string
}

interface PortfolioData {
    platform: string
    total_value: number
    total_profit: number
    total_invested: number
    profit_rate: number
    position_count: number
    top_positions: Array<{
        asset_code: string
        asset_name: string
        value: number
        profit_rate: number
    }>
}

interface AssetAllocationData {
    category: string
    value: number
    percentage: number
    count: number
}

const Overview: React.FC = () => {
    const [overviewData, setOverviewData] = useState<OverviewData | null>(null)
    const [portfolioData, setPortfolioData] = useState<PortfolioData[]>([])
    const [assetAllocation, setAssetAllocation] = useState<AssetAllocationData[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchOverviewData = async () => {
        try {
            setLoading(true)
            setError(null)
            
            const [overviewRes, portfolioRes, allocationRes] = await Promise.all([
                fetch('/api/v1/overview/summary'),
                fetch('/api/v1/overview/portfolio'),
                fetch('/api/v1/overview/asset-allocation')
            ])

            if (overviewRes.ok) {
                const overview = await overviewRes.json()
                setOverviewData(overview)
            }

            if (portfolioRes.ok) {
                const portfolio = await portfolioRes.json()
                setPortfolioData(portfolio)
            }

            if (allocationRes.ok) {
                const allocation = await allocationRes.json()
                setAssetAllocation(allocation)
            }
        } catch (err) {
            setError('获取数据失败，请稍后重试')
            console.error('获取总览数据失败:', err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchOverviewData()
    }, [])

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: 'CNY',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value)
    }

    const formatPercentage = (value: number) => {
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
    }

    const getProfitColor = (value: number) => {
        return value >= 0 ? '#3f8600' : '#cf1322'
    }

    const getProfitIcon = (value: number) => {
        return value >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />
    }

    const portfolioColumns = [
        {
            title: '平台',
            dataIndex: 'platform',
            key: 'platform',
            render: (platform: string) => (
                <Tag color={platform === '基金' ? 'blue' : platform === 'IBKR' ? 'green' : 'orange'}>
                    {platform}
                </Tag>
            )
        },
        {
            title: '总资产',
            dataIndex: 'total_value',
            key: 'total_value',
            render: (value: number) => formatCurrency(value)
        },
        {
            title: '总收益',
            dataIndex: 'total_profit',
            key: 'total_profit',
            render: (value: number) => (
                <span style={{ color: getProfitColor(value) }}>
                    {formatCurrency(value)}
                </span>
            )
        },
        {
            title: '收益率',
            dataIndex: 'profit_rate',
            key: 'profit_rate',
            render: (value: number) => (
                <span style={{ color: getProfitColor(value) }}>
                    {getProfitIcon(value)} {formatPercentage(value)}
                </span>
            )
        },
        {
            title: '持仓数量',
            dataIndex: 'position_count',
            key: 'position_count'
        }
    ]

    const topPositionsColumns = [
        {
            title: '资产代码',
            dataIndex: 'asset_code',
            key: 'asset_code',
            width: 120
        },
        {
            title: '资产名称',
            dataIndex: 'asset_name',
            key: 'asset_name',
            ellipsis: true
        },
        {
            title: '市值',
            dataIndex: 'value',
            key: 'value',
            render: (value: number) => formatCurrency(value)
        },
        {
            title: '收益率',
            dataIndex: 'profit_rate',
            key: 'profit_rate',
            render: (value: number) => (
                <span style={{ color: getProfitColor(value) }}>
                    {formatPercentage(value)}
                </span>
            )
        }
    ]

    if (loading) {
        return (
            <div style={{ padding: 24, textAlign: 'center' }}>
                <Spin size="large" />
                <p style={{ marginTop: 16 }}>正在加载总览数据...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div style={{ padding: 24 }}>
                <Alert
                    message="加载失败"
                    description={error}
                    type="error"
                    showIcon
                    action={
                        <Button size="small" onClick={fetchOverviewData}>
                            重试
                        </Button>
                    }
                />
            </div>
        )
    }

    return (
        <div style={{ padding: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>投资组合总览</h1>
                    <p style={{ color: '#666', margin: 0 }}>
                        最后更新: {overviewData?.last_updated ? new Date(overviewData.last_updated).toLocaleString('zh-CN') : '未知'}
                    </p>
                </div>
                <Button 
                    type="primary" 
                    icon={<ReloadOutlined />} 
                    onClick={fetchOverviewData}
                >
                    刷新数据
                </Button>
            </div>

            {/* 关键指标 */}
            {overviewData && (
                <Row gutter={16} style={{ marginBottom: 24 }}>
                    <Col xs={24} sm={12} md={6}>
                        <Card>
                            <Statistic
                                title="总资产"
                                value={overviewData.total_assets}
                                prefix="¥"
                                valueStyle={{ color: '#1890ff', fontSize: 24 }}
                            />
                        </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Card>
                            <Statistic
                                title="总收益"
                                value={overviewData.total_profit}
                                prefix="¥"
                                valueStyle={{ color: getProfitColor(overviewData.total_profit), fontSize: 24 }}
                                suffix={
                                    <span style={{ fontSize: 14 }}>
                                        {getProfitIcon(overviewData.total_profit_rate)}
                                        {formatPercentage(overviewData.total_profit_rate)}
                                    </span>
                                }
                            />
                        </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Card>
                            <Statistic
                                title="本月收益"
                                value={overviewData.month_profit}
                                prefix="¥"
                                valueStyle={{ color: getProfitColor(overviewData.month_profit), fontSize: 24 }}
                            />
                        </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Card>
                            <Statistic
                                title="持仓数量"
                                value={overviewData.total_positions}
                                valueStyle={{ fontSize: 24 }}
                                suffix="只"
                            />
                        </Card>
                    </Col>
                </Row>
            )}

            <Row gutter={16}>
                {/* 资产配置 */}
                <Col xs={24} lg={12} style={{ marginBottom: 16 }}>
                    <Card 
                        title={
                            <span>
                                <PieChartOutlined /> 资产配置
                            </span>
                        }
                    >
                        {assetAllocation.map((item, index) => (
                            <div key={item.category} style={{ marginBottom: 16 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                    <span>{item.category}</span>
                                    <span>{formatCurrency(item.value)} ({item.percentage.toFixed(1)}%)</span>
                                </div>
                                <Progress 
                                    percent={item.percentage} 
                                    strokeColor={['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'][index % 5]}
                                    showInfo={false}
                                />
                            </div>
                        ))}
                    </Card>
                </Col>

                {/* 平台投资组合 */}
                <Col xs={24} lg={12} style={{ marginBottom: 16 }}>
                    <Card 
                        title={
                            <span>
                                <BarChartOutlined /> 平台投资组合
                            </span>
                        }
                    >
                        <Table
                            dataSource={portfolioData}
                            columns={portfolioColumns}
                            pagination={false}
                            size="small"
                            rowKey="platform"
                        />
                    </Card>
                </Col>
            </Row>

            {/* 各平台持仓详情 */}
            {portfolioData.map(portfolio => (
                <Card 
                    key={portfolio.platform}
                    title={
                        <span>
                            <FundOutlined /> {portfolio.platform} 持仓详情
                        </span>
                    }
                    style={{ marginBottom: 16 }}
                >
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                        <Col span={6}>
                            <Statistic
                                title="总资产"
                                value={portfolio.total_value}
                                prefix="¥"
                                valueStyle={{ fontSize: 18 }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="总收益"
                                value={portfolio.total_profit}
                                prefix="¥"
                                valueStyle={{ color: getProfitColor(portfolio.total_profit), fontSize: 18 }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="收益率"
                                value={portfolio.profit_rate}
                                suffix="%"
                                valueStyle={{ color: getProfitColor(portfolio.profit_rate), fontSize: 18 }}
                                prefix={getProfitIcon(portfolio.profit_rate)}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="持仓数量"
                                value={portfolio.position_count}
                                suffix="只"
                                valueStyle={{ fontSize: 18 }}
                            />
                        </Col>
                    </Row>
                    
                    {portfolio.top_positions.length > 0 && (
                        <div>
                            <h4 style={{ marginBottom: 12 }}>
                                <TrophyOutlined /> 主要持仓
                            </h4>
                            <Table
                                dataSource={portfolio.top_positions}
                                columns={topPositionsColumns}
                                pagination={false}
                                size="small"
                                rowKey="asset_code"
                            />
                        </div>
                    )}
                </Card>
            ))}
        </div>
    )
}

export default Overview