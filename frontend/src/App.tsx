import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import MobileLayout from './components/MobileLayout'
import { useDeviceDetection } from './hooks/useDeviceDetection'
import Dashboard from './pages/Dashboard'
import MobileDashboard from './pages/MobileDashboard'
import Operations from './pages/Operations'
import MobileOperations from './pages/MobileOperations'
import Positions from './pages/Positions'
import MobilePositions from './pages/MobilePositions'
import Funds from './pages/Funds'
import MobileFunds from './pages/MobileFunds'
import Analysis from './pages/Analysis'
import { OKXManagementPage } from './pages/OKXManagement'
import ExchangeRates from './pages/ExchangeRates'
import WiseManagementPage from './pages/WiseManagement'
import PayPalManagementPage from './pages/PayPalManagement'
import IBKRManagementPage from './pages/IBKRManagement'
import React from 'react'

function App() {
    const deviceInfo = useDeviceDetection()
    
    // 强制输出调试信息 - 无论什么情况都要看到
    console.log('🔥 APP 组件渲染 - 强制调试信息')
    console.log('🔍 设备检测信息:', {
        isMobile: deviceInfo.isMobile,
        isTablet: deviceInfo.isTablet,
        isDesktop: deviceInfo.isDesktop,
        screenWidth: deviceInfo.screenWidth,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
    })
    
    // 根据设备类型选择布局组件和页面组件
    const LayoutComponent = deviceInfo.isMobile ? MobileLayout : Layout
    const DashboardComponent = deviceInfo.isMobile ? MobileDashboard : Dashboard
    const OperationsComponent = deviceInfo.isMobile ? MobileOperations : Operations
    const PositionsComponent = deviceInfo.isMobile ? MobilePositions : Positions
    const FundsComponent = deviceInfo.isMobile ? MobileFunds : Funds

    console.log('📱 当前使用组件:', {
        Layout: deviceInfo.isMobile ? 'MobileLayout' : 'Layout',
        Dashboard: deviceInfo.isMobile ? 'MobileDashboard' : 'Dashboard',
        Operations: deviceInfo.isMobile ? 'MobileOperations' : 'Operations',
        Positions: deviceInfo.isMobile ? 'MobilePositions' : 'Positions',
        Funds: deviceInfo.isMobile ? 'MobileFunds' : 'Funds'
    })

    // 强制在页面上显示设备信息
    React.useEffect(() => {
        const debugInfo = document.createElement('div')
        debugInfo.id = 'debug-device-info'
        debugInfo.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: ${deviceInfo.isMobile ? '#52c41a' : '#ff4d4f'};
            color: white;
            padding: 8px;
            font-size: 14px;
            z-index: 99999;
            text-align: center;
            font-weight: bold;
        `
        debugInfo.innerHTML = `
            ${deviceInfo.isMobile ? '📱 移动端模式' : '🖥️ 桌面端模式'} | 
            宽度: ${deviceInfo.screenWidth}px | 
            时间: ${new Date().toLocaleTimeString()}
        `
        
        // 移除旧的调试信息
        const old = document.getElementById('debug-device-info')
        if (old) old.remove()
        
        document.body.appendChild(debugInfo)
        
        // 5秒后自动隐藏
        setTimeout(() => {
            if (document.getElementById('debug-device-info')) {
                debugInfo.style.display = 'none'
            }
        }, 5000)
    }, [deviceInfo.isMobile, deviceInfo.screenWidth])

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                {/* 添加设备信息显示（仅开发环境） */}
                {process.env.NODE_ENV === 'development' && (
                    <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        background: 'rgba(0,0,0,0.8)',
                        color: 'white',
                        padding: '4px 8px',
                        fontSize: '10px',
                        zIndex: 9999,
                        borderRadius: '0 0 4px 0'
                    }}>
                        {deviceInfo.isMobile ? '📱Mobile' : '🖥️Desktop'} | {deviceInfo.screenWidth}px
                    </div>
                )}
                
                <LayoutComponent>
                    <Routes>
                        <Route path="/" element={<DashboardComponent />} />
                        <Route path="/operations" element={<OperationsComponent />} />
                        <Route path="/positions" element={<PositionsComponent />} />
                        <Route path="/funds" element={<FundsComponent />} />
                        <Route path="/analysis" element={<Analysis />} />
                        <Route path="/exchange-rates" element={<ExchangeRates />} />
                        <Route path="/okx" element={<OKXManagementPage />} />
                        <Route path="/wise" element={<WiseManagementPage />} />
                        <Route path="/paypal" element={<PayPalManagementPage />} />
                        <Route path="/ibkr" element={<IBKRManagementPage />} />
                    </Routes>
                </LayoutComponent>
            </div>
        </Router>
    )
}

export default App 