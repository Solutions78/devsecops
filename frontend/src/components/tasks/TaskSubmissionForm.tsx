import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Tooltip,
  Chip,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Send as SendIcon,
  ExpandMore as ExpandMoreIcon,
  SmartToy as AgentIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  Description as DocsIcon,
  Transform as RefactorIcon,
  Assessment as TestIcon,
  Compare as DifferenceIcon,
  PlayArrow as ExecuteIcon,
} from '@mui/icons-material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient, { TaskSubmission } from '../../services/api'
import DirectorySelector from '../DirectorySelector'

const agentIntents = [
  {
    intent: 'code_review',
    label: 'Code Review',
    icon: CodeIcon,
    description: 'Comprehensive code quality analysis with security vulnerability detection',
    params: {
      directory: { label: 'Project Directory', type: 'text', required: true, placeholder: '/path/to/project' },
      extensions: { label: 'File Extensions', type: 'text', required: false, placeholder: '.py,.js,.ts' },
    },
  },
  {
    intent: 'security_audit',
    label: 'Security Audit',
    icon: SecurityIcon,
    description: 'OWASP Top 10 vulnerability detection and compliance checking',
    params: {
      directory: { label: 'Project Directory', type: 'text', required: true, placeholder: '/path/to/project' },
      compliance_standards: { label: 'Standards', type: 'text', required: false, placeholder: 'owasp,nist' },
    },
  },
  {
    intent: 'test_engineer',
    label: 'Test Generation',
    icon: TestIcon,
    description: 'Generate comprehensive test suites with 90% coverage targets',
    params: {
      directory: { label: 'Project Directory', type: 'text', required: true, placeholder: '/path/to/project' },
      test_types: { label: 'Test Types', type: 'text', required: false, placeholder: 'unit,integration,api' },
    },
  },
  {
    intent: 'generate_docstrings',
    label: 'Documentation',
    icon: DocsIcon,
    description: 'Generate Google-style docstrings for all functions and classes',
    params: {
      directory: { label: 'Project Directory', type: 'text', required: true, placeholder: '/path/to/project' },
      style: { label: 'Style', type: 'select', options: ['google', 'numpy', 'sphinx'], required: false },
    },
  },
  {
    intent: 'refactor',
    label: 'Refactoring',
    icon: RefactorIcon,
    description: 'Identify code duplication and suggest architectural improvements',
    params: {
      directory: { label: 'Project Directory', type: 'text', required: true, placeholder: '/path/to/project' },
      focus_areas: { label: 'Focus Areas', type: 'text', required: false, placeholder: 'performance,maintainability' },
    },
  },
  {
    intent: 'annotate_diff',
    label: 'Diff Analysis',
    icon: DifferenceIcon,
    description: 'Analyze git diffs and explain changes with impact assessment',
    params: {
      commit_hash: { label: 'Commit Hash', type: 'text', required: false, placeholder: 'abc123def456' },
      diff: { label: 'Raw Diff', type: 'textarea', required: false, placeholder: 'Paste git diff output...' },
    },
  },
  {
    intent: 'execute',
    label: 'Code Execution',
    icon: ExecuteIcon,
    description: 'Execute code in sandboxed environment with runtime validation',
    params: {
      code: { label: 'Code', type: 'textarea', required: true, placeholder: 'print("Hello, World!")' },
      timeout: { label: 'Timeout (seconds)', type: 'number', required: false, placeholder: '30' },
    },
  },
]

export default function TaskSubmissionForm() {
  const [selectedIntent, setSelectedIntent] = useState('')
  const [params, setParams] = useState<Record<string, any>>({})
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const submitTaskMutation = useMutation({
    mutationFn: (task: TaskSubmission) => apiClient.submitTask(task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      setSelectedIntent('')
      setParams({})
      setError('')
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Failed to submit task')
    },
  })

  const selectedAgentConfig = agentIntents.find(a => a.intent === selectedIntent)

  const handleParamChange = (paramKey: string, value: any) => {
    setParams(prev => ({
      ...prev,
      [paramKey]: value,
    }))
  }


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!selectedIntent) {
      setError('Please select an agent intent')
      return
    }

    // Validate required parameters
    if (selectedAgentConfig) {
      for (const [key, config] of Object.entries(selectedAgentConfig.params)) {
        if (config.required && !params[key]) {
          setError(`${config.label} is required`)
          return
        }
      }
    }

    await submitTaskMutation.mutateAsync({
      intent: selectedIntent,
      params,
    })
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AgentIcon sx={{ mr: 1 }} color="primary" />
          <Typography variant="h6">Submit New Task</Typography>
        </Box>

        <form onSubmit={handleSubmit}>
          <Tooltip title="Select which AI agent should handle this task" arrow placement="top">
            <TextField
              select
              fullWidth
              label="Agent Intent"
              value={selectedIntent}
              onChange={(e) => setSelectedIntent(e.target.value)}
              sx={{ mb: 3 }}
              disabled={submitTaskMutation.isPending}
            >
              {agentIntents.map((agent) => {
                const IconComponent = agent.icon
                return (
                  <MenuItem key={agent.intent} value={agent.intent}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconComponent fontSize="small" />
                      <Box>
                        <Typography variant="body2">{agent.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {agent.description}
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                )
              })}
            </TextField>
          </Tooltip>

          {selectedAgentConfig && (
            <Accordion sx={{ mb: 3 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">Task Parameters</Typography>
                <Chip
                  label={`${Object.keys(selectedAgentConfig.params).length} parameters`}
                  size="small"
                  sx={{ ml: 2 }}
                />
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {Object.entries(selectedAgentConfig.params).map(([key, config]) => (
                    <Grid item xs={12} sm={6} key={key}>
                      <Tooltip title={`Configure ${config.label.toLowerCase()} for the ${selectedAgentConfig.label} agent`} arrow>
                        {config.type === 'select' ? (
                          <TextField
                            select
                            fullWidth
                            label={config.label}
                            value={params[key] || ''}
                            onChange={(e) => handleParamChange(key, e.target.value)}
                            required={config.required}
                            disabled={submitTaskMutation.isPending}
                          >
                            {config.options?.map((option: string) => (
                              <MenuItem key={option} value={option}>
                                {option}
                              </MenuItem>
                            ))}
                          </TextField>
                        ) : key === 'directory' ? (
                          <DirectorySelector
                            value={params[key] || ''}
                            onChange={(path) => handleParamChange(key, path)}
                            label={config.label}
                            placeholder={config.placeholder}
                            required={config.required}
                            disabled={submitTaskMutation.isPending}
                          />
                        ) : (
                          <TextField
                            fullWidth
                            label={config.label}
                            type={config.type === 'number' ? 'number' : 'text'}
                            multiline={config.type === 'textarea'}
                            rows={config.type === 'textarea' ? 4 : 1}
                            value={params[key] || ''}
                            onChange={(e) => handleParamChange(key, e.target.value)}
                            placeholder={config.placeholder}
                            required={config.required}
                            disabled={submitTaskMutation.isPending}
                          />
                        )}
                      </Tooltip>
                    </Grid>
                  ))}
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {submitTaskMutation.isSuccess && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Task submitted successfully! Check the tasks page for progress.
            </Alert>
          )}

          <Tooltip title="Submit task to the selected AI agent for processing" arrow>
            <span>
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={submitTaskMutation.isPending ? <CircularProgress size={20} /> : <SendIcon />}
                disabled={!selectedIntent || submitTaskMutation.isPending}
                fullWidth
              >
                {submitTaskMutation.isPending ? 'Submitting Task...' : 'Submit Task'}
              </Button>
            </span>
          </Tooltip>
        </form>
      </CardContent>
    </Card>
  )
}