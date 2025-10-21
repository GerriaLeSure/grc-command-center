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
import { CloudUpload } from '@mui/icons-material'
import { getEvidence, getEvidenceSummary } from '../services/api'

export default function Evidence() {
  const { data: evidence } = useQuery({
    queryKey: ['evidence'],
    queryFn: async () => {
      const response = await getEvidence()
      return response.data
    },
  })

  const { data: summary } = useQuery({
    queryKey: ['evidenceSummary'],
    queryFn: async () => {
      const response = await getEvidenceSummary()
      return response.data
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Verified':
        return 'success'
      case 'Collected':
        return 'info'
      case 'Pending':
        return 'warning'
      case 'Expired':
      case 'Rejected':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Evidence Collection</Typography>
        <Button variant="contained" startIcon={<CloudUpload />}>
          Upload Evidence
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Total Evidence
            </Typography>
            <Typography variant="h4">{summary?.total_evidence || 0}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Verified
            </Typography>
            <Typography variant="h4" color="success.main">
              {summary?.by_status?.Verified || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Expiring Soon
            </Typography>
            <Typography variant="h4" color="warning.main">
              {summary?.expiring_within_30_days || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Automated Collections
            </Typography>
            <Typography variant="h4" color="primary">
              Active
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Evidence by Framework */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Evidence by Framework
        </Typography>
        <Grid container spacing={2}>
          {summary?.by_framework &&
            Object.entries(summary.by_framework).map(([framework, count]: [string, any]) => (
              <Grid item xs={12} sm={6} md={3} key={framework}>
                <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Typography variant="subtitle2">{framework}</Typography>
                  <Typography variant="h5" color="primary">
                    {count}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    items collected
                  </Typography>
                </Box>
              </Grid>
            ))}
        </Grid>
      </Paper>

      {/* Evidence Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Evidence ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Framework</TableCell>
              <TableCell>Control ID</TableCell>
              <TableCell>Collection Date</TableCell>
              <TableCell>File Name</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {evidence?.map((item: any) => (
              <TableRow key={item.id}>
                <TableCell>{item.evidence_id}</TableCell>
                <TableCell>{item.title}</TableCell>
                <TableCell>
                  <Chip label={item.evidence_type} size="small" variant="outlined" />
                </TableCell>
                <TableCell>
                  <Chip label={item.status} size="small" color={getStatusColor(item.status)} />
                </TableCell>
                <TableCell>{item.framework || 'N/A'}</TableCell>
                <TableCell>{item.control_id || 'N/A'}</TableCell>
                <TableCell>
                  {item.collection_date
                    ? new Date(item.collection_date).toLocaleDateString()
                    : 'N/A'}
                </TableCell>
                <TableCell>{item.file_name || 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}