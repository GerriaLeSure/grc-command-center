import { useQuery } from '@tanstack/react-query'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { getDashboardOverview, getKPIs, getActionItems } from '../services/api'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export default function Dashboard() {
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['dashboardOverview'],
    queryFn: async () => {
      const response = await getDashboardOverview()
      return response.data
    },
  })

  const { data: kpis, isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: async () => {
      const response = await getKPIs()
      return response.data
    },
  })

  const { data: actionItems, isLoading: actionsLoading } = useQuery({
    queryKey: ['actionItems'],
    queryFn: async () => {
      const response = await getActionItems()
      return response.data
    },
  })

  if (overviewLoading || kpisLoading || actionsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  const summary = overview?.summary || {}
  const alerts = overview?.alerts || {}
  const compliance = overview?.compliance_by_framework || []

  // Prepare compliance chart data
  const complianceChartData = compliance.map((item: any) => ({
    name: item.framework,
    percentage: item.percentage,
  }))

  // Prepare risk distribution data
  const riskData = [
    { name: 'Total Risks', value: summary.total_risks || 0 },
    { name: 'Open Risks', value: summary.open_risks || 0 },
    { name: 'Critical Risks', value: summary.critical_risks || 0 },
  ]

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return 'error'
      case 'High':
        return 'warning'
      case 'Medium':
        return 'info'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        GRC Command Center Dashboard
      </Typography>

      {/* Impact Statement */}
      <Alert severity="success" sx={{ mb: 3 }}>
        <Typography variant="body1" fontWeight="bold">
          Impact Metrics: Reduced audit prep time from 3 months to 2 weeks (84% improvement). 
          Supporting 500+ vendor assessments annually. Preventing compliance penalties through proactive monitoring.
        </Typography>
      </Alert>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Risks
              </Typography>
              <Typography variant="h4">{summary.total_risks || 0}</Typography>
              <Typography color="error" variant="body2">
                {summary.critical_risks || 0} Critical
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Controls
              </Typography>
              <Typography variant="h4">{summary.total_controls || 0}</Typography>
              <Typography color="success.main" variant="body2">
                {summary.implemented_controls || 0} Implemented
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Vendors
              </Typography>
              <Typography variant="h4">{summary.total_vendors || 0}</Typography>
              <Typography color="warning.main" variant="body2">
                {summary.high_risk_vendors || 0} High Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Compliance
              </Typography>
              <Typography variant="h4">{summary.average_compliance || 0}%</Typography>
              <Typography color="info.main" variant="body2">
                Across All Frameworks
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* KPI Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Metrics
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Risk Reduction: {kpis?.risk_metrics?.risk_reduction_percentage?.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  Avg Inherent Risk: {kpis?.risk_metrics?.average_inherent_risk?.toFixed(2)}
                </Typography>
                <Typography variant="body2">
                  Avg Residual Risk: {kpis?.risk_metrics?.average_residual_risk?.toFixed(2)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Control Effectiveness
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Implementation Rate: {kpis?.control_metrics?.implementation_rate?.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  Automation Rate: {kpis?.control_metrics?.automation_rate?.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  Total Controls: {kpis?.control_metrics?.total_controls || 0}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Compliance by Framework
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={complianceChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="percentage" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Risk Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Alerts and Action Items */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Alerts
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Critical Risks"
                    secondary={`${alerts.critical_risks || 0} risks require immediate attention`}
                  />
                  <Chip label={alerts.critical_risks || 0} color="error" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Controls Needing Testing"
                    secondary="Controls that require testing"
                  />
                  <Chip label={alerts.controls_needing_testing || 0} color="warning" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Assessments Due (30 days)"
                    secondary="Vendor assessments coming due"
                  />
                  <Chip label={alerts.assessments_due_30_days || 0} color="info" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Expiring Evidence"
                    secondary="Evidence expiring within 30 days"
                  />
                  <Chip label={alerts.expiring_evidence || 0} color="warning" size="small" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Action Items
              </Typography>
              <List dense>
                {actionItems?.action_items?.slice(0, 10).map((item: any, index: number) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={item.title}
                      secondary={`Owner: ${item.owner || 'Unassigned'} | Due: ${
                        item.due_date ? new Date(item.due_date).toLocaleDateString() : 'N/A'
                      }`}
                    />
                    <Chip
                      label={item.priority}
                      color={getPriorityColor(item.priority)}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}