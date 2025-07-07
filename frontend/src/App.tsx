import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import MobileLayout from './components/MobileLayout'
import { useDeviceDetection } from './hooks/useDeviceDetection'
import Dashboard from './pages/Dashboard'
import MobileDashboard from './pages/MobileDashboard'
import Operations from './pages/Operations'
import Positions from './pages/Positions'
import Funds from './pages/Funds'
import Analysis from './pages/Analysis'
import { OKXManagementPage } from './pages/OKXManagement'
import ExchangeRates from './pages/ExchangeRates'
import WiseManagementPage from './pages/WiseManagement'

function App() {
    const { isMobile } = useDeviceDetection()
    
    // 根据设备类型选择布局组件和Dashboard组件
    const LayoutComponent = isMobile ? MobileLayout : Layout
    const DashboardComponent = isMobile ? MobileDashboard : Dashboard

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <LayoutComponent>
                    <Routes>
                        <Route path="/" element={<DashboardComponent />} />
                        <Route path="/operations" element={<Operations />} />
                        <Route path="/positions" element={<Positions />} />
                        <Route path="/funds" element={<Funds />} />
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