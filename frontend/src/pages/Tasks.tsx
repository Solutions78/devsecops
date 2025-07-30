import { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Collapse,
  Divider,
} from '@mui/material'
import {
  CheckCircle as CompleteIcon,
  Error as ErrorIcon,
  PlayArrow as RunningIcon,
  Schedule as PendingIcon,
  ExpandMore as ExpandMoreIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useTasks } from '../hooks/useWebSocket'
import apiClient, { TaskResult } from '../services/api'
import TaskSubmissionForm from '../components/tasks/TaskSubmissionForm'

const statusIcons = {
  pending: PendingIcon,
  running: RunningIcon,
  completed: CompleteIcon,
  failed: ErrorIcon,
}

const statusColors = {
  pending: 'info' as const,
  running: 'warning' as const,
  completed: 'success' as const,
  failed: 'error' as const,
}

export default function Tasks() {
  const [expandedTask, setExpandedTask] = useState<string | null>(null)
  const { data: tasks, isLoading, refetch } = useTasks()
  const queryClient = useQueryClient()

  const cancelTaskMutation = useMutation({
    mutationFn: (taskId: string) => apiClient.cancelTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const handleExpandTask = (taskId: string) => {
    setExpandedTask(expandedTask === taskId ? null : taskId)
  }

  const handleCancelTask = async (taskId: string) => {
    await cancelTaskMutation.mutateAsync(taskId)
  }

  const formatIntent = (intent: string) => {
    return intent
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Tasks
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Submit tasks and monitor execution across AI agents
          </Typography>
        </Box>
        <Tooltip title="Refresh task list">
          <IconButton onClick={() => refetch()} disabled={isLoading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={4}>
          <TaskSubmissionForm />
        </Grid>

        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Queue
              </Typography>
              {isLoading ? (
                <LinearProgress />
              ) : !tasks || tasks.length === 0 ? (
                <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ py: 4 }}>
                  No tasks found. Submit a task to get started!
                </Typography>
              ) : (
                <List disablePadding>
                  {tasks.map((task: TaskResult, index: number) => {
                    const StatusIcon = statusIcons[task.status]
                    const statusColor = statusColors[task.status]
                    const isExpanded = expandedTask === task.id

                    return (
                      <Box key={task.id}>
                        <ListItem
                          disablePadding
                          sx={{
                            p: 2,
                            border: task.status === 'failed' ? 1 : 0,
                            borderColor: 'error.main',
                            borderRadius: 1,
                            mb: 1,
                          }}
                        >
                          <ListItemIcon>
                            <StatusIcon color={statusColor} />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                <Typography variant="subtitle1">
                                  {formatIntent(task.intent)}
                                </Typography>
                                <Chip
                                  label={task.status}
                                  color={statusColor}
                                  size="small"
                                />
                                <Chip
                                  label={task.agent_name}
                                  variant="outlined"
                                  size="small"
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  Created: {formatTime(task.created_at)}
                                </Typography>
                                {task.updated_at !== task.created_at && (
                                  <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                                    Updated: {formatTime(task.updated_at)}
                                  </Typography>
                                )}
                              </Box>
                            }
                            primaryTypographyProps={{ component: 'div' }}
                            secondaryTypographyProps={{ component: 'div' }}
                          />
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {(task.status === 'pending' || task.status === 'running') && (
                              <Tooltip title="Cancel task">
                                <IconButton
                                  size="small"
                                  onClick={() => handleCancelTask(task.id)}
                                  disabled={cancelTaskMutation.isPending}
                                >
                                  <CancelIcon />
                                </IconButton>
                              </Tooltip>
                            )}
                            <Tooltip title={isExpanded ? 'Collapse details' : 'Expand details'}>
                              <IconButton
                                size="small"
                                onClick={() => handleExpandTask(task.id)}
                                sx={{
                                  transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                                  transition: 'transform 0.2s',
                                }}
                              >
                                <ExpandMoreIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </ListItem>

                        <Collapse in={isExpanded}>
                          <Box sx={{ p: 2, backgroundColor: 'action.hover', borderRadius: 1, mx: 2, mb: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Task Details
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              <strong>ID:</strong> {task.id}
                            </Typography>
                            {task.result && (
                              <Box sx={{ mb: 1 }}>
                                <Typography variant="body2" gutterBottom>
                                  <strong>Result:</strong>
                                </Typography>
                                <Box
                                  sx={{
                                    p: 1,
                                    backgroundColor: 'background.paper',
                                    borderRadius: 1,
                                    fontFamily: 'monospace',
                                    fontSize: '0.875rem',
                                    maxHeight: 200,
                                    overflow: 'auto',
                                  }}
                                >
                                  {typeof task.result === 'string'
                                    ? task.result
                                    : JSON.stringify(task.result, null, 2)}
                                </Box>
                              </Box>
                            )}
                            {task.error && (
                              <Box sx={{ mb: 1 }}>
                                <Typography variant="body2" gutterBottom color="error">
                                  <strong>Error:</strong>
                                </Typography>
                                <Box
                                  sx={{
                                    p: 1,
                                    backgroundColor: 'error.dark',
                                    color: 'error.contrastText',
                                    borderRadius: 1,
                                    fontFamily: 'monospace',
                                    fontSize: '0.875rem',
                                  }}
                                >
                                  {task.error}
                                </Box>
                              </Box>
                            )}
                          </Box>
                        </Collapse>

                        {index < tasks.length - 1 && <Divider />}
                      </Box>
                    )
                  })}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}