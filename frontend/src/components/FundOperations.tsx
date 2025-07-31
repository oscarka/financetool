import React, { useState, useEffect } from 'react'
import { Card, Button, Form, Input, Select, DatePicker, InputNumber, message, Table, Space, Tag, Modal, Popconfirm, Tooltip, Radio, Row, Col } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'

import dayjs from 'dayjs'

const { Option } = Select
const { TextArea } = Input
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
    strategy?: string
    emotion_score?: number
    notes?: string
    status: 'pending' | 'confirmed' | 'cancelled' | 'processed'
    created_at: string
    latest_nav?: number | null
    dca_plan_id?: number | null
}

interface FundOperationForm {
    operation_date: string
    operation_type: 'buy' | 'sell' | 'dividend'
    asset_code: string
    asset_name: string
    amount: number
    fee?: number
    nav?: number
    quantity?: number
    strategy?: string
    emotion_score?: number
    notes?: string
    sell_mode?: 'amount' | 'quantity'
    position_select?: string
    status?: 'pending' | 'confirmed' | 'cancelled'
}

// 搜索筛选参数接口
interface SearchParams {
    asset_code?: string
    operation_type?: string
    start_date?: string
    end_date?: string
    dca_plan_id?: number
    status?: string
}

const FundOperations: React.FC = () => {
    const [form] = Form.useForm()
    const [searchForm] = Form.useForm()
    const [operations, setOperations] = useState<FundOperation[]>([])
    const [loading, setLoading] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [modalVisible, setModalVisible] = useState(false)
    const [editingOperation, setEditingOperation] = useState<FundOperation | null>(null)
    const [quantityManuallySet, setQuantityManuallySet] = useState(false)
    const [latestNavMap, setLatestNavMap] = useState<{ [code: string]: number }>({})
    const [modalMode, setModalMode] = useState<'view' | 'edit' | 'create'>('create')
    const [availablePositions, setAvailablePositions] = useState<any[]>([])
    const [sellMode, setSellMode] = useState<'amount' | 'quantity'>('quantity')
    const [currentOperationType, setCurrentOperationType] = useState<'buy' | 'sell' | 'dividend'>('buy')

    // 搜索筛选相关状态
    const [searchParams, setSearchParams] = useState<SearchParams>({})
    const [dcaPlans, setDcaPlans] = useState<any[]>([])

    // 分页相关状态
    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 20,
        total: 0
    })

    // 分红处理相关状态
    const [dividendModalVisible, setDividendModalVisible] = useState(false)
    const [processingDividend, setProcessingDividend] = useState<FundOperation | null>(null)
    const [dividendProcessType, setDividendProcessType] = useState<'reinvest' | 'withdraw' | 'skip'>('reinvest')

    // 批量查所有基金的最新净值 - 已优化：后端已包含最新净值，无需前端单独获取
    const fetchLatestNavs = async (operations: FundOperation[]) => {
        // 优化：移除前端的单独API调用，后端已经返回latest_nav字段
        // 这个函数现在只用于处理latest_nav字段，构建navMap用于显示
        const navMap: { [code: string]: number } = {}
        operations.forEach(op => {
            if (op.latest_nav && op.asset_code) {
                navMap[op.asset_code] = op.latest_nav
            }
        })
        setLatestNavMap(navMap)
        console.log('[日志] 优化后的navMap（来自后端）:', navMap)
    }

    // 获取可用持仓
    const fetchAvailablePositions = async () => {
        try {
            const res = await fundAPI.getAvailablePositions()
            if (res.success && res.data) {
                setAvailablePositions(res.data || [])
            }
        } catch (error) {
            console.error('获取可用持仓失败:', error)
        }
    }

    // 获取定投计划列表
    const fetchDcaPlans = async () => {
        try {
            const res = await fundAPI.getDCAPlans()
            if (res.success && res.data) {
                setDcaPlans(res.data || [])
            }
        } catch (error) {
            console.error('获取定投计划失败:', error)
        }
    }

    // 获取操作记录列表
    const fetchOperations = async (params: SearchParams = {}, page: number = 1, pageSize: number = 20) => {
        setLoading(true)
        try {
            const response = await fundAPI.getFundOperations({
                ...params,
                page,
                page_size: pageSize
            })
            console.log('[日志] fetchOperations response', response)
            if (response.success && response.data) {
                setOperations(response.data || [])
                console.log('[日志] setOperations', response.data)
                fetchLatestNavs(response.data || [])

                // 更新分页信息
                if (response.total !== undefined) {
                    setPagination({
                        current: page,
                        pageSize,
                        total: response.total
                    })
                }
            }
        } catch (error: any) {
            console.error('获取操作记录失败:', error)
            message.error('获取操作记录失败')
        } finally {
            setLoading(false)
        }
    }

    // 处理搜索筛选
    const handleSearch = async (values: any) => {
        const params: SearchParams = {}

        if (values.asset_code) params.asset_code = values.asset_code
        if (values.operation_type) params.operation_type = values.operation_type
        if (values.dca_plan_id) params.dca_plan_id = values.dca_plan_id
        if (values.status) params.status = values.status

        if (values.date_range && values.date_range.length === 2) {
            params.start_date = dayjs(values.date_range[0]).format('YYYY-MM-DD')
            params.end_date = dayjs(values.date_range[1]).format('YYYY-MM-DD')
        }

        setSearchParams(params)
        await fetchOperations(params, 1, pagination.pageSize)
    }

    // 重置搜索
    const handleReset = async () => {
        searchForm.resetFields()
        setSearchParams({})
        await fetchOperations({}, 1, pagination.pageSize)
    }

    // 处理分红
    const handleProcessDividend = async () => {
        if (!processingDividend) return

        setSubmitting(true)
        try {
            const response = await fundAPI.processDividend(processingDividend.id, dividendProcessType)
            if (response.success) {
                message.success('分红处理成功')
                setDividendModalVisible(false)
                setProcessingDividend(null)
                fetchOperations(searchParams, pagination.current, pagination.pageSize) // 刷新列表
            } else {
                message.error('分红处理失败')
            }
        } catch (error: any) {
            console.error('处理分红失败:', error)
            message.error('处理分红失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    useEffect(() => {
        fetchOperations({}, 1, 20)
        fetchAvailablePositions()
        fetchDcaPlans()
    }, [])

    // 提交操作记录
    const handleSubmit = async (values: FundOperationForm) => {
        setSubmitting(true)
        console.log('[日志] handleSubmit 提交前', values)
        try {
            const operationData = {
                ...values,
                operation_date: dayjs(values.operation_date).format('YYYY-MM-DDTHH:mm:ss')
            }

            // 移除前端特有的字段
            delete operationData.sell_mode
            delete operationData.position_select

            // 修复：无论 quantity 是否填写，都要传递，清空时传 null
            if (operationData.quantity == null) {
                operationData.quantity = null as any
            }
            // 如果净值为空则不传，但手续费即使是0也要传递（用于触发份额重新计算）
            if (!operationData.nav) delete operationData.nav
            // 手续费字段保留，即使是0也要传递，用于触发份额重新计算
            if (operationData.fee === undefined || operationData.fee === null) {
                operationData.fee = 0
            }

            let response
            if (editingOperation) {
                // 编辑模式
                response = await fundAPI.updateFundOperation(editingOperation.id, operationData)
            } else {
                // 新增模式
                response = await fundAPI.createFundOperation(operationData)
            }
            console.log('[日志] handleSubmit 接口返回', response)
            if (response.success) {
                message.success(editingOperation ? '操作记录修改成功' : '操作记录创建成功')
                form.resetFields()
                setModalVisible(false)
                setEditingOperation(null)
                setQuantityManuallySet(false)
                setSellMode('quantity')
                setCurrentOperationType('buy')
                fetchOperations({}, pagination.current, pagination.pageSize) // 刷新列表
                fetchAvailablePositions() // 刷新可用持仓
                console.log('[日志] handleSubmit 调用fetchOperations')
            } else {
                message.error(editingOperation ? '修改失败' : '创建失败')
            }
        } catch (error: any) {
            console.error(editingOperation ? '修改操作记录失败:' : '创建操作记录失败:', error)
            message.error(editingOperation ? '修改失败，请稍后重试' : '创建失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 删除操作记录
    const handleDelete = async (record: FundOperation) => {
        console.log('[日志] 点击删除', record)
        if (!record.id) return
        setSubmitting(true)
        try {
            const response = await fundAPI.deleteFundOperation(record.id)
            if (response.success) {
                message.success('删除成功')
                fetchOperations({}, pagination.current, pagination.pageSize)
                fetchAvailablePositions() // 刷新可用持仓
            } else {
                message.error('删除失败')
            }
        } catch (error: any) {
            console.error('删除操作记录失败:', error)
            message.error('删除失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 基金代码自动带出名称
    const handleFundCodeBlur = async () => {
        const code = form.getFieldValue('asset_code')
        if (code && code.length === 6) {
            try {
                const res = await fundAPI.getFundInfo(code)
                if (res.success && res.data && res.data.fund_info) {
                    form.setFieldsValue({ asset_name: res.data.fund_info.fund_name })
                } else {
                    message.info('未查到该基金信息，请先录入基金基本信息')
                }
            } catch (e) {
                message.error('查询基金信息失败')
            }
        }
    }

    // 表格列定义
    const columns = [
        {
            title: '操作日期',
            dataIndex: 'operation_date',
            key: 'operation_date',
            render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm')
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
            title: '金额',
            dataIndex: 'amount',
            key: 'amount',
            render: (amount: any) => `¥${Number(amount).toFixed(2)}`
        },
        {
            title: '手续费',
            dataIndex: 'fee',
            key: 'fee',
            render: (fee: any) => fee ? `¥${Number(fee).toFixed(4)}` : '-'
        },
        {
            title: '操作净值',
            dataIndex: 'nav',
            key: 'nav',
            render: (nav: any) => nav ? `¥${Number(nav).toFixed(4)}` : '-'
        },
        {
            title: '最新净值',
            dataIndex: 'latest_nav',
            key: 'latest_nav',
            render: (value: any) => value ? `¥${Number(value).toFixed(4)}` : '-'
        },
        {
            title: '份额',
            dataIndex: 'quantity',
            key: 'quantity',
            render: (quantity: any) => quantity ? Number(quantity).toFixed(4) : '-'
        },
        {
            title: '当前市值',
            key: 'current_value',
            render: (_: any, record: FundOperation) => {
                const value = record.latest_nav && record.quantity ? record.latest_nav * record.quantity : null
                return value ? `¥${value.toFixed(2)}` : '-'
            }
        },
        {
            title: '定投计划',
            dataIndex: 'dca_plan_id',
            key: 'dca_plan_id',
            render: (dca_plan_id: number | null) => {
                if (!dca_plan_id) return '-'
                const plan = dcaPlans.find(p => p.id === dca_plan_id)
                return plan ? (
                    <Tooltip title={`计划: ${plan.plan_name}`}>
                        <Tag color="blue">定投</Tag>
                    </Tooltip>
                ) : (
                    <Tag color="blue">定投</Tag>
                )
            }
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                const statusMap = {
                    pending: { text: '待确认', color: 'orange' },
                    confirmed: { text: '已确认', color: 'green' },
                    cancelled: { text: '已取消', color: 'red' },
                    processed: { text: '已处理', color: 'blue' }
                }
                const config = statusMap[status as keyof typeof statusMap] || { text: status, color: 'default' }
                return <Tag color={config.color}>{config.text}</Tag>
            }
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: FundOperation) => (
                <Space size={4}>
                    <Tooltip title="查看">
                        <Button
                            type="link"
                            size="small"
                            icon={<EyeOutlined />}
                            style={{ padding: 0 }}
                            onClick={() => {
                                setEditingOperation(record)
                                setModalVisible(true)
                                setModalMode('view')
                                setQuantityManuallySet(true)
                                setCurrentOperationType(record.operation_type)
                                form.setFieldsValue({ ...record, operation_date: dayjs(record.operation_date) })
                            }}
                        />
                    </Tooltip>
                    <Tooltip title="编辑">
                        <Button
                            type="link"
                            size="small"
                            icon={<EditOutlined />}
                            style={{ padding: 0 }}
                            onClick={() => {
                                setEditingOperation(record)
                                setModalVisible(true)
                                setModalMode('edit')
                                setQuantityManuallySet(true)
                                setCurrentOperationType(record.operation_type)
                                form.setFieldsValue({ ...record, operation_date: dayjs(record.operation_date) })
                            }}
                        />
                    </Tooltip>
                    {record.operation_type === 'dividend' && record.status !== 'processed' && (
                        <Tooltip title="处理分红">
                            <Button
                                type="link"
                                size="small"
                                style={{ padding: 0, color: '#1890ff' }}
                                onClick={() => {
                                    setProcessingDividend(record)
                                    setDividendModalVisible(true)
                                    setDividendProcessType('reinvest')
                                }}
                            >
                                处理分红
                            </Button>
                        </Tooltip>
                    )}
                    <Popconfirm
                        title="确定要删除这条记录吗？"
                        onConfirm={() => handleDelete(record)}
                    >
                        <Tooltip title="删除">
                            <Button
                                type="link"
                                size="small"
                                danger
                                icon={<DeleteOutlined />}
                                style={{ padding: 0 }}
                            />
                        </Tooltip>
                    </Popconfirm>
                </Space>
            )
        }
    ]

    return (
        <div className="space-y-6">
            {/* 操作按钮 */}
            <Card>
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-lg font-medium">基金操作记录</h3>
                        <p className="text-sm text-gray-500 mt-1">
                            记录基金买入、卖出等操作，系统自动计算份额和收益
                        </p>
                    </div>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => {
                            setEditingOperation(null)
                            setModalVisible(true)
                            setCurrentOperationType('buy')
                            setSellMode('quantity')
                            setQuantityManuallySet(false)
                            form.resetFields()
                            form.setFieldsValue({
                                operation_type: 'buy',
                                sell_mode: 'quantity',
                                emotion_score: 5
                            })
                        }}
                    >
                        新增操作
                    </Button>
                </div>
            </Card>

            {/* 搜索筛选栏 */}
            <Card>
                <Form
                    form={searchForm}
                    layout="inline"
                    onFinish={handleSearch}
                    style={{ marginBottom: 0 }}
                >
                    <Row gutter={[16, 16]} style={{ width: '100%' }}>
                        <Col xs={24} sm={12} md={6}>
                            <Form.Item name="operation_type" label="操作类型">
                                <Select placeholder="全部" allowClear style={{ width: '100%' }}>
                                    <Option value="buy">买入</Option>
                                    <Option value="sell">卖出</Option>
                                    <Option value="dividend">分红</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={6}>
                            <Form.Item name="asset_code" label="基金代码">
                                <Input placeholder="请输入基金代码" />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={6}>
                            <Form.Item name="date_range" label="日期范围">
                                <RangePicker style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={6}>
                            <Form.Item name="dca_plan_id" label="定投计划">
                                <Select placeholder="全部" allowClear style={{ width: '100%' }}>
                                    {dcaPlans.map(plan => (
                                        <Option key={plan.id} value={plan.id}>
                                            {plan.plan_name}
                                        </Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={6}>
                            <Form.Item name="status" label="状态">
                                <Select placeholder="全部" allowClear style={{ width: '100%' }}>
                                    <Option value="pending">待确认</Option>
                                    <Option value="confirmed">已确认</Option>
                                    <Option value="cancelled">已取消</Option>
                                    <Option value="processed">已处理</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col xs={24} sm={12} md={6}>
                            <Form.Item>
                                <Space>
                                    <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                                        搜索
                                    </Button>
                                    <Button onClick={handleReset} icon={<ReloadOutlined />}>
                                        重置
                                    </Button>
                                </Space>
                            </Form.Item>
                        </Col>
                    </Row>
                </Form>
            </Card>

            {/* 操作记录表格 */}
            <Card>
                <Table
                    columns={columns}
                    dataSource={operations}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        current: pagination.current,
                        pageSize: pagination.pageSize,
                        total: pagination.total,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                        onChange: (page, pageSize) => {
                            fetchOperations(searchParams, page, pageSize)
                        },
                        onShowSizeChange: (_current, size) => {
                            fetchOperations(searchParams, 1, size)
                        }
                    }}
                />
            </Card>

            {/* 操作记录表单弹窗 */}
            <Modal
                title={modalMode === 'view' ? '查看操作记录' : editingOperation ? '编辑操作记录' : '新增操作记录'}
                open={modalVisible}
                onCancel={() => {
                    setModalVisible(false)
                    setEditingOperation(null)
                    setModalMode('create')
                    setCurrentOperationType('buy')
                    setSellMode('quantity')
                    setQuantityManuallySet(false)
                    form.resetFields()
                }}
                footer={modalMode === 'view' ? [
                    <Button key="close" onClick={() => {
                        setModalVisible(false);
                        setEditingOperation(null);
                        setModalMode('create');
                        setCurrentOperationType('buy');
                        setSellMode('quantity');
                        setQuantityManuallySet(false);
                    }}>关闭</Button>
                ] : editingOperation ? [
                    <Button key="cancel" onClick={() => {
                        setModalVisible(false);
                        setEditingOperation(null);
                        setModalMode('create');
                        setCurrentOperationType('buy');
                        setSellMode('quantity');
                        setQuantityManuallySet(false);
                    }}>取消</Button>,
                    <Button key="submit" type="primary" loading={submitting} onClick={() => form.submit()}>保存</Button>
                ] : [
                    <Button key="cancel" onClick={() => {
                        setModalVisible(false);
                        setCurrentOperationType('buy');
                        setSellMode('quantity');
                        setQuantityManuallySet(false);
                    }}>取消</Button>,
                    <Button key="submit" type="primary" loading={submitting} onClick={() => form.submit()}>提交</Button>
                ]}
                width={600}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                    onValuesChange={(changed, all) => {
                        // 用户主动清空份额，允许自动计算
                        if ('quantity' in changed && (changed.quantity === undefined || changed.quantity === null || changed.quantity === '')) {
                            setQuantityManuallySet(false)
                        }
                        // 用户手动输入份额，禁止自动计算
                        if ('quantity' in changed && changed.quantity) {
                            setQuantityManuallySet(true)
                        }

                        // 买入操作的自动计算逻辑
                        if (currentOperationType === 'buy' && !quantityManuallySet && (changed.amount !== undefined || changed.nav !== undefined || changed.fee !== undefined) && (all.quantity === undefined || all.quantity === null)) {
                            const amount = all.amount || 0
                            const fee = all.fee || 0
                            const nav = all.nav || 0
                            if (amount > 0 && nav > 0) {
                                const shares = (amount - fee) / nav
                                form.setFieldsValue({ quantity: Number.isFinite(shares) ? Number(shares.toFixed(4)) : undefined })
                                console.log('[日志] 买入操作自动设置 quantity', shares)
                            }
                        }

                        // 卖出操作的自动计算逻辑
                        if (currentOperationType === 'sell') {
                            const nav = all.nav || 0
                            const fee = all.fee || 0

                            // 按金额卖出：输入金额，自动算份额
                            if (sellMode === 'amount' && changed.amount !== undefined && nav > 0) {
                                const amount = all.amount || 0
                                if (amount > 0) {
                                    const shares = (amount - fee) / nav
                                    form.setFieldsValue({ quantity: Number.isFinite(shares) ? Number(shares.toFixed(4)) : undefined })
                                    console.log('[日志] 卖出操作按金额计算份额', shares)
                                }
                            }

                            // 按份额卖出：输入份额，自动算金额
                            if (sellMode === 'quantity' && changed.quantity !== undefined && nav > 0) {
                                const quantity = all.quantity || 0
                                if (quantity > 0) {
                                    // 修正公式：金额 = 份额 × 净值 - 手续费
                                    const amount = quantity * nav - fee
                                    form.setFieldsValue({ amount: Number.isFinite(amount) ? Number(amount.toFixed(2)) : undefined })
                                    console.log('[日志] 卖出操作按份额计算金额', amount)
                                }
                            }
                        }
                    }}
                    initialValues={{
                        operation_type: 'buy',
                        emotion_score: 5,
                        sell_mode: 'quantity'
                    }}
                    disabled={modalMode === 'view'}
                >
                    <Form.Item
                        label="操作日期"
                        name="operation_date"
                        rules={[{ required: true, message: '请选择操作日期' }]}
                    >
                        <DatePicker
                            showTime
                            format="YYYY-MM-DD HH:mm:ss"
                            placeholder="选择操作日期和时间"
                            style={{ width: '100%' }}
                        />
                    </Form.Item>

                    <Form.Item
                        label="操作类型"
                        name="operation_type"
                        rules={[{ required: true, message: '请选择操作类型' }]}
                    >
                        <Select
                            placeholder="选择操作类型"
                            onChange={(value) => {
                                setCurrentOperationType(value)
                                if (value === 'sell') {
                                    fetchAvailablePositions()
                                    form.setFieldsValue({
                                        sell_mode: 'quantity',
                                        amount: undefined,
                                        quantity: undefined,
                                        nav: undefined,
                                        asset_code: undefined,
                                        asset_name: undefined
                                    })
                                    setSellMode('quantity')
                                }
                            }}
                        >
                            <Option value="buy">买入</Option>
                            <Option value="sell">卖出</Option>
                            <Option value="dividend">分红</Option>
                        </Select>
                    </Form.Item>

                    {/* 卖出操作的特殊字段 */}
                    {currentOperationType === 'sell' && (
                        <>
                            <Form.Item
                                label="卖出方式"
                                name="sell_mode"
                                initialValue="quantity"
                            >
                                <Radio.Group onChange={e => {
                                    setSellMode(e.target.value)
                                    // 切换卖出方式时清空相关字段，避免脏数据
                                    form.setFieldsValue({ amount: undefined, quantity: undefined })
                                }}>
                                    <Radio value="amount">按金额卖出</Radio>
                                    <Radio value="quantity">按份额卖出</Radio>
                                </Radio.Group>
                            </Form.Item>

                            <Form.Item
                                label="选择持仓"
                                name="position_select"
                            >
                                <Select
                                    placeholder="选择要卖出的基金持仓"
                                    onChange={(value) => {
                                        const position = availablePositions.find(p => p.asset_code === value)
                                        if (position) {
                                            const latestNav = latestNavMap[position.asset_code]
                                            form.setFieldsValue({
                                                asset_code: position.asset_code,
                                                asset_name: position.asset_name,
                                                nav: latestNav !== undefined ? latestNav : position.current_nav
                                            })
                                        }
                                    }}
                                >
                                    {availablePositions.map(pos => (
                                        <Option key={pos.asset_code} value={pos.asset_code}>
                                            {pos.asset_name} ({pos.asset_code}) - 持仓: {Number(pos.total_shares).toFixed(4)}份
                                        </Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </>
                    )}

                    <Form.Item
                        label="基金代码"
                        name="asset_code"
                        rules={[{ required: true, message: '请输入基金代码' }]}
                    >
                        <Input
                            placeholder={currentOperationType === 'sell' ? "选择持仓后自动填充" : "请输入6位基金代码，如：000001"}
                            onBlur={handleFundCodeBlur}
                            disabled={currentOperationType === 'sell'}
                        />
                    </Form.Item>

                    <Form.Item
                        label="基金名称"
                        name="asset_name"
                        rules={[{ required: true, message: '请输入基金名称' }]}
                    >
                        <Input
                            placeholder="请输入基金名称"
                            disabled={currentOperationType === 'sell'}
                        />
                    </Form.Item>

                    <Form.Item
                        label={currentOperationType === 'sell' && sellMode === 'quantity' ? "卖出金额" : "操作金额"}
                        name="amount"
                        rules={[{ required: true, message: '请输入操作金额' }]}
                    >
                        <InputNumber
                            placeholder={currentOperationType === 'sell' && sellMode === 'quantity' ? "按份额计算后自动填充" : "请输入操作金额"}
                            min={0}
                            precision={2}
                            style={{ width: '100%' }}
                            addonAfter="元"
                            disabled={currentOperationType === 'sell' && sellMode === 'quantity'}
                        />
                    </Form.Item>

                    <Form.Item
                        label="净值"
                        name="nav"
                    >
                        <InputNumber
                            placeholder="请输入操作当日净值"
                            min={0}
                            precision={4}
                            style={{ width: '100%' }}
                        />
                    </Form.Item>

                    <Form.Item
                        label="手续费"
                        name="fee"
                    >
                        <InputNumber
                            placeholder="请输入手续费"
                            min={0}
                            precision={4}
                            style={{ width: '100%' }}
                            addonAfter="元"
                        />
                    </Form.Item>

                    <Form.Item
                        label={currentOperationType === 'sell' && sellMode === 'quantity' ? "卖出份额" : "份额"}
                        name="quantity"
                    >
                        <InputNumber
                            placeholder={currentOperationType === 'sell' && sellMode === 'quantity' ? "按份额计算后自动填充" : "如有特殊份额可手动填写，否则自动计算"}
                            min={0}
                            precision={4}
                            style={{ width: '100%' }}
                            disabled={currentOperationType === 'sell' && sellMode === 'amount'}
                            onChange={() => setQuantityManuallySet(true)}
                        />
                    </Form.Item>

                    <Form.Item
                        label="投资策略"
                        name="strategy"
                    >
                        <TextArea
                            placeholder="记录本次操作的投资策略和逻辑"
                            rows={3}
                        />
                    </Form.Item>

                    <Form.Item
                        label="情绪评分"
                        name="emotion_score"
                        rules={[{ required: true, message: '请选择情绪评分' }]}
                    >
                        <Select placeholder="选择情绪评分（1-10分）">
                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(score => (
                                <Option key={score} value={score}>
                                    {score}分 - {score <= 3 ? '恐慌' : score <= 5 ? '谨慎' : score <= 7 ? '理性' : '贪婪'}
                                </Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        label="备注"
                        name="notes"
                    >
                        <TextArea
                            placeholder="其他备注信息"
                            rows={2}
                        />
                    </Form.Item>

                    {/* 状态管理 */}
                    {editingOperation && (
                        <Form.Item
                            label="状态"
                            name="status"
                        >
                            <Select placeholder="选择状态">
                                <Option value="pending">待确认</Option>
                                <Option value="confirmed">已确认</Option>
                                <Option value="cancelled">已取消</Option>
                            </Select>
                        </Form.Item>
                    )}
                </Form>
            </Modal>

            {/* 分红处理弹窗 */}
            <Modal
                title="处理分红"
                open={dividendModalVisible}
                onCancel={() => {
                    setDividendModalVisible(false)
                    setProcessingDividend(null)
                }}
                onOk={handleProcessDividend}
                confirmLoading={submitting}
                okText="确认处理"
                cancelText="取消"
            >
                {processingDividend && (
                    <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <h4 className="font-medium mb-2">分红信息</h4>
                            <div className="space-y-2 text-sm">
                                <div><span className="text-gray-600">基金：</span>{processingDividend.asset_name} ({processingDividend.asset_code})</div>
                                <div><span className="text-gray-600">分红日期：</span>{dayjs(processingDividend.operation_date).format('YYYY-MM-DD')}</div>
                                <div><span className="text-gray-600">分红金额：</span>¥{Number(processingDividend.amount).toFixed(2)}</div>
                            </div>
                        </div>

                        <div>
                            <h4 className="font-medium mb-3">选择处理方式</h4>
                            <Radio.Group
                                value={dividendProcessType}
                                onChange={e => setDividendProcessType(e.target.value)}
                            >
                                <Space direction="vertical">
                                    <Radio value="reinvest">
                                        <div>
                                            <div className="font-medium">转投入</div>
                                            <div className="text-sm text-gray-600">将分红金额自动买入该基金</div>
                                        </div>
                                    </Radio>
                                    <Radio value="withdraw">
                                        <div>
                                            <div className="font-medium">提现</div>
                                            <div className="text-sm text-gray-600">将分红金额提取为现金</div>
                                        </div>
                                    </Radio>
                                    <Radio value="skip">
                                        <div>
                                            <div className="font-medium">暂不处理</div>
                                            <div className="text-sm text-gray-600">仅标记为已处理，不创建新操作</div>
                                        </div>
                                    </Radio>
                                </Space>
                            </Radio.Group>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    )
}

export default FundOperations 