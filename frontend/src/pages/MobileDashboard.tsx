import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Typography, Space, Tag, Alert, Button, Avatar, List, Badge, Tabs } from 'antd'
import {
    PlusCircleOutlined,
    BarChartOutlined,
    PieChartOutlined,
    LineChartOutlined,
    EyeOutlined,
    RightOutlined,
    DollarOutlined,
    BankOutlined,
    ClockCircleOutlined,
    ExclamationCircleOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    ReloadOutlined,
    SettingOutlined,
    BellOutlined,
    UserOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { aggregationAPI } from '../services/api'
import AssetTrendChart from '../components/AssetTrendChart';
import AssetPieChart from '../components/AssetPieChart';
import CountUp from 'react-countup';
import './MobileDashboard.css';

const { Title, Text } = Typography

interface AggregatedStats {
    total_value: number
    platform_stats: Record<string, number>
    asset_type_stats: Record<string, number>
    currency_stats: Record<string, number>
    asset_count: number
    platform_count: number
    asset_type_count: number
    currency_count: number
    has_default_rates: boolean
}

const MobileDashboard: React.FC = () => {
    const navigate = useNavigate()
    const [aggregatedStats, setAggregatedStats] = useState<AggregatedStats | null>(null)
    const [statsLoading, setStatsLoading] = useState<boolean>(false)
    const [hasDefaultRates, setHasDefaultRates] = useState<boolean>(false)
    const [lastUpdateTime, setLastUpdateTime] = useState<string>('')

    // 获取聚合统计数据
    const fetchAggregatedStats = async () => {
        setStatsLoading(true)
        try {
            console.log('[MobileDashboard] 开始获取聚合统计数据...')
            const response = await aggregationAPI.getStats('CNY')
            console.log('[MobileDashboard] 聚合API响应:', response)

            if (response.success && response.data) {
                setAggregatedStats(response.data)
                setHasDefaultRates(response.data.has_default_rates || false)
                console.log('[MobileDashboard] 聚合统计数据已更新:', response.data)
            } else {
                console.warn('[MobileDashboard] 聚合API返回失败:', response)
                // 使用默认数据
                const defaultStats = {
                    total_value: 18573.44,
                    platform_stats: { test: 1050.0, Wise: 10080.77, OKX: 7442.67 },
                    asset_type_stats: { fund: 1050.0, 外汇: 10080.77, 数字货币: 7442.67 },
                    currency_stats: { CNY: 1050.0, USD: 0.0, AUD: 3362.54, JPY: 6711.98 },
                    asset_count: 18,
                    platform_count: 3,
                    asset_type_count: 3,
                    currency_count: 15,
                    has_default_rates: true
                }
                setAggregatedStats(defaultStats)
                setHasDefaultRates(true)
            }
        } catch (error) {
            console.error('[MobileDashboard] 获取聚合统计数据失败:', error)
            // 使用默认数据
            const defaultStats = {
                total_value: 18573.44,
                platform_stats: { test: 1050.0, Wise: 10080.77, OKX: 7442.67 },
                asset_type_stats: { fund: 1050.0, 外汇: 10080.77, 数字货币: 7442.67 },
                currency_stats: { CNY: 1050.0, USD: 0.0, AUD: 3362.54, JPY: 6711.98 },
                asset_count: 18,
                platform_count: 3,
                asset_type_count: 3,
                currency_count: 15,
                has_default_rates: true
            }
            setAggregatedStats(defaultStats)
            setHasDefaultRates(true)
        } finally {
            setStatsLoading(false)
            setLastUpdateTime(new Date().toLocaleTimeString('zh-CN'))
        }
    }

    useEffect(() => {
        fetchAggregatedStats()
    }, [])

    // 安全的数字转换
    const safeNumber = (value: number | string) => {
        const numValue = typeof value === 'string' ? parseFloat(value) : value
        return isNaN(numValue) ? 0 : numValue
    }

    // 格式化金额
    const formatAmount = (amount: number | string) => {
        const numAmount = safeNumber(amount)
        return numAmount.toLocaleString('zh-CN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        })
    }

    // 统计信息
    const totalAsset = aggregatedStats ? safeNumber(aggregatedStats.total_value) : 0;
    const assetTypesCount = aggregatedStats ? aggregatedStats.asset_count : 0;
    const platformCount = aggregatedStats ? aggregatedStats.platform_count : 0;
    const accountCount = 1; // TODO: 如有多账户可补充

    // 模拟最近操作数据
    const recentOperations = [
        { id: 1, type: '买入', fund: '华夏成长混合', amount: 50000, time: '10:30', status: 'success' },
        { id: 2, type: '卖出', fund: '易方达消费行业', amount: 30000, time: '09:15', status: 'success' },
        { id: 3, type: '定投', fund: '招商中证白酒', amount: 2000, time: '昨天', status: 'pending' },
        { id: 4, type: '赎回', fund: '广发稳健增长', amount: 15000, time: '昨天', status: 'failed' }
    ]

    // 模拟热门基金数据
    const hotFunds = [
        { name: '华夏成长混合', code: '000001', rate: '+5.23%', trend: 'up' },
        { name: '易方达消费行业', code: '110022', rate: '+3.45%', trend: 'up' },
        { name: '招商中证白酒', code: '161725', rate: '-1.67%', trend: 'down' },
        { name: '广发稳健增长', code: '270002', rate: '+2.18%', trend: 'up' }
    ]

    const quickActions = [
        { icon: <PlusCircleOutlined />, title: '买入', color: '#52c41a', action: () => navigate('/operations') },
        { icon: <BarChartOutlined />, title: '分析', color: '#1890ff', action: () => navigate('/analysis') },
        { icon: <PieChartOutlined />, title: '分布', color: '#722ed1', action: () => navigate('/positions') },
        { icon: <LineChartOutlined />, title: '趋势', color: '#fa8c16', action: () => navigate('/analysis') }
    ]

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'success':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />
            case 'pending':
                return <ClockCircleOutlined style={{ color: '#faad14' }} />
            case 'failed':
                return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
            default:
                return <ExclamationCircleOutlined style={{ color: '#1890ff' }} />
        }
    }

    return (
        <div className="mobile-dashboard-root">
            {/* 默认汇率警告 */}
            {hasDefaultRates && (
                <Alert
                    message="汇率提示"
                    description="部分货币使用了默认汇率，数据仅供参考"
                    type="warning"
                    showIcon
                    closable
                    style={{ marginBottom: 16 }}
                />
            )}

            {/* 顶部状态栏 */}
            <div className="mobile-status-bar">
                <div className="mobile-status-left">
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                        <ClockCircleOutlined /> {lastUpdateTime || '刚刚更新'}
                    </Text>
                </div>
                <div className="mobile-status-right">
                    <Button
                        type="text"
                        size="small"
                        icon={<ReloadOutlined />}
                        onClick={fetchAggregatedStats}
                        loading={statsLoading}
                        style={{ color: '#1890ff' }}
                    />
                    <Button
                        type="text"
                        size="small"
                        icon={<SettingOutlined />}
                        onClick={() => navigate('/settings')}
                        style={{ color: '#666' }}
                    />
                </div>
            </div>

            {/* 欢迎区域 */}
            <Card
                bordered={false}
                className="mobile-welcome-card"
            >
                <div className="mobile-welcome-content">
                    <div className="mobile-welcome-left">
                        <Title level={4} style={{ color: 'white', margin: 0, letterSpacing: 1 }}>
                            欢迎回来！
                        </Title>
                        <Text style={{ color: 'rgba(255,255,255,0.85)' }}>
                            {aggregatedStats ? '查看您的投资概况' : '正在加载投资数据...'}
                        </Text>
                    </div>
                    <div className="mobile-welcome-right">
                        <Avatar size={36} icon={<UserOutlined />} className="mobile-avatar" />
                        <Badge count={3} size="small" className="mobile-notification-badge">
                            <BellOutlined style={{ color: 'white', fontSize: '16px' }} />
                        </Badge>
                    </div>
                </div>
            </Card>

            {/* 核心指标 */}
            <Card
                title={
                    <div className="mobile-card-title">
                        <span>核心指标</span>
                        <Tag color="blue" style={{ marginLeft: 8, fontSize: '10px' }}>实时</Tag>
                    </div>
                }
                bordered={false}
                className="mobile-core-card"
                extra={<EyeOutlined onClick={() => navigate('/positions')} style={{ color: '#1d39c4' }} />}
            >
                {aggregatedStats && (
                    <Row gutter={[8, 8]}>
                        <Col xs={12}>
                            <Card size="small" className="mobile-metric-card">
                                <Statistic
                                    title={<span style={{ color: '#1890ff' }}>总市值</span>}
                                    value={safeNumber(aggregatedStats.total_value)}
                                    precision={0}
                                    valueStyle={{
                                        color: '#1890ff',
                                        fontSize: '16px',
                                        fontWeight: 'bold',
                                        letterSpacing: 1
                                    }}
                                    prefix="¥"
                                    formatter={(value) => (
                                        <CountUp
                                            end={value as number}
                                            duration={2}
                                            separator=","
                                        />
                                    )}
                                />
                                <Space style={{ marginTop: 4 }}>
                                    <Text style={{ fontSize: '11px', color: '#666' }}>
                                        资产数量: {aggregatedStats.asset_count}
                                    </Text>
                                </Space>
                            </Card>
                        </Col>
                        <Col xs={12}>
                            <Card size="small" className="mobile-metric-card">
                                <Statistic
                                    title={<span style={{ color: '#52c41a' }}>平台数量</span>}
                                    value={aggregatedStats.platform_count}
                                    valueStyle={{
                                        color: '#52c41a',
                                        fontSize: '16px',
                                        fontWeight: 'bold',
                                        letterSpacing: 1
                                    }}
                                    prefix=""
                                    formatter={(value) => (
                                        <CountUp
                                            end={value as number}
                                            duration={2}
                                        />
                                    )}
                                />
                                <Space style={{ marginTop: 4 }}>
                                    <Text style={{ fontSize: '11px', color: '#666' }}>
                                        资产类型: {aggregatedStats.asset_type_count}
                                    </Text>
                                </Space>
                            </Card>
                        </Col>
                    </Row>
                )}
            </Card>

            {/* 投资概览 */}
            {aggregatedStats && (
                <Card
                    title={<span style={{ color: '#1d39c4', fontWeight: 600, fontSize: 14 }}>资产概览</span>}
                    bordered={false}
                    size="small"
                    className="mobile-overview-card"
                >
                    <Row gutter={[8, 8]}>
                        <Col xs={12}>
                            <div className="mobile-overview-block mobile-overview-block-blue">
                                <DollarOutlined style={{ color: '#1890ff', fontSize: '14px', marginBottom: '2px' }} />
                                <Text type="secondary" style={{ fontSize: '11px' }}>
                                    总资产
                                </Text>
                                <div className="mobile-overview-amount">
                                    ¥{formatAmount(aggregatedStats.total_value)}
                                </div>
                                <Text style={{ color: '#1890ff', fontSize: '11px' }}>
                                    市值
                                </Text>
                            </div>
                        </Col>
                        <Col xs={12}>
                            <div className="mobile-overview-block mobile-overview-block-purple">
                                <BankOutlined style={{ color: '#722ed1', fontSize: '14px', marginBottom: '2px' }} />
                                <Text type="secondary" style={{ fontSize: '11px' }}>
                                    资产数量
                                </Text>
                                <div className="mobile-overview-amount">
                                    {aggregatedStats.asset_count || 0}
                                </div>
                                <Text style={{ color: '#722ed1', fontSize: '11px' }}>
                                    个资产
                                </Text>
                            </div>
                        </Col>
                    </Row>
                </Card>
            )}

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
                            title="资产数量"
                            value={assetTypesCount}
                            valueStyle={{ color: '#52c41a', fontWeight: 'bold', fontSize: 18 }}
                        />
                    </Card>
                </Col>
            </Row>
            <Row gutter={8} style={{ marginBottom: 16 }}>
                <Col span={12}>
                    <Card bordered={false} style={{ background: '#fffbe6' }}>
                        <Statistic
                            title="平台数量"
                            value={platformCount}
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
                        {aggregatedStats?.asset_type_stats && Object.entries(aggregatedStats.asset_type_stats).map(([type, value]) => (
                            <div key={type} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '12px 0', borderBottom: '1px solid #f0f0f0'
                            }}>
                                <span style={{ fontWeight: 600 }}>{type}</span>
                                <span>{value}</span>
                                <span style={{ color: '#1890ff' }}>￥{safeNumber(value).toLocaleString()}</span>
                                <span style={{ color: '#52c41a' }}>${safeNumber(value).toLocaleString()}</span>
                                <span style={{ color: '#666' }}>
                                    {aggregatedStats.has_default_rates ? '（默认）' : ''}
                                </span>
                            </div>
                        ))}
                    </Card>
                </Tabs.TabPane>
            </Tabs>

            {/* 热门基金和最近操作合并 */}
            <Card
                title={<span style={{ color: '#1d39c4', fontWeight: 600, fontSize: 14 }}>热门基金 & 最近操作</span>}
                bordered={false}
                className="mobile-hot-funds-card"
            >
                <Row gutter={[8, 8]}>
                    <Col xs={12}>
                        <div style={{ marginBottom: 8 }}>
                            <Text strong style={{ fontSize: '12px', color: '#666' }}>热门基金</Text>
                        </div>
                        <List
                            size="small"
                            dataSource={hotFunds.slice(0, 2)}
                            renderItem={(item) => (
                                <List.Item className="mobile-hot-fund-item" style={{ padding: '4px 0 !important' }}>
                                    <div className="mobile-hot-fund-info">
                                        <div className="mobile-hot-fund-name">{item.name}</div>
                                        <div className="mobile-hot-fund-code">{item.code}</div>
                                    </div>
                                    <div className="mobile-hot-fund-rate">
                                        <Text style={{
                                            color: item.trend === 'up' ? '#3f8600' : '#cf1322',
                                            fontWeight: 'bold',
                                            fontSize: '11px'
                                        }}>
                                            {item.rate}
                                        </Text>
                                        {item.trend === 'up' ? (
                                            <ArrowUpOutlined style={{ color: '#3f8600', marginLeft: 2, fontSize: '10px' }} />
                                        ) : (
                                            <ArrowDownOutlined style={{ color: '#cf1322', marginLeft: 2, fontSize: '10px' }} />
                                        )}
                                    </div>
                                </List.Item>
                            )}
                        />
                    </Col>
                    <Col xs={12}>
                        <div style={{ marginBottom: 8 }}>
                            <Text strong style={{ fontSize: '12px', color: '#666' }}>最近操作</Text>
                        </div>
                        <List
                            size="small"
                            dataSource={recentOperations.slice(0, 2)}
                            renderItem={(item) => (
                                <List.Item className="mobile-recent-item" style={{ padding: '4px 0 !important' }}>
                                    <div className="mobile-recent-icon">
                                        {getStatusIcon(item.status)}
                                    </div>
                                    <div className="mobile-recent-content">
                                        <div className="mobile-recent-title">
                                            {item.type} - {item.fund}
                                        </div>
                                        <div className="mobile-recent-time">
                                            {item.time}
                                        </div>
                                    </div>
                                    <div className="mobile-recent-amount">
                                        ¥{item.amount.toLocaleString()}
                                    </div>
                                </List.Item>
                            )}
                        />
                    </Col>
                </Row>
            </Card>

            {/* 快速操作 */}
            <Card
                title={<span style={{ color: '#1d39c4', fontWeight: 600, fontSize: 14 }}>快速操作</span>}
                bordered={false}
                className="mobile-action-card"
            >
                <Row gutter={[8, 8]}>
                    {quickActions.map((action) => (
                        <Col xs={12} key={action.title}>
                            <Card
                                size="small"
                                hoverable
                                className="mobile-action-item"
                                onClick={action.action}
                            >
                                <div className="mobile-action-item-inner">
                                    <Space>
                                        <div className="mobile-action-icon" style={{ background: action.color }}>
                                            {action.icon}
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: 'bold', marginBottom: '1px', fontSize: '12px' }}>
                                                {action.title}
                                            </div>
                                        </div>
                                    </Space>
                                    <RightOutlined style={{ color: '#999', fontSize: '10px' }} />
                                </div>
                            </Card>
                        </Col>
                    ))}
                </Row>
            </Card>

            {/* 平台分布 */}
            {aggregatedStats && (
                <Card
                    title={<span style={{ color: '#1d39c4', fontWeight: 600, fontSize: 14 }}>平台分布</span>}
                    bordered={false}
                    size="small"
                    className="mobile-fund-card"
                >
                    <Space direction="vertical" size={4} style={{ width: '100%' }}>
                        {Object.entries(aggregatedStats.platform_stats).map(([platform, value]) => (
                            <div key={platform} className="mobile-fund-row">
                                <Text type="secondary">{platform}</Text>
                                <Text style={{ fontWeight: 'bold' }}>¥{safeNumber(value).toLocaleString()}</Text>
                            </div>
                        ))}
                        <div className="mobile-fund-row">
                            <Text type="secondary">总平台数</Text>
                            <Text style={{ fontWeight: 'bold' }}>{aggregatedStats.platform_count} 个</Text>
                        </div>
                    </Space>
                </Card>
            )}

            {/* 风险提示 */}
            <Alert
                message="投资有风险，入市需谨慎"
                description="本应用仅用于投资记录和分析，不构成投资建议。"
                type="warning"
                showIcon
                className="mobile-risk-alert"
            />
        </div>
    )
}

export default MobileDashboard