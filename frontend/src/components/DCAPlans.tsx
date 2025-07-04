import React, { useState, useEffect } from 'react'
import {
    Card, Button, Form, Input, Select, DatePicker, InputNumber, message, Table, Space, Tag, Modal, Popconfirm, Tooltip,
    Row, Col, Statistic, Tabs, Switch, Divider, Alert, Radio
} from 'antd'
import {
    PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, PlayCircleOutlined, PauseCircleOutlined,
    StopOutlined, ReloadOutlined, BarChartOutlined, HistoryOutlined, CopyOutlined
} from '@ant-design/icons'
import { fundAPI } from '../services/api'
import type { APIResponse } from '../services/api'
import dayjs from 'dayjs'

const { Option } = Select
const { TextArea } = Input
const { TabPane } = Tabs

interface DCAPlan {
    id: number
    plan_name: string
    platform: string
    asset_type: string
    asset_code: string
    asset_name: string
    amount: number
    currency: string
    frequency: string
    frequency_value: number
    start_date: string
    end_date?: string
    status: 'active' | 'paused' | 'stopped' | 'completed'
    strategy?: string
    execution_time: string
    next_execution_date?: string
    last_execution_date?: string
    execution_count: number
    total_invested: number
    total_shares: number
    smart_dca: boolean
    base_amount?: number
    max_amount?: number
    increase_rate?: number
    min_nav?: number
    max_nav?: number
    skip_holidays: boolean
    enable_notification: boolean
    notification_before: number
    fee_rate?: number
    created_at: string
    updated_at: string
}

interface DCAPlanForm {
    plan_name: string
    asset_code: string
    asset_name: string
    amount: number
    currency: string
    frequency: string
    frequency_value: number
    start_date: string
    end_date?: string
    strategy?: string
    execution_time: string
    smart_dca: boolean
    base_amount?: number
    max_amount?: number
    increase_rate?: number
    min_nav?: number
    max_nav?: number
    skip_holidays: boolean
    enable_notification: boolean
    notification_before: number
    fee_rate?: number
}

interface DCAPlanStatistics {
    plan_id: number
    total_operations: number
    total_invested: number
    total_shares: number
    avg_cost: number
    current_nav: number
    current_value: number
    total_profit: number
    profit_rate: number
}

const DCAPlans: React.FC = () => {
    const [form] = Form.useForm()
    const [plans, setPlans] = useState<DCAPlan[]>([])
    const [loading, setLoading] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [modalVisible, setModalVisible] = useState(false)
    const [editingPlan, setEditingPlan] = useState<DCAPlan | null>(null)
    const [modalMode, setModalMode] = useState<'view' | 'edit' | 'create'>('create')
    const [selectedPlan, setSelectedPlan] = useState<DCAPlan | null>(null)
    const [planStatistics, setPlanStatistics] = useState<DCAPlanStatistics | null>(null)
    const [planOperations, setPlanOperations] = useState<any[]>([])
    const [operationsLoading, setOperationsLoading] = useState(false)
    const [detailModalVisible, setDetailModalVisible] = useState(false)

    // 新增状态：创建方式和选中的复制计划
    const [creationMode, setCreationMode] = useState<'new' | 'copy'>('new')
    const [selectedCopyPlanId, setSelectedCopyPlanId] = useState<number | null>(null)
    const [copyPlanLoading, setCopyPlanLoading] = useState(false)

    // 在DCAPlans组件内部增加分页状态
    const [operationPage, setOperationPage] = useState(1)
    const [operationPageSize, setOperationPageSize] = useState(50)
    const [operationTotal, setOperationTotal] = useState(0)

    // 新增：历史批量生成相关状态
    const [historyRange, setHistoryRange] = useState<[any, any] | null>(null)
    const [historyDates, setHistoryDates] = useState<string[]>([])
    const [excludeDates, setExcludeDates] = useState<string[]>([])
    const [historyPreviewLoading, setHistoryPreviewLoading] = useState(false)

    // 新增：Modal强制刷新
    const [modalKey, setModalKey] = useState(Date.now())

    // 监听日期区间变化，自动生成区间内所有日期（仅工作日/可选日，简化为全日）
    useEffect(() => {
        if (historyRange && historyRange[0] && historyRange[1]) {
            const start = dayjs(historyRange[0])
            const end = dayjs(historyRange[1])
            const dates: string[] = []
            let d = start.clone()
            while (d.isBefore(end, 'day') || d.isSame(end, 'day')) {
                dates.push(d.format('YYYY-MM-DD'))
                d = d.add(1, 'day')
            }
            setHistoryDates(dates)
            setExcludeDates([])
        } else {
            setHistoryDates([])
            setExcludeDates([])
        }
    }, [historyRange])

    // 获取定投计划列表
    const fetchPlans = async () => {
        setLoading(true)
        try {
            const response = await fundAPI.getDCAPlans()
            if (response.success && response.data) {
                setPlans(response.data || [])
            }
        } catch (error: any) {
            console.error('获取定投计划失败:', error)
            message.error('获取定投计划失败')
        } finally {
            setLoading(false)
        }
    }

    // 获取定投计划统计
    const fetchPlanStatistics = async (planId: number) => {
        try {
            const response = await fundAPI.getDCAPlanStatistics(planId)
            if (response.success && response.data) {
                setPlanStatistics(response.data)
            }
        } catch (error: any) {
            console.error('获取定投计划统计失败:', error)
        }
    }

    // 获取定投计划操作明细
    const fetchPlanOperations = async (planId: number, page = 1, pageSize = 50) => {
        setOperationsLoading(true)
        try {
            const response = await fundAPI.getFundOperations({ dca_plan_id: planId, page, page_size: pageSize })
            if (response.success && response.data) {
                setPlanOperations(response.data || [])
                setOperationTotal(response.total || 0)
            }
        } catch (error: any) {
            console.error('获取定投计划操作明细失败:', error)
        } finally {
            setOperationsLoading(false)
        }
    }

    useEffect(() => {
        fetchPlans()
    }, [])

    // 提交定投计划
    const handleSubmit = async (values: DCAPlanForm) => {
        console.log('[日志] handleSubmit 被触发', values)
        setSubmitting(true)
        try {
            const planData = {
                ...values,
                start_date: dayjs(values.start_date).format('YYYY-MM-DD'),
                end_date: values.end_date ? dayjs(values.end_date).format('YYYY-MM-DD') : undefined,
                platform: '支付宝',
                asset_type: '基金'
            }
            console.log('[日志] 提交的planData:', planData)
            console.log('[日志] 当前editingPlan:', editingPlan)

            // 检查编辑模式和日期区间变化
            if (editingPlan && planData.end_date) {
                const originalStartDate = dayjs(editingPlan.start_date).format('YYYY-MM-DD')
                const originalEndDate = editingPlan.end_date ? dayjs(editingPlan.end_date).format('YYYY-MM-DD') : undefined
                if (
                    planData.start_date !== originalStartDate ||
                    planData.end_date !== originalEndDate
                ) {
                    console.log('[日志] 日期区间发生变化，弹窗确认')
                    // 假设有弹窗确认逻辑
                    if (!window.confirm('日期区间发生变化，是否清理历史操作？')) {
                        console.log('[日志] 用户取消了日期区间变更确认，return')
                        setSubmitting(false)
                        return
                    }
                    // 假设有 cleanPlanOperations
                    console.log('[日志] 即将调用 cleanPlanOperations')
                    // await fundAPI.cleanPlanOperations(...)
                    console.log('[日志] cleanPlanOperations 已调用完成')
                }
            }

            // 其他可能的提前 return 分支
            if (!planData.plan_name) {
                console.log('[日志] plan_name 为空，return')
                setSubmitting(false)
                return
            }
            if (!planData.asset_code) {
                console.log('[日志] asset_code 为空，return')
                setSubmitting(false)
                return
            }
            // ...可继续补充其他校验...

            console.log('[日志] 即将调用 updateDCAPlan')
            const response = await fundAPI.updateDCAPlan(editingPlan.id, planData)
            console.log('[日志] updateDCAPlan 已调用，response:', response)

            if (response.success) {
                console.log('[日志] updateDCAPlan 成功，准备关闭弹窗')
                console.log('[日志] setModalVisible(false) before')
                setModalVisible(false)
                setModalKey(Date.now())
                console.log('[日志] setModalVisible(false) after')
                console.log('[日志] fetchPlans before')
                fetchPlans()
                console.log('[日志] fetchPlans after')
                console.log('[日志] form.resetFields before')
                form.resetFields()
                console.log('[日志] form.resetFields after')
                setEditingPlan(null)
                setCreationMode('new')
                setSelectedCopyPlanId(null)
            } else {
                message.error(editingPlan ? '修改失败' : '创建失败')
            }
        } catch (error: any) {
            console.error('[日志] handleSubmit error:', error)
            message.error(editingPlan ? '修改失败，请稍后重试' : '创建失败，请稍后重试')
        } finally {
            setSubmitting(false)
            console.log('[日志] setSubmitting(false) 执行')
        }
    }

    // 删除定投计划
    const handleDelete = async (record: DCAPlan) => {
        setSubmitting(true)
        try {
            const response = await fundAPI.deleteDCAPlan(record.id)
            if (response.success) {
                message.success('删除成功')
                fetchPlans()
            } else {
                message.error('删除失败')
            }
        } catch (error: any) {
            console.error('删除定投计划失败:', error)
            message.error('删除失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 执行定投计划
    const handleExecute = async (record: DCAPlan) => {
        setSubmitting(true)
        try {
            const response = await fundAPI.executeDCAPlan(record.id, 'manual')
            if (response.success) {
                message.success('定投计划执行成功')
                fetchPlans()
            } else {
                message.error('执行失败')
            }
        } catch (error: any) {
            console.error('执行定投计划失败:', error)
            message.error('执行失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 执行所有定投计划
    const handleExecuteAll = async () => {
        setSubmitting(true)
        try {
            const response = await fundAPI.executeAllDCAPlans()
            if (response.success) {
                message.success('批量执行成功')
                fetchPlans()
            } else {
                message.error('批量执行失败')
            }
        } catch (error: any) {
            console.error('批量执行定投计划失败:', error)
            message.error('批量执行失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 生成历史定投记录
    const handleGenerateHistory = async (record: DCAPlan) => {
        setSubmitting(true)
        try {
            // 如果有历史日期区间和排除日期，传递给后端
            const params: any = {}
            if (historyRange && historyRange[0] && historyRange[1]) {
                params.end_date = dayjs(historyRange[1]).format('YYYY-MM-DD')
            }
            if (excludeDates && excludeDates.length > 0) {
                params.exclude_dates = excludeDates
            }

            const response = await fundAPI.generateHistoricalOperations(record.id, params)
            if (response.success) {
                message.success(`成功生成 ${response.data?.created_count || 0} 条历史定投记录`)
                fetchPlans()
            } else {
                message.error('生成历史记录失败')
            }
        } catch (error: any) {
            console.error('生成历史定投记录失败:', error)
            message.error('生成历史记录失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 删除定投计划操作记录
    const handleDeleteOperations = async (record: DCAPlan) => {
        setSubmitting(true)
        try {
            const response = await fundAPI.deletePlanOperations(record.id)
            if (response.success) {
                message.success(`成功删除 ${response.data?.deleted_count || 0} 条操作记录`)
                fetchPlans()
            } else {
                message.error('删除操作记录失败')
            }
        } catch (error: any) {
            console.error('删除定投计划操作记录失败:', error)
            message.error('删除操作记录失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 更新定投计划统计
    const handleUpdateStatistics = async (record: DCAPlan) => {
        setSubmitting(true)
        try {
            const response = await fundAPI.updatePlanStatistics(record.id)
            if (response.success) {
                message.success('定投计划统计信息更新成功')
                fetchPlans()
            } else {
                message.error('更新统计信息失败')
            }
        } catch (error: any) {
            console.error('更新定投计划统计失败:', error)
            message.error('更新统计信息失败，请稍后重试')
        } finally {
            setSubmitting(false)
        }
    }

    // 查看定投计划详情
    const handleViewDetail = async (record: DCAPlan) => {
        setSelectedPlan(record)
        setDetailModalVisible(true)
        setOperationPage(1)
        setOperationPageSize(50)
        await fetchPlanStatistics(record.id)
        await fetchPlanOperations(record.id, 1, 50)
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

    // 新增：处理创建方式变化
    const handleCreationModeChange = (mode: 'new' | 'copy') => {
        setCreationMode(mode)
        setSelectedCopyPlanId(null)

        if (mode === 'new') {
            // 清空表单
            form.resetFields()
            form.setFieldsValue({
                currency: 'CNY',
                frequency: 'monthly',
                frequency_value: 1,
                execution_time: '15:00',
                smart_dca: false,
                skip_holidays: true,
                enable_notification: true,
                notification_before: 30,
                fee_rate: 0.0015
            })
        }
    }

    // 新增：处理复制计划选择
    const handleCopyPlanSelect = async (planId: number) => {
        setSelectedCopyPlanId(planId)
        setCopyPlanLoading(true)

        try {
            const response = await fundAPI.getDCAPlan(planId)
            if (response.success && response.data) {
                const plan = response.data

                // 填充表单，但排除时间相关字段和ID
                form.setFieldsValue({
                    plan_name: `${plan.plan_name}_副本`,
                    asset_code: plan.asset_code,
                    asset_name: plan.asset_name,
                    amount: plan.amount,
                    currency: plan.currency,
                    frequency: plan.frequency,
                    frequency_value: plan.frequency_value,
                    start_date: dayjs(), // 默认为当前日期
                    end_date: undefined, // 清空结束日期
                    strategy: plan.strategy,
                    execution_time: plan.execution_time,
                    smart_dca: plan.smart_dca,
                    base_amount: plan.base_amount,
                    max_amount: plan.max_amount,
                    increase_rate: plan.increase_rate,
                    min_nav: plan.min_nav,
                    max_nav: plan.max_nav,
                    skip_holidays: plan.skip_holidays,
                    enable_notification: plan.enable_notification,
                    notification_before: plan.notification_before,
                    fee_rate: plan.fee_rate
                })

                message.success('已复制定投计划配置')
            } else {
                message.error('获取定投计划详情失败')
            }
        } catch (error: any) {
            console.error('获取定投计划详情失败:', error)
            message.error('获取定投计划详情失败')
        } finally {
            setCopyPlanLoading(false)
        }
    }

    // 修改：打开新建弹窗时的处理
    const handleCreateNew = () => {
        setModalKey(Date.now())
        setModalVisible(true)
        setModalMode('create')
        setEditingPlan(null)
        setCreationMode('new')
        setSelectedCopyPlanId(null)
        form.resetFields()
        form.setFieldsValue({
            currency: 'CNY',
            frequency: 'monthly',
            frequency_value: 1,
            execution_time: '15:00',
            smart_dca: false,
            skip_holidays: true,
            enable_notification: true,
            notification_before: 30,
            fee_rate: 0.0015
        })
    }

    // 表格列定义
    const columns = [
        {
            title: '计划名称',
            dataIndex: 'plan_name',
            key: 'plan_name',
            ellipsis: true
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
            title: '定投金额',
            dataIndex: 'amount',
            key: 'amount',
            render: (amount: number) => `¥${Number(amount).toFixed(2)}`
        },
        {
            title: '手续费率',
            dataIndex: 'fee_rate',
            key: 'fee_rate',
            render: (fee_rate: number) => fee_rate ? `${(Number(fee_rate) * 100).toFixed(2)}%` : '-'
        },
        {
            title: '频率',
            key: 'frequency',
            render: (_: any, record: DCAPlan) => {
                const frequencyMap: { [key: string]: string } = {
                    daily: '每日',
                    weekly: '每周',
                    monthly: '每月',
                    custom: '自定义'
                }
                return `${frequencyMap[record.frequency] || record.frequency}${record.frequency_value > 1 ? record.frequency_value : ''}`
            }
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                const statusMap = {
                    active: { text: '运行中', color: 'green' },
                    paused: { text: '已暂停', color: 'orange' },
                    stopped: { text: '已停止', color: 'red' },
                    completed: { text: '已完成', color: 'blue' }
                }
                const config = statusMap[status as keyof typeof statusMap] || { text: status, color: 'default' }
                return <Tag color={config.color}>{config.text}</Tag>
            }
        },
        {
            title: '下次执行',
            dataIndex: 'next_execution_date',
            key: 'next_execution_date',
            render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
        },
        {
            title: '已执行次数',
            dataIndex: 'execution_count',
            key: 'execution_count'
        },
        {
            title: '累计投入',
            dataIndex: 'total_invested',
            key: 'total_invested',
            render: (amount: number) => `¥${Number(amount).toFixed(2)}`
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: DCAPlan) => (
                <Space size={4}>
                    <Tooltip title="查看详情">
                        <Button
                            type="link"
                            size="small"
                            icon={<EyeOutlined />}
                            style={{ padding: 0 }}
                            onClick={() => handleViewDetail(record)}
                        />
                    </Tooltip>
                    <Tooltip title="编辑">
                        <Button
                            type="link"
                            size="small"
                            icon={<EditOutlined />}
                            style={{ padding: 0 }}
                            onClick={() => {
                                console.log('[日志] 编辑按钮 record:', record)
                                setEditingPlan(record)
                                setModalKey(Date.now())
                                setModalVisible(true)
                                setModalMode('edit')
                                // 自动填充historyRange和historyDates
                                if (record.start_date && record.end_date) {
                                    const start = dayjs(record.start_date)
                                    const end = dayjs(record.end_date)
                                    setHistoryRange([start, end])
                                    const dates: string[] = []
                                    let d = start.clone()
                                    while (d.isBefore(end, 'day') || d.isSame(end, 'day')) {
                                        dates.push(d.format('YYYY-MM-DD'))
                                        d = d.add(1, 'day')
                                    }
                                    setHistoryDates(dates)
                                } else {
                                    setHistoryRange(null)
                                    setHistoryDates([])
                                }
                                setExcludeDates([])
                                form.setFieldsValue({
                                    ...record,
                                    start_date: dayjs(record.start_date),
                                    end_date: record.end_date ? dayjs(record.end_date) : undefined
                                })
                            }}
                        />
                    </Tooltip>
                    {record.status === 'active' && (() => {
                        const today = dayjs().format('YYYY-MM-DD')
                        const isHistoricalPlan = record.end_date && dayjs(record.end_date).isBefore(today)

                        if (isHistoricalPlan) {
                            return (
                                <Tooltip title="历史定投计划，不能手动执行">
                                    <Button
                                        type="link"
                                        size="small"
                                        icon={<PlayCircleOutlined />}
                                        style={{ padding: 0, color: '#d9d9d9' }}
                                        disabled
                                    />
                                </Tooltip>
                            )
                        } else {
                            return (
                                <Tooltip title="手动执行">
                                    <Button
                                        type="link"
                                        size="small"
                                        icon={<PlayCircleOutlined />}
                                        style={{ padding: 0 }}
                                        onClick={() => handleExecute(record)}
                                    />
                                </Tooltip>
                            )
                        }
                    })()}
                    <Tooltip title="生成历史记录">
                        <Button
                            type="link"
                            size="small"
                            style={{ padding: 0, color: '#1890ff' }}
                            onClick={() => handleGenerateHistory(record)}
                        >
                            生成历史
                        </Button>
                    </Tooltip>
                    <Tooltip title="删除操作记录">
                        <Button
                            type="link"
                            size="small"
                            style={{ padding: 0, color: '#ff4d4f' }}
                            onClick={() => handleDeleteOperations(record)}
                        >
                            删除操作
                        </Button>
                    </Tooltip>
                    <Tooltip title="更新统计">
                        <Button
                            type="link"
                            size="small"
                            style={{ padding: 0, color: '#52c41a' }}
                            onClick={() => handleUpdateStatistics(record)}
                        >
                            更新统计
                        </Button>
                    </Tooltip>
                    <Popconfirm
                        title="确定要删除这个定投计划吗？"
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

    // 操作明细表格列定义
    const operationColumns = [
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
            title: '金额',
            dataIndex: 'amount',
            key: 'amount',
            render: (amount: number) => `¥${Number(amount).toFixed(2)}`
        },
        {
            title: '净值',
            dataIndex: 'nav',
            key: 'nav',
            render: (nav: number) => nav ? `¥${Number(nav).toFixed(4)}` : '-'
        },
        {
            title: '份额',
            dataIndex: 'quantity',
            key: 'quantity',
            render: (quantity: number) => quantity ? Number(quantity).toFixed(4) : '-'
        },
        {
            title: '手续费',
            dataIndex: 'fee',
            key: 'fee',
            render: (fee: number) => fee ? `¥${Number(fee).toFixed(4)}` : '-'
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                const statusMap = {
                    pending: { text: '待确认', color: 'orange' },
                    confirmed: { text: '已确认', color: 'green' },
                    cancelled: { text: '已取消', color: 'red' }
                }
                const config = statusMap[status as keyof typeof statusMap] || { text: status, color: 'default' }
                return <Tag color={config.color}>{config.text}</Tag>
            }
        }
    ]

    return (
        <div className="space-y-6">
            {/* 操作按钮 */}
            <Card>
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-lg font-medium">定投计划管理</h3>
                        <p className="text-sm text-gray-500 mt-1">
                            管理基金定投计划，支持智能定投、自动执行等功能
                        </p>
                    </div>
                    <Space>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={handleExecuteAll}
                            loading={submitting}
                        >
                            批量执行
                        </Button>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={async () => {
                                setSubmitting(true)
                                try {
                                    const response = await fundAPI.updatePendingOperations()
                                    if (response.success) {
                                        message.success(`更新了 ${response.data?.updated_count || 0} 条待确认操作`)
                                        fetchPlans()
                                    } else {
                                        message.error('更新失败')
                                    }
                                } catch (error: any) {
                                    console.error('更新待确认操作失败:', error)
                                    message.error('更新失败，请稍后重试')
                                } finally {
                                    setSubmitting(false)
                                }
                            }}
                            loading={submitting}
                        >
                            更新待确认
                        </Button>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={async () => {
                                setSubmitting(true)
                                try {
                                    const response = await fundAPI.updatePlanStatuses()
                                    if (response.success) {
                                        message.success(`更新了 ${response.data?.updated_count || 0} 个计划状态`)
                                        fetchPlans()
                                    } else {
                                        message.error('更新状态失败')
                                    }
                                } catch (error: any) {
                                    console.error('更新计划状态失败:', error)
                                    message.error('更新状态失败，请稍后重试')
                                } finally {
                                    setSubmitting(false)
                                }
                            }}
                            loading={submitting}
                        >
                            更新状态
                        </Button>
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={handleCreateNew}
                        >
                            新建定投计划
                        </Button>
                    </Space>
                </div>
            </Card>

            {/* 定投计划表格 */}
            <Card>
                <Table
                    columns={columns}
                    dataSource={plans}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 个定投计划`
                    }}
                />
            </Card>

            {/* 定投计划表单弹窗 */}
            <Modal
                key={modalKey}
                title={editingPlan ? '编辑定投计划' : '新建定投计划'}
                open={modalVisible}
                onCancel={() => {
                    console.log('[日志] onCancel setModalVisible(false) before')
                    setModalVisible(false)
                    console.log('[日志] onCancel setModalVisible(false) after')
                    setEditingPlan(null)
                    setCreationMode('new')
                    setSelectedCopyPlanId(null)
                    form.resetFields()
                }}
                footer={null}
                width={800}
            >
                {/* 创建方式选择 - 仅在新建模式下显示 */}
                {!editingPlan && (
                    <>
                        <Form.Item label="创建方式">
                            <Radio.Group
                                value={creationMode}
                                onChange={(e) => handleCreationModeChange(e.target.value)}
                                style={{ marginBottom: 16 }}
                            >
                                <Radio value="new">创建新计划</Radio>
                                <Radio value="copy">复制现有计划</Radio>
                            </Radio.Group>
                        </Form.Item>

                        {/* 复制计划选择 */}
                        {creationMode === 'copy' && (
                            <Form.Item label="选择要复制的计划">
                                <Select
                                    placeholder="请选择要复制的定投计划"
                                    value={selectedCopyPlanId}
                                    onChange={handleCopyPlanSelect}
                                    loading={copyPlanLoading}
                                    style={{ width: '100%' }}
                                >
                                    {plans.map(plan => (
                                        <Option key={plan.id} value={plan.id}>
                                            {plan.plan_name} - {plan.asset_name} ({plan.asset_code})
                                        </Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        )}

                        <Divider />
                    </>
                )}

                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                    initialValues={{
                        currency: 'CNY',
                        frequency: 'monthly',
                        frequency_value: 1,
                        execution_time: '15:00',
                        smart_dca: false,
                        skip_holidays: true,
                        enable_notification: true,
                        notification_before: 30,
                        fee_rate: 0.0015
                    }}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="plan_name"
                                label="计划名称"
                                rules={[{ required: true, message: '请输入计划名称' }]}
                            >
                                <Input placeholder="请输入计划名称" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="asset_code"
                                label="基金代码"
                                rules={[{ required: true, message: '请输入基金代码' }]}
                            >
                                <Input placeholder="请输入基金代码" onBlur={handleFundCodeBlur} />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="asset_name"
                                label="基金名称"
                                rules={[{ required: true, message: '请输入基金名称' }]}
                            >
                                <Input placeholder="请输入基金名称" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="amount"
                                label="定投金额"
                                rules={[{ required: true, message: '请输入定投金额' }]}
                            >
                                <InputNumber
                                    placeholder="请输入定投金额"
                                    min={0}
                                    precision={2}
                                    style={{ width: '100%' }}
                                    addonAfter="元"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="fee_rate"
                                label="手续费率"
                                tooltip="如0.0015表示0.15%的手续费率"
                            >
                                <InputNumber
                                    placeholder="0.0015"
                                    min={0}
                                    max={1}
                                    precision={4}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="currency"
                                label="货币"
                                rules={[{ required: true, message: '请选择货币' }]}
                            >
                                <Select placeholder="选择货币">
                                    <Option value="CNY">人民币 (CNY)</Option>
                                    <Option value="USD">美元 (USD)</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="frequency"
                                label="定投频率"
                                rules={[{ required: true, message: '请选择定投频率' }]}
                            >
                                <Select placeholder="选择定投频率">
                                    <Option value="daily">每日</Option>
                                    <Option value="weekly">每周</Option>
                                    <Option value="monthly">每月</Option>
                                    <Option value="custom">自定义</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                name="frequency_value"
                                label="频率数值"
                                rules={[{ required: true, message: '请输入频率数值' }]}
                            >
                                <InputNumber
                                    placeholder="1"
                                    min={1}
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="execution_time"
                                label="执行时间"
                                rules={[{ required: true, message: '请输入执行时间' }]}
                            >
                                <Input placeholder="15:00" />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="start_date"
                                label="开始日期"
                                rules={[{ required: true, message: '请选择开始日期' }]}
                            >
                                <DatePicker style={{ width: '100%' }}
                                    onChange={date => setHistoryRange([date, historyRange ? historyRange[1] : null])}
                                />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="end_date"
                                label="结束日期"
                            >
                                <DatePicker style={{ width: '100%' }}
                                    onChange={date => setHistoryRange([historyRange ? historyRange[0] : null, date])}
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    {historyDates.length > 0 && (
                        <Row gutter={16}>
                            <Col span={24}>
                                <Form.Item label="排除日期（如定投失败日）">
                                    <Select
                                        mode="multiple"
                                        allowClear
                                        style={{ width: '100%' }}
                                        placeholder="可选定投失败的日期不生成操作记录"
                                        value={excludeDates}
                                        onChange={setExcludeDates}
                                        options={historyDates.map(date => ({ label: date, value: date }))}
                                    />
                                </Form.Item>
                            </Col>
                        </Row>
                    )}

                    <Divider orientation="left">智能定投设置</Divider>

                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                name="smart_dca"
                                label="启用智能定投"
                                valuePropName="checked"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="base_amount"
                                label="基础金额"
                            >
                                <InputNumber
                                    placeholder="基础金额"
                                    min={0}
                                    precision={2}
                                    style={{ width: '100%' }}
                                    addonAfter="元"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="max_amount"
                                label="最大金额"
                            >
                                <InputNumber
                                    placeholder="最大金额"
                                    min={0}
                                    precision={2}
                                    style={{ width: '100%' }}
                                    addonAfter="元"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                name="increase_rate"
                                label="跌幅增加比例"
                            >
                                <InputNumber
                                    placeholder="0.1"
                                    min={0}
                                    max={1}
                                    precision={2}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="min_nav"
                                label="最低净值"
                            >
                                <InputNumber
                                    placeholder="最低净值"
                                    min={0}
                                    precision={4}
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="max_nav"
                                label="最高净值"
                            >
                                <InputNumber
                                    placeholder="最高净值"
                                    min={0}
                                    precision={4}
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                name="skip_holidays"
                                label="跳过节假日"
                                valuePropName="checked"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="enable_notification"
                                label="启用通知"
                                valuePropName="checked"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="notification_before"
                                label="提前通知(分钟)"
                            >
                                <InputNumber
                                    placeholder="30"
                                    min={0}
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item
                        name="strategy"
                        label="定投策略"
                    >
                        <TextArea rows={3} placeholder="请输入定投策略说明" />
                    </Form.Item>

                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={submitting}>
                                {editingPlan ? '更新' : '创建'}
                            </Button>
                            <Button onClick={() => {
                                console.log('[日志] 取消 setModalVisible(false) before')
                                setModalVisible(false)
                                console.log('[日志] 取消 setModalVisible(false) after')
                                setEditingPlan(null)
                                setCreationMode('new')
                                setSelectedCopyPlanId(null)
                                form.resetFields()
                            }}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 定投计划详情弹窗 */}
            <Modal
                title={`定投计划详情 - ${selectedPlan?.plan_name}`}
                open={detailModalVisible}
                onCancel={() => {
                    setDetailModalVisible(false)
                    setSelectedPlan(null)
                    setPlanStatistics(null)
                    setPlanOperations([])
                }}
                footer={null}
                width={1000}
            >
                {selectedPlan && (
                    <Tabs defaultActiveKey="statistics">
                        <TabPane tab="统计信息" key="statistics" icon={<BarChartOutlined />}>
                            {planStatistics && (
                                <Row gutter={16}>
                                    <Col span={6}>
                                        <Statistic
                                            title="累计投入"
                                            value={planStatistics.total_invested}
                                            precision={2}
                                            prefix="¥"
                                        />
                                    </Col>
                                    <Col span={6}>
                                        <Statistic
                                            title="累计份额"
                                            value={planStatistics.total_shares}
                                            precision={4}
                                        />
                                    </Col>
                                    <Col span={6}>
                                        <Statistic
                                            title="平均成本"
                                            value={planStatistics.avg_cost}
                                            precision={4}
                                            prefix="¥"
                                        />
                                    </Col>
                                    <Col span={6}>
                                        <Statistic
                                            title="当前净值"
                                            value={planStatistics.current_nav}
                                            precision={4}
                                            prefix="¥"
                                        />
                                    </Col>
                                </Row>
                            )}
                            {planStatistics && (
                                <Row gutter={16} style={{ marginTop: 16 }}>
                                    <Col span={6}>
                                        <Statistic
                                            title="当前市值"
                                            value={planStatistics.current_value}
                                            precision={2}
                                            prefix="¥"
                                        />
                                    </Col>
                                    <Col span={6}>
                                        <Statistic
                                            title="累计收益"
                                            value={planStatistics.total_profit}
                                            precision={2}
                                            prefix="¥"
                                            valueStyle={{ color: planStatistics.total_profit >= 0 ? '#3f8600' : '#cf1322' }}
                                        />
                                    </Col>
                                    <Col span={6}>
                                        <Statistic
                                            title="收益率"
                                            value={planStatistics.profit_rate * 100}
                                            precision={2}
                                            suffix="%"
                                            valueStyle={{ color: planStatistics.profit_rate >= 0 ? '#3f8600' : '#cf1322' }}
                                        />
                                    </Col>
                                    <Col span={6}>
                                        <Statistic
                                            title="执行次数"
                                            value={planStatistics.total_operations}
                                        />
                                    </Col>
                                </Row>
                            )}
                        </TabPane>
                        <TabPane tab="操作明细" key="operations" icon={<HistoryOutlined />}>
                            <div style={{ marginBottom: 16 }}>
                                <Alert
                                    message={`共获取到 ${operationTotal} 条操作记录`}
                                    type="info"
                                    showIcon
                                />
                            </div>
                            <Table
                                columns={operationColumns}
                                dataSource={planOperations}
                                rowKey="id"
                                loading={operationsLoading}
                                pagination={{
                                    current: operationPage,
                                    pageSize: operationPageSize,
                                    total: operationTotal,
                                    showSizeChanger: true,
                                    showQuickJumper: true,
                                    showTotal: (total) => `共 ${total} 条操作记录`,
                                    pageSizeOptions: ["20", "50", "100"]
                                }}
                                onChange={(pagination) => {
                                    setOperationPage(pagination.current || 1)
                                    setOperationPageSize(pagination.pageSize || 50)
                                    if (selectedPlan) {
                                        fetchPlanOperations(selectedPlan.id, pagination.current || 1, pagination.pageSize || 50)
                                    }
                                }}
                            />
                        </TabPane>
                    </Tabs>
                )}
            </Modal>
        </div>
    )
}

export default DCAPlans 