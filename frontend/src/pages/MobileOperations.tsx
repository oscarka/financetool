import React, { useState, useEffect } from 'react'
import { Card, Button, Tag, Space, FloatButton, Modal, Form, Input, Select, DatePicker, message, Empty } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, FilterOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'
import dayjs from 'dayjs'

const { Option } = Select
const { RangePicker } = DatePicker

interface FundOperation {
    id: number
    operation_date: string
    operation_type: 'buy' | 'sell' | 'dividend'
    asset_code: string
    asset_name: string
    amount: number
    quantity?: number
    price?: number
    nav?: number
    fee?: number
    status: 'pending' | 'confirmed' | 'cancelled' | 'processed'
    latest_nav?: number | null
    dca_plan_id?: number | null
}

const MobileOperations: React.FC = () => {
    console.log('📱 MobileOperations 组件已渲染', {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        screenWidth: window.innerWidth,
        screenHeight: window.innerHeight
    })
    
    // 强制输出到页面（用于调试）
    useEffect(() => {
        console.log('🚀 MobileOperations useEffect 执行')
        // 在页面顶部添加可见的调试信息
        const debugEl = document.createElement('div')
        debugEl.style.cssText = `
            position: fixed;
            top: 50px;
            left: 10px;
            background: #52c41a;
            color: white;
            padding: 4px 8px;
            font-size: 12px;
            z-index: 10000;
            border-radius: 4px;
        `
        debugEl.textContent = '✅ MobileOperations已加载'
        document.body.appendChild(debugEl)
        
        // 3秒后移除
        setTimeout(() => {
            document.body.removeChild(debugEl)
        }, 3000)
    }, [])
    
    const [operations, setOperations] = useState<FundOperation[]>([])
    const [loading, setLoading] = useState(false)
    const [filterVisible, setFilterVisible] = useState(false)
    const [filterForm] = Form.useForm()
    const [hasMore, setHasMore] = useState(true)
    const [page, setPage] = useState(1)

    // 获取操作记录
    const fetchOperations = async (isRefresh = false) => {
        setLoading(true)
        try {
            const currentPage = isRefresh ? 1 : page
            const response = await fundAPI.getFundOperations({
                page: currentPage,
                page_size: 20
            })
            
            if (response.success && response.data) {
                if (isRefresh) {
                    setOperations(response.data || [])
                    setPage(2)
                } else {
                    setOperations(prev => [...prev, ...(response.data || [])])
                    setPage(prev => prev + 1)
                }
                
                setHasMore((response.data || []).length === 20)
            }
        } catch (error) {
            message.error('获取操作记录失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchOperations(true)
    }, [])

    // 加载更多
    const loadMore = () => {
        if (!loading && hasMore) {
            fetchOperations(false)
        }
    }

    // 删除操作
    const handleDelete = async (id: number) => {
        try {
            const response = await fundAPI.deleteFundOperation(id)
            if (response.success) {
                message.success('删除成功')
                setOperations(prev => prev.filter(op => op.id !== id))
            }
        } catch (error) {
            message.error('删除失败')
        }
    }

    // 获取操作类型样式
    const getOperationTypeStyle = (type: string) => {
        const styles = {
            buy: { color: '#52c41a', background: '#f6ffed', border: '1px solid #b7eb8f' },
            sell: { color: '#ff4d4f', background: '#fff2f0', border: '1px solid #ffadd2' },
            dividend: { color: '#1890ff', background: '#f0f5ff', border: '1px solid #adc6ff' }
        }
        return styles[type as keyof typeof styles] || styles.buy
    }

    // 获取状态样式
    const getStatusColor = (status: string) => {
        const colors = {
            pending: 'orange',
            confirmed: 'green',
            cancelled: 'red',
            processed: 'blue'
        }
        return colors[status as keyof typeof colors] || 'default'
    }

    // 格式化金额
    const formatAmount = (amount: number) => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: 'CNY',
            minimumFractionDigits: 2
        }).format(amount)
    }

    // 查看操作详情
    const handleViewOperation = (operation: FundOperation) => {
        Modal.info({
            title: '操作详情',
            width: '90%',
            content: (
                <div style={{ marginTop: 16 }}>
                    <div style={{ marginBottom: 12 }}>
                        <strong>基金代码：</strong>{operation.asset_code}
                    </div>
                    <div style={{ marginBottom: 12 }}>
                        <strong>基金名称：</strong>{operation.asset_name}
                    </div>
                    <div style={{ marginBottom: 12 }}>
                        <strong>操作类型：</strong>
                        {operation.operation_type === 'buy' ? '买入' : 
                         operation.operation_type === 'sell' ? '卖出' : '分红'}
                    </div>
                    <div style={{ marginBottom: 12 }}>
                        <strong>操作日期：</strong>{dayjs(operation.operation_date).format('YYYY-MM-DD HH:mm:ss')}
                    </div>
                    <div style={{ marginBottom: 12 }}>
                        <strong>操作金额：</strong>{formatAmount(operation.amount)}
                    </div>
                    {operation.quantity && (
                        <div style={{ marginBottom: 12 }}>
                            <strong>份额：</strong>{Number(operation.quantity).toFixed(2)}
                        </div>
                    )}
                    {operation.nav && (
                        <div style={{ marginBottom: 12 }}>
                            <strong>净值：</strong>¥{Number(operation.nav).toFixed(4)}
                        </div>
                    )}
                    {operation.fee && (
                        <div style={{ marginBottom: 12 }}>
                            <strong>手续费：</strong>{formatAmount(operation.fee)}
                        </div>
                    )}
                    <div style={{ marginBottom: 12 }}>
                        <strong>状态：</strong>
                        <Tag color={getStatusColor(operation.status)} style={{ marginLeft: 8 }}>
                            {operation.status === 'pending' ? '待确认' :
                             operation.status === 'confirmed' ? '已确认' :
                             operation.status === 'cancelled' ? '已取消' : '已处理'}
                        </Tag>
                    </div>
                    {operation.dca_plan_id && (
                        <div style={{ marginBottom: 12 }}>
                            <strong>定投计划ID：</strong>{operation.dca_plan_id}
                        </div>
                    )}
                </div>
            ),
            onOk() {},
        })
    }

    // 编辑操作
    const handleEditOperation = (_operation: FundOperation) => {
        // TODO: 实现编辑功能
        message.info('编辑操作功能开发中')
    }

    // 渲染操作卡片
    const renderOperationCard = (operation: FundOperation) => (
        <Card
            key={operation.id}
            size="small"
            style={{ marginBottom: 12 }}
            bodyStyle={{ padding: '12px 16px' }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                    {/* 第一行：操作类型和日期 */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <div style={{ 
                            ...getOperationTypeStyle(operation.operation_type),
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                        }}>
                            {operation.operation_type === 'buy' ? '买入' : 
                             operation.operation_type === 'sell' ? '卖出' : '分红'}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                            {dayjs(operation.operation_date).format('MM-DD HH:mm')}
                        </div>
                    </div>

                    {/* 第二行：基金信息 */}
                    <div style={{ marginBottom: 8 }}>
                        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: 2 }}>
                            {operation.asset_code}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.2' }}>
                            {operation.asset_name}
                        </div>
                    </div>

                    {/* 第三行：金额和份额 */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                        <div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                                {formatAmount(operation.amount)}
                            </div>
                            {operation.quantity && (
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    份额：{Number(operation.quantity).toFixed(2)}
                                </div>
                            )}
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            {operation.nav && (
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                    净值：¥{Number(operation.nav).toFixed(4)}
                                </div>
                            )}
                            {operation.latest_nav && (
                                <div style={{ fontSize: '12px', color: '#1890ff' }}>
                                    最新：¥{Number(operation.latest_nav).toFixed(4)}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* 第四行：状态和操作 */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Tag color={getStatusColor(operation.status)}>
                            {operation.status === 'pending' ? '待确认' :
                             operation.status === 'confirmed' ? '已确认' :
                             operation.status === 'cancelled' ? '已取消' : '已处理'}
                        </Tag>
                        <Space size={4}>
                            <Button 
                                type="text" 
                                size="small" 
                                icon={<EyeOutlined />}
                                style={{ padding: '0 4px' }}
                                onClick={() => handleViewOperation(operation)}
                            />
                            <Button 
                                type="text" 
                                size="small" 
                                icon={<EditOutlined />}
                                style={{ padding: '0 4px' }}
                                onClick={() => handleEditOperation(operation)}
                            />
                            <Button 
                                type="text" 
                                size="small" 
                                danger
                                icon={<DeleteOutlined />}
                                style={{ padding: '0 4px' }}
                                onClick={() => {
                                    Modal.confirm({
                                        title: '确认删除',
                                        content: '确定要删除这条操作记录吗？',
                                        onOk: () => handleDelete(operation.id)
                                    })
                                }}
                            />
                        </Space>
                    </div>
                </div>
            </div>
        </Card>
    )

    return (
        <div style={{ paddingBottom: '80px' }}>
            {/* 页面标题 */}
            <Card 
                bordered={false}
                style={{ marginBottom: 16 }}
                bodyStyle={{ padding: '16px' }}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>操作记录</h2>
                        <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
                            记录您的投资操作和决策
                        </p>
                    </div>
                    <Button 
                        type="primary" 
                        size="small" 
                        icon={<FilterOutlined />}
                        onClick={() => setFilterVisible(true)}
                    >
                        筛选
                    </Button>
                </div>
            </Card>

            {/* 操作列表 */}
            <div style={{ padding: '0 16px' }}>
                {operations.length === 0 && !loading ? (
                    <Empty 
                        description="暂无操作记录"
                        style={{ marginTop: 60 }}
                    />
                ) : (
                    <>
                        {operations.map(renderOperationCard)}
                        
                        {/* 加载更多 */}
                        {hasMore && (
                            <div style={{ textAlign: 'center', marginTop: 16 }}>
                                <Button 
                                    loading={loading}
                                    onClick={loadMore}
                                    type="dashed"
                                    block
                                >
                                    {loading ? '加载中...' : '加载更多'}
                                </Button>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* 悬浮按钮 */}
            <FloatButton
                icon={<PlusOutlined />}
                type="primary"
                style={{ right: 24, bottom: 80 }}
                onClick={() => {
                    // TODO: 打开添加操作记录弹窗
                    message.info('添加操作记录功能开发中')
                }}
            />

            {/* 筛选弹窗 */}
            <Modal
                title="筛选操作记录"
                open={filterVisible}
                onCancel={() => setFilterVisible(false)}
                footer={null}
                width="90%"
                style={{ top: 20 }}
            >
                <Form
                    form={filterForm}
                    layout="vertical"
                    onFinish={(values) => {
                        console.log('筛选条件:', values)
                        setFilterVisible(false)
                        // TODO: 实现筛选逻辑
                    }}
                >
                    <Form.Item label="基金代码" name="asset_code">
                        <Input placeholder="请输入基金代码" />
                    </Form.Item>
                    
                    <Form.Item label="操作类型" name="operation_type">
                        <Select placeholder="请选择操作类型" allowClear>
                            <Option value="buy">买入</Option>
                            <Option value="sell">卖出</Option>
                            <Option value="dividend">分红</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item label="状态" name="status">
                        <Select placeholder="请选择状态" allowClear>
                            <Option value="pending">待确认</Option>
                            <Option value="confirmed">已确认</Option>
                            <Option value="cancelled">已取消</Option>
                            <Option value="processed">已处理</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item label="日期范围" name="date_range">
                        <RangePicker style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item>
                        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                            <Button onClick={() => filterForm.resetFields()}>
                                重置
                            </Button>
                            <Button type="primary" htmlType="submit">
                                确定
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    )
}

export default MobileOperations