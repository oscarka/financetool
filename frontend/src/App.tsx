import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Operations from './pages/Operations'
import Positions from './pages/Positions'
import Funds from './pages/Funds'
import Analysis from './pages/Analysis'
import { OKXManagementPage } from './pages/OKXManagement'
import ExchangeRates from './pages/ExchangeRates'
import WiseManagementPage from './pages/WiseManagement'

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <Layout>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/operations" element={<Operations />} />
                        <Route path="/positions" element={<Positions />} />
                        <Route path="/funds" element={<Funds />} />
                        <Route path="/analysis" element={<Analysis />} />
                        <Route path="/exchange-rates" element={<ExchangeRates />} />
                        <Route path="/okx" element={<OKXManagementPage />} />
                        <Route path="/wise" element={<WiseManagementPage />} />
                    </Routes>
                </Layout>
            </div>
        </Router>
    )
}

export default App 