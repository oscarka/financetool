import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Space, Button, message, Input, Divider } from 'antd'
import { SyncOutlined, BarChartOutlined, SearchOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'
import type { APIResponse } from '../services/api'

interface FundOperation {
    id: number
    operation_date: string
    operation_type: 'buy' | 'sell' | 'dividend'
    asset_code: string
    asset_name: string
    amount: number
    strategy?: string
    emotion_score?: number
    notes?: string
}

interface AnalysisData {
    total_operations: number
    buy_operations: number
    sell_operations: number
    total_invested: number
    total_profit: number
    avg_emotion_score: number
    most_active_fund: string
    best_performing_fund: string
    worst_performing_fund: string
}

interface NavHistoryItem {
    id: number
    fund_code: string
    nav_date: string
    nav: number
    accumulated_nav?: number
    source: string
}

const FundAnalysis: React.FC = () => {
    const [operations, setOperations] = useState<FundOperation[]>([])
    const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
    const [loading, setLoading] = useState(false)

    // 历史净值查询相关状态
    const [fundCode, setFundCode] = useState('')
    const [navHistory, setNavHistory] = useState<NavHistoryItem[]>([])
    const [navLoading, setNavLoading] = useState(false)
    const [navPagination, setNavPagination] = useState({
        current: 1,
        pageSize: 20,
        total: 0,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total: number) => `共 ${total} 条记录`
    })

    // 获取分析数据
    const fetchAnalysisData = async () => {
        setLoading(true)
        try {
            const [operationsResponse, positionsResponse] = await Promise.all([
                fundAPI.getFundOperations(),
                fundAPI.getFundPositions()
            ])

            if (operationsResponse.success && operationsResponse.data) {
                const ops = operationsResponse.data || []
                setOperations(ops)

                // 计算分析数据
                const analysis: AnalysisData = {
                    total_operations: ops.length,
                    buy_operations: ops.filter(op => op.operation_type === 'buy').length,
                    sell_operations: ops.filter(op => op.operation_type === 'sell').length,
                    total_invested: ops.filter(op => op.operation_type === 'buy')
                        .reduce((sum, op) => sum + op.amount, 0),
                    total_profit: 0, // 需要从持仓数据计算
                    avg_emotion_score: ops.length > 0
                        ? ops.reduce((sum, op) => sum + (op.emotion_score || 5), 0) / ops.length
                        : 0,
                    most_active_fund: '',
                    best_performing_fund: '',
                    worst_performing_fund: ''
                }

                // 计算最活跃基金
                const fundCounts = ops.reduce((acc, op) => {
                    acc[op.asset_code] = (acc[op.asset_code] || 0) + 1
                    return acc
                }, {} as Record<string, number>)

                if (Object.keys(fundCounts).length > 0) {
                    analysis.most_active_fund = Object.entries(fundCounts)
                        .sort(([, a], [, b]) => b - a)[0][0]
                }

                setAnalysisData(analysis)
            }
        } catch (error: any) {
            console.error('获取分析数据失败:', error)
            message.error('获取分析数据失败')
        } finally {
            setLoading(false)
        }
    }

    // 查询历史净值
    const fetchNavHistory = async (forceUpdate = false) => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        setNavLoading(true)
        try {
            const response = await fundAPI.getFundNavHistoryByCode(fundCode.trim(), forceUpdate)

            if (response.success && response.data) {
                const history = response.data.nav_history || []
                setNavHistory(history)
                setNavPagination(prev => ({
                    ...prev,
                    total: history.length
                }))
                message.success(`成功获取 ${history.length} 条历史净值记录`)
            } else {
                message.error(response.message || '获取历史净值失败')
            }
        } catch (error: any) {
            console.error('获取历史净值失败:', error)
            message.error('获取历史净值失败')
        } finally {
            setNavLoading(false)
        }
    }

    // 处理分页变化
    const handleNavPaginationChange = (page: number, pageSize: number) => {
        setNavPagination(prev => ({
            ...prev,
            current: page,
            pageSize: pageSize
        }))
    }

    useEffect(() => {
        fetchAnalysisData()
    }, [])

    // 操作记录表格列定义
    const columns = [
        {
            title: '操作日期',
            dataIndex: 'operation_date',
            key: 'operation_date',
            render: (date: string) => new Date(date).toLocaleDateString()
        },
        {
            title: '操作类型',
            dataIndex: 'operation_type',
            key: 'operation_type',
            render: (type: string) => {
                const typeMap = {
                    buy: { text: '买入', color: 'green' },
                    sell: { text: '卖出', color: 'red' },
                    dividend: { text: '分红', color: 'blue' }
                }
                const config = typeMap[type as keyof typeof typeMap] || { text: type, color: 'default' }
                return <Tag color={config.color}>{config.text}</Tag>
            }
        },
        {
            title: '基金代码',
            dataIndex: 'asset_code',
            key: 'asset_code'
        },
        {
            title: '基金名称',
            dataIndex: 'asset_name',
            key: 'asset_name',
            ellipsis: true
        },
        {
            title: '操作金额',
            dataIndex: 'amount',
            key: 'amount',
            render: (amount: number) => `¥${amount.toFixed(2)}`
        },
        {
            title: '情绪评分',
            dataIndex: 'emotion_score',
            key: 'emotion_score',
            render: (score: number) => {
                let color = 'default'
                let text = '未知'
                if (score <= 3) { color = 'red'; text = '恐慌' }
                else if (score <= 5) { color = 'orange'; text = '谨慎' }
                else if (score <= 7) { color = 'blue'; text = '理性' }
                else { color = 'green'; text = '贪婪' }
                return <Tag color={color}>{score}分 - {text}</Tag>
            }
        },
        {
            title: '投资策略',
            dataIndex: 'strategy',
            key: 'strategy',
            ellipsis: true,
            render: (strategy: string) => strategy || '-'
        }
    ]

    // 历史净值表格列定义
    const navColumns = [
        {
            title: '日期',
            dataIndex: 'nav_date',
            key: 'nav_date',
            render: (date: string) => new Date(date).toLocaleDateString()
        },
        {
            title: '单位净值',
            dataIndex: 'nav',
            key: 'nav',
            render: (nav: number) => nav?.toFixed(4) || '-'
        },
        {
            title: '累计净值',
            dataIndex: 'accumulated_nav',
            key: 'accumulated_nav',
            render: (nav: number) => nav?.toFixed(4) || '-'
        },
        {
            title: '数据来源',
            dataIndex: 'source',
            key: 'source',
            render: (source: string) => <Tag color="blue">{source}</Tag>
        }
    ]

    return (
        <div className="space-y-6">
            {/* 分析概览 */}
            {analysisData && (
                <Card>
                    <Row gutter={16}>
                        <Col span={6}>
                            <Statistic
                                title="总操作次数"
                                value={analysisData.total_operations}
                                valueStyle={{ color: '#1890ff' }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="买入次数"
                                value={analysisData.buy_operations}
                                valueStyle={{ color: '#3f8600' }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="卖出次数"
                                value={analysisData.sell_operations}
                                valueStyle={{ color: '#cf1322' }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="平均情绪评分"
                                value={analysisData.avg_emotion_score}
                                precision={1}
                                valueStyle={{ color: '#722ed1' }}
                            />
                        </Col>
                    </Row>
                    <Row gutter={16} style={{ marginTop: 16 }}>
                        <Col span={8}>
                            <Statistic
                                title="累计投入"
                                value={analysisData.total_invested}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ color: '#3f8600' }}
                            />
                        </Col>
                        <Col span={8}>
                            <Statistic
                                title="累计收益"
                                value={analysisData.total_profit}
                                precision={2}
                                prefix="¥"
                                valueStyle={{ color: analysisData.total_profit >= 0 ? '#3f8600' : '#cf1322' }}
                            />
                        </Col>
                        <Col span={8}>
                            <Statistic
                                title="最活跃基金"
                                value={analysisData.most_active_fund || '暂无'}
                                valueStyle={{ color: '#1890ff' }}
                            />
                        </Col>
                    </Row>
                </Card>
            )}

            {/* 历史净值查询 */}
            <Card title="历史净值查询">
                <Row gutter={16} align="middle">
                    <Col span={8}>
                        <Input
                            placeholder="请输入基金代码（如：004042）"
                            value={fundCode}
                            onChange={(e) => setFundCode(e.target.value)}
                            onPressEnter={() => fetchNavHistory()}
                            prefix={<SearchOutlined />}
                        />
                    </Col>
                    <Col span={16}>
                        <Space>
                            <Button
                                type="primary"
                                icon={<SearchOutlined />}
                                loading={navLoading}
                                onClick={() => fetchNavHistory()}
                            >
                                查询历史净值
                            </Button>
                            <Button
                                icon={<SyncOutlined />}
                                loading={navLoading}
                                onClick={() => fetchNavHistory(true)}
                            >
                                强制更新
                            </Button>
                        </Space>
                    </Col>
                </Row>

                {navHistory.length > 0 && (
                    <>
                        <Divider />
                        <Table
                            columns={navColumns}
                            dataSource={navHistory.slice(
                                (navPagination.current - 1) * navPagination.pageSize,
                                navPagination.current * navPagination.pageSize
                            )}
                            rowKey="id"
                            loading={navLoading}
                            pagination={navPagination}
                            onChange={(pagination) => {
                                handleNavPaginationChange(pagination.current || 1, pagination.pageSize || 20)
                            }}
                            scroll={{ x: 600 }}
                        />
                    </>
                )}
            </Card>

            {/* 操作记录分析 */}
            <Card
                title="操作记录分析"
                extra={
                    <Space>
                        <Button
                            icon={<BarChartOutlined />}
                            onClick={() => message.info('图表功能正在开发中...')}
                        >
                            收益图表
                        </Button>
                        <Button
                            type="primary"
                            icon={<SyncOutlined />}
                            loading={loading}
                            onClick={fetchAnalysisData}
                        >
                            刷新数据
                        </Button>
                    </Space>
                }
            >
                <Table
                    columns={columns}
                    dataSource={operations}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`
                    }}
                />
            </Card>

            {/* 空状态 */}
            {!loading && operations.length === 0 && (
                <Card>
                    <div className="text-center py-8">
                        <div className="text-gray-500 mb-4">
                            暂无操作记录数据
                        </div>
                        <p className="text-sm text-gray-400">
                            请先在"操作记录"中添加基金操作
                        </p>
                    </div>
                </Card>
            )}
        </div>
    )
}

export default FundAnalysis 