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
} from '@mui/icons-material'

interface Secret {
  name: string
  created: string
  updated: string
  version: string
}

export default function SecretsManager() {
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
    setDialogMode('view')
    setSecretName(secret.name)
    setSecretValue('sk-1234567890abcdef...') // Mock value
    setSelectedSecret(secret)
    setShowSecretValue(false)
    setOpenDialog(true)
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
              <Typography variant="body2">
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
    </Box>
  )
}