import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Switch,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Snackbar,
  IconButton,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  BugReport as TestIcon,
  Description as DocsIcon,
  Architecture as RefactorIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient, { AgentConfiguration } from '../services/api'

const categoryIcons = {
  security: SecurityIcon,
  testing: TestIcon,
  documentation: DocsIcon,
  development: CodeIcon,
  refactoring: RefactorIcon,
  orchestration: RefactorIcon,
} as const

const categoryColors = {
  security: 'error',
  testing: 'success',
  documentation: 'info',
  development: 'primary',
  refactoring: 'warning',
  orchestration: 'secondary',
} as const

// Master list of all available tools across all agent types
const getAllAvailableTools = () => [
  // Analysis Tools
  'file_analysis',
  'code_analyzer',
  'dependency_analyzer',
  'complexity_analyzer',
  'pattern_detector',

  // Security Tools  
  'security_scan',
  'vulnerability_scanner',
  'owasp_checker',
  'secret_detector',
  'compliance_checker',

  // Testing Tools
  'test_generator',
  'coverage_analyzer',
  'mock_creator',
  'integration_tester',

  // Documentation Tools
  'docstring_formatter',
  'type_analyzer',
  'api_documenter',
  
  // Development Tools
  'dependency_check',
  'dependency_mapper',
  'refactoring_analyzer',
  'code_formatter',

  // Execution Tools
  'sandbox_executor',
  'runtime_validator',
  'output_analyzer',
  'performance_profiler',

  // Git/Version Control Tools
  'diff_parser',
  'impact_analyzer',
  'change_summarizer',
  'commit_analyzer',

  // Review/Summary Tools
  'change_analyzer',
  'summary_formatter',
  'reviewer_helper',
  'quality_metrics',

  // Orchestration Tools
  'workflow_planner',
  'task_coordinator',
  'dependency_manager',
  'result_aggregator',
]

interface AgentConfigDialogProps {
  open: boolean
  onClose: () => void
  agentConfig: AgentConfiguration | null
  onSave: (config: AgentConfiguration) => void
  isAdministrator: boolean
}

function AgentConfigDialog({ open, onClose, agentConfig, onSave, isAdministrator }: AgentConfigDialogProps) {
  const [config, setConfig] = useState<AgentConfiguration | null>(null)

  useEffect(() => {
    if (agentConfig) {
      setConfig({ ...agentConfig })
    }
  }, [agentConfig])

  const handleSave = () => {
    if (config) {
      onSave(config)
    }
  }

  const updateConfig = (field: string, value: any) => {
    if (!config) return
    
    if (field.includes('.')) {
      const [parent, child] = field.split('.')
      setConfig({
        ...config,
        [parent]: {
          ...(config as any)[parent],
          [child]: value,
        },
      })
    } else {
      setConfig({
        ...config,
        [field]: value,
      })
    }
  }

  const updateTool = (index: number, field: string, value: any) => {
    if (!config) return
    
    const updatedTools = [...config.available_tools]
    updatedTools[index] = {
      ...updatedTools[index],
      [field]: value,
    }
    
    setConfig({
      ...config,
      available_tools: updatedTools,
    })
  }

  const handleToolChange = (toolName: string, enabled: boolean) => {
    if (!config) return

    const existingToolIndex = config.available_tools.findIndex(t => t.name === toolName)
    
    if (enabled) {
      // Add or enable the tool
      if (existingToolIndex >= 0) {
        // Tool exists, just enable it
        updateTool(existingToolIndex, 'enabled', true)
      } else {
        // Add new tool
        const newTool = {
          name: toolName,
          enabled: true,
          parameters: {}
        }
        setConfig({
          ...config,
          available_tools: [...config.available_tools, newTool]
        })
      }
    } else {
      // Disable or remove the tool
      if (existingToolIndex >= 0) {
        updateTool(existingToolIndex, 'enabled', false)
      }
    }
  }

  if (!config) return null

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon />
          Configure {config.display_name}
          <IconButton
            edge="end"
            color="inherit"
            onClick={onClose}
            sx={{ ml: 'auto' }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ mt: 1 }}>
        <Grid container spacing={3}>
          {/* Basic Configuration */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Basic Configuration
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Display Name"
                  value={config.display_name}
                  onChange={(e) => updateConfig('display_name', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={config.category}
                    label="Category"
                    onChange={(e) => updateConfig('category', e.target.value)}
                  >
                    <MenuItem value="security">Security</MenuItem>
                    <MenuItem value="testing">Testing</MenuItem>
                    <MenuItem value="documentation">Documentation</MenuItem>
                    <MenuItem value="development">Development</MenuItem>
                    <MenuItem value="refactoring">Refactoring</MenuItem>
                    <MenuItem value="orchestration">Orchestration</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Description"
                  value={config.description}
                  onChange={(e) => updateConfig('description', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.enabled}
                      onChange={(e) => updateConfig('enabled', e.target.checked)}
                    />
                  }
                  label="Enabled"
                />
              </Grid>
            </Grid>
          </Grid>

          {/* Prompt Configuration */}
          <Grid item xs={12}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Prompt Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="System Prompt"
                      value={config.prompt_config.system_prompt}
                      onChange={(e) => updateConfig('prompt_config.system_prompt', e.target.value)}
                      helperText="The system message that defines the agent's role and behavior"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="User Prompt Template"
                      value={config.prompt_config.user_prompt_template}
                      onChange={(e) => updateConfig('prompt_config.user_prompt_template', e.target.value)}
                      helperText="Template for user messages. Use {content} as placeholder for input"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography gutterBottom>
                      Temperature: {config.prompt_config.temperature}
                    </Typography>
                    <Slider
                      value={config.prompt_config.temperature}
                      onChange={(_, value) => updateConfig('prompt_config.temperature', value)}
                      min={0}
                      max={2}
                      step={0.1}
                      marks={[
                        { value: 0, label: '0 (Focused)' },
                        { value: 1, label: '1 (Balanced)' },
                        { value: 2, label: '2 (Creative)' },
                      ]}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Max Tokens"
                      value={config.prompt_config.max_tokens || ''}
                      onChange={(e) => updateConfig('prompt_config.max_tokens', 
                        e.target.value ? parseInt(e.target.value) : null)}
                      helperText="Maximum tokens in response (empty = no limit)"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Tools Configuration */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Tools Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {getAllAvailableTools().map((toolName) => {
                    const existingToolIndex = config.available_tools.findIndex(t => t.name === toolName)
                    const isEnabled = existingToolIndex >= 0 ? config.available_tools[existingToolIndex].enabled : false
                    const toolExists = existingToolIndex >= 0

                    return (
                      <Grid item xs={12} sm={6} key={toolName}>
                        <Card variant="outlined" sx={{ 
                          opacity: toolExists ? 1 : 0.7,
                          border: toolExists && isEnabled ? '2px solid' : undefined,
                          borderColor: toolExists && isEnabled ? 'primary.main' : undefined 
                        }}>
                          <CardContent sx={{ py: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={isEnabled}
                                    onChange={(e) => handleToolChange(toolName, e.target.checked)}
                                    disabled={!isAdministrator}
                                  />
                                }
                                label={
                                  <Box>
                                    <Typography variant="body2" sx={{ fontWeight: toolExists ? 'medium' : 'normal' }}>
                                      {toolName}
                                    </Typography>
                                    {!toolExists && (
                                      <Typography variant="caption" color="text.secondary">
                                        Available to add
                                      </Typography>
                                    )}
                                  </Box>
                                }
                                sx={{ flex: 1 }}
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    )
                  })}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Runtime Configuration */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Runtime Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Max Concurrent Tasks"
                      value={config.max_concurrent_tasks}
                      onChange={(e) => updateConfig('max_concurrent_tasks', parseInt(e.target.value))}
                      inputProps={{ min: 1 }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Timeout (seconds)"
                      value={config.timeout_seconds}
                      onChange={(e) => updateConfig('timeout_seconds', parseInt(e.target.value))}
                      inputProps={{ min: 30 }}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          startIcon={<SaveIcon />}
        >
          Save Configuration
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default function AgentConfig() {
  const { isAdministrator } = useAuth()
  const [selectedAgent, setSelectedAgent] = useState<AgentConfiguration | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' })
  
  const queryClient = useQueryClient()

  // Fetch agent configurations
  const { data: configurations = [], isLoading, error } = useQuery({
    queryKey: ['agent-configurations'],
    queryFn: () => apiClient.getAgentConfigurations(),
    retry: false,
  })

  // Initialize default configurations
  const initializeMutation = useMutation({
    mutationFn: (force: boolean = false) => apiClient.initializeDefaultConfigurations(force),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-configurations'] })
      setSnackbar({ open: true, message: 'Default configurations initialized successfully', severity: 'success' })
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: `Failed to initialize configurations: ${error.message}`, severity: 'error' })
    },
  })

  // Update configuration
  const updateMutation = useMutation({
    mutationFn: ({ agentId, config }: { agentId: string; config: Partial<AgentConfiguration> }) =>
      apiClient.updateAgentConfiguration(agentId, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-configurations'] })
      setSnackbar({ open: true, message: 'Configuration updated successfully', severity: 'success' })
      setDialogOpen(false)
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: `Failed to update configuration: ${error.message}`, severity: 'error' })
    },
  })

  const handleConfigureAgent = (config: AgentConfiguration) => {
    setSelectedAgent(config)
    setDialogOpen(true)
  }

  const handleSaveConfiguration = (config: AgentConfiguration) => {
    updateMutation.mutate({ agentId: config.agent_id, config })
  }

  const handleInitialize = () => {
    initializeMutation.mutate(false)
  }

  const handleForceRefresh = () => {
    initializeMutation.mutate(true)
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading agent configurations...</Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Agent Configuration
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure AI agent prompts, tools, and runtime parameters
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => queryClient.invalidateQueries({ queryKey: ['agent-configurations'] })}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            color="warning"
            startIcon={<RefreshIcon />}
            onClick={handleForceRefresh}
            disabled={initializeMutation.isPending}
          >
            Force Refresh Configs
          </Button>
          {configurations.length === 0 && (
            <Button
              variant="contained"
              onClick={handleInitialize}
              disabled={initializeMutation.isPending}
            >
              Initialize Default Configs
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load agent configurations. {configurations.length === 0 && (
            <Button size="small" onClick={handleInitialize} sx={{ ml: 1 }}>
              Initialize Default Configurations
            </Button>
          )}
        </Alert>
      )}

      <Grid container spacing={3}>
        {configurations.map((config) => {
          const CategoryIcon = categoryIcons[config.category as keyof typeof categoryIcons] || CodeIcon
          const categoryColor = categoryColors[config.category as keyof typeof categoryColors] || 'primary'

          return (
            <Grid item xs={12} md={6} lg={4} key={config.agent_id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CategoryIcon color={categoryColor} sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      {config.display_name}
                    </Typography>
                    <Chip
                      size="small"
                      label={config.enabled ? 'Enabled' : 'Disabled'}
                      color={config.enabled ? 'success' : 'default'}
                      sx={{ ml: 'auto' }}
                    />
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {config.description}
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Chip
                      size="small"
                      label={config.category}
                      color={categoryColor}
                      variant="outlined"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      size="small"
                      label={`v${config.version}`}
                      variant="outlined"
                    />
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Temperature
                    </Typography>
                    <Typography variant="caption">
                      {config.prompt_config.temperature}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Tools
                    </Typography>
                    <Typography variant="caption">
                      {config.available_tools.filter(t => t.enabled).length}/{config.available_tools.length}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">
                      Max Tasks
                    </Typography>
                    <Typography variant="caption">
                      {config.max_concurrent_tasks}
                    </Typography>
                  </Box>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    startIcon={<SettingsIcon />}
                    onClick={() => handleConfigureAgent(config)}
                    disabled={updateMutation.isPending}
                  >
                    Configure
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      <AgentConfigDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        agentConfig={selectedAgent}
        onSave={handleSaveConfiguration}
        isAdministrator={isAdministrator}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}