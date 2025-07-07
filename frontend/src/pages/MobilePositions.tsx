import React, { useState, useEffect } from 'react'
import { Card, Button, message, Empty, Statistic, Row, Col } from 'antd'
import { ReloadOutlined, ArrowUpOutlined, ArrowDownOutlined, EyeOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'

interface Position {
    asset_code: string
    asset_name: string
    total_quantity: number
    average_nav: number
    current_nav: number | null
    total_cost: number
    current_value: number | null
    total_return: number | null
    return_rate: number | null
    last_operation_date: string
}

interface PositionSummary {
    total_cost: number
    current_value: number
    total_return: number
    return_rate: number
    position_count: number
}

const MobilePositions: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([])
    const [summary, setSummary] = useState<PositionSummary | null>(null)
    const [loading, setLoading] = useState(false)

    // 获取持仓数据
    const fetchPositions = async () => {
        setLoading(true)
        try {
            const [positionsRes, summaryRes] = await Promise.all([
                fundAPI.getFundPositions(),
                fundAPI.getPositionSummary()
            ])

            if (positionsRes.success && positionsRes.data) {
                setPositions(positionsRes.data || [])
            }

            if (summaryRes.success && summaryRes.data) {
                setSummary(summaryRes.data)
            }
        } catch (error) {
            message.error('获取持仓数据失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchPositions()
    }, [])

    // 格式化金额
    const formatAmount = (amount: number | null) => {
        if (amount === null) return '-'
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: 'CNY',
            minimumFractionDigits: 2
        }).format(amount)
    }

    // 格式化百分比
    const formatPercent = (rate: number | null) => {
        if (rate === null) return '-'
        return `${(rate * 100).toFixed(2)}%`
    }

    // 获取收益颜色
    const getReturnColor = (value: number | null) => {
        if (value === null) return '#666'
        return value >= 0 ? '#52c41a' : '#ff4d4f'
    }

    // 渲染持仓卡片
    const renderPositionCard = (position: Position) => (
        <Card
            key={position.asset_code}
            size="small"
            style={{ marginBottom: 12 }}
            bodyStyle={{ padding: '12px 16px' }}
        >
            {/* 基金信息 */}
            <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: 2 }}>
                            {position.asset_code}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.2' }}>
                            {position.asset_name}
                        </div>
                    </div>
                    <Button 
                        type="text" 
                        size="small" 
                        icon={<EyeOutlined />}
                        style={{ padding: '0 4px' }}
                    />
                </div>
            </div>

            {/* 持仓数据 */}
            <Row gutter={[8, 8]} style={{ marginBottom: 12 }}>
                <Col span={12}>
                    <div style={{ textAlign: 'center', padding: '8px', background: '#fafafa', borderRadius: '4px' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>持仓份额</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                            {position.total_quantity.toFixed(2)}
                        </div>
                    </div>
                </Col>
                <Col span={12}>
                    <div style={{ textAlign: 'center', padding: '8px', background: '#fafafa', borderRadius: '4px' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>平均成本</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                            ¥{position.average_nav.toFixed(4)}
                        </div>
                    </div>
                </Col>
            </Row>

            {/* 净值信息 */}
            <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '12px', color: '#666' }}>当前净值</span>
                    <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                        {position.current_nav ? `¥${position.current_nav.toFixed(4)}` : '-'}
                    </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '12px', color: '#666' }}>单位收益</span>
                    <span style={{ 
                        fontSize: '12px', 
                        fontWeight: 'bold',
                        color: position.current_nav ? getReturnColor(position.current_nav - position.average_nav) : '#666'
                    }}>
                        {position.current_nav ? 
                            `¥${(position.current_nav - position.average_nav).toFixed(4)}` : '-'}
                    </span>
                </div>
            </div>

            {/* 投资金额和收益 */}
            <div style={{ 
                padding: '8px 12px',
                background: '#f0f5ff',
                borderRadius: '6px',
                marginBottom: 12
            }}>
                <Row gutter={16}>
                    <Col span={8}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>总成本</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                {formatAmount(position.total_cost)}
                            </div>
                        </div>
                    </Col>
                    <Col span={8}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>当前市值</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                {formatAmount(position.current_value)}
                            </div>
                        </div>
                    </Col>
                    <Col span={8}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>收益</div>
                            <div style={{ 
                                fontSize: '14px', 
                                fontWeight: 'bold',
                                color: getReturnColor(position.total_return)
                            }}>
                                {formatAmount(position.total_return)}
                            </div>
                        </div>
                    </Col>
                </Row>
            </div>

            {/* 收益率 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: '#666' }}>收益率</span>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    {position.return_rate !== null && (
                        <>
                            {position.return_rate >= 0 ? 
                                <ArrowUpOutlined style={{ color: '#52c41a', marginRight: 4 }} /> :
                                <ArrowDownOutlined style={{ color: '#ff4d4f', marginRight: 4 }} />
                            }
                        </>
                    )}
                    <span style={{ 
                        fontSize: '14px', 
                        fontWeight: 'bold',
                        color: getReturnColor(position.return_rate)
                    }}>
                        {formatPercent(position.return_rate)}
                    </span>
                </div>
            </div>
        </Card>
    )

    return (
        <div style={{ paddingBottom: '20px' }}>
            {/* 页面标题和刷新按钮 */}
            <Card 
                bordered={false}
                style={{ marginBottom: 16 }}
                bodyStyle={{ padding: '16px' }}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>持仓</h2>
                        <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
                            查看当前所有资产的持仓状态
                        </p>
                    </div>
                    <Button 
                        type="primary" 
                        size="small" 
                        icon={<ReloadOutlined />}
                        loading={loading}
                        onClick={fetchPositions}
                    >
                        刷新
                    </Button>
                </div>
            </Card>

            {/* 持仓汇总 */}
            {summary && (
                <Card 
                    bordered={false}
                    style={{ marginBottom: 16 }}
                    bodyStyle={{ padding: '16px' }}
                >
                    <div style={{ marginBottom: 12 }}>
                        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold' }}>持仓汇总</h3>
                    </div>
                    
                    <Row gutter={[8, 8]}>
                        <Col span={12}>
                            <Statistic 
                                title="总成本"
                                value={summary.total_cost}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ fontSize: '16px' }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="当前市值"
                                value={summary.current_value}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ fontSize: '16px' }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="总收益"
                                value={summary.total_return}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ 
                                    fontSize: '16px',
                                    color: getReturnColor(summary.total_return)
                                }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="收益率"
                                value={summary.return_rate * 100}
                                precision={2}
                                suffix="%"
                                valueStyle={{ 
                                    fontSize: '16px',
                                    color: getReturnColor(summary.return_rate)
                                }}
                            />
                        </Col>
                    </Row>
                </Card>
            )}

            {/* 持仓列表 */}
            <div style={{ padding: '0 16px' }}>
                {positions.length === 0 && !loading ? (
                    <Empty 
                        description="暂无持仓记录"
                        style={{ marginTop: 60 }}
                    />
                ) : (
                    positions.map(renderPositionCard)
                )}
            </div>
        </div>
    )
}

export default MobilePositions