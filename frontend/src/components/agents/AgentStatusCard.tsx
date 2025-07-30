import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  CircularProgress,
  Tooltip,
} from '@mui/material'
import {
  CheckCircle as CompleteIcon,
  Error as ErrorIcon,
  PlayArrow as RunningIcon,
  Help as UnknownIcon,
} from '@mui/icons-material'
import { AgentStatus } from '../../services/api'

// New modal for task submission / status
import AgentTaskDialog from './AgentTaskDialog'

import { useState } from 'react'

interface AgentStatusCardProps {
  agent: AgentStatus
}

const statusConfig = {
  idle: {
    color: 'success' as const,
    icon: CompleteIcon,
    label: 'Online',
  },
  running: {
    color: 'warning' as const,
    icon: RunningIcon,
    label: 'Running',
  },
  complete: {
    color: 'success' as const,
    icon: CompleteIcon,
    label: 'Complete',
  },
  error: {
    color: 'error' as const,
    icon: ErrorIcon,
    label: 'Error',
  },
  offline: {
    color: 'error' as const,
    icon: ErrorIcon,
    label: 'Offline',
  },
  unknown: {
    color: 'inherit' as const,
    icon: UnknownIcon,
    label: 'Unknown',
  },
}

// Default config for unrecognized statuses
const defaultConfig = {
  color: 'inherit' as const,
  icon: UnknownIcon,
  label: 'Unknown',
}

export default function AgentStatusCard({ agent }: AgentStatusCardProps) {
  console.log('AgentStatusCard rendering with status:', agent.status, 'config:', statusConfig[agent.status as keyof typeof statusConfig]?.label)
  const config = statusConfig[agent.status as keyof typeof statusConfig] || defaultConfig
  const StatusIcon = config.icon

  // Local state to control the modal visibility
  const [open, setOpen] = useState(false)

  const formatAgentName = (name: string) => {
    return name
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const timeAgo = (timestamp: string) => {
    const now = new Date()
    const updated = new Date(timestamp)
    const diff = now.getTime() - updated.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return 'Just now'
    if (minutes === 1) return '1 minute ago'
    if (minutes < 60) return `${minutes} minutes ago`
    
    const hours = Math.floor(minutes / 60)
    if (hours === 1) return '1 hour ago'
    if (hours < 24) return `${hours} hours ago`
    
    const days = Math.floor(hours / 24)
    return `${days} days ago`
  }

  return (
    <>
    <Card 
      onClick={() => setOpen(true)}
      sx={{ 
        height: '100%',
        cursor: 'pointer',
        border: agent.status === 'error' ? '1px solid' : undefined,
        borderColor: agent.status === 'error' ? 'error.main' : undefined,
        transition: 'transform 0.15s ease-in-out',
        '&:hover': {
          transform: 'scale(1.02)',
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ position: 'relative', mr: 2 }}>
            <StatusIcon color={config.color} />
            {agent.status === 'running' && (
              <CircularProgress
                size={24}
                sx={{
                  position: 'absolute',
                  top: -2,
                  left: -2,
                  color: 'warning.main',
                }}
              />
            )}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontSize: '1rem' }}>
              {formatAgentName(agent.name)}
            </Typography>
            <Chip
              label={config.label}
              color={config.color}
              size="small"
              sx={{ mt: 0.5 }}
            />
          </Box>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Tasks Completed: {agent.tasks_completed}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Last Updated: {timeAgo(agent.last_updated)}
          </Typography>
        </Box>

        {agent.current_task && (
          <Tooltip title={agent.current_task} arrow>
            <Typography
              variant="body2"
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                backgroundColor: 'action.hover',
                padding: 1,
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
              }}
            >
              {agent.current_task}
            </Typography>
          </Tooltip>
        )}
      </CardContent>
    </Card>
    <AgentTaskDialog open={open} onClose={() => setOpen(false)} agent={agent} />
    </>
  )
}
