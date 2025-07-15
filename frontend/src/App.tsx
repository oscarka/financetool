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
import ConfigManagementPage from './pages/ConfigManagement'
import SchedulerManagementPage from './pages/SchedulerManagementPage'
import React from 'react'

function App() {
    const deviceInfo = useDeviceDetection();

    // 根据设备类型选择布局组件和页面组件
    const LayoutComponent = deviceInfo.isMobile ? MobileLayout : Layout;
    const DashboardComponent = deviceInfo.isMobile ? MobileDashboard : Dashboard
    const OperationsComponent = deviceInfo.isMobile ? MobileOperations : Operations
    const PositionsComponent = deviceInfo.isMobile ? MobilePositions : Positions
    const FundsComponent = deviceInfo.isMobile ? MobileFunds : Funds

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
                    </Routes>
                </LayoutComponent>
        </Router>
    )
}

export default App 