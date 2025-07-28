import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
} from '@mui/material'
import {
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  Cloud as CloudIcon,
} from '@mui/icons-material'

export default function SystemHealthCard() {
  // Mock data - in real app, this would come from API
  const healthMetrics = {
    cpu: { usage: 25, status: 'healthy' },
    memory: { usage: 68, status: 'healthy' },
    storage: { usage: 45, status: 'healthy' },
    network: { latency: 12, status: 'healthy' },
    azure: { connection: 'active', status: 'healthy' },
  }

  const getProgressColor = (usage: number) => {
    if (usage < 50) return 'success'
    if (usage < 80) return 'warning'
    return 'error'
  }

  const getStatusChip = (status: string) => {
    const color = status === 'healthy' ? 'success' : 'error'
    return <Chip label={status} color={color} size="small" />
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Health
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <MemoryIcon sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="body2">CPU Usage</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={healthMetrics.cpu.usage}
                color={getProgressColor(healthMetrics.cpu.usage)}
                sx={{ mb: 1 }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                  {healthMetrics.cpu.usage}%
                </Typography>
                {getStatusChip(healthMetrics.cpu.status)}
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <MemoryIcon sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="body2">Memory</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={healthMetrics.memory.usage}
                color={getProgressColor(healthMetrics.memory.usage)}
                sx={{ mb: 1 }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                  {healthMetrics.memory.usage}%
                </Typography>
                {getStatusChip(healthMetrics.memory.status)}
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <StorageIcon sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="body2">Storage</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={healthMetrics.storage.usage}
                color={getProgressColor(healthMetrics.storage.usage)}
                sx={{ mb: 1 }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                  {healthMetrics.storage.usage}%
                </Typography>
                {getStatusChip(healthMetrics.storage.status)}
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CloudIcon sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="body2">Azure Connection</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <NetworkIcon fontSize="small" />
                <Typography variant="caption" color="text.secondary">
                  {healthMetrics.network.latency}ms latency
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="success.main">
                  Active
                </Typography>
                {getStatusChip(healthMetrics.azure.status)}
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}