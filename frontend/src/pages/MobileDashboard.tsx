import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Typography, Space, Progress } from 'antd'
import {
    ArrowUpOutlined,
    ArrowDownOutlined,
    PlusCircleOutlined,
    BarChartOutlined,
    PieChartOutlined,
    LineChartOutlined,
    EyeOutlined,
    RightOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { fundAPI } from '../services/api'

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
    
    // 获取持仓汇总数据
    const fetchStats = async () => {
        setLoading(true)
        try {
            const response = await fundAPI.getPositionSummary()
            if (response.success && response.data) {
                setStats(response.data)
            }
        } catch (error) {
            console.error('获取统计数据失败:', error)
        } finally {
            setLoading(false)
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

            {/* 核心指标 */}
            <Card 
                title="核心指标" 
                bordered={false} 
                style={{ marginBottom: 16 }}
                extra={<EyeOutlined onClick={() => navigate('/positions')} />}
                loading={loading}
            >
                {stats && (
                    <Row gutter={[12, 12]}>
                        <Col xs={12}>
                            <Card size="small" style={{ textAlign: 'center' }}>
                                <Statistic
                                    title="总市值"
                                    value={safeNumber(stats.total_value)}
                                    precision={0}
                                    valueStyle={{
                                        color: '#1890ff',
                                        fontSize: '20px',
                                        fontWeight: 'bold'
                                    }}
                                    prefix="¥"
                                />
                                <Space style={{ marginTop: 8 }}>
                                    {safeNumber(stats.total_profit) >= 0 ? (
                                        <ArrowUpOutlined style={{ color: '#3f8600' }} />
                                    ) : (
                                        <ArrowDownOutlined style={{ color: '#cf1322' }} />
                                    )}
                                    <Text style={{ 
                                        color: safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322',
                                        fontSize: '12px'
                                    }}>
                                        {formatPercent(stats.total_profit_rate)}
                                    </Text>
                                </Space>
                                <Progress 
                                    percent={Math.min(Math.abs(safeNumber(stats.total_profit_rate) * 100), 100)} 
                                    showInfo={false} 
                                    size="small"
                                    style={{ marginTop: 8 }}
                                    strokeColor={safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322'}
                                />
                            </Card>
                        </Col>
                        <Col xs={12}>
                            <Card size="small" style={{ textAlign: 'center' }}>
                                <Statistic
                                    title="总收益"
                                    value={Math.abs(safeNumber(stats.total_profit))}
                                    precision={0}
                                    valueStyle={{
                                        color: safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322',
                                        fontSize: '20px',
                                        fontWeight: 'bold'
                                    }}
                                    prefix={safeNumber(stats.total_profit) >= 0 ? '+¥' : '-¥'}
                                />
                                <Space style={{ marginTop: 8 }}>
                                    {safeNumber(stats.total_profit) >= 0 ? (
                                        <ArrowUpOutlined style={{ color: '#3f8600' }} />
                                    ) : (
                                        <ArrowDownOutlined style={{ color: '#cf1322' }} />
                                    )}
                                    <Text style={{ 
                                        color: safeNumber(stats.total_profit) >= 0 ? '#3f8600' : '#cf1322',
                                        fontSize: '12px'
                                    }}>
                                        {formatPercent(stats.total_profit_rate)}
                                    </Text>
                                </Space>
                                <Progress 
                                    percent={Math.min(Math.abs(safeNumber(stats.total_profit_rate) * 100), 100)} 
                                    showInfo={false} 
                                    size="small"
                                    style={{ marginTop: 8 }}
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
                    title="投资概览" 
                    bordered={false} 
                    style={{ marginBottom: 16 }}
                >
                    <Row gutter={[12, 12]}>
                        <Col xs={12}>
                            <div style={{ 
                                textAlign: 'center', 
                                padding: '12px',
                                background: '#f0f5ff',
                                borderRadius: '8px'
                            }}>
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                    累计投入
                                </Text>
                                <div style={{ 
                                    fontSize: '18px', 
                                    fontWeight: 'bold',
                                    color: '#1890ff',
                                    margin: '4px 0'
                                }}>
                                    ¥{formatAmount(stats.total_invested)}
                                </div>
                                <Text style={{ 
                                    color: '#1890ff',
                                    fontSize: '12px'
                                }}>
                                    本金
                                </Text>
                            </div>
                        </Col>
                        <Col xs={12}>
                            <div style={{ 
                                textAlign: 'center', 
                                padding: '12px',
                                background: '#fafafa',
                                borderRadius: '8px'
                            }}>
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                    持仓数量
                                </Text>
                                <div style={{ 
                                    fontSize: '18px', 
                                    fontWeight: 'bold',
                                    color: '#722ed1',
                                    margin: '4px 0'
                                }}>
                                    {stats.asset_count || 0}
                                </div>
                                <Text style={{ 
                                    color: '#722ed1',
                                    fontSize: '12px'
                                }}>
                                    个基金
                                </Text>
                            </div>
                        </Col>
                    </Row>
                </Card>
            )}

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