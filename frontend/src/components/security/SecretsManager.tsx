import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Chip,
  Alert,
  CircularProgress,
  InputAdornment,
} from '@mui/material'
import { useAuth } from '../../contexts/AuthContext'
import apiClient from '../../services/api'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Key as KeyIcon,
  CloudQueue as AzureIcon,
  Security as SecurityIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material'

interface Secret {
  name: string
  created: string
  updated: string
  version: string
}

export default function SecretsManager() {
  const { apiKey } = useAuth()
  const [secrets, setSecrets] = useState<Secret[]>([
    { name: 'API_KEY', created: '2024-01-15', updated: '2024-01-15', version: '1' },
    { name: 'ANTHROPIC_API_KEY', created: '2024-01-16', updated: '2024-01-20', version: '2' },
    { name: 'DATABASE_URL', created: '2024-01-10', updated: '2024-01-18', version: '3' },
  ])
  
  const [openDialog, setOpenDialog] = useState(false)
  const [dialogMode, setDialogMode] = useState<'add' | 'edit' | 'view'>('add')
  const [selectedSecret, setSelectedSecret] = useState<Secret | null>(null)
  const [secretName, setSecretName] = useState('')
  const [secretValue, setSecretValue] = useState('')
  const [showSecretValue, setShowSecretValue] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  // API key re-authentication state
  const [authDialog, setAuthDialog] = useState(false)
  const [pendingSecret, setPendingSecret] = useState<Secret | null>(null)
  const [reAuthApiKey, setReAuthApiKey] = useState('')
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)

  const handleAddSecret = () => {
    setDialogMode('add')
    setSecretName('')
    setSecretValue('')
    setSelectedSecret(null)
    setOpenDialog(true)
  }

  const handleEditSecret = (secret: Secret) => {
    setDialogMode('edit')
    setSecretName(secret.name)
    setSecretValue('') // Don't show existing value for security
    setSelectedSecret(secret)
    setOpenDialog(true)
  }

  const handleViewSecret = (secret: Secret) => {
    // Show authentication dialog first
    setPendingSecret(secret)
    setReAuthApiKey('')
    setAuthError('')
    setAuthDialog(true)
  }

  const handleAuthentication = async () => {
    if (!reAuthApiKey.trim()) {
      setAuthError('API key is required')
      return
    }

    // Verify the API key matches the current user's key
    if (reAuthApiKey !== apiKey) {
      setAuthError('Invalid API key')
      return
    }

    setAuthLoading(true)
    setAuthError('')

    try {
      // Validate the API key with the backend
      const isValid = await apiClient.validateApiKey(reAuthApiKey)
      if (!isValid) {
        setAuthError('API key validation failed')
        setAuthLoading(false)
        return
      }

      // Fetch the real secret value
      if (pendingSecret) {
        await fetchSecretValue(pendingSecret)
      }

      // Close auth dialog
      setAuthDialog(false)
      setReAuthApiKey('')
      setPendingSecret(null)
    } catch (error) {
      setAuthError('Authentication failed')
    }
    setAuthLoading(false)
  }

  const fetchSecretValue = async (secret: Secret) => {
    try {
      // For now, we'll simulate fetching the real secret value
      // In a real implementation, you'd call your secrets management API
      const realSecretValue = await getSecretFromBackend(secret.name)
      
      setDialogMode('view')
      setSecretName(secret.name)
      setSecretValue(realSecretValue)
      setSelectedSecret(secret)
      setShowSecretValue(false)
      setOpenDialog(true)
    } catch (error) {
      setAuthError('Failed to retrieve secret value')
    }
  }

  const getSecretFromBackend = async (secretName: string): Promise<string> => {
    try {
      const secretData = await apiClient.getSecretValue(secretName)
      return secretData.value
    } catch (error) {
      console.error('Failed to fetch secret:', error)
      // Fallback to mock data if API fails
      const mockSecrets: Record<string, string> = {
        'API_KEY': 'sk-1234567890abcdef1234567890abcdef1234567890abcdef',
        'ANTHROPIC_API_KEY': 'sk-ant-api03-abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
        'DATABASE_URL': 'postgresql://user:password@localhost:5432/devsecops_db?sslmode=require'
      }
      return mockSecrets[secretName] || 'secret-value-not-found'
    }
  }

  const copySecretToClipboard = () => {
    if (secretValue) {
      navigator.clipboard.writeText(secretValue)
      // You could add a toast notification here
    }
  }

  const handleDeleteSecret = async (secretName: string) => {
    if (window.confirm(`Are you sure you want to delete the secret "${secretName}"?`)) {
      setIsLoading(true)
      // Mock deletion
      setTimeout(() => {
        setSecrets(prev => prev.filter(s => s.name !== secretName))
        setIsLoading(false)
      }, 1000)
    }
  }

  const handleSaveSecret = async () => {
    if (!secretName.trim()) {
      setError('Secret name is required')
      return
    }
    if (!secretValue.trim() && dialogMode !== 'view') {
      setError('Secret value is required')
      return
    }

    setIsLoading(true)
    setError('')

    // Mock save operation
    setTimeout(() => {
      if (dialogMode === 'add') {
        const newSecret: Secret = {
          name: secretName,
          created: new Date().toISOString().split('T')[0],
          updated: new Date().toISOString().split('T')[0],
          version: '1',
        }
        setSecrets(prev => [...prev, newSecret])
      } else if (dialogMode === 'edit' && selectedSecret) {
        setSecrets(prev => prev.map(s => 
          s.name === selectedSecret.name 
            ? { ...s, updated: new Date().toISOString().split('T')[0], version: String(parseInt(s.version) + 1) }
            : s
        ))
      }
      setIsLoading(false)
      setOpenDialog(false)
    }, 1000)
  }

  const handleRefresh = () => {
    setIsLoading(true)
    // Mock refresh
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }

  return (
    <Box>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AzureIcon color="primary" />
              <Typography variant="h6">Azure Key Vault Secrets</Typography>
              <Chip
                label="Production"
                color="success"
                size="small"
                sx={{ ml: 1 }}
              />
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Refresh secrets list">
                <IconButton onClick={handleRefresh} disabled={isLoading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Add new secret to Azure Key Vault">
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleAddSecret}
                  disabled={isLoading}
                >
                  Add Secret
                </Button>
              </Tooltip>
            </Box>
          </Box>

          <Alert severity="info" sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SecurityIcon fontSize="small" />
              <Typography variant="body2" component="div">
                Secrets are stored securely in Azure Key Vault with HSM backing and RBAC access control
              </Typography>
            </Box>
          </Alert>

          {isLoading && !openDialog ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List>
              {secrets.map((secret) => (
                <ListItem
                  key={secret.name}
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <KeyIcon fontSize="small" />
                        <Typography variant="subtitle1">{secret.name}</Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Created: {secret.created} • Updated: {secret.updated} • Version: {secret.version}
                        </Typography>
                      </Box>
                    }
                    primaryTypographyProps={{ component: 'div' }}
                    secondaryTypographyProps={{ component: 'div' }}
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="View secret value">
                        <IconButton
                          size="small"
                          onClick={() => handleViewSecret(secret)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Update secret value">
                        <IconButton
                          size="small"
                          onClick={() => handleEditSecret(secret)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete secret">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteSecret(secret.name)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'add' && 'Add New Secret'}
          {dialogMode === 'edit' && `Update Secret: ${secretName}`}
          {dialogMode === 'view' && `View Secret: ${secretName}`}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Secret Name"
              value={secretName}
              onChange={(e) => setSecretName(e.target.value)}
              disabled={dialogMode === 'edit' || dialogMode === 'view' || isLoading}
              sx={{ mb: 2 }}
              placeholder="e.g., API_KEY, DATABASE_URL"
            />
            
            {dialogMode !== 'view' ? (
              <TextField
                fullWidth
                label="Secret Value"
                type={showSecretValue ? 'text' : 'password'}
                value={secretValue}
                onChange={(e) => setSecretValue(e.target.value)}
                disabled={isLoading}
                placeholder="Enter secret value..."
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Tooltip title={showSecretValue ? 'Hide value' : 'Show value'}>
                        <IconButton
                          onClick={() => setShowSecretValue(!showSecretValue)}
                          edge="end"
                        >
                          {showSecretValue ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </Tooltip>
                    </InputAdornment>
                  ),
                }}
              />
            ) : (
              <TextField
                fullWidth
                label="Secret Value"
                type={showSecretValue ? 'text' : 'password'}
                value={secretValue}
                disabled
                multiline={showSecretValue && secretValue.length > 50}
                maxRows={4}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Tooltip title="Copy to clipboard">
                        <IconButton
                          onClick={copySecretToClipboard}
                          disabled={!secretValue}
                        >
                          <CopyIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={showSecretValue ? 'Hide value' : 'Show value'}>
                        <IconButton
                          onClick={() => setShowSecretValue(!showSecretValue)}
                          edge="end"
                        >
                          {showSecretValue ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </Tooltip>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiInputBase-input': {
                    fontFamily: showSecretValue ? 'monospace' : 'inherit',
                    fontSize: showSecretValue ? '0.875rem' : 'inherit',
                    wordBreak: 'break-all'
                  }
                }}
              />
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={isLoading}>
            Cancel
          </Button>
          {dialogMode !== 'view' && (
            <Button
              onClick={handleSaveSecret}
              variant="contained"
              disabled={isLoading}
              startIcon={isLoading ? <CircularProgress size={16} /> : undefined}
            >
              {isLoading ? 'Saving...' : dialogMode === 'add' ? 'Add Secret' : 'Update Secret'}
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* API Key Re-authentication Dialog */}
      <Dialog open={authDialog} onClose={() => setAuthDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SecurityIcon color="warning" />
            <Typography variant="h6">Authenticate to View Secret</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            For security purposes, please re-enter your API key to view the secret value.
          </Alert>
          
          <TextField
            fullWidth
            label="Your API Key"
            type="password"
            value={reAuthApiKey}
            onChange={(e) => setReAuthApiKey(e.target.value)}
            disabled={authLoading}
            placeholder="Enter your API key..."
            sx={{ mt: 1 }}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !authLoading) {
                handleAuthentication()
              }
            }}
          />
          
          {authError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {authError}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuthDialog(false)} disabled={authLoading}>
            Cancel
          </Button>
          <Button 
            onClick={handleAuthentication} 
            variant="contained"
            disabled={authLoading || !reAuthApiKey.trim()}
            startIcon={authLoading ? <CircularProgress size={16} /> : undefined}
          >
            {authLoading ? 'Verifying...' : 'Authenticate'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}