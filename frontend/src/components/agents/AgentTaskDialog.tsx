import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Typography,
  Alert,
  CircularProgress,
  Box,
} from '@mui/material'

import apiClient, { AgentStatus } from '../../services/api'

interface AgentTaskDialogProps {
  open: boolean
  onClose: () => void
  agent: AgentStatus
}

// Allowed task intents that can be submitted via the UI.  
// This list MUST stay in sync with the backend `validate_intent` implementation.
const allowedIntents: string[] = [
  'code_review',
  'test_engineer',
  'security_audit',
  'generate_docstrings',
  'refactor',
  'annotate_diff',
  'pr_summary',
  'execute',
  'orchestrate',
]

export default function AgentTaskDialog({ open, onClose, agent }: AgentTaskDialogProps) {
  const isIdle = agent.status === 'idle'

  // --- Form state (only used when the agent is idle) -----------------------
  const [intent, setIntent] = useState<string>('code_review')
  const [params, setParams] = useState<string>('{}')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    setError(null)
    let parsedParams: Record<string, any> = {}

    try {
      parsedParams = params.trim() ? JSON.parse(params) : {}
    } catch (err: any) {
      setError('Parameters must be valid JSON')
      return
    }

    setIsSubmitting(true)
    try {
      await apiClient.submitTask({ intent, params: parsedParams })
      onClose()
    } catch (err: any) {
      // Attempt to extract error message from axios response structure
      const msg = err?.response?.data?.detail || err.message || 'Failed to submit task'
      setError(msg)
    } finally {
      setIsSubmitting(false)
    }
  }

  // ------------------------------------------------------------------------

  const renderIdleContent = () => (
    <>
      <Typography sx={{ mb: 2 }}>
        Submit a new task to the <strong>{agent.name}</strong> agent.
      </Typography>
      <TextField
        select
        label="Intent"
        fullWidth
        margin="dense"
        value={intent}
        onChange={(e) => setIntent(e.target.value)}
      >
        {allowedIntents.map((opt) => (
          <MenuItem key={opt} value={opt}>
            {opt}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label="Parameters (JSON)"
        fullWidth
        margin="dense"
        multiline
        minRows={4}
        value={params}
        onChange={(e) => setParams(e.target.value)}
        placeholder='{"directory": "/path/to/project"}'
      />
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </>
  )

  const renderBusyContent = () => (
    <Box>
      <Typography variant="body2" sx={{ mb: 1 }}>
        <strong>Status:</strong> {agent.status}
      </Typography>
      {agent.current_task && (
        <Typography variant="body2" sx={{ mb: 1 }}>
          <strong>Current Task:</strong> {agent.current_task}
        </Typography>
      )}
      <Typography variant="body2" sx={{ mb: 1 }}>
        <strong>Tasks Completed:</strong> {agent.tasks_completed}
      </Typography>
      <Typography variant="body2" sx={{ mb: 1 }}>
        <strong>Last Updated:</strong> {agent.last_updated}
      </Typography>
    </Box>
  )

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {isIdle ? 'Submit Task' : 'Agent Status'}
      </DialogTitle>
      <DialogContent dividers>
        {isIdle ? renderIdleContent() : renderBusyContent()}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>Close</Button>
        {isIdle && (
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}
