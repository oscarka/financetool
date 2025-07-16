import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import DynamicLayout from './components/DynamicLayout'
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
import ConfigManagementPage from './pages/ConfigManagement'
import SchedulerManagementPage from './pages/SchedulerManagementPage'
import MenuManagementPage from './pages/MenuManagement'
import React from 'react'

function App() {
    const deviceInfo = useDeviceDetection();

    // 根据设备类型选择布局组件和页面组件
    const LayoutComponent = deviceInfo.isMobile ? MobileLayout : DynamicLayout;
    const DashboardComponent = deviceInfo.isMobile ? MobileDashboard : Dashboard
    const OperationsComponent = deviceInfo.isMobile ? MobileOperations : Operations
    const PositionsComponent = deviceInfo.isMobile ? MobilePositions : Positions
    const FundsComponent = deviceInfo.isMobile ? MobileFunds : Funds



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
        return () => {
        };
    }, [deviceInfo.isMobile, deviceInfo.screenWidth])


    return (
        <Router>
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
                        <Route path="/config" element={<ConfigManagementPage />} />
                        <Route path="/scheduler" element={<SchedulerManagementPage />} />
                        <Route path="/menu" element={<MenuManagementPage />} />
                    </Routes>
                </LayoutComponent>
        </Router>
    )
}

export default App 