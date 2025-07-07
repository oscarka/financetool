import React, { useState, useEffect } from 'react'
import { Input, Button, Card, Descriptions, Spin, message, Space } from 'antd'
import { SearchOutlined, SyncOutlined, PlusOutlined } from '@ant-design/icons'
import { fundAPI } from '../services/api'


const { Search } = Input

interface FundInfo {
    fund_code: string
    fund_name: string
    fund_type?: string
    management_fee?: number
    purchase_fee?: number
    redemption_fee?: number
    min_purchase?: number
    risk_level?: string
}

interface FundNav {
    nav?: number
    accumulated_nav?: number
    growth_rate?: number
    nav_date?: string
    source?: string
    estimated_nav?: number
    estimated_time?: string
}

const FundSearch: React.FC = () => {
    const [fundCode, setFundCode] = useState('')
    const [fundInfo, setFundInfo] = useState<FundInfo | null>(null)
    const [fundNav, setFundNav] = useState<FundNav | null>(null)
    const [loading, setLoading] = useState(false)
    const [syncing, setSyncing] = useState(false)
    const [navLoading, setNavLoading] = useState(false)
    const [navSyncing, setNavSyncing] = useState(false)

    const fetchLatestNav = async (code: string) => {
        try {
            let navResponse = await fundAPI.getLatestNav(code)
            console.log('【日志】自动查找最新净值接口返回:', navResponse)
            if (navResponse.success && navResponse.data && navResponse.data.fund_nav) {
                setFundNav(navResponse.data.fund_nav)
            } else {
                // 净值不存在，设置为null但不影响基金信息显示
                setFundNav(null)
                console.log('【日志】净值不存在，需要手动同步')
            }
        } catch (error: any) {
            console.log('【日志】获取净值失败:', error)
            // 净值获取失败，设置为null但不影响基金信息显示
            setFundNav(null)
        }
    }

    const handleSearch = async (code: string) => {
        if (!code.trim()) {
            message.warning('请输入基金代码')
            return
        }

        setLoading(true)
        setNavLoading(true)
        try {
            // 获取基金基本信息
            const response = await fundAPI.getFundInfo(code)
            console.log('【日志】基金基本信息接口返回:', response)
            if (response.success && response.data?.fund_info) {
                setFundInfo(response.data.fund_info)
                message.success('基金信息获取成功')

                // 获取最新净值（自动查找/同步）
                await fetchLatestNav(code)
            } else {
                message.info('未找到基金信息，可以尝试同步')
                setFundInfo(null)
                setFundNav(null)
            }
        } catch (error: any) {
            console.error('搜索基金失败:', error)
            if (error.response?.status === 404) {
                message.info('基金不存在，可以尝试从外部API同步')
                setFundInfo(null)
                setFundNav(null)
            } else {
                message.error('搜索失败，请检查网络连接')
            }
        } finally {
            setLoading(false)
            setNavLoading(false)
        }
    }

    const handleSync = async () => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        setSyncing(true)
        try {
            const response = await fundAPI.syncFundInfo(fundCode)
            if (response.success) {
                message.success('基金信息同步成功')
                // 重新获取基金信息
                await handleSearch(fundCode)
            } else {
                message.error('同步失败')
            }
        } catch (error: any) {
            console.error('同步基金信息失败:', error)
            message.error('同步失败，请稍后重试')
        } finally {
            setSyncing(false)
        }
    }

    const handleSyncNav = async () => {
        if (!fundCode.trim()) {
            message.warning('请输入基金代码')
            return
        }

        setNavSyncing(true)
        try {
            const response = await fundAPI.syncLatestNav(fundCode)
            console.log('【日志】同步最新净值接口返回:', response)
            if (response.success) {
                message.success('基金净值同步成功')
                // 重新获取净值信息
                try {
                    const navResponse = await fundAPI.getLatestNav(fundCode)
                    console.log('【日志】同步后最新净值接口返回:', navResponse)
                    if (navResponse.success && navResponse.data && navResponse.data.fund_nav) {
                        setFundNav(navResponse.data.fund_nav)
                    }
                } catch (navError: any) {
                    console.log('获取净值失败:', navError)
                }
            } else {
                message.error('净值同步失败')
            }
        } catch (error: any) {
            console.error('同步基金净值失败:', error)
            message.error('净值同步失败，请稍后重试')
        } finally {
            setNavSyncing(false)
        }
    }

    const handleAddToDatabase = async () => {
        if (!fundInfo) {
            message.warning('没有基金信息可添加')
            return
        }

        try {
            const response = await fundAPI.createFundInfo({
                fund_code: fundInfo.fund_code,
                fund_name: fundInfo.fund_name,
                fund_type: fundInfo.fund_type,
                management_fee: fundInfo.management_fee,
                purchase_fee: fundInfo.purchase_fee,
                redemption_fee: fundInfo.redemption_fee,
                min_purchase: fundInfo.min_purchase,
                risk_level: fundInfo.risk_level,
            })

            if (response.success) {
                message.success('基金信息已添加到数据库')
            } else {
                message.error('添加失败')
            }
        } catch (error: any) {
            console.error('添加基金信息失败:', error)
            message.error('添加失败，请稍后重试')
        }
    }

    // 在fundNav变化时打印日志，避免在JSX中直接console.log
    useEffect(() => {
        if (fundNav) {
            console.log('【日志】渲染用的fundNav:', fundNav)
        }
    }, [fundNav])

    return (
        <div className="space-y-6">
            {/* 搜索区域 */}
            <Card title="基金搜索" className="shadow-sm">
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div className="flex gap-2">
                        <Search
                            placeholder="请输入基金代码（如：000001）"
                            value={fundCode}
                            onChange={(e) => setFundCode(e.target.value)}
                            onSearch={handleSearch}
                            enterButton={<SearchOutlined />}
                            loading={loading}
                            style={{ flex: 1 }}
                        />
                        <Button
                            type="primary"
                            icon={<SyncOutlined />}
                            loading={syncing}
                            onClick={handleSync}
                        >
                            同步信息
                        </Button>
                    </div>

                    <div className="text-sm text-gray-500">
                        💡 提示：输入6位基金代码，如 000001（华夏成长混合）
                    </div>
                </Space>
            </Card>

            {/* 搜索结果 */}
            {loading && (
                <Card>
                    <div className="text-center py-8">
                        <Spin size="large" />
                        <div className="mt-4 text-gray-500">正在搜索基金信息...</div>
                    </div>
                </Card>
            )}

            {fundInfo && (
                <Card
                    title="基金信息"
                    extra={
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={handleAddToDatabase}
                        >
                            添加到数据库
                        </Button>
                    }
                    className="shadow-sm"
                >
                    <Descriptions bordered column={2}>
                        <Descriptions.Item label="基金代码">{fundInfo.fund_code}</Descriptions.Item>
                        <Descriptions.Item label="基金名称">{fundInfo.fund_name}</Descriptions.Item>
                        <Descriptions.Item label="基金类型">{fundInfo.fund_type || '未知'}</Descriptions.Item>
                        <Descriptions.Item label="风险等级">{fundInfo.risk_level || '未知'}</Descriptions.Item>
                        <Descriptions.Item label="管理费率">
                            {fundInfo.management_fee !== undefined && fundInfo.management_fee !== null
                                ? `${(fundInfo.management_fee * 100).toFixed(2)}%`
                                : '未知'}
                        </Descriptions.Item>
                        <Descriptions.Item label="申购费率">
                            {fundInfo.purchase_fee !== undefined && fundInfo.purchase_fee !== null
                                ? `${(fundInfo.purchase_fee * 100).toFixed(2)}%`
                                : '未知'}
                        </Descriptions.Item>
                        <Descriptions.Item label="赎回费率">
                            {fundInfo.redemption_fee !== undefined && fundInfo.redemption_fee !== null
                                ? `${(fundInfo.redemption_fee * 100).toFixed(2)}%`
                                : '未知'}
                        </Descriptions.Item>
                        <Descriptions.Item label="最小申购金额">
                            {fundInfo.min_purchase !== undefined && fundInfo.min_purchase !== null
                                ? `${fundInfo.min_purchase}元`
                                : '未知'}
                        </Descriptions.Item>
                    </Descriptions>

                    {/* 基金净值信息 */}
                    {navLoading ? (
                        <div className="mt-4 text-center">
                            <Spin size="small" />
                            <span className="ml-2 text-gray-500">正在获取净值信息...</span>
                        </div>
                    ) : fundNav ? (
                        <div className="mt-4">
                            <div className="flex justify-between items-center mb-3">
                                <h4>最新净值信息</h4>
                                <Button
                                    type="primary"
                                    size="small"
                                    icon={<SyncOutlined />}
                                    loading={navSyncing}
                                    onClick={handleSyncNav}
                                >
                                    同步净值
                                </Button>
                            </div>
                            <Descriptions bordered column={2} size="small">
                                <Descriptions.Item label="单位净值">
                                    {fundNav.nav !== undefined && fundNav.nav !== null ? fundNav.nav.toFixed(4) : '未知'}
                                </Descriptions.Item>
                                <Descriptions.Item label="累计净值">
                                    {fundNav.accumulated_nav !== undefined && fundNav.accumulated_nav !== null ? fundNav.accumulated_nav.toFixed(4) : '未知'}
                                </Descriptions.Item>
                                <Descriptions.Item label="日增长率">
                                    {fundNav.growth_rate !== undefined && fundNav.growth_rate !== null
                                        ? `${fundNav.growth_rate >= 0 ? '+' : ''}${fundNav.growth_rate.toFixed(2)}%`
                                        : '未知'}
                                </Descriptions.Item>
                                <Descriptions.Item label="净值日期">
                                    {fundNav.nav_date || '未知'}
                                </Descriptions.Item>
                                <Descriptions.Item label="数据来源">
                                    {fundNav.source || '未知'}
                                </Descriptions.Item>
                                <Descriptions.Item label="估算净值">
                                    {fundNav.estimated_nav !== undefined && fundNav.estimated_nav !== null ? Number(fundNav.estimated_nav).toFixed(4) : '未知'}
                                </Descriptions.Item>
                                <Descriptions.Item label="估值时间">
                                    {fundNav.estimated_time || '未知'}
                                </Descriptions.Item>
                            </Descriptions>
                        </div>
                    ) : (
                        <div className="mt-4 text-center">
                            <div className="text-gray-500 mb-2">暂无净值信息</div>
                            <Button
                                type="primary"
                                size="small"
                                icon={<SyncOutlined />}
                                loading={navSyncing}
                                onClick={handleSyncNav}
                            >
                                同步净值
                            </Button>
                        </div>
                    )}
                </Card>
            )}

            {/* 未找到基金时的提示 */}
            {!loading && !fundInfo && fundCode && (
                <Card className="shadow-sm">
                    <div className="text-center py-8">
                        <div className="text-gray-500 mb-4">
                            未找到基金代码 <strong>{fundCode}</strong> 的信息
                        </div>
                        <Space>
                            <Button type="primary" onClick={handleSync}>
                                尝试从外部API同步
                            </Button>
                            <div className="text-sm text-gray-400">
                                基金可能不存在或需要从天天基金网同步数据
                            </div>
                        </Space>
                    </div>
                </Card>
            )}
        </div>
    )
}

export default FundSearch 