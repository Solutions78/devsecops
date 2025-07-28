import { useEffect } from 'react'
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material'
import {
  SmartToy as AgentsIcon,
  Assignment as TasksIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material'
import { useAgents, useTasks } from '../hooks/useWebSocket'
import { useWebSocket } from '../hooks/useWebSocket'
import AgentStatusCard from '../components/agents/AgentStatusCard'
import RecentTasksCard from '../components/tasks/RecentTasksCard'
import SystemHealthCard from '../components/monitoring/SystemHealthCard'

export default function Dashboard() {
  const { connect } = useWebSocket()
  const { data: agents, isLoading: agentsLoading } = useAgents()
  const { data: tasks, isLoading: tasksLoading } = useTasks()

  useEffect(() => {
    connect()
  }, [connect])

  const agentStats = {
    total: agents?.length || 0,
    running: agents?.filter(a => a.status === 'running').length || 0,
    idle: agents?.filter(a => a.status === 'idle').length || 0,
    error: agents?.filter(a => a.status === 'error').length || 0,
  }

  const taskStats = {
    total: tasks?.length || 0,
    pending: tasks?.filter(t => t.status === 'pending').length || 0,
    running: tasks?.filter(t => t.status === 'running').length || 0,
    completed: tasks?.filter(t => t.status === 'completed').length || 0,
    failed: tasks?.filter(t => t.status === 'failed').length || 0,
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        DevSecOps Orchestrator Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Monitor your AI agents, track tasks, and manage secure operations
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Overview Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AgentsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Agents</Typography>
              </Box>
              <Typography variant="h4" gutterBottom>
                {agentStats.total}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`${agentStats.running} Running`}
                  color="success"
                  size="small"
                />
                <Chip
                  label={`${agentStats.idle} Idle`}
                  color="info"
                  size="small"
                />
                {agentStats.error > 0 && (
                  <Chip
                    label={`${agentStats.error} Error`}
                    color="error"
                    size="small"
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TasksIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Tasks</Typography>
              </Box>
              <Typography variant="h4" gutterBottom>
                {taskStats.total}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`${taskStats.running} Running`}
                  color="warning"
                  size="small"
                />
                <Chip
                  label={`${taskStats.completed} Done`}
                  color="success"
                  size="small"
                />
                {taskStats.failed > 0 && (
                  <Chip
                    label={`${taskStats.failed} Failed`}
                    color="error"
                    size="small"
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Security</Typography>
              </Box>
              <Typography variant="body2" gutterBottom>
                Azure Key Vault
              </Typography>
              <Chip
                label="Active"
                color="success"
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PerformanceIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Performance</Typography>
              </Box>
              <Typography variant="body2" gutterBottom>
                System Load
              </Typography>
              <LinearProgress
                variant="determinate"
                value={25}
                sx={{ mt: 1 }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                25% CPU Usage
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Status Grid */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              {agentsLoading ? (
                <LinearProgress />
              ) : (
                <Grid container spacing={2}>
                  {agents?.map((agent) => (
                    <Grid item xs={12} sm={6} md={4} key={agent.name}>
                      <AgentStatusCard agent={agent} />
                    </Grid>
                  ))}
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Tasks */}
        <Grid item xs={12} lg={4}>
          <RecentTasksCard tasks={tasks?.slice(0, 5) || []} isLoading={tasksLoading} />
        </Grid>

        {/* System Health */}
        <Grid item xs={12}>
          <SystemHealthCard />
        </Grid>
      </Grid>
    </Box>
  )
}