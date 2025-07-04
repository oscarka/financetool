import React, { useState, useEffect } from 'react'
import { Card, Table, Statistic, Row, Col, Tag, Space, Button, message, Typography, Divider } from 'antd'
import { SyncOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'
import type { APIResponse } from '../services/api'

interface FundPosition {
    id: number
    platform: string
    asset_type: string
    asset_code: string
    asset_name: string
    currency: string
    quantity: number
    avg_cost: number
    current_price: number
    current_value: number
    total_invested: number
    total_profit: number
    profit_rate: number
    last_updated: string
}

interface PositionSummary {
    total_invested: number
    total_value: number
    total_profit: number
    total_profit_rate: number
    asset_count: number
    profitable_count: number
    loss_count: number
}

const { Title, Text } = Typography

const FundPositions: React.FC = () => {
    const [positions, setPositions] = useState<FundPosition[]>([])
    const [summary, setSummary] = useState<PositionSummary | null>(null)
    const [loading, setLoading] = useState(false)

    // 获取持仓数据
    const fetchPositions = async () => {
        setLoading(true)
        try {
            const [positionsResponse, summaryResponse] = await Promise.all([
                fundAPI.getFundPositions(),
                fundAPI.getPositionSummary()
            ])

            if (positionsResponse.success && positionsResponse.data) {
                setPositions(
                    positionsResponse.data.map((item: any, idx: number) => ({
                        ...item,
                        id: idx + 1,
                        quantity: item.total_shares,
                        current_price: item.current_nav,
                    }))
                )
            }

            if (summaryResponse.success && summaryResponse.data) {
                setSummary(summaryResponse.data || null)
            }
        } catch (error: any) {
            console.error('获取持仓数据失败:', error)
            message.error('获取持仓数据失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchPositions()
    }, [])

    console.log('[调试] summary:', summary)

    // 表格列定义
    const columns = [
        {
            title: '基金代码',
            dataIndex: 'asset_code',
            key: 'asset_code',
            width: 100
        },
        {
            title: '基金名称',
            dataIndex: 'asset_name',
            key: 'asset_name',
            ellipsis: true
        },
        {
            title: '持仓份额',
            dataIndex: 'quantity',
            key: 'quantity',
            render: (quantity: number) => Number(quantity).toFixed(4)
        },
        {
            title: '平均成本',
            dataIndex: 'avg_cost',
            key: 'avg_cost',
            render: (cost: number) => `¥${Number(cost).toFixed(4)}`
        },
        {
            title: '当前价格',
            dataIndex: 'current_price',
            key: 'current_price',
            render: (price: number) => `¥${Number(price).toFixed(4)}`
        },
        {
            title: '当前市值',
            dataIndex: 'current_value',
            key: 'current_value',
            render: (value: number) => `¥${Number(value).toFixed(2)}`
        },
        {
            title: '累计投入',
            dataIndex: 'total_invested',
            key: 'total_invested',
            render: (invested: number) => `¥${Number(invested).toFixed(2)}`
        },
        {
            title: '累计收益',
            dataIndex: 'total_profit',
            key: 'total_profit',
            render: (profit: number) => {
                const color = profit >= 0 ? 'green' : 'red'
                const icon = profit >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />
                return (
                    <Tag color={color} icon={icon}>
                        {profit >= 0 ? '+' : ''}¥{Number(profit).toFixed(2)}
                    </Tag>
                )
            }
        },
        {
            title: '收益率',
            dataIndex: 'profit_rate',
            key: 'profit_rate',
            render: (rate: number) => {
                const color = rate >= 0 ? 'green' : 'red'
                const icon = rate >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />
                return (
                    <Tag color={color} icon={icon}>
                        {rate >= 0 ? '+' : ''}{(Number(rate) * 100).toFixed(2)}%
                    </Tag>
                )
            }
        },
        {
            title: '更新时间',
            dataIndex: 'last_updated',
            key: 'last_updated',
            render: (date: string) => new Date(date).toLocaleString()
        }
    ]

    if (!summary) {
        return <div style={{ padding: 32, textAlign: 'center', color: '#888' }}>正在加载持仓汇总...</div>;
    }
    if (!positions || positions.length === 0) {
        return <div style={{ padding: 32, textAlign: 'center', color: '#888' }}>暂无基金持仓数据</div>;
    }

    return (
        <div className="space-y-6">
            {/* 持仓汇总统计（大号、色彩区分） */}
            <Card style={{ marginBottom: 24, background: '#f6ffed', border: '1px solid #b7eb8f' }}>
                <Row gutter={32} align="middle">
                    <Col span={6}>
                        <Title level={2} style={{ color: '#1890ff', margin: 0 }}>¥{Number(summary.total_value).toFixed(2)}</Title>
                        <Text type="secondary">总市值</Text>
                    </Col>
                    <Col span={6}>
                        <Title level={4} style={{ color: '#3f8600', margin: 0 }}>¥{Number(summary.total_invested).toFixed(2)}</Title>
                        <Text type="secondary">累计投入</Text>
                    </Col>
                    <Col span={6}>
                        <Title level={4} style={{ color: summary.total_profit >= 0 ? '#3f8600' : '#cf1322', margin: 0 }}>{summary.total_profit >= 0 ? '+' : ''}¥{Number(summary.total_profit).toFixed(2)}</Title>
                        <Text type="secondary">累计盈亏</Text>
                    </Col>
                    <Col span={6}>
                        <Title level={4} style={{ color: summary.total_profit_rate >= 0 ? '#3f8600' : '#cf1322', margin: 0 }}>{summary.total_profit_rate >= 0 ? '+' : ''}{(Number(summary.total_profit_rate) * 100).toFixed(2)}%</Title>
                        <Text type="secondary">总收益率</Text>
                    </Col>
                </Row>
                <Divider style={{ margin: '16px 0' }} />
                <Row gutter={32}>
                    <Col span={6}><Statistic title="持仓基金数" value={summary.asset_count} valueStyle={{ color: '#1890ff' }} /></Col>
                    <Col span={6}><Statistic title="盈利基金数" value={summary.profitable_count} valueStyle={{ color: '#3f8600' }} /></Col>
                    <Col span={6}><Statistic title="亏损基金数" value={summary.loss_count} valueStyle={{ color: '#cf1322' }} /></Col>
                </Row>
            </Card>

            {/* 基金持仓卡片分组展示 */}
            <Row gutter={[24, 24]}>
                {positions.map(pos => {
                    const profitColor = pos.total_profit >= 0 ? '#3f8600' : '#cf1322'
                    const rateColor = pos.profit_rate >= 0 ? '#3f8600' : '#cf1322'
                    return (
                        <Col xs={24} sm={12} md={8} lg={6} key={pos.id}>
                            <Card
                                title={<span style={{ fontWeight: 600, color: '#1890ff' }}>{pos.asset_name} <Text type="secondary">({pos.asset_code})</Text></span>}
                                bordered
                                style={{ minHeight: 260, width: '100%' }}
                                extra={<Tag color={pos.platform === '支付宝' ? 'blue' : 'purple'}>{pos.platform}</Tag>}
                            >
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0 }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#333' }}>持有份额</span>
                                        <span className="value" style={{ flex: 1, minWidth: 0, fontFamily: 'Menlo, Consolas, monospace', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{Number(pos.quantity).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                        <span className="unit" style={{ marginLeft: 4, flexShrink: 0, color: '#888' }}>份</span>
                                    </div>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0 }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#333' }}>当前净值</span>
                                        <span className="value" style={{ flex: 1, minWidth: 0, fontFamily: 'Menlo, Consolas, monospace', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{Number(pos.current_price).toFixed(4)}</span>
                                        <span className="unit" style={{ marginLeft: 4, flexShrink: 0, color: '#888' }}></span>
                                    </div>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0 }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#333' }}>市值</span>
                                        <span className="value" style={{ flex: 1, minWidth: 0, fontFamily: 'Menlo, Consolas, monospace', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{Number(pos.current_value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                        <span className="unit" style={{ marginLeft: 4, flexShrink: 0, color: '#888' }}>元</span>
                                    </div>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0 }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#333' }}>成本</span>
                                        <span className="value" style={{ flex: 1, minWidth: 0, fontFamily: 'Menlo, Consolas, monospace', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{Number(pos.avg_cost).toFixed(4)}</span>
                                        <span className="unit" style={{ marginLeft: 4, flexShrink: 0, color: '#888' }}></span>
                                    </div>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0 }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#333' }}>累计投入</span>
                                        <span className="value" style={{ flex: 1, minWidth: 0, fontFamily: 'Menlo, Consolas, monospace', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{Number(pos.total_invested).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                        <span className="unit" style={{ marginLeft: 4, flexShrink: 0, color: '#888' }}>元</span>
                                    </div>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0, marginTop: 6, alignItems: 'flex-start' }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#333', marginTop: 2 }}>浮动盈亏</span>
                                        <div className="profit-block" style={{ flex: 1, minWidth: 0, textAlign: 'right' }}>
                                            <div
                                                style={{
                                                    fontWeight: 700,
                                                    fontSize: 20,
                                                    color: profitColor,
                                                    fontFamily: 'Menlo, Consolas, monospace',
                                                    lineHeight: 1.2,
                                                }}
                                            >
                                                {pos.total_profit >= 0 ? '+' : ''}
                                                {Number(pos.total_profit).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} 元
                                            </div>
                                            <div
                                                style={{
                                                    fontWeight: 600,
                                                    fontSize: 15,
                                                    color: profitColor,
                                                    fontFamily: 'Menlo, Consolas, monospace',
                                                    marginTop: 2,
                                                }}
                                            >
                                                {pos.profit_rate >= 0 ? '+' : ''}
                                                {(Number(pos.profit_rate) * 100).toFixed(2)}%
                                            </div>
                                        </div>
                                    </div>
                                    <div className="fund-row" style={{ display: 'flex', minWidth: 0, marginTop: 8 }}>
                                        <span className="label" style={{ width: 72, flexShrink: 0, color: '#888', fontSize: 13 }}>最近操作：</span>
                                        <span className="value" style={{ flex: 1, minWidth: 0, color: '#888', fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{pos.last_updated ? pos.last_updated.replace('T', ' ').slice(0, 19) : ''}</span>
                                    </div>
                                </div>
                            </Card>
                        </Col>
                    )
                })}
            </Row>
            <style>{`
            .fund-row {
                display: flex;
                align-items: baseline;
                font-size: 16px;
                margin-bottom: 2px;
            }
            .label {
                min-width: 80px;
                color: #333;
                font-weight: 500;
            }
            .value {
                min-width: 100px;
                text-align: right;
                font-variant-numeric: tabular-nums;
                font-family: 'Menlo', 'Consolas', monospace, sans-serif;
            }
            .unit {
                min-width: 36px;
                color: #888;
                margin-left: 2px;
                text-align: left;
            }
            .profit-row .profit {
                min-width: 100px;
                font-weight: bold;
            }
            `}</style>

            {/* 原有表格明细作为补充 */}
            <Card
                title="基金持仓明细（表格）"
                extra={
                    <Button
                        type="primary"
                        icon={<SyncOutlined />}
                        loading={loading}
                        onClick={fetchPositions}
                    >
                        刷新数据
                    </Button>
                }
                style={{ marginTop: 32 }}
            >
                <Table
                    columns={columns}
                    dataSource={positions}
                    rowKey="id"
                    loading={loading}
                    pagination={false}
                    scroll={{ x: 1200 }}
                />
            </Card>
        </div>
    )
}

export default FundPositions 