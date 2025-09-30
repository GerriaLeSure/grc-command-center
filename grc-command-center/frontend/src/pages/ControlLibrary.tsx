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
  Button,
} from '@mui/material'
import { Shield } from '@mui/icons-material'
import { getControls, getControlCoverage, initializeFrameworks } from '../services/api'
import toast from 'react-hot-toast'

export default function ControlLibrary() {
  const { data: controls, isLoading } = useQuery({
    queryKey: ['controls'],
    queryFn: async () => {
      const response = await getControls()
      return response.data
    },
  })

  const { data: coverage } = useQuery({
    queryKey: ['controlCoverage'],
    queryFn: async () => {
      const response = await getControlCoverage()
      return response.data
    },
  })

  const handleInitializeFrameworks = async () => {
    try {
      await initializeFrameworks()
      toast.success('Frameworks initialized successfully')
    } catch (error) {
      toast.error('Failed to initialize frameworks')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Implemented':
        return 'success'
      case 'Partially Implemented':
        return 'warning'
      case 'Not Implemented':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Control Library</Typography>
        <Button variant="outlined" onClick={handleInitializeFrameworks}>
          Initialize Frameworks
        </Button>
      </Box>

      {/* Coverage Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Total Controls
            </Typography>
            <Typography variant="h4">{coverage?.total_controls || 0}</Typography>
          </Paper>
        </Grid>
        {coverage?.by_status &&
          Object.entries(coverage.by_status).map(([status, data]: [string, any]) => (
            <Grid item xs={12} sm={6} md={3} key={status}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  {status}
                </Typography>
                <Typography variant="h5">{data.count}</Typography>
                <Typography variant="body2" color="primary">
                  {data.percentage?.toFixed(1)}%
                </Typography>
              </Paper>
            </Grid>
          ))}
      </Grid>

      {/* Framework Coverage */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Framework Coverage
        </Typography>
        <Grid container spacing={2}>
          {coverage?.by_framework?.map((framework: any) => (
            <Grid item xs={12} md={4} key={framework.framework}>
              <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                <Typography variant="subtitle1">{framework.framework}</Typography>
                <Typography variant="h4" color="primary">
                  {framework.coverage_percentage?.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {framework.implemented} / {framework.total_controls} controls
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Controls Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Control ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Effectiveness</TableCell>
              <TableCell>Automation</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {controls?.map((control: any) => (
              <TableRow key={control.id}>
                <TableCell>{control.control_id}</TableCell>
                <TableCell>{control.title}</TableCell>
                <TableCell>
                  <Chip label={control.control_type} size="small" variant="outlined" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={control.status}
                    size="small"
                    color={getStatusColor(control.status)}
                  />
                </TableCell>
                <TableCell>{control.owner || 'Unassigned'}</TableCell>
                <TableCell>
                  {control.effectiveness_rating ? `${control.effectiveness_rating}/5` : 'N/A'}
                </TableCell>
                <TableCell>
                  {control.automation_level !== null ? `${control.automation_level}%` : 'N/A'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}