import React from 'react'
import { Card, Row, Col, Statistic, Button, Space } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, PlusOutlined, BarChartOutlined, FundOutlined } from '@ant-design/icons'

const stats = [
    { name: '总资产', value: 125000, prefix: '¥', change: 12.5, positive: true },
    { name: '总收益', value: 15000, prefix: '¥', change: 8.2, positive: true },
    { name: '本月收益', value: 2500, prefix: '¥', change: 3.1, positive: true },
    { name: '持仓数量', value: 8, change: 2, positive: true },
]

const Dashboard: React.FC = () => {
    return (
        <div style={{ padding: 24 }}>
            <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>总览</h1>
            <p style={{ color: '#666', marginBottom: 24 }}>查看您的投资组合概览和关键指标</p>
            <Row gutter={16} style={{ marginBottom: 24 }}>
                {stats.map((item) => (
                    <Col xs={24} sm={12} md={6} key={item.name}>
                        <Card>
                            <Statistic
                                title={item.name}
                                value={item.value}
                                prefix={item.prefix}
                                valueStyle={{ color: item.positive ? '#3f8600' : '#cf1322' }}
                                suffix={
                                    <span>
                                        {item.positive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                                        {item.change}%
                                    </span>
                                }
                            />
                        </Card>
                    </Col>
                ))}
            </Row>
            <h2 style={{ fontSize: 18, fontWeight: 500, marginBottom: 16 }}>快速操作</h2>
            <Space>
                <Button type="primary" icon={<PlusOutlined />}>添加操作记录</Button>
                <Button icon={<BarChartOutlined />}>查看持仓</Button>
                <Button icon={<FundOutlined />}>收益分析</Button>
            </Space>
        </div>
    )
}

export default Dashboard 