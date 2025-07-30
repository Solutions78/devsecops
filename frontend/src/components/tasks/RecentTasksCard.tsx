import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Divider,
} from '@mui/material'
import {
  Assignment as TaskIcon,
  CheckCircle as CompleteIcon,
  Error as ErrorIcon,
  PlayArrow as RunningIcon,
  Schedule as PendingIcon,
} from '@mui/icons-material'
import { TaskResult } from '../../services/api'

interface RecentTasksCardProps {
  tasks: TaskResult[]
  isLoading: boolean
}

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

export default function RecentTasksCard({ tasks, isLoading }: RecentTasksCardProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatIntent = (intent: string) => {
    return intent
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TaskIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Recent Tasks</Typography>
        </Box>

        {isLoading ? (
          <LinearProgress />
        ) : tasks.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ py: 4 }}>
            No recent tasks
          </Typography>
        ) : (
          <List disablePadding>
            {tasks.map((task, index) => {
              const StatusIcon = statusIcons[task.status]
              const statusColor = statusColors[task.status]

              return (
                <Box key={task.id}>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <StatusIcon color={statusColor} fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" sx={{ flex: 1 }}>
                            {formatIntent(task.intent)}
                          </Typography>
                          <Chip
                            label={task.status}
                            color={statusColor}
                            size="small"
                            sx={{ fontSize: '0.6875rem', height: 20 }}
                          />
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {task.agent_name} • {formatTime(task.created_at)}
                          </Typography>
                        </Box>
                      }
                      primaryTypographyProps={{ component: 'div' }}
                      secondaryTypographyProps={{ component: 'div' }}
                    />
                  </ListItem>
                  {index < tasks.length - 1 && (
                    <Divider sx={{ my: 1 }} />
                  )}
                </Box>
              )
            })}
          </List>
        )}
      </CardContent>
    </Card>
  )
}