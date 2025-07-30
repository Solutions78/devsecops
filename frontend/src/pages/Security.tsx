import { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Snackbar,
} from '@mui/material'
import {
  CloudQueue as AzureIcon,
  VpnKey as KeyIcon,
  Security as SecurityIcon,
  Shield as ShieldIcon,
  Lock as LockIcon,
  Visibility as AuditIcon,
  VerifiedUser as AuthIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Person as UserIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../services/api'
import SecretsManager from '../components/security/SecretsManager'

export default function Security() {
  const [createUserOpen, setCreateUserOpen] = useState(false)
  const [newUserRole, setNewUserRole] = useState<'administrator' | 'user'>('user')
  const [newUserDescription, setNewUserDescription] = useState('')
  const [createdApiKey, setCreatedApiKey] = useState('')
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' })

  const queryClient = useQueryClient()

  // Fetch users
  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => apiClient.listUsers(),
    refetchInterval: 30000,
  })

  // Create user mutation
  const createUserMutation = useMutation({
    mutationFn: ({ role, description }: { role: 'administrator' | 'user'; description?: string }) =>
      apiClient.createUser(role, description),
    onSuccess: (data) => {
      setCreatedApiKey(data.api_key)
      setSnackbar({ open: true, message: 'User created successfully!', severity: 'success' })
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setNewUserDescription('')
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to create user', severity: 'error' })
    },
  })

  // Delete user mutation
  const deleteUserMutation = useMutation({
    mutationFn: (apiKey: string) => apiClient.deleteUser(apiKey),
    onSuccess: () => {
      setSnackbar({ open: true, message: 'User deleted successfully!', severity: 'success' })
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to delete user', severity: 'error' })
    },
  })

  const handleCreateUser = () => {
    createUserMutation.mutate({ role: newUserRole, description: newUserDescription })
  }

  const handleDeleteUser = (apiKey: string) => {
    if (window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      deleteUserMutation.mutate(apiKey)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setSnackbar({ open: true, message: 'Copied to clipboard!', severity: 'success' })
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Management
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Azure Active Directory and Key Vault integration with enterprise-grade security
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Azure Key Vault Overview */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Azure Key Vault provides hardware-backed security for all secrets" arrow>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AzureIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Azure Key Vault</Typography>
                  <Chip label="Active" color="success" size="small" sx={{ ml: 'auto' }} />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Enterprise-grade secret management with HSM backing and Azure AD integration
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <ShieldIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2" component="div">
                      Hardware Security Module (HSM) backing
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LockIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2" component="div">
                      Role-based access control (RBAC)
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AuditIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2" component="div">
                      Comprehensive audit logging
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AuthIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2" component="div">
                      Azure Active Directory authentication
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Tooltip>
        </Grid>

        {/* API Key Management */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Automated API key rotation and multi-backend storage" arrow>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <KeyIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">API Key Management</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Secure API key rotation with zero-downtime deployment
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <ShieldIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2" component="div">
                      Automatic key rotation policies
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LockIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2" component="div">
                      Multi-backend storage (keyring + vault)
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AuthIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2" component="div">
                      Zero secrets in source code
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AuditIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2" component="div">
                      Encrypted local backup
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Tooltip>
        </Grid>

        {/* Secrets Management Interface */}
        <Grid item xs={12}>
          <SecretsManager />
        </Grid>

        {/* User Management */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <UserIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">User Management</Typography>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setCreateUserOpen(true)}
                  disabled={createUserMutation.isPending}
                >
                  Create User
                </Button>
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Manage API keys and user access roles for the DevSecOps orchestrator
              </Typography>

              {usersLoading ? (
                <Typography>Loading users...</Typography>
              ) : (
                <List>
                  {users.map((user: any, index: number) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {user.role === 'administrator' ? (
                              <AdminIcon color="primary" fontSize="small" />
                            ) : (
                              <UserIcon color="secondary" fontSize="small" />
                            )}
                            <Typography variant="subtitle2">
                              {user.role === 'administrator' ? 'Administrator' : 'User'}
                            </Typography>
                            <Chip 
                              label={user.api_key_masked} 
                              size="small" 
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {user.description && (
                              <Typography variant="body2" color="text.secondary">
                                {user.description}
                              </Typography>
                            )}
                            <Typography variant="caption" color="text.secondary">
                              Created: {new Date(user.created_at).toLocaleDateString()} 
                              {user.last_used && ` • Last used: ${new Date(user.last_used).toLocaleDateString()}`}
                            </Typography>
                          </Box>
                        }
                        primaryTypographyProps={{ component: 'div' }}
                        secondaryTypographyProps={{ component: 'div' }}
                      />
                      <ListItemSecondaryAction>
                        <Tooltip title="Delete user">
                          <IconButton
                            edge="end"
                            onClick={() => handleDeleteUser(user.api_key_masked.replace('...', ''))}
                            disabled={deleteUserMutation.isPending}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Security Features */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Security Architecture</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Tooltip title="All API endpoints require Bearer token authentication" arrow>
                    <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1, height: '100%' }}>
                      <AuthIcon color="primary" sx={{ mb: 1 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Authentication
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Bearer token authentication with secure API key validation
                      </Typography>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Tooltip title="Comprehensive input sanitization prevents injection attacks" arrow>
                    <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1, height: '100%' }}>
                      <ShieldIcon color="primary" sx={{ mb: 1 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Input Validation
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Comprehensive sanitization and validation for all inputs
                      </Typography>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Tooltip title="Agents execute in isolated sandboxed environments" arrow>
                    <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1, height: '100%' }}>
                      <LockIcon color="primary" sx={{ mb: 1 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Secure Execution
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Sandboxed agent execution with resource limitations
                      </Typography>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Tooltip title="Complete audit trail for all system operations" arrow>
                    <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1, height: '100%' }}>
                      <AuditIcon color="primary" sx={{ mb: 1 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Audit Logging
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Complete audit trail for compliance and monitoring
                      </Typography>
                    </Box>
                  </Tooltip>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Create User Dialog */}
      <Dialog open={createUserOpen} onClose={() => setCreateUserOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                value={newUserRole}
                label="Role"
                onChange={(e) => setNewUserRole(e.target.value as 'administrator' | 'user')}
              >
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="administrator">Administrator</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Description (optional)"
              value={newUserDescription}
              onChange={(e) => setNewUserDescription(e.target.value)}
              placeholder="e.g., Development team member, External contractor, etc."
            />

            {newUserRole === 'administrator' && (
              <Alert severity="warning">
                Administrators have full access to all features including user management and security settings.
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateUserOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateUser} 
            variant="contained"
            disabled={createUserMutation.isPending}
          >
            {createUserMutation.isPending ? 'Creating...' : 'Create User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* API Key Display Dialog */}
      <Dialog open={!!createdApiKey} onClose={() => setCreatedApiKey('')} maxWidth="md" fullWidth>
        <DialogTitle>User Created Successfully</DialogTitle>
        <DialogContent>
          <Alert severity="success" sx={{ mb: 2 }}>
            New {newUserRole} user has been created successfully!
          </Alert>
          
          <Typography variant="body2" sx={{ mb: 2 }}>
            <strong>Important:</strong> This is the only time you'll see the full API key. Please copy it now and store it securely.
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 2, border: 1, borderColor: 'divider', borderRadius: 1, bgcolor: 'grey.50' }}>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', wordBreak: 'break-all', flex: 1, color: 'text.primary' }}>
              {createdApiKey}
            </Typography>
            <IconButton onClick={() => copyToClipboard(createdApiKey)}>
              <CopyIcon />
            </IconButton>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatedApiKey('')} variant="contained">
            I've Saved the API Key
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
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