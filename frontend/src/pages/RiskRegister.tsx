import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material'
import { Add, FileDownload, FileUpload, Edit, Delete } from '@mui/icons-material'
import toast from 'react-hot-toast'
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts'
import {
  getRisks,
  getRiskHeatmap,
  getRiskStatistics,
  createRisk,
  updateRisk,
  deleteRisk,
  importRisksExcel,
  exportRisksExcel,
} from '../services/api'

export default function RiskRegister() {
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedRisk, setSelectedRisk] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data: risks, isLoading } = useQuery({
    queryKey: ['risks'],
    queryFn: async () => {
      const response = await getRisks()
      return response.data
    },
  })

  const { data: heatmap } = useQuery({
    queryKey: ['riskHeatmap'],
    queryFn: async () => {
      const response = await getRiskHeatmap()
      return response.data
    },
  })

  const { data: statistics } = useQuery({
    queryKey: ['riskStatistics'],
    queryFn: async () => {
      const response = await getRiskStatistics()
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: createRisk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] })
      toast.success('Risk created successfully')
      setOpenDialog(false)
    },
    onError: () => {
      toast.error('Failed to create risk')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteRisk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] })
      toast.success('Risk deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete risk')
    },
  })

  const handleExport = async () => {
    try {
      const response = await exportRisksExcel()
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `risk_register_${new Date().toISOString().split('T')[0]}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Risks exported successfully')
    } catch (error) {
      toast.error('Failed to export risks')
    }
  }

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      try {
        await importRisksExcel(file)
        queryClient.invalidateQueries({ queryKey: ['risks'] })
        toast.success('Risks imported successfully')
      } catch (error) {
        toast.error('Failed to import risks')
      }
    }
  }

  const getRiskLevelColor = (score: number) => {
    if (score >= 15) return 'error'
    if (score >= 10) return 'warning'
    if (score >= 5) return 'info'
    return 'success'
  }

  const getRiskLevel = (score: number) => {
    if (score >= 15) return 'Critical'
    if (score >= 10) return 'High'
    if (score >= 5) return 'Medium'
    return 'Low'
  }

  // Prepare heatmap data for chart
  const heatmapData = heatmap?.map((item: any) => ({
    x: item.likelihood,
    y: item.impact,
    z: item.count,
    level: item.risk_level,
  })) || []

  const HEATMAP_COLORS: any = {
    'Critical': '#d32f2f',
    'High': '#f57c00',
    'Medium': '#fbc02d',
    'Low': '#388e3c',
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Risk Register</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<FileUpload />}
            component="label"
            sx={{ mr: 1 }}
          >
            Import
            <input type="file" hidden accept=".xlsx,.xls" onChange={handleImport} />
          </Button>
          <Button
            variant="outlined"
            startIcon={<FileDownload />}
            onClick={handleExport}
            sx={{ mr: 1 }}
          >
            Export
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {
              setSelectedRisk(null)
              setOpenDialog(true)
            }}
          >
            Add Risk
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Total Risks
            </Typography>
            <Typography variant="h4">{statistics?.total_risks || 0}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Critical Risks
            </Typography>
            <Typography variant="h4" color="error">
              {statistics?.by_risk_level?.Critical || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Avg Inherent Score
            </Typography>
            <Typography variant="h4">
              {statistics?.average_inherent_score?.toFixed(1) || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Avg Residual Score
            </Typography>
            <Typography variant="h4">
              {statistics?.average_residual_score?.toFixed(1) || 0}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Risk Heatmap */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Risk Heatmap
        </Typography>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid />
            <XAxis
              type="number"
              dataKey="x"
              name="Likelihood"
              domain={[0, 6]}
              label={{ value: 'Likelihood', position: 'bottom' }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Impact"
              domain={[0, 6]}
              label={{ value: 'Impact', angle: -90, position: 'left' }}
            />
            <ZAxis type="number" dataKey="z" range={[100, 1000]} name="Count" />
            <Tooltip crosshair={{ strokeDasharray: '3 3' }} />
            <Scatter data={heatmapData}>
              {heatmapData.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={HEATMAP_COLORS[entry.level] || '#999'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </Paper>

      {/* Risks Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Risk ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Inherent Risk</TableCell>
              <TableCell>Residual Risk</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {risks?.map((risk: any) => (
              <TableRow key={risk.id}>
                <TableCell>{risk.risk_id}</TableCell>
                <TableCell>{risk.title}</TableCell>
                <TableCell>
                  <Chip label={risk.category} size="small" />
                </TableCell>
                <TableCell>
                  <Chip label={risk.status} size="small" color="info" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${risk.inherent_risk_score} - ${getRiskLevel(risk.inherent_risk_score)}`}
                    size="small"
                    color={getRiskLevelColor(risk.inherent_risk_score)}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${risk.residual_risk_score} - ${getRiskLevel(risk.residual_risk_score)}`}
                    size="small"
                    color={getRiskLevelColor(risk.residual_risk_score)}
                  />
                </TableCell>
                <TableCell>{risk.owner || 'Unassigned'}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedRisk(risk)
                      setOpenDialog(true)
                    }}
                  >
                    <Edit fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this risk?')) {
                        deleteMutation.mutate(risk.risk_id)
                      }
                    }}
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}