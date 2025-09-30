import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Paper,
  Grid,
  LinearProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
} from '@mui/material'
import { Assessment } from '@mui/icons-material'
import { getComplianceDashboard, initializeComplianceFrameworks } from '../services/api'
import toast from 'react-hot-toast'

export default function ComplianceDashboard() {
  const { data: frameworks, isLoading, refetch } = useQuery({
    queryKey: ['complianceDashboard'],
    queryFn: async () => {
      const response = await getComplianceDashboard()
      return response.data
    },
  })

  const handleInitialize = async () => {
    try {
      await initializeComplianceFrameworks()
      toast.success('Compliance frameworks initialized')
      refetch()
    } catch (error) {
      toast.error('Failed to initialize frameworks')
    }
  }

  const getComplianceColor = (percentage: number) => {
    if (percentage >= 95) return 'success'
    if (percentage >= 70) return 'warning'
    return 'error'
  }

  const getComplianceColorValue = (percentage: number) => {
    if (percentage >= 95) return '#4caf50'
    if (percentage >= 70) return '#ff9800'
    return '#f44336'
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Compliance Dashboard</Typography>
        <Button variant="outlined" onClick={handleInitialize}>
          Initialize Frameworks
        </Button>
      </Box>

      <Typography variant="h6" gutterBottom>
        Real-time Compliance Status by Framework
      </Typography>

      <Grid container spacing={3}>
        {frameworks?.map((framework: any) => (
          <Grid item xs={12} md={6} lg={4} key={framework.framework_name}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Assessment sx={{ mr: 1 }} />
                  <Typography variant="h6">{framework.framework_name}</Typography>
                </Box>

                <Box mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2" color="textSecondary">
                      Compliance Percentage
                    </Typography>
                    <Typography variant="h5" color="primary">
                      {framework.compliance_percentage.toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={framework.compliance_percentage}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getComplianceColorValue(framework.compliance_percentage),
                      },
                    }}
                  />
                </Box>

                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">
                    Status:
                    <Chip
                      label={framework.status}
                      size="small"
                      color={getComplianceColor(framework.compliance_percentage)}
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography variant="body2">
                    {framework.compliant_count} / {framework.total_count} Requirements
                  </Typography>
                </Box>

                {framework.critical_gaps.length > 0 && (
                  <Box>
                    <Typography variant="body2" color="error" gutterBottom>
                      Critical Gaps:
                    </Typography>
                    <List dense>
                      {framework.critical_gaps.slice(0, 3).map((gap: string, index: number) => (
                        <ListItem key={index} sx={{ py: 0 }}>
                          <ListItemText
                            primary={gap}
                            primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Summary Section */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Overall Compliance Summary
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="textSecondary">
              Active Frameworks
            </Typography>
            <Typography variant="h4">{frameworks?.length || 0}</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="textSecondary">
              Average Compliance
            </Typography>
            <Typography variant="h4">
              {frameworks?.length > 0
                ? (
                    frameworks.reduce((sum: number, f: any) => sum + f.compliance_percentage, 0) /
                    frameworks.length
                  ).toFixed(1)
                : 0}
              %
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="textSecondary">
              Total Requirements
            </Typography>
            <Typography variant="h4">
              {frameworks?.reduce((sum: number, f: any) => sum + f.total_count, 0) || 0}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}