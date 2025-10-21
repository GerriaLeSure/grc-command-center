import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RiskRegister from './pages/RiskRegister'
import ControlLibrary from './pages/ControlLibrary'
import ComplianceDashboard from './pages/ComplianceDashboard'
import VendorRisk from './pages/VendorRisk'
import Evidence from './pages/Evidence'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/risks" element={<RiskRegister />} />
        <Route path="/controls" element={<ControlLibrary />} />
        <Route path="/compliance" element={<ComplianceDashboard />} />
        <Route path="/vendors" element={<VendorRisk />} />
        <Route path="/evidence" element={<Evidence />} />
      </Routes>
    </Layout>
  )
}

export default App