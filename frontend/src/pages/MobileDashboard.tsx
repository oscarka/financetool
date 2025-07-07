import React from 'react'
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

const { Title, Text } = Typography

const MobileDashboard: React.FC = () => {
    const navigate = useNavigate()
    
    const stats = [
        { 
            name: '总资产', 
            value: 125000, 
            change: '+12.5%', 
            changeType: 'positive',
            trend: 85 
        },
        { 
            name: '总收益', 
            value: 15000, 
            change: '+8.2%', 
            changeType: 'positive',
            trend: 72
        },
        { 
            name: '本月收益', 
            value: 2500, 
            change: '+3.1%', 
            changeType: 'positive',
            trend: 45
        },
        { 
            name: '持仓数量', 
            value: 8, 
            change: '+2', 
            changeType: 'positive',
            trend: 60
        },
    ]

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
                        今天是投资的好日子
                    </Text>
                </Space>
            </Card>

            {/* 核心指标 */}
            <Card 
                title="核心指标" 
                bordered={false} 
                style={{ marginBottom: 16 }}
                extra={<EyeOutlined />}
            >
                <Row gutter={[12, 12]}>
                    {stats.slice(0, 2).map((item) => (
                        <Col xs={12} key={item.name}>
                            <Card size="small" style={{ textAlign: 'center' }}>
                                <Statistic
                                    title={item.name}
                                    value={item.value}
                                    precision={item.name.includes('数量') ? 0 : 0}
                                    valueStyle={{
                                        color: item.changeType === 'positive' ? '#3f8600' : '#cf1322',
                                        fontSize: '20px',
                                        fontWeight: 'bold'
                                    }}
                                    prefix={item.name.includes('数量') ? null : '¥'}
                                />
                                <Space style={{ marginTop: 8 }}>
                                    {item.changeType === 'positive' ? (
                                        <ArrowUpOutlined style={{ color: '#3f8600' }} />
                                    ) : (
                                        <ArrowDownOutlined style={{ color: '#cf1322' }} />
                                    )}
                                    <Text style={{ 
                                        color: item.changeType === 'positive' ? '#3f8600' : '#cf1322',
                                        fontSize: '12px'
                                    }}>
                                        {item.change}
                                    </Text>
                                </Space>
                                <Progress 
                                    percent={item.trend} 
                                    showInfo={false} 
                                    size="small"
                                    style={{ marginTop: 8 }}
                                />
                            </Card>
                        </Col>
                    ))}
                </Row>
            </Card>

            {/* 收益概览 */}
            <Card 
                title="收益概览" 
                bordered={false} 
                style={{ marginBottom: 16 }}
            >
                <Row gutter={[12, 12]}>
                    {stats.slice(2).map((item) => (
                        <Col xs={12} key={item.name}>
                            <div style={{ 
                                textAlign: 'center', 
                                padding: '12px',
                                background: '#fafafa',
                                borderRadius: '8px'
                            }}>
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                    {item.name}
                                </Text>
                                <div style={{ 
                                    fontSize: '18px', 
                                    fontWeight: 'bold',
                                    color: item.changeType === 'positive' ? '#3f8600' : '#cf1322',
                                    margin: '4px 0'
                                }}>
                                    {item.name.includes('数量') ? item.value : `¥${item.value.toLocaleString()}`}
                                </div>
                                <Text style={{ 
                                    color: item.changeType === 'positive' ? '#3f8600' : '#cf1322',
                                    fontSize: '12px'
                                }}>
                                    {item.change}
                                </Text>
                            </div>
                        </Col>
                    ))}
                </Row>
            </Card>

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

            {/* 今日摘要 */}
            <Card 
                title="今日摘要" 
                bordered={false}
                size="small"
            >
                <Space direction="vertical" size={8} style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary">今日收益</Text>
                        <Text style={{ color: '#3f8600', fontWeight: 'bold' }}>+¥1,250</Text>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary">活跃基金</Text>
                        <Text>5 个</Text>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary">待处理操作</Text>
                        <Text style={{ color: '#faad14' }}>2 个</Text>
                    </div>
                </Space>
            </Card>
        </div>
    )
}

export default MobileDashboard