import React from 'react'
import { Card, Row, Col, Button, Statistic, Typography } from 'antd'
import {
    DollarOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined,
    BarChartOutlined,
    PlusCircleOutlined
} from '@ant-design/icons'

const { Title, Paragraph } = Typography

const Dashboard: React.FC = () => {
    const stats = [
        { name: '总资产', value: 125000, change: '+12.5%', changeType: 'positive' },
        { name: '总收益', value: 15000, change: '+8.2%', changeType: 'positive' },
        { name: '本月收益', value: 2500, change: '+3.1%', changeType: 'positive' },
        { name: '持仓数量', value: 8, change: '+2', changeType: 'positive' },
    ]

    return (
        <div>
            <div style={{ marginBottom: 32 }}>
                <Title level={2}>总览</Title>
                <Paragraph type="secondary">
                    查看您的投资组合概览和关键指标
                </Paragraph>
            </div>

            <Card style={{ marginBottom: 24 }}>
                <Paragraph type="secondary">欢迎使用多资产投资记录与收益分析系统！</Paragraph>
            </Card>

            {/* 统计卡片 */}
            <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
                {stats.map((item) => (
                    <Col xs={24} sm={12} lg={6} key={item.name}>
                        <Card>
                            <Statistic
                                title={item.name}
                                value={item.value}
                                precision={item.name.includes('数量') ? 0 : 2}
                                valueStyle={{
                                    color: item.changeType === 'positive' ? '#3f8600' : '#cf1322',
                                    fontSize: '24px',
                                    fontWeight: 'bold'
                                }}
                                prefix={item.name.includes('数量') ? null : '¥'}
                                suffix={
                                    <span style={{
                                        fontSize: '14px',
                                        color: item.changeType === 'positive' ? '#3f8600' : '#cf1322',
                                        marginLeft: '8px'
                                    }}>
                                        {item.changeType === 'positive' ? (
                                            <ArrowUpOutlined />
                                        ) : (
                                            <ArrowDownOutlined />
                                        )}
                                        {item.change}
                                    </span>
                                }
                            />
                        </Card>
                    </Col>
                ))}
            </Row>

            {/* 快速操作 */}
            <div>
                <Title level={3} style={{ marginBottom: 16 }}>快速操作</Title>
                <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} lg={8}>
                        <Button
                            type="dashed"
                            size="large"
                            icon={<PlusCircleOutlined />}
                            style={{
                                width: '100%',
                                height: '120px',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <div>添加操作记录</div>
                        </Button>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                        <Button
                            type="dashed"
                            size="large"
                            icon={<BarChartOutlined />}
                            style={{
                                width: '100%',
                                height: '120px',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <div>查看持仓</div>
                        </Button>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                        <Button
                            type="dashed"
                            size="large"
                            icon={<ArrowUpOutlined />}
                            style={{
                                width: '100%',
                                height: '120px',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <div>收益分析</div>
                        </Button>
                    </Col>
                </Row>
            </div>
        </div>
    )
}

export default Dashboard 