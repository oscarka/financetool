import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu } from 'antd'
import {
    HomeOutlined,
    PlusCircleOutlined,
    BarChartOutlined,
    DollarOutlined,
    PieChartOutlined,
    SettingOutlined,
    GlobalOutlined,
    BankOutlined,
    PayCircleOutlined,
    StockOutlined
} from '@ant-design/icons'

const { Sider, Content } = AntLayout

interface LayoutProps {
    children: React.ReactNode
}

const navigation = [
    { name: '仪表板', href: '/', icon: HomeOutlined },
    { name: '投资总览', href: '/overview', icon: PieChartOutlined },
    { name: '操作记录', href: '/operations', icon: PlusCircleOutlined },
    { name: '持仓', href: '/positions', icon: BarChartOutlined },
    { name: '基金', href: '/funds', icon: DollarOutlined },
    { name: '汇率', href: '/exchange-rates', icon: GlobalOutlined },
    { name: '分析', href: '/analysis', icon: PieChartOutlined },
    { name: 'OKX管理', href: '/okx', icon: SettingOutlined },
    { name: 'Wise管理', href: '/wise', icon: BankOutlined },
    { name: 'PayPal管理', href: '/paypal', icon: PayCircleOutlined },
    { name: 'IBKR管理', href: '/ibkr', icon: StockOutlined },
]

// 调试日志
console.log('🔍 [Layout] Navigation menu loaded:', navigation.map(item => `${item.name} (${item.href})`))
console.log('🎯 [Layout] IBKR menu item exists:', navigation.find(item => item.href === '/ibkr') ? 'YES ✅' : 'NO ❌')

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const location = useLocation()

    const menuItems = navigation.map((item) => ({
        key: item.href,
        icon: React.createElement(item.icon),
        label: <Link to={item.href}>{item.name}</Link>,
    }))

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            <Sider
                width={256}
                style={{
                    background: '#fff',
                    borderRight: '1px solid #f0f0f0',
                }}
                breakpoint="lg"
                collapsedWidth="0"
            >
                <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                    <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#262626' }}>
                        个人财务管理系统
                    </h1>
                </div>
                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    style={{ height: '100%', borderRight: 0 }}
                    items={menuItems}
                />
            </Sider>
            <AntLayout>
                <Content style={{ margin: '24px 16px', padding: 24, background: '#f5f5f5' }}>
                    {children}
                </Content>
            </AntLayout>
        </AntLayout>
    )
}

export default Layout 