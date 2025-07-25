import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Typography, Space, Progress, Tag, Alert, Button, Avatar, List, Badge } from 'antd'
import {
    ArrowUpOutlined,
    ArrowDownOutlined,
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
    UserOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { fundAPI } from '../services/api'
import AssetTrendChart from '../components/AssetTrendChart';
import CountUp from 'react-countup';
import './MobileDashboard.css';

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
    const [loading, setLoading] = useState(false)
    const [stats, setStats] = useState<DashboardStats | null>(null)
    const [lastUpdateTime, setLastUpdateTime] = useState<string>('')
    
    // 获取持仓汇总数据
    const fetchStats = async () => {
        setLoading(true)
        try {
            const response = await fundAPI.getPositionSummary()
            if (response.success && response.data) {
                setStats(response.data)
            } else {
                // Mock数据 - 生成移动端统计数据
                const mockStats = {
                    total_value: 1200000,
                    total_invested: 1000000,
                    total_profit: 200000,
                    total_profit_rate: 0.20,
                    asset_count: 12,
                    profitable_count: 8,
                    loss_count: 4
                }
                setStats(mockStats)
            }
        } catch (error) {
            // Mock数据 - 生成移动端统计数据
            const mockStats = {
                total_value: 1200000,
                total_invested: 1000000,
                total_profit: 200000,
                total_profit_rate: 0.20,
                asset_count: 12,
                profitable_count: 8,
                loss_count: 4
            }
            setStats(mockStats)
        } finally {
            setLoading(false)
            setLastUpdateTime(new Date().toLocaleTimeString('zh-CN'))
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

    // 格式化金额
    const formatAmount = (amount: number | string) => {
        const numAmount = safeNumber(amount)
        return numAmount.toLocaleString('zh-CN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        })
    }

    // 格式化百分比
    const formatPercent = (rate: number | string) => {
        const numRate = safeNumber(rate)
        return `${numRate >= 0 ? '+' : ''}${(numRate * 100).toFixed(2)}%`
    }

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
        {
            title: '添加操作',
            description: '记录新的投资操作',
            icon: PlusCircleOutlined,
            color: '#1890ff',
            path: '/operations',
            badge: 'new'
        },
        {
            title: '查看持仓',
            description: '查看当前投资持仓',
            icon: BarChartOutlined,
            color: '#52c41a',
            path: '/positions',
            badge: null
        },
        {
            title: '收益分析',
            description: '分析投资收益情况',
            icon: PieChartOutlined,
            color: '#faad14',
            path: '/analysis',
            badge: null
        },
        {
            title: '基金管理',
            description: '管理基金投资',
            icon: LineChartOutlined,
            color: '#722ed1',
            path: '/funds',
            badge: null
        }
    ]

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'success': return <CheckCircleOutlined style={{ color: '#52c41a' }} />
            case 'pending': return <ClockCircleOutlined style={{ color: '#faad14' }} />
            case 'failed': return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
            default: return <ExclamationCircleOutlined style={{ color: '#1890ff' }} />
        }
    }

    return (
        <div className="mobile-dashboard-root">
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
                        onClick={fetchStats}
                        loading={loading}
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
                            {stats ? '查看您的投资概况' : '正在加载投资数据...'}
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
                extra={<EyeOutlined onClick={() => navigate('/positions')} style={{color:'#1d39c4'}} />}
                loading={loading}
            >
                {stats && (
                    <Row gutter={[8, 8]}>
                        <Col xs={12}>
                            <Card size="small" className="mobile-metric-card">
                                <Statistic
                                    title={<span style={{color:'#1890ff'}}>总市值</span>}
                                    value={safeNumber(stats.total_value)}
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
                                    {safeNumber(stats.total_profit) >= 0 ? (
                                        <ArrowUpOutlined style={{ color: '#3f8600' }} />
                                    ) : (
                                        <ArrowDownOutlined style={{ color: '#cf1322' }} />
                                    )}
                                    <Text style={{ 
                                        color: safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322',
                                        fontSize: '11px'
                                    }}>
                                        {formatPercent(stats.total_profit_rate)}
                                    </Text>
                                </Space>
                                <Progress 
                                    percent={Math.min(Math.abs(safeNumber(stats.total_profit_rate) * 100), 100)} 
                                    showInfo={false} 
                                    size="small"
                                    style={{ marginTop: 4 }}
                                    strokeColor={safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322'}
                                />
                            </Card>
                        </Col>
                        <Col xs={12}>
                            <Card size="small" className="mobile-metric-card">
                                <Statistic
                                    title={<span style={{color:safeNumber(stats.total_profit)>=0?'#3f8600':'#cf1322'}}>总收益</span>}
                                    value={Math.abs(safeNumber(stats.total_profit))}
                                    precision={0}
                                    valueStyle={{
                                        color: safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322',
                                        fontSize: '16px',
                                        fontWeight: 'bold',
                                        letterSpacing: 1
                                    }}
                                    prefix={safeNumber(stats.total_profit) >= 0 ? '+¥' : '-¥'}
                                    formatter={(value) => (
                                        <CountUp 
                                            end={value as number} 
                                            duration={2}
                                            separator=","
                                        />
                                    )}
                                />
                                <Space style={{ marginTop: 4 }}>
                                    {safeNumber(stats.total_profit) >= 0 ? (
                                        <ArrowUpOutlined style={{ color: '#3f8600' }} />
                                    ) : (
                                        <ArrowDownOutlined style={{ color: '#cf1322' }} />
                                    )}
                                    <Text style={{ 
                                        color: safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322',
                                        fontSize: '11px'
                                    }}>
                                        {formatPercent(stats.total_profit_rate)}
                                    </Text>
                                </Space>
                                <Progress 
                                    percent={Math.min(Math.abs(safeNumber(stats.total_profit_rate) * 100), 100)} 
                                    showInfo={false} 
                                    size="small"
                                    style={{ marginTop: 4 }}
                                    strokeColor={safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322'}
                                />
                            </Card>
                        </Col>
                    </Row>
                )}
            </Card>

            {/* 投资概览 */}
            {stats && (
                <Card 
                    title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:14}}>投资概览</span>} 
                    bordered={false} 
                    className="mobile-overview-card"
                >
                    <Row gutter={[8, 8]}>
                        <Col xs={12}>
                            <div className="mobile-overview-block mobile-overview-block-blue">
                                <DollarOutlined style={{ color: '#1890ff', fontSize: '14px', marginBottom: '2px' }} />
                                <Text type="secondary" style={{ fontSize: '11px' }}>
                                    累计投入
                                </Text>
                                <div className="mobile-overview-amount">
                                    ¥{formatAmount(stats.total_invested)}
                                </div>
                                <Text style={{ color: '#1890ff', fontSize: '11px' }}>
                                    本金
                                </Text>
                            </div>
                        </Col>
                        <Col xs={12}>
                            <div className="mobile-overview-block mobile-overview-block-purple">
                                <BankOutlined style={{ color: '#722ed1', fontSize: '14px', marginBottom: '2px' }} />
                                <Text type="secondary" style={{ fontSize: '11px' }}>
                                    持仓数量
                                </Text>
                                <div className="mobile-overview-amount">
                                    {stats.asset_count || 0}
                                </div>
                                <Text style={{ color: '#722ed1', fontSize: '11px' }}>
                                    个基金
                                </Text>
                            </div>
                        </Col>
                    </Row>
                </Card>
            )}

            {/* 资产趋势 */}
            <Card 
                title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:14}}>资产趋势</span>} 
                bordered={false}
                className="mobile-chart-card"
            >
                <div>
                    <AssetTrendChart baseCurrency="CNY" days={30} />
                </div>
            </Card>

            {/* 热门基金和最近操作合并 */}
            <Card 
                title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:14}}>热门基金 & 最近操作</span>} 
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
                title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:14}}>快速操作</span>} 
                bordered={false}
                className="mobile-action-card"
            >
                <Row gutter={[8, 8]}>
                    {quickActions.map((action) => {
                        const IconComponent = action.icon
                        return (
                            <Col xs={12} key={action.title}>
                                <Card
                                    size="small"
                                    hoverable
                                    className="mobile-action-item"
                                    onClick={() => navigate(action.path)}
                                >
                                    <div className="mobile-action-item-inner">
                                        <Space>
                                            <div className="mobile-action-icon" style={{ background: action.color }}>
                                                <IconComponent style={{ color: 'white', fontSize: '14px' }} />
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 'bold', marginBottom: '1px', fontSize: '12px' }}>
                                                    {action.title}
                                                    {action.badge && (
                                                        <Tag color="red" style={{ marginLeft: 4, fontSize: '9px' }}>
                                                            {action.badge}
                                                        </Tag>
                                                    )}
                                                </div>
                                                <Text type="secondary" style={{ fontSize: '10px' }}>
                                                    {action.description}
                                                </Text>
                                            </div>
                                        </Space>
                                        <RightOutlined style={{ color: '#999', fontSize: '10px' }} />
                                    </div>
                                </Card>
                            </Col>
                        )
                    })}
                </Row>
            </Card>

            {/* 基金分布 */}
            {stats && (
                <Card 
                    title={<span style={{color:'#1d39c4',fontWeight:600,fontSize:14}}>基金分布</span>} 
                    bordered={false}
                    size="small"
                    className="mobile-fund-card"
                >
                    <Space direction="vertical" size={4} style={{ width: '100%' }}>
                        <div className="mobile-fund-row">
                            <Text type="secondary">总基金数</Text>
                            <Text style={{ fontWeight: 'bold' }}>{stats.asset_count} 个</Text>
                        </div>
                        <div className="mobile-fund-row">
                            <Text type="secondary">盈利基金</Text>
                            <Text style={{ color: '#3f8600', fontWeight: 'bold' }}>{stats.profitable_count} 个</Text>
                        </div>
                        <div className="mobile-fund-row">
                            <Text type="secondary">亏损基金</Text>
                            <Text style={{ color: '#cf1322', fontWeight: 'bold' }}>{stats.loss_count} 个</Text>
                        </div>
                        {stats.asset_count > 0 && (
                            <div style={{ marginTop: 8 }}>
                                <Progress 
                                    percent={(stats.profitable_count / stats.asset_count) * 100}
                                    showInfo={false}
                                    strokeColor="#3f8600"
                                    trailColor="#cf1322"
                                />
                                <div className="mobile-fund-progress-labels">
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