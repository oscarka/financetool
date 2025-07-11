import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Table, Tag, Space, Button, message, Input, Divider, Statistic, Checkbox, TimePicker, Modal, Form } from 'antd'
import { SyncOutlined, SearchOutlined, DownloadOutlined, ClockCircleOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'
import dayjs from 'dayjs'

interface NavHistoryItem {
    id: number
    fund_code: string
    nav_date: string
    nav: number
    accumulated_nav?: number
    source: string
    dividend_amount?: number
    dividend_date?: string
    record_date?: string
}

const FundNavManagement: React.FC = () => {
    // 历史净值查询相关状态
    const [fundCode, setFundCode] = useState('')
    const [navHistory, setNavHistory] = useState<NavHistoryItem[]>([])
    const [navLoading, setNavLoading] = useState(false)
    const [dividendLoading, setDividendLoading] = useState(false)
    const [navPagination, setNavPagination] = useState({
        current: 1,
        pageSize: 20,
        total: 0,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total: number) => `共 ${total} 条记录`
    })
    const [showDividend, setShowDividend] = useState(false)
    const [onlyDividend, setOnlyDividend] = useState(false)

    // 定时任务相关状态
    const [schedulerJobs, setSchedulerJobs] = useState<any[]>([])
    const [schedulerLoading, setSchedulerLoading] = useState(false)
    const [updateTimeModalVisible, setUpdateTimeModalVisible] = useState(false)
    const [selectedJob, setSelectedJob] = useState<any>(null)
    const [updateTimeForm] = Form.useForm()

    // 查询历史净值
    const fetchNavHistory = async (forceUpdate = false) => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        // 防重复点击
        if (navLoading) {
            message.warning('正在查询净值中，请稍候...')
            return
        }

        setNavLoading(true)
        try {
            const response = await fundAPI.getFundNavHistoryByCode(fundCode.trim(), forceUpdate, false) // 不包含分红数据

            if (response.success && response.data) {
                let history = response.data.nav_history || []
                setNavHistory(history)
                setNavPagination(prev => ({
                    ...prev,
                    total: history.length,
                    current: 1 // 重置到第一页
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

    // 同步分红数据
    const syncDividendData = async () => {
        if (!fundCode.trim()) {
            message.warning('请先输入基金代码')
            return
        }

        // 防重复点击
        if (dividendLoading) {
            message.warning('正在同步分红数据中，请稍候...')
            return
        }

        setDividendLoading(true)
        try {
            console.log('开始同步分红数据...')
            const response = await fundAPI.syncFundDividends(fundCode.trim())
            console.log('分红数据同步完成:', response)

            if (response.success) {
                message.success(response.message || '分红数据同步成功')
                // 同步成功后，如果当前显示分红，则重新查询
                if (showDividend) {
                    await fetchNavHistoryWithDividend()
                }
            } else {
                message.error(response.message || '分红数据同步失败')
            }
        } catch (error: any) {
            console.error('同步分红数据失败:', error)
            if (error.code === 'ECONNABORTED') {
                message.error('同步分红数据超时，请稍后重试')
            } else {
                message.error('同步分红数据失败: ' + (error.message || '未知错误'))
            }
        } finally {
            setDividendLoading(false)
        }
    }

    // 查询包含分红的历史净值（只查询数据库中已有的分红数据）
    const fetchNavHistoryWithDividend = async () => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        // 防重复点击
        if (navLoading) {
            message.warning('正在查询中，请稍候...')
            return
        }

        setNavLoading(true)
        try {
            // 只查询数据库中已有的分红数据，不自动拉取
            const response = await fundAPI.getFundNavHistoryByCode(fundCode.trim(), false, true) // 包含分红数据

            if (response.success && response.data) {
                let history = response.data.nav_history || []

                // 如果选择只显示分红记录，则过滤数据
                if (onlyDividend && showDividend) {
                    history = history.filter((item: NavHistoryItem) => item.dividend_amount && item.dividend_amount > 0)
                }

                setNavHistory(history)
                setNavPagination(prev => ({
                    ...prev,
                    total: history.length,
                    current: 1 // 重置到第一页
                }))

                // 检查是否有分红数据
                const hasDividendData = history.some((item: NavHistoryItem) => item.dividend_amount && item.dividend_amount > 0)
                if (showDividend && !hasDividendData) {
                    message.info('当前基金暂无分红数据，请点击"同步分红数据"按钮获取最新分红信息')
                } else {
                    message.success(`成功获取 ${history.length} 条历史净值记录`)
                }
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

    // 导出历史净值数据
    const exportNavHistory = () => {
        if (navHistory.length === 0) {
            message.warning('没有数据可导出')
            return
        }

        const csvContent = [
            ['日期', '基金代码', '单位净值', '累计净值', '分红金额', '分红发放日', '数据来源'],
            ...navHistory.map(item => [
                item.nav_date,
                item.fund_code,
                item.nav?.toString() || '',
                item.accumulated_nav?.toString() || '',
                item.dividend_amount?.toString() || '',
                item.dividend_date || '',
                item.source
            ])
        ].map(row => row.join(',')).join('\n')

        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `${fundCode}_历史净值_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        message.success('历史净值数据导出成功')
    }

    // 获取定时任务列表
    const fetchSchedulerJobs = async () => {
        setSchedulerLoading(true)
        try {
            const response = await fundAPI.getSchedulerJobs()
            if (response.success && response.data) {
                setSchedulerJobs(response.data.jobs || [])
            } else {
                message.error(response.message || '获取定时任务失败')
            }
        } catch (error: any) {
            console.error('获取定时任务失败:', error)
            message.error('获取定时任务失败')
        } finally {
            setSchedulerLoading(false)
        }
    }

    // 启动定时任务调度器
    const startScheduler = async () => {
        try {
            const response = await fundAPI.startScheduler()
            if (response.success) {
                message.success(response.message || '定时任务调度器已启动')
                fetchSchedulerJobs()
            } else {
                message.error(response.message || '启动定时任务调度器失败')
            }
        } catch (error: any) {
            console.error('启动定时任务调度器失败:', error)
            message.error('启动定时任务调度器失败')
        }
    }

    // 停止定时任务调度器
    const stopScheduler = async () => {
        try {
            const response = await fundAPI.stopScheduler()
            if (response.success) {
                message.success(response.message || '定时任务调度器已停止')
                fetchSchedulerJobs()
            } else {
                message.error(response.message || '停止定时任务调度器失败')
            }
        } catch (error: any) {
            console.error('停止定时任务调度器失败:', error)
            message.error('停止定时任务调度器失败')
        }
    }

    // 重启定时任务调度器
    const restartScheduler = async () => {
        try {
            const response = await fundAPI.restartScheduler()
            if (response.success) {
                message.success(response.message || '定时任务调度器已重启')
                fetchSchedulerJobs()
            } else {
                message.error(response.message || '重启定时任务调度器失败')
            }
        } catch (error: any) {
            console.error('重启定时任务调度器失败:', error)
            message.error('重启定时任务调度器失败')
        }
    }

    // 手动执行净值更新
    const manualUpdateNavs = async () => {
        try {
            const response = await fundAPI.manualUpdateNavs()
            if (response.success) {
                message.success(response.message || '手动净值更新任务执行完成')
            } else {
                message.error(response.message || '手动净值更新任务执行失败')
            }
        } catch (error: any) {
            console.error('手动净值更新任务执行失败:', error)
            message.error('手动净值更新任务执行失败')
        }
    }

    // 更新任务执行时间
    const updateJobSchedule = async (values: any) => {
        if (!selectedJob) return

        try {
            const time = values.time
            const hour = time.hour()
            const minute = time.minute()

            const response = await fundAPI.updateJobSchedule(selectedJob.id, hour, minute)
            if (response.success) {
                message.success(response.message || '任务执行时间更新成功')
                setUpdateTimeModalVisible(false)
                fetchSchedulerJobs()
            } else {
                message.error(response.message || '更新任务执行时间失败')
            }
        } catch (error: any) {
            console.error('更新任务执行时间失败:', error)
            message.error('更新任务执行时间失败')
        }
    }

    // 打开更新时间模态框
    const openUpdateTimeModal = (job: any) => {
        setSelectedJob(job)
        // 从trigger字符串中解析时间
        const triggerStr = job.trigger
        const timeMatch = triggerStr.match(/cron\[h=(\d+),m=(\d+)/)
        if (timeMatch) {
            const hour = parseInt(timeMatch[1])
            const minute = parseInt(timeMatch[2])
            updateTimeForm.setFieldsValue({
                time: dayjs().hour(hour).minute(minute)
            })
        }
        setUpdateTimeModalVisible(true)
    }

    // 组件加载时获取定时任务列表
    useEffect(() => {
        fetchSchedulerJobs()
    }, [])

    // 历史净值表格列定义
    const navColumns = [
        {
            title: '日期',
            dataIndex: 'nav_date',
            key: 'nav_date',
            render: (date: string) => new Date(date).toLocaleDateString()
        },
        {
            title: '基金代码',
            dataIndex: 'fund_code',
            key: 'fund_code',
            width: 100
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
    ] as any[];
    if (showDividend) {
        navColumns.push({
            title: '分红金额',
            dataIndex: 'dividend_amount',
            key: 'dividend_amount',
            render: (dividend: number) => dividend ? dividend.toFixed(4) : '-',
        });
        navColumns.push({
            title: '分红发放日',
            dataIndex: 'dividend_date',
            key: 'dividend_date',
            render: (date: string) => date || '-',
        });
    }
    navColumns.push({
        title: '数据来源',
        dataIndex: 'source',
        key: 'source',
        render: (source: string) => <Tag color="blue">{source}</Tag>
    });

    return (
        <div className="space-y-6">
            {/* 净值管理概览 */}
            <Card>
                <Row gutter={16}>
                    <Col span={8}>
                        <Statistic
                            title="当前查询基金"
                            value={fundCode || '未选择'}
                            valueStyle={{ color: fundCode ? '#1890ff' : '#999' }}
                        />
                    </Col>
                    <Col span={8}>
                        <Statistic
                            title="历史记录数"
                            value={navHistory.length}
                            valueStyle={{ color: '#3f8600' }}
                        />
                    </Col>
                    <Col span={8}>
                        <Statistic
                            title="最新净值日期"
                            value={navHistory.length > 0 ? new Date(navHistory[0].nav_date).toLocaleDateString() : '无数据'}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Col>
                </Row>
            </Card>

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
                    <Col span={8}>
                        <Space>
                            <Checkbox
                                checked={showDividend}
                                onChange={async e => {
                                    setShowDividend(e.target.checked)
                                    if (!e.target.checked) {
                                        setOnlyDividend(false) // 取消显示分红时，也取消只显示分红记录
                                        // 重新查询不包含分红的数据
                                        if (fundCode.trim()) {
                                            await fetchNavHistory()
                                        }
                                    } else {
                                        // 勾选显示分红时，只查询数据库中的分红数据，不自动拉取
                                        if (fundCode.trim()) {
                                            await fetchNavHistoryWithDividend()
                                        }
                                    }
                                }}
                            >
                                显示分红
                            </Checkbox>
                            {showDividend && (
                                <Checkbox
                                    checked={onlyDividend}
                                    onChange={e => setOnlyDividend(e.target.checked)}
                                >
                                    只显示分红记录
                                </Checkbox>
                            )}
                        </Space>
                    </Col>
                    <Col span={8}>
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
                                强制更新净值
                            </Button>
                            <Button
                                icon={<SyncOutlined />}
                                loading={dividendLoading}
                                onClick={syncDividendData}
                            >
                                同步分红数据
                            </Button>
                            <Button
                                icon={<DownloadOutlined />}
                                disabled={navHistory.length === 0}
                                onClick={exportNavHistory}
                            >
                                导出数据
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
                            rowKey={record => record.id || record.nav_date}
                            loading={navLoading}
                            pagination={{
                                current: navPagination.current,
                                pageSize: navPagination.pageSize,
                                total: navPagination.total,
                                showSizeChanger: true,
                                showQuickJumper: true,
                                showTotal: navPagination.showTotal,
                                onChange: handleNavPaginationChange
                            }}
                            scroll={{ x: 900 }}
                        />
                    </>
                )}
            </Card>

            {/* 定时任务管理 */}
            <Card
                title={
                    <Space>
                        <ClockCircleOutlined />
                        定时任务管理
                    </Space>
                }
                extra={
                    <Space>
                        <Button
                            type="primary"
                            icon={<PlayCircleOutlined />}
                            onClick={startScheduler}
                        >
                            启动调度器
                        </Button>
                        <Button
                            danger
                            icon={<PauseCircleOutlined />}
                            onClick={stopScheduler}
                        >
                            停止调度器
                        </Button>
                        <Button
                            type="default"
                            icon={<SyncOutlined />}
                            onClick={restartScheduler}
                        >
                            重启调度器
                        </Button>
                        <Button
                            icon={<SyncOutlined />}
                            onClick={manualUpdateNavs}
                        >
                            手动更新净值
                        </Button>
                        <Button
                            icon={<SyncOutlined />}
                            onClick={fetchSchedulerJobs}
                            loading={schedulerLoading}
                        >
                            刷新
                        </Button>
                    </Space>
                }
            >
                <Table
                    columns={[
                        {
                            title: '任务名称',
                            dataIndex: 'name',
                            key: 'name',
                            render: (name: string) => <Tag color="blue">{name}</Tag>
                        },
                        {
                            title: '任务ID',
                            dataIndex: 'id',
                            key: 'id',
                            width: 150
                        },
                        {
                            title: '下次执行时间',
                            dataIndex: 'next_run_time',
                            key: 'next_run_time',
                            render: (time: string) => time ? new Date(time).toLocaleString() : '未设置'
                        },
                        {
                            title: '执行规则',
                            dataIndex: 'trigger',
                            key: 'trigger',
                            render: (trigger: string) => {
                                const match = trigger.match(/cron\[h=(\d+),m=(\d+)/)
                                if (match) {
                                    return `每天 ${match[1]}:${match[2].padStart(2, '0')}`
                                }
                                return trigger
                            }
                        },
                        {
                            title: '操作',
                            key: 'action',
                            width: 120,
                            render: (_, record: any) => (
                                <Button
                                    type="link"
                                    size="small"
                                    onClick={() => openUpdateTimeModal(record)}
                                >
                                    修改时间
                                </Button>
                            )
                        }
                    ]}
                    dataSource={schedulerJobs}
                    rowKey="id"
                    loading={schedulerLoading}
                    pagination={false}
                    size="small"
                />
            </Card>

            {/* 使用说明 */}
            <Card title="使用说明">
                <div className="space-y-2 text-sm text-gray-600">
                    <p>• <strong>查询历史净值</strong>：输入基金代码，点击查询按钮获取历史净值数据</p>
                    <p>• <strong>强制更新</strong>：从外部API重新获取最新净值数据，覆盖本地缓存</p>
                    <p>• <strong>定时任务</strong>：系统会自动在指定时间更新净值、执行定投计划等</p>
                    <p>• <strong>导出数据</strong>：将查询到的历史净值数据导出为CSV文件</p>
                    <p>• <strong>数据来源</strong>：历史净值数据来源于akshare开源数据接口</p>
                    <p>• <strong>分页显示</strong>：支持分页浏览大量历史数据，每页默认显示20条记录</p>
                </div>
            </Card>

            {/* 更新时间模态框 */}
            <Modal
                title="修改任务执行时间"
                open={updateTimeModalVisible}
                onCancel={() => setUpdateTimeModalVisible(false)}
                footer={null}
            >
                <Form
                    form={updateTimeForm}
                    onFinish={updateJobSchedule}
                    layout="vertical"
                >
                    <Form.Item
                        label="执行时间"
                        name="time"
                        rules={[{ required: true, message: '请选择执行时间' }]}
                    >
                        <TimePicker
                            format="HH:mm"
                            placeholder="选择执行时间"
                            style={{ width: '100%' }}
                        />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                确定
                            </Button>
                            <Button onClick={() => setUpdateTimeModalVisible(false)}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    )
}

export default FundNavManagement 