import React from 'react'
import { Tabs } from 'antd'
import FundSearch from '../components/FundSearch'
import FundOperations from '../components/FundOperations'
import FundPositions from '../components/FundPositions'
import FundAnalysis from '../components/FundAnalysis'
import FundNavManagement from '../components/FundNavManagement'
import DCAPlans from '../components/DCAPlans'

const { TabPane } = Tabs

const Funds: React.FC = () => {
    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">基金管理</h1>
                <p className="mt-2 text-sm text-gray-700">
                    管理基金投资、净值同步和定投计划
                </p>
            </div>

            <Tabs defaultActiveKey="search" size="large">
                <TabPane tab="基金搜索" key="search">
                    <FundSearch />
                </TabPane>
                <TabPane tab="操作记录" key="operations">
                    <FundOperations />
                </TabPane>
                <TabPane tab="持仓管理" key="positions">
                    <FundPositions />
                </TabPane>
                <TabPane tab="基金列表" key="list">
                    <div className="bg-white shadow rounded-lg p-6">
                        <p className="text-gray-500">基金列表功能正在开发中...</p>
                    </div>
                </TabPane>
                <TabPane tab="收益分析" key="analysis">
                    <FundAnalysis />
                </TabPane>
                <TabPane tab="净值管理" key="nav">
                    <FundNavManagement />
                </TabPane>
                <TabPane tab="定投计划" key="dca">
                    <DCAPlans />
                </TabPane>
            </Tabs>
        </div>
    )
}

export default Funds 