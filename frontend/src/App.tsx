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

function App() {
    const { isMobile } = useDeviceDetection()
    
    // 根据设备类型选择布局组件和页面组件
    const LayoutComponent = isMobile ? MobileLayout : Layout
    const DashboardComponent = isMobile ? MobileDashboard : Dashboard
    const OperationsComponent = isMobile ? MobileOperations : Operations
    const PositionsComponent = isMobile ? MobilePositions : Positions
    const FundsComponent = isMobile ? MobileFunds : Funds

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
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
                    </Routes>
                </LayoutComponent>
            </div>
        </Router>
    )
}

export default App 