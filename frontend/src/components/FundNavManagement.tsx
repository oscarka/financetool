import React, { useState } from 'react'
import { Card, Row, Col, Table, Tag, Space, Button, message, Input, Divider, Statistic, Checkbox, Modal, Select, Alert } from 'antd'
import { SyncOutlined, SearchOutlined, DownloadOutlined, DeleteOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'

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

    // 估算数据相关状态
    const [estimateData, setEstimateData] = useState<any>(null)
    const [estimateLoading, setEstimateLoading] = useState(false)

    // 数据管理相关状态
    const [sourceFilter, setSourceFilter] = useState<string>('all')
    const [showDataManagement, setShowDataManagement] = useState(false)
    const [dataStats, setDataStats] = useState<any>(null)
    const [deleteModalVisible, setDeleteModalVisible] = useState(false)
    const [deleteLoading, setDeleteLoading] = useState(false)
    const [selectedSource, setSelectedSource] = useState<string>('')

    // 数据管理相关状态
    const [sourceFilter, setSourceFilter] = useState<string>('all')
    const [showDataManagement, setShowDataManagement] = useState(false)
    const [dataStats, setDataStats] = useState<any>(null)
    const [deleteModalVisible, setDeleteModalVisible] = useState(false)
    const [deleteLoading, setDeleteLoading] = useState(false)
    const [selectedSource, setSelectedSource] = useState<string>('')

    // 查询基金估算净值
    const fetchEstimate = async () => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        if (estimateLoading) {
            message.warning('正在查询估算数据中，请稍候...')
            return
        }

        setEstimateLoading(true)
        try {
            const response = await fundAPI.getFundEstimate(fundCode.trim())

            if (response.success && response.data) {
                setEstimateData(response.data)
                message.success('获取估算数据成功')
            } else {
                message.error(response.message || '获取估算数据失败')
                setEstimateData(null)
            }
        } catch (error: any) {
            console.error('获取估算数据失败:', error)
            message.error('获取估算数据失败')
            setEstimateData(null)
        } finally {
            setEstimateLoading(false)
        }
    }

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
                
                // 根据来源筛选
                if (sourceFilter !== 'all') {
                    history = history.filter((item: NavHistoryItem) => item.source === sourceFilter)
                }
                
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

    // 获取数据统计信息
    const fetchDataStats = async () => {
        try {
            const response = await fundAPI.getNavDataStats()
            if (response.success && response.data) {
                setDataStats(response.data)
            }
        } catch (error: any) {
            console.error('获取数据统计失败:', error)
        }
    }

    // 删除指定来源的数据
    const deleteSourceData = async () => {
        if (!selectedSource) {
            message.warning('请选择要删除的数据来源')
            return
        }

        setDeleteLoading(true)
        try {
            const response = await fundAPI.deleteNavBySource(selectedSource)
            if (response.success) {
                message.success(`成功删除 ${response.data?.deleted_count || 0} 条${selectedSource}来源的数据`)
                setDeleteModalVisible(false)
                setSelectedSource('')
                // 重新获取数据统计
                await fetchDataStats()
            } else {
                message.error(response.message || '删除失败')
            }
        } catch (error: any) {
            console.error('删除数据失败:', error)
            message.error('删除失败')
        } finally {
            setDeleteLoading(false)
        }
    }

    // 增量更新数据
    const incrementalUpdate = async () => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        try {
            const response = await fundAPI.incrementalUpdateNav(fundCode.trim())
            if (response.success) {
                message.success(`增量更新成功，新增 ${response.data?.new_count || 0} 条记录`)
                // 重新获取数据
                await fetchNavHistory()
            } else {
                message.error(response.message || '增量更新失败')
            }
        } catch (error: any) {
            console.error('增量更新失败:', error)
            message.error('增量更新失败')
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
            message.error('同步分红数据失败')
        } finally {
            setDividendLoading(false)
        }
    }

    // 查询包含分红的历史净值
    const fetchNavHistoryWithDividend = async () => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        setNavLoading(true)
        try {
            const response = await fundAPI.getFundNavHistoryByCode(fundCode.trim(), false, true) // 包含分红数据

            if (response.success && response.data) {
                let history = response.data.nav_history || []
                
                // 根据来源筛选
                if (sourceFilter !== 'all') {
                    history = history.filter((item: NavHistoryItem) => item.source === sourceFilter)
                }
                
                // 如果只显示分红记录
                if (onlyDividend) {
                    history = history.filter((item: NavHistoryItem) => item.dividend_amount && item.dividend_amount > 0)
                }
                
                setNavHistory(history)
                setNavPagination(prev => ({
                    ...prev,
                    total: history.length,
                    current: 1
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
        render: (source: string) => <Tag color={source === 'akshare' ? 'green' : source === 'api' ? 'red' : 'blue'}>{source}</Tag>
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

            {/* 数据管理面板 */}
            <Card 
                title="数据管理" 
                extra={
                    <Button 
                        type="primary" 
                        onClick={() => {
                            setShowDataManagement(!showDataManagement)
                            if (!showDataManagement) {
                                fetchDataStats()
                            }
                        }}
                    >
                        {showDataManagement ? '隐藏' : '显示'}数据管理
                    </Button>
                }
            >
                {showDataManagement && (
                    <div className="space-y-4">
                        <Alert
                            message="数据来源说明"
                            description="akshare: 历史确认数据（推荐保留） | api: 天天基金API数据（可删除）"
                            type="info"
                            showIcon
                        />
                        
                        {dataStats && (
                            <Row gutter={16}>
                                <Col span={6}>
                                    <Statistic
                                        title="akshare数据"
                                        value={dataStats.akshare_count || 0}
                                        valueStyle={{ color: '#3f8600' }}
                                    />
                                </Col>
                                <Col span={6}>
                                    <Statistic
                                        title="api数据"
                                        value={dataStats.api_count || 0}
                                        valueStyle={{ color: '#cf1322' }}
                                    />
                                </Col>
                                <Col span={6}>
                                    <Statistic
                                        title="总记录数"
                                        value={dataStats.total_count || 0}
                                        valueStyle={{ color: '#1890ff' }}
                                    />
                                </Col>
                                <Col span={6}>
                                    <Statistic
                                        title="基金数量"
                                        value={dataStats.fund_count || 0}
                                        valueStyle={{ color: '#722ed1' }}
                                    />
                                </Col>
                            </Row>
                        )}
                        
                        <Space>
                            <Button
                                danger
                                icon={<DeleteOutlined />}
                                onClick={() => setDeleteModalVisible(true)}
                                disabled={!dataStats || (dataStats.api_count || 0) === 0}
                            >
                                删除api来源数据
                            </Button>
                            <Button
                                type="primary"
                                icon={<SyncOutlined />}
                                onClick={incrementalUpdate}
                                disabled={!fundCode.trim()}
                            >
                                增量更新
                            </Button>
                        </Space>
                    </div>
                )}
            </Card>

            {/* 历史净值查询 */}
            <Card title="历史净值查询">
                <Row gutter={16} align="middle">
                    <Col span={6}>
                        <Input
                            placeholder="请输入基金代码（如：004042）"
                            value={fundCode}
                            onChange={(e) => setFundCode(e.target.value)}
                            onPressEnter={() => fetchNavHistory()}
                            prefix={<SearchOutlined />}
                        />
                    </Col>
                    <Col span={6}>
                        <Select
                            placeholder="选择数据来源"
                            value={sourceFilter}
                            onChange={setSourceFilter}
                            style={{ width: '100%' }}
                        >
                            <Select.Option value="all">全部来源</Select.Option>
                            <Select.Option value="akshare">akshare</Select.Option>
                            <Select.Option value="api">api</Select.Option>
                        </Select>
                    </Col>
                    <Col span={6}>
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
                    <Col span={6}>
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
                                type="dashed"
                                loading={estimateLoading}
                                onClick={fetchEstimate}
                            >
                                查询估算净值
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

            {/* 估算数据显示 */}
            {estimateData && (
                <Card title="当天估算净值" style={{ marginTop: 16 }}>
                    <Row gutter={16}>
                        <Col span={6}>
                            <Statistic
                                title="估算净值"
                                value={estimateData.estimate_nav}
                                precision={4}
                                valueStyle={{ color: '#1890ff' }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="估算时间"
                                value={estimateData.estimate_time}
                                valueStyle={{ color: '#722ed1' }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="确认净值"
                                value={estimateData.confirmed_nav}
                                precision={4}
                                valueStyle={{ color: '#3f8600' }}
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="确认日期"
                                value={estimateData.confirmed_date}
                                valueStyle={{ color: '#cf1322' }}
                            />
                        </Col>
                    </Row>
                    <Row gutter={16} style={{ marginTop: 16 }}>
                        <Col span={12}>
                            <Statistic
                                title="涨跌幅"
                                value={estimateData.growth_rate}
                                precision={2}
                                suffix="%"
                                valueStyle={{
                                    color: estimateData.growth_rate > 0 ? '#3f8600' :
                                        estimateData.growth_rate < 0 ? '#cf1322' : '#666'
                                }}
                            />
                        </Col>
                        <Col span={12}>
                            <Statistic
                                title="数据来源"
                                value="天天基金估算"
                                valueStyle={{ color: '#faad14' }}
                            />
                        </Col>
                    </Row>
                    <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f6f8fa', borderRadius: 6 }}>
                        <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
                            <strong>说明：</strong>估算净值是天天基金根据当日市场情况预估的净值，仅供参考。
                            确认净值是基金公司公布的正式净值，通常在交易日下午15:00后公布。
                        </p>
                    </div>
                </Card>
            )}

            {/* 删除确认对话框 */}
            <Modal
                title="确认删除"
                open={deleteModalVisible}
                onOk={deleteSourceData}
                onCancel={() => {
                    setDeleteModalVisible(false)
                    setSelectedSource('')
                }}
                confirmLoading={deleteLoading}
            >
                <div style={{ marginBottom: 16 }}>
                    <ExclamationCircleOutlined style={{ color: '#faad14', marginRight: 8 }} />
                    您确定要删除所有api来源的数据吗？
                </div>
                <Alert
                    message="删除说明"
                    description="此操作将删除所有来源为'api'的净值数据，这些数据来自天天基金API的估算值。删除后只保留akshare的历史确认数据。"
                    type="warning"
                    showIcon
                />
            </Modal>

            {/* 使用说明 */}
            <Card title="使用说明">
                <div className="space-y-2 text-sm text-gray-600">
                    <p>• <strong>查询历史净值</strong>：输入基金代码，点击查询按钮获取历史净值数据</p>
                    <p>• <strong>数据来源筛选</strong>：可以按akshare或api来源筛选数据</p>
                    <p>• <strong>强制更新</strong>：从akshare重新获取最新历史净值数据</p>
                    <p>• <strong>增量更新</strong>：只获取缺失的历史净值数据，提高效率</p>
                    <p>• <strong>删除api数据</strong>：安全删除天天基金API来源的估算数据</p>
                    <p>• <strong>导出数据</strong>：将查询到的历史净值数据导出为CSV文件</p>
                    <p>• <strong>数据来源</strong>：akshare提供历史确认数据，天天基金API提供实时估算数据</p>
                    <p>• <strong>分页显示</strong>：支持分页浏览大量历史数据，每页默认显示20条记录</p>
                    <p>• <strong>分红数据</strong>：支持显示和同步基金分红数据</p>
                </div>
            </Card>
        </div>
    )
}

export default FundNavManagement 