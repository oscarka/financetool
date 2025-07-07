import React, { useState, useEffect } from 'react'
import { Card, Button, message, Empty, Statistic, Row, Col, Space, Modal, FloatButton, Tag } from 'antd'
import { 
    ReloadOutlined, 
    LineChartOutlined,
    PlusOutlined
} from '@ant-design/icons'
import { fundAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'

interface Position {
    asset_code: string
    asset_name: string
    total_shares: number | string
    avg_cost: number | string
    current_nav: number | string
    current_value: number | string
    total_invested: number | string
    total_profit: number | string
    profit_rate: number | string
    last_updated: string
}

interface PositionSummary {
    total_invested: number | string
    total_value: number | string
    total_profit: number | string
    total_profit_rate: number | string
    asset_count: number
    profitable_count: number
    loss_count: number
}

// 错误边界组件
class MobilePositionsErrorBoundary extends React.Component<
    { children: React.ReactNode },
    { hasError: boolean; error?: Error }
> {
    constructor(props: { children: React.ReactNode }) {
        super(props)
        this.state = { hasError: false }
    }

    static getDerivedStateFromError(error: Error) {
        console.error('❌ [ERROR BOUNDARY] MobilePositions 错误:', error)
        return { hasError: true, error }
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('❌ [ERROR BOUNDARY] MobilePositions 详细错误信息:', {
            error: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack
        })
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '20px', textAlign: 'center' }}>
                    <Card title="页面出错了" style={{ maxWidth: 400, margin: '0 auto' }}>
                        <p>持仓页面遇到了问题，正在诊断中...</p>
                        <p style={{ fontSize: '12px', color: '#666' }}>
                            错误信息: {this.state.error?.message}
                        </p>
                        <Button 
                            type="primary" 
                            onClick={() => {
                                this.setState({ hasError: false })
                                window.location.reload()
                            }}
                        >
                            重新加载
                        </Button>
                    </Card>
                </div>
            )
        }

        return this.props.children
    }
}

const MobilePositions: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([])
    const [summary, setSummary] = useState<PositionSummary | null>(null)
    const [loading, setLoading] = useState(false)
    const [selectedPosition, setSelectedPosition] = useState<Position | null>(null)
    const [detailVisible, setDetailVisible] = useState(false)
    const navigate = useNavigate()

    console.log('🔄 [DEBUG] MobilePositions 组件版本: v3.0.0 (增强错误处理)')
    console.log('🔄 [DEBUG] 组件状态:', { 
        positionsCount: positions.length, 
        summaryExists: !!summary, 
        loading 
    })

    // 强制输出到页面（用于调试）
    useEffect(() => {
        console.log('🚀 MobilePositions useEffect 执行')
        // 在页面顶部添加可见的调试信息
        const debugEl = document.createElement('div')
        debugEl.style.cssText = `
            position: fixed;
            top: 110px;
            left: 10px;
            background: #722ed1;
            color: white;
            padding: 4px 8px;
            font-size: 12px;
            z-index: 10000;
            border-radius: 4px;
        `
        debugEl.textContent = '✅ MobilePositions已加载'
        document.body.appendChild(debugEl)
        
        // 3秒后移除
        setTimeout(() => {
            if (document.body.contains(debugEl)) {
                document.body.removeChild(debugEl)
            }
        }, 3000)
    }, [])

    // 获取持仓数据
    const fetchPositions = async () => {
        console.log('📡 [DEBUG] 开始获取持仓数据...')
        setLoading(true)
        try {
            const [positionsRes, summaryRes] = await Promise.all([
                fundAPI.getFundPositions(),
                fundAPI.getPositionSummary()
            ])

            console.log('📡 [DEBUG] 持仓API原始响应:', positionsRes)
            console.log('📡 [DEBUG] 汇总API原始响应:', summaryRes)

            if (positionsRes.success && positionsRes.data) {
                console.log('📊 [DEBUG] 持仓数据详情:', positionsRes.data)
                
                // 检查数据类型
                if (positionsRes.data.length > 0) {
                    const firstPosition = positionsRes.data[0]
                    console.log('🔍 [DEBUG] 第一个持仓数据类型检查:', {
                        total_shares: {
                            value: firstPosition.total_shares,
                            type: typeof firstPosition.total_shares,
                            hasToFixed: typeof firstPosition.total_shares?.toFixed === 'function'
                        },
                        current_nav: {
                            value: firstPosition.current_nav,
                            type: typeof firstPosition.current_nav,
                            hasToFixed: typeof firstPosition.current_nav?.toFixed === 'function'
                        },
                        total_profit: {
                            value: firstPosition.total_profit,
                            type: typeof firstPosition.total_profit
                        }
                    })
                }
                
                setPositions(positionsRes.data || [])
            } else {
                console.warn('⚠️ [DEBUG] 持仓API响应失败:', positionsRes)
                message.error('获取持仓数据失败')
            }

            if (summaryRes.success && summaryRes.data) {
                console.log('📊 [DEBUG] 汇总数据详情:', summaryRes.data)
                console.log('🔍 [DEBUG] 汇总数据类型检查:', {
                    total_value: {
                        value: summaryRes.data.total_value,
                        type: typeof summaryRes.data.total_value
                    },
                    total_profit: {
                        value: summaryRes.data.total_profit,
                        type: typeof summaryRes.data.total_profit
                    }
                })
                setSummary(summaryRes.data)
            } else {
                console.warn('⚠️ [DEBUG] 汇总API响应失败:', summaryRes)
            }
        } catch (error) {
            console.error('❌ [DEBUG] 获取持仓数据异常:', error)
            message.error('获取持仓数据失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchPositions()
    }, [])

    // 格式化金额
    const formatAmount = (amount: number | string) => {
        const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount
        if (isNaN(numAmount)) return '¥0.00'
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: 'CNY',
            minimumFractionDigits: 2
        }).format(numAmount)
    }

    // 格式化百分比
    const formatPercent = (rate: number | string) => {
        const numRate = typeof rate === 'string' ? parseFloat(rate) : rate
        if (isNaN(numRate)) return '0.00%'
        return `${(numRate * 100).toFixed(2)}%`
    }

    // 安全的数字格式化
    const safeToFixed = (value: number | string, digits: number = 2) => {
        console.log(`🔧 [DEBUG] safeToFixed 调用:`, { value, type: typeof value, digits })
        const numValue = typeof value === 'string' ? parseFloat(value) : value
        if (isNaN(numValue)) {
            console.log(`⚠️ [DEBUG] safeToFixed 无效值，返回默认:`, '0.' + '0'.repeat(digits))
            return '0.' + '0'.repeat(digits)
        }
        const result = numValue.toFixed(digits)
        console.log(`✅ [DEBUG] safeToFixed 成功:`, { input: value, output: result })
        return result
    }

    // 安全的数字转换
    const safeNumber = (value: number | string) => {
        console.log(`🔧 [DEBUG] safeNumber 调用:`, { value, type: typeof value })
        const numValue = typeof value === 'string' ? parseFloat(value) : value
        const result = isNaN(numValue) ? 0 : numValue
        console.log(`✅ [DEBUG] safeNumber 结果:`, { input: value, output: result })
        return result
    }

    // 获取收益颜色
    const getReturnColor = (value: number | string) => {
        const numValue = safeNumber(value)
        const color = numValue >= 0 ? '#52c41a' : '#ff4d4f'
        console.log(`🎨 [DEBUG] getReturnColor:`, { value, numValue, color })
        return color
    }

    // 查看持仓详情
    const handleViewDetail = (position: Position) => {
        console.log('👁️ [DEBUG] 查看详情按钮点击:', position)
        try {
            setSelectedPosition(position)
            setDetailVisible(true)
        } catch (error) {
            console.error('❌ [DEBUG] 查看详情失败:', error)
            message.error('打开详情失败')
        }
    }

    // 编辑持仓（跳转到操作记录页面）
    const handleEdit = (position: Position) => {
        console.log('✏️ [DEBUG] 编辑按钮点击:', position)
        try {
            // 跳转到操作记录页面，并筛选该基金
            navigate(`/operations?fund=${position.asset_code}`)
        } catch (error) {
            console.error('❌ [DEBUG] 编辑跳转失败:', error)
            message.error('跳转失败')
        }
    }

    // 查看基金详情
    const handleViewFund = (position: Position) => {
        console.log('📈 [DEBUG] 基金详情按钮点击:', position)
        try {
            // TODO: 跳转到基金详情页面
            message.info(`查看${position.asset_code}基金详情`)
        } catch (error) {
            console.error('❌ [DEBUG] 查看基金详情失败:', error)
        }
    }

    // 买入基金
    const handleBuy = (position: Position) => {
        console.log('💰 [DEBUG] 买入按钮点击:', position)
        try {
            // TODO: 打开买入弹窗或跳转到买入页面
            message.info(`买入${position.asset_code}`)
        } catch (error) {
            console.error('❌ [DEBUG] 买入操作失败:', error)
        }
    }

    // 卖出基金
    const handleSell = (position: Position) => {
        console.log('💸 [DEBUG] 卖出按钮点击:', position)
        try {
            // TODO: 打开卖出弹窗或跳转到卖出页面
            message.info(`卖出${position.asset_code}`)
        } catch (error) {
            console.error('❌ [DEBUG] 卖出操作失败:', error)
        }
    }

    // 渲染持仓卡片
    const renderPositionCard = (position: Position) => {
        const profitColor = getReturnColor(position.total_profit)
        const profitRateColor = getReturnColor(position.profit_rate)
        
        return (
            <Card
                key={position.asset_code}
                style={{ 
                    marginBottom: 12,
                    border: safeNumber(position.total_profit) >= 0 ? '1px solid #b7eb8f' : '1px solid #ffadd2'
                }}
                bodyStyle={{ padding: '16px' }}
            >
                {/* 基金信息头部 */}
                <div style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ 
                                fontWeight: 'bold', 
                                fontSize: '16px', 
                                marginBottom: 2,
                                color: '#1890ff'
                            }}>
                                {position.asset_code}
                            </div>
                            <div style={{ 
                                fontSize: '13px', 
                                color: '#666', 
                                lineHeight: '1.3',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                            }}>
                                {position.asset_name}
                            </div>
                        </div>
                        <div style={{ marginLeft: 12, flexShrink: 0 }}>
                            <Tag color={safeNumber(position.total_profit) >= 0 ? 'green' : 'red'}>
                                {safeNumber(position.total_profit) >= 0 ? '盈利' : '亏损'}
                            </Tag>
                        </div>
                    </div>
                </div>

                {/* 核心数据展示 */}
                <div style={{ 
                    background: safeNumber(position.total_profit) >= 0 ? '#f6ffed' : '#fff2f0',
                    padding: '12px',
                    borderRadius: '8px',
                    marginBottom: 12
                }}>
                    <Row gutter={16}>
                        <Col span={12}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '18px', fontWeight: 'bold', color: profitColor }}>
                                    {safeNumber(position.total_profit) >= 0 ? '+' : ''}{formatAmount(position.total_profit)}
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>累计收益</div>
                            </div>
                        </Col>
                        <Col span={12}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '18px', fontWeight: 'bold', color: profitRateColor }}>
                                    {safeNumber(position.profit_rate) >= 0 ? '+' : ''}{formatPercent(position.profit_rate)}
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>收益率</div>
                            </div>
                        </Col>
                    </Row>
                </div>

                {/* 详细数据 */}
                <Row gutter={[8, 8]} style={{ marginBottom: 12 }}>
                    <Col span={12}>
                        <div style={{ 
                            textAlign: 'center', 
                            padding: '8px', 
                            background: '#fafafa', 
                            borderRadius: '4px' 
                        }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                {formatAmount(position.current_value)}
                            </div>
                            <div style={{ fontSize: '11px', color: '#666' }}>当前市值</div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ 
                            textAlign: 'center', 
                            padding: '8px', 
                            background: '#fafafa', 
                            borderRadius: '4px' 
                        }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                {formatAmount(position.total_invested)}
                            </div>
                            <div style={{ fontSize: '11px', color: '#666' }}>累计投入</div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ 
                            textAlign: 'center', 
                            padding: '8px', 
                            background: '#fafafa', 
                            borderRadius: '4px' 
                        }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                {safeToFixed(position.total_shares, 2)}
                            </div>
                            <div style={{ fontSize: '11px', color: '#666' }}>持仓份额</div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ 
                            textAlign: 'center', 
                            padding: '8px', 
                            background: '#fafafa', 
                            borderRadius: '4px' 
                        }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                ¥{safeToFixed(position.current_nav, 4)}
                            </div>
                            <div style={{ fontSize: '11px', color: '#666' }}>当前净值</div>
                        </div>
                    </Col>
                </Row>

                {/* 操作按钮 */}
                <div style={{ 
                    borderTop: '1px solid #f0f0f0', 
                    paddingTop: '12px'
                }}>
                    <Row gutter={8}>
                        <Col span={6}>
                            <Button 
                                type="primary"
                                size="small"
                                block
                                onClick={() => handleViewDetail(position)}
                            >
                                详情
                            </Button>
                        </Col>
                        <Col span={6}>
                            <Button 
                                size="small"
                                block
                                onClick={() => handleViewFund(position)}
                            >
                                基金
                            </Button>
                        </Col>
                        <Col span={6}>
                            <Button 
                                type="primary"
                                size="small"
                                block
                                style={{ background: '#52c41a', borderColor: '#52c41a' }}
                                onClick={() => handleBuy(position)}
                            >
                                买入
                            </Button>
                        </Col>
                        <Col span={6}>
                            <Button 
                                danger
                                size="small"
                                block
                                onClick={() => handleSell(position)}
                            >
                                卖出
                            </Button>
                        </Col>
                    </Row>
                </div>
            </Card>
        )
    }

    return (
        <div style={{ paddingBottom: '80px' }}>
            {/* 页面标题和刷新按钮 */}
            <Card 
                bordered={false}
                style={{ marginBottom: 16 }}
                bodyStyle={{ padding: '16px' }}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>持仓管理</h2>
                        <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
                            查看和管理基金持仓
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
                    title={
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <span>持仓汇总</span>
                            <Tag 
                                color={safeNumber(summary.total_profit) >= 0 ? 'green' : 'red'}
                                style={{ marginLeft: 8 }}
                            >
                                {safeNumber(summary.total_profit) >= 0 ? '总体盈利' : '总体亏损'}
                            </Tag>
                        </div>
                    }
                    bordered={false}
                    style={{ 
                        marginBottom: 16,
                        background: safeNumber(summary.total_profit) >= 0 ? '#f6ffed' : '#fff2f0',
                        border: `1px solid ${safeNumber(summary.total_profit) >= 0 ? '#b7eb8f' : '#ffadd2'}`
                    }}
                    bodyStyle={{ padding: '16px' }}
                >
                    <Row gutter={[8, 12]}>
                        <Col span={12}>
                            <Statistic 
                                title="总市值"
                                value={safeNumber(summary.total_value)}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ 
                                    fontSize: '20px', 
                                    fontWeight: 'bold', 
                                    color: '#1890ff' 
                                }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="累计投入"
                                value={safeNumber(summary.total_invested)}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ fontSize: '16px' }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="累计收益"
                                value={Math.abs(safeNumber(summary.total_profit))}
                                precision={2}
                                prefix={safeNumber(summary.total_profit) >= 0 ? '+¥' : '-¥'}
                                valueStyle={{ 
                                    fontSize: '18px',
                                    fontWeight: 'bold',
                                    color: getReturnColor(summary.total_profit)
                                }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic 
                                title="总收益率"
                                value={Math.abs(safeNumber(summary.total_profit_rate) * 100)}
                                precision={2}
                                prefix={safeNumber(summary.total_profit_rate) >= 0 ? '+' : '-'}
                                suffix="%"
                                valueStyle={{ 
                                    fontSize: '18px',
                                    fontWeight: 'bold',
                                    color: getReturnColor(summary.total_profit_rate)
                                }}
                            />
                        </Col>
                    </Row>
                    
                    <div style={{ 
                        marginTop: 16, 
                        paddingTop: 16, 
                        borderTop: '1px solid #f0f0f0',
                        display: 'flex',
                        justifyContent: 'space-around',
                        textAlign: 'center'
                    }}>
                        <div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                                {summary.asset_count || 0}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>持仓基金</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                                {summary.profitable_count || 0}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>盈利基金</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#ff4d4f' }}>
                                {summary.loss_count || 0}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>亏损基金</div>
                        </div>
                    </div>
                </Card>
            )}

            {/* 持仓列表 */}
            <div style={{ padding: '0 16px' }}>
                {positions.length === 0 && !loading ? (
                    <Empty 
                        description="暂无持仓记录"
                        style={{ marginTop: 60 }}
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                    >
                        <Button 
                            type="primary" 
                            onClick={() => navigate('/operations')}
                        >
                            去记录第一笔操作
                        </Button>
                    </Empty>
                ) : (
                    positions.map(renderPositionCard)
                )}
            </div>

            {/* 悬浮按钮 */}
            <FloatButton.Group
                trigger="click"
                type="primary"
                style={{ right: 24, bottom: 80 }}
                icon={<PlusOutlined />}
            >
                <FloatButton 
                    icon={<PlusOutlined />} 
                    tooltip="记录操作"
                    onClick={() => navigate('/operations')}
                />
                <FloatButton 
                    icon={<LineChartOutlined />} 
                    tooltip="收益分析"
                    onClick={() => navigate('/analysis')}
                />
            </FloatButton.Group>

            {/* 持仓详情弹窗 */}
            <Modal
                title="持仓详情"
                open={detailVisible}
                onCancel={() => setDetailVisible(false)}
                footer={null}
                width="90%"
                style={{ top: 20 }}
            >
                {selectedPosition && (
                    <div>
                        <Card
                            title={`${selectedPosition.asset_code} - ${selectedPosition.asset_name}`}
                            style={{ marginBottom: 16 }}
                        >
                            <Row gutter={[16, 16]}>
                                <Col span={12}>
                                    <Statistic
                                        title="持仓份额"
                                        value={safeNumber(selectedPosition.total_shares)}
                                        precision={2}
                                        suffix="份"
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="平均成本"
                                        value={safeNumber(selectedPosition.avg_cost)}
                                        precision={4}
                                        prefix="¥"
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="当前净值"
                                        value={safeNumber(selectedPosition.current_nav)}
                                        precision={4}
                                        prefix="¥"
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="单位收益"
                                        value={safeNumber(selectedPosition.current_nav) - safeNumber(selectedPosition.avg_cost)}
                                        precision={4}
                                        prefix={safeNumber(selectedPosition.current_nav) - safeNumber(selectedPosition.avg_cost) >= 0 ? '+¥' : '-¥'}
                                        valueStyle={{
                                            color: getReturnColor(safeNumber(selectedPosition.current_nav) - safeNumber(selectedPosition.avg_cost))
                                        }}
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="当前市值"
                                        value={safeNumber(selectedPosition.current_value)}
                                        precision={2}
                                        prefix="¥"
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="累计投入"
                                        value={safeNumber(selectedPosition.total_invested)}
                                        precision={2}
                                        prefix="¥"
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="累计收益"
                                        value={Math.abs(safeNumber(selectedPosition.total_profit))}
                                        precision={2}
                                        prefix={safeNumber(selectedPosition.total_profit) >= 0 ? '+¥' : '-¥'}
                                        valueStyle={{
                                            color: getReturnColor(selectedPosition.total_profit)
                                        }}
                                    />
                                </Col>
                                <Col span={12}>
                                    <Statistic
                                        title="收益率"
                                        value={Math.abs(safeNumber(selectedPosition.profit_rate) * 100)}
                                        precision={2}
                                        prefix={safeNumber(selectedPosition.profit_rate) >= 0 ? '+' : '-'}
                                        suffix="%"
                                        valueStyle={{
                                            color: getReturnColor(selectedPosition.profit_rate)
                                        }}
                                    />
                                </Col>
                            </Row>
                        </Card>

                        <div style={{ textAlign: 'center' }}>
                            <Space>
                                <Button 
                                    type="primary"
                                    onClick={() => {
                                        setDetailVisible(false)
                                        handleEdit(selectedPosition)
                                    }}
                                >
                                    查看操作记录
                                </Button>
                                <Button 
                                    onClick={() => {
                                        setDetailVisible(false)
                                        handleBuy(selectedPosition)
                                    }}
                                >
                                    买入
                                </Button>
                                <Button 
                                    danger
                                    onClick={() => {
                                        setDetailVisible(false)
                                        handleSell(selectedPosition)
                                    }}
                                >
                                    卖出
                                </Button>
                            </Space>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    )
}

// 导出包装了错误边界的组件
const MobilePositionsWithErrorBoundary: React.FC = () => (
    <MobilePositionsErrorBoundary>
        <MobilePositions />
    </MobilePositionsErrorBoundary>
)

export default MobilePositionsWithErrorBoundary