import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Drawer, Button } from 'antd'
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
    MenuOutlined,
    StockOutlined,
    ToolOutlined,
    ClockCircleOutlined,
    RobotOutlined
} from '@ant-design/icons'

const { Header, Content } = AntLayout

interface MobileLayoutProps {
    children: React.ReactNode
}

const navigation = [
    { name: '总览', href: '/', icon: HomeOutlined },
    { name: '操作', href: '/operations', icon: PlusCircleOutlined },
    { name: '持仓', href: '/positions', icon: BarChartOutlined },
    { name: '基金', href: '/funds', icon: DollarOutlined },
    { name: '汇率', href: '/exchange-rates', icon: GlobalOutlined },
    { name: '分析', href: '/analysis', icon: PieChartOutlined },
    { name: 'AI测试', href: '/ai-analyst-test', icon: RobotOutlined },
    { name: 'OKX', href: '/okx', icon: SettingOutlined },
    { name: 'Wise', href: '/wise', icon: BankOutlined },
    { name: 'PayPal', href: '/paypal', icon: PayCircleOutlined },
    { name: 'IBKR', href: '/ibkr', icon: StockOutlined },
    { name: '配置', href: '/config', icon: ToolOutlined },
    { name: '调度器', href: '/scheduler', icon: ClockCircleOutlined },
]

const MobileLayout: React.FC<MobileLayoutProps> = ({ children }) => {
    const location = useLocation()
    const [drawerVisible, setDrawerVisible] = useState(false)

    const menuItems = navigation.map((item) => ({
        key: item.href,
        icon: React.createElement(item.icon),
        label: <Link to={item.href} onClick={() => setDrawerVisible(false)}>{item.name}</Link>,
    }))

    // 获取当前页面名称
    const currentPage = navigation.find(item => item.href === location.pathname)?.name || '首页'

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            <Header
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: '#001529',
                    padding: '0 16px',
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    zIndex: 1000,
                    height: '56px',
                }}
            >
                <div style={{ color: 'white', fontSize: '16px', fontWeight: 500 }}>
                    {currentPage}
                </div>
                <Button
                    type="text"
                    icon={<MenuOutlined />}
                    onClick={() => setDrawerVisible(true)}
                    style={{
                        color: 'white',
                        border: 'none',
                        background: 'transparent',
                        fontSize: '18px',
                    }}
                />
            </Header>

            <Drawer
                title="个人财务管理系统"
                placement="right"
                onClose={() => setDrawerVisible(false)}
                open={drawerVisible}
                width={280}
                styles={{
                    body: { padding: 0 }
                }}
            >
                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    style={{ height: '100%', borderRight: 0 }}
                    items={menuItems}
                />
            </Drawer>

            <Content
                style={{
                    marginTop: '56px', // Header高度
                    padding: '16px',
                    background: '#f5f5f5',
                    minHeight: 'calc(100vh - 56px)',
                }}
            >
                {children}
            </Content>
        </AntLayout>
    )
}

export default MobileLayout