import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Dashboard
export const getDashboardOverview = () => api.get('/dashboard/overview')
export const getMetricsTrends = (days: number = 30) => api.get(`/dashboard/metrics/trends?days=${days}`)
export const getKPIs = () => api.get('/dashboard/metrics/kpis')
export const getActionItems = () => api.get('/dashboard/action-items')

// Risks
export const getRisks = (params?: any) => api.get('/risks/', { params })
export const getRisk = (riskId: string) => api.get(`/risks/${riskId}`)
export const createRisk = (data: any) => api.post('/risks/', data)
export const updateRisk = (riskId: string, data: any) => api.put(`/risks/${riskId}`, data)
export const deleteRisk = (riskId: string) => api.delete(`/risks/${riskId}`)
export const getRiskHeatmap = () => api.get('/risks/analytics/heatmap')
export const getRiskStatistics = () => api.get('/risks/analytics/statistics')
export const importRisksExcel = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/risks/import/excel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export const exportRisksExcel = (filters?: any) => api.post('/risks/export/excel', filters, {
  responseType: 'blob'
})

// Controls
export const getControls = (params?: any) => api.get('/controls/', { params })
export const getControl = (controlId: string) => api.get(`/controls/${controlId}`)
export const createControl = (data: any) => api.post('/controls/', data)
export const updateControl = (controlId: string, data: any) => api.put(`/controls/${controlId}`, data)
export const getFrameworks = () => api.get('/controls/frameworks/')
export const initializeFrameworks = () => api.post('/controls/frameworks/initialize')
export const getControlCoverage = () => api.get('/controls/analytics/coverage')
export const getControlMappings = (controlId: string) => api.get(`/controls/mappings/${controlId}`)

// Compliance
export const getComplianceFrameworks = () => api.get('/compliance/frameworks/')
export const getComplianceFramework = (frameworkId: string) => api.get(`/compliance/frameworks/${frameworkId}`)
export const getFrameworkRequirements = (frameworkId: string) => api.get(`/compliance/frameworks/${frameworkId}/requirements`)
export const calculateFrameworkCompliance = (frameworkId: string) => api.put(`/compliance/frameworks/${frameworkId}/calculate`)
export const getComplianceDashboard = () => api.get('/compliance/dashboard')
export const getGapAnalysis = (frameworkId: string) => api.get(`/compliance/analytics/gap-analysis/${frameworkId}`)
export const initializeComplianceFrameworks = () => api.post('/compliance/frameworks/initialize')
export const updateRequirementStatus = (requirementId: string, data: any) => api.put(`/compliance/requirements/${requirementId}`, data)

// Vendors
export const getVendors = (params?: any) => api.get('/vendors/', { params })
export const getVendor = (vendorId: string) => api.get(`/vendors/${vendorId}`)
export const createVendor = (data: any) => api.post('/vendors/', data)
export const updateVendor = (vendorId: string, data: any) => api.put(`/vendors/${vendorId}`, data)
export const createVendorAssessment = (data: any) => api.post('/vendors/assessments/', data)
export const getVendorAssessments = (vendorId: string) => api.get(`/vendors/assessments/${vendorId}`)
export const completeAssessment = (assessmentId: string, scores: any) => api.post(`/vendors/assessments/${assessmentId}/complete`, scores)
export const getVendorRiskDistribution = () => api.get('/vendors/analytics/risk-distribution')

// Evidence
export const getEvidence = (params?: any) => api.get('/evidence/', { params })
export const getEvidenceById = (evidenceId: string) => api.get(`/evidence/${evidenceId}`)
export const createEvidence = (data: any) => api.post('/evidence/', data)
export const uploadEvidence = (file: File, metadata: any) => {
  const formData = new FormData()
  formData.append('file', file)
  Object.keys(metadata).forEach(key => {
    formData.append(key, metadata[key])
  })
  return api.post('/evidence/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export const verifyEvidence = (evidenceId: string, reviewer: string, notes?: string) => 
  api.put(`/evidence/${evidenceId}/verify`, { reviewer, notes })
export const getEvidenceCollections = () => api.get('/evidence/collections/')
export const getEvidenceSummary = () => api.get('/evidence/analytics/summary')

// Integrations
export const getAwsFindings = (severity?: string) => api.get('/integrations/aws/security-hub/findings', { params: { severity } })
export const importAwsFindings = (severityFilter?: string) => api.post('/integrations/aws/security-hub/import-risks', { severity_filter: severityFilter })
export const getJiraIssues = (project?: string) => api.get('/integrations/jira/issues', { params: { project } })
export const createJiraIssue = (data: any) => api.post('/integrations/jira/create-issue', data)
export const getServiceNowIncidents = () => api.get('/integrations/servicenow/incidents')
export const checkIntegrationsHealth = () => api.get('/integrations/health')

export default api