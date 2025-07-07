import React, { useState, useEffect } from 'react'
import { Card, Button, message, Empty, Statistic, Row, Col } from 'antd'
import { ReloadOutlined, ArrowUpOutlined, ArrowDownOutlined, EyeOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'

interface Position {
    asset_code: string
    asset_name: string
    total_shares: number
    avg_cost: number
    current_nav: number
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

const MobilePositions: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([])
    const [summary, setSummary] = useState<PositionSummary | null>(null)
    const [loading, setLoading] = useState(false)

    console.log('[DEBUG] MobilePositions 组件渲染, positions:', positions, 'summary:', summary, 'loading:', loading)

    // 获取持仓数据
    const fetchPositions = async () => {
        console.log('[DEBUG] 开始获取持仓数据...')
        setLoading(true)
        try {
            console.log('[DEBUG] 正在调用持仓API...')
            const [positionsRes, summaryRes] = await Promise.all([
                fundAPI.getFundPositions(),
                fundAPI.getPositionSummary()
            ])

            console.log('[DEBUG] 持仓API响应:', positionsRes)
            console.log('[DEBUG] 汇总API响应:', summaryRes)

            if (positionsRes.success && positionsRes.data) {
                console.log('[DEBUG] 设置持仓数据:', positionsRes.data)
                setPositions(positionsRes.data || [])
            } else {
                console.warn('[DEBUG] 持仓API响应失败:', positionsRes)
            }

            if (summaryRes.success && summaryRes.data) {
                console.log('[DEBUG] 设置汇总数据:', summaryRes.data)
                setSummary(summaryRes.data)
            } else {
                console.warn('[DEBUG] 汇总API响应失败:', summaryRes)
            }
        } catch (error) {
            console.error('[DEBUG] 获取持仓数据异常:', error)
            message.error('获取持仓数据失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchPositions()
    }, [])

    useEffect(() => {
        console.log('[DEBUG] 持仓数据更新 - positions.length:', positions.length, 'summary:', summary)
    }, [positions, summary])

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
                            {position.total_shares.toFixed(2)}
                        </div>
                    </div>
                </Col>
                <Col span={12}>
                    <div style={{ textAlign: 'center', padding: '8px', background: '#fafafa', borderRadius: '4px' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>平均成本</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                            ¥{position.avg_cost.toFixed(4)}
                        </div>
                    </div>
                </Col>
            </Row>

            {/* 净值信息 */}
            <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '12px', color: '#666' }}>当前净值</span>
                    <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                        ¥{position.current_nav.toFixed(4)}
                    </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '12px', color: '#666' }}>单位收益</span>
                    <span style={{ 
                        fontSize: '12px', 
                        fontWeight: 'bold',
                        color: getReturnColor(position.current_nav - position.avg_cost)
                    }}>
                        ¥{(position.current_nav - position.avg_cost).toFixed(4)}
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
                                {formatAmount(position.total_invested)}
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
                                color: getReturnColor(position.total_profit)
                            }}>
                                {formatAmount(position.total_profit)}
                            </div>
                        </div>
                    </Col>
                </Row>
            </div>

            {/* 收益率 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: '#666' }}>收益率</span>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    {position.profit_rate >= 0 ? 
                        <ArrowUpOutlined style={{ color: '#52c41a', marginRight: 4 }} /> :
                        <ArrowDownOutlined style={{ color: '#ff4d4f', marginRight: 4 }} />
                    }
                    <span style={{ 
                        fontSize: '14px', 
                        fontWeight: 'bold',
                        color: getReturnColor(position.profit_rate)
                    }}>
                        {formatPercent(position.profit_rate)}
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
                                value={summary.total_invested}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ fontSize: '16px' }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="当前市值"
                                value={summary.total_value}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ fontSize: '16px' }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="总收益"
                                value={summary.total_profit}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ 
                                    fontSize: '16px',
                                    color: getReturnColor(summary.total_profit)
                                }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="收益率"
                                value={summary.total_profit_rate * 100}
                                precision={2}
                                suffix="%"
                                valueStyle={{ 
                                    fontSize: '16px',
                                    color: getReturnColor(summary.total_profit_rate)
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