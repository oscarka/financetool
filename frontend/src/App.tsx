import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Operations from './pages/Operations'
import Positions from './pages/Positions'
import Funds from './pages/Funds'
import Analysis from './pages/Analysis'

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
                    </Routes>
                </Layout>
            </div>
        </Router>
    )
}

export default App 