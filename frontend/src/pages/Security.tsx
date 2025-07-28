import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Tooltip,
} from '@mui/material'
import {
  CloudQueue as AzureIcon,
  VpnKey as KeyIcon,
  Security as SecurityIcon,
  Shield as ShieldIcon,
  Lock as LockIcon,
  Visibility as AuditIcon,
  VerifiedUser as AuthIcon,
} from '@mui/icons-material'
import SecretsManager from '../components/security/SecretsManager'

export default function Security() {
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
                    <Typography variant="body2">
                      Hardware Security Module (HSM) backing
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LockIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2">
                      Role-based access control (RBAC)
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AuditIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2">
                      Comprehensive audit logging
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AuthIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="body2">
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
                    <Typography variant="body2">
                      Automatic key rotation policies
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LockIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2">
                      Multi-backend storage (keyring + vault)
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AuthIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2">
                      Zero secrets in source code
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AuditIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="body2">
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
    </Box>
  )
}