import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Grid,
} from '@mui/material'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { getVendors, getVendorRiskDistribution } from '../services/api'

const RISK_COLORS: any = {
  Critical: '#d32f2f',
  High: '#f57c00',
  Medium: '#fbc02d',
  Low: '#388e3c',
}

export default function VendorRisk() {
  const { data: vendors } = useQuery({
    queryKey: ['vendors'],
    queryFn: async () => {
      const response = await getVendors()
      return response.data
    },
  })

  const { data: distribution } = useQuery({
    queryKey: ['vendorRiskDistribution'],
    queryFn: async () => {
      const response = await getVendorRiskDistribution()
      return response.data
    },
  })

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Critical':
        return 'error'
      case 'High':
        return 'warning'
      case 'Medium':
        return 'info'
      case 'Low':
        return 'success'
      default:
        return 'default'
    }
  }

  // Prepare chart data
  const chartData = distribution?.risk_distribution
    ? Object.entries(distribution.risk_distribution).map(([level, data]: [string, any]) => ({
        name: level,
        value: data.count,
      }))
    : []

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Vendor Risk Management
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Active Vendors
            </Typography>
            <Typography variant="h4">{distribution?.total_active_vendors || 0}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Assessments This Year
            </Typography>
            <Typography variant="h4">
              {distribution?.assessments_completed_this_year || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Upcoming Assessments
            </Typography>
            <Typography variant="h4" color="warning.main">
              {distribution?.upcoming_assessments_30_days || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Target: Annual Assessments
            </Typography>
            <Typography variant="h4" color="success.main">
              500+
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Risk Distribution Chart */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Vendor Risk Distribution
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(entry) => `${entry.name}: ${entry.value}`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#999'} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Paper>

      {/* Vendors Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Vendor ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Service Type</TableCell>
              <TableCell>Data Access</TableCell>
              <TableCell>Last Assessment</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {vendors?.map((vendor: any) => (
              <TableRow key={vendor.id}>
                <TableCell>{vendor.vendor_id}</TableCell>
                <TableCell>{vendor.name}</TableCell>
                <TableCell>
                  <Chip label={vendor.status} size="small" color="info" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={vendor.risk_level || 'Not Assessed'}
                    size="small"
                    color={vendor.risk_level ? getRiskColor(vendor.risk_level) : 'default'}
                  />
                </TableCell>
                <TableCell>{vendor.risk_score?.toFixed(1) || 'N/A'}</TableCell>
                <TableCell>{vendor.service_type || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={vendor.data_access ? 'Yes' : 'No'}
                    size="small"
                    color={vendor.data_access ? 'warning' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  {vendor.last_assessment_date
                    ? new Date(vendor.last_assessment_date).toLocaleDateString()
                    : 'Never'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}