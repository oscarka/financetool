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
    StockOutlined
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
    { name: 'OKX', href: '/okx', icon: SettingOutlined },
    { name: 'Wise', href: '/wise', icon: BankOutlined },
    { name: 'PayPal', href: '/paypal', icon: PayCircleOutlined },
    { name: 'IBKR', href: '/ibkr', icon: StockOutlined },
]

// 调试日志  
console.log('📱 [MobileLayout] Navigation menu loaded:', navigation.map(item => `${item.name} (${item.href})`))
console.log('🎯 [MobileLayout] IBKR menu item exists:', navigation.find(item => item.href === '/ibkr') ? 'YES ✅' : 'NO ❌')

const MobileLayout: React.FC<MobileLayoutProps> = ({ children }) => {
    const location = useLocation()
    const [drawerVisible, setDrawerVisible] = useState(false)

    const menuItems = navigation.map((item) => ({
        key: item.href,
        icon: React.createElement(item.icon),
        label: <Link to={item.href} onClick={() => setDrawerVisible(false)}>{item.name}</Link>,
    }))

    // 底部导航主要功能
    const bottomNavItems = navigation.slice(0, 4)

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            {/* 顶部导航栏 */}
            <Header 
                style={{ 
                    background: '#fff', 
                    padding: '0 16px',
                    borderBottom: '1px solid #f0f0f0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    zIndex: 1000,
                    height: '56px'
                }}
            >
                <h1 style={{ 
                    margin: 0, 
                    fontSize: '18px', 
                    fontWeight: 600, 
                    color: '#262626',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                }}>
                    投资管理
                </h1>
                <Button
                    type="text"
                    icon={<MenuOutlined />}
                    onClick={() => setDrawerVisible(true)}
                    size="large"
                />
            </Header>

            {/* 主内容区域 */}
            <Content 
                style={{ 
                    margin: '56px 0 60px 0', // 为顶部和底部导航留出空间
                    padding: '16px',
                    background: '#f5f5f5',
                    minHeight: 'calc(100vh - 116px)'
                }}
            >
                {children}
            </Content>

            {/* 底部导航栏 */}
            <div
                style={{
                    position: 'fixed',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: '#fff',
                    borderTop: '1px solid #f0f0f0',
                    padding: '8px 0',
                    zIndex: 1000,
                    height: '60px'
                }}
            >
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-around',
                    alignItems: 'center',
                    height: '100%'
                }}>
                    {bottomNavItems.map((item) => {
                        const isActive = location.pathname === item.href
                        const IconComponent = item.icon
                        return (
                            <Link
                                key={item.href}
                                to={item.href}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    textDecoration: 'none',
                                    color: isActive ? '#1890ff' : '#666',
                                    fontSize: '12px',
                                    minWidth: '60px'
                                }}
                            >
                                <IconComponent style={{ fontSize: '20px', marginBottom: '2px' }} />
                                <span>{item.name}</span>
                            </Link>
                        )
                    })}
                </div>
            </div>

            {/* 侧边抽屉菜单 */}
            <Drawer
                title="菜单"
                placement="right"
                onClose={() => setDrawerVisible(false)}
                open={drawerVisible}
                width={280}
            >
                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    style={{ border: 'none' }}
                    items={menuItems}
                />
            </Drawer>
        </AntLayout>
    )
}

export default MobileLayout