import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
} from '@mui/material'
import {
  CloudQueue as AzureIcon,
  VpnKey as KeyIcon,
  Security as SecurityIcon,
} from '@mui/icons-material'

export default function Security() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Management
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Azure Active Directory and Key Vault integration
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AzureIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Azure Key Vault</Typography>
                <Chip label="Active" color="success" size="small" sx={{ ml: 'auto' }} />
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Enterprise-grade secret management with HSM backing
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  • Hardware Security Module (HSM) backing
                </Typography>
                <Typography variant="body2">
                  • Role-based access control (RBAC)
                </Typography>
                <Typography variant="body2">
                  • Audit logging and monitoring
                </Typography>
                <Typography variant="body2">
                  • Azure AD authentication
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <KeyIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">API Key Management</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Secure API key rotation and management
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  • Automatic key rotation
                </Typography>
                <Typography variant="body2">
                  • Multi-backend storage
                </Typography>
                <Typography variant="body2">
                  • Zero secrets in code
                </Typography>
                <Typography variant="body2">
                  • Encrypted local backup
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Security Features</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Authentication
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Bearer token authentication for all API endpoints
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Input Validation
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Comprehensive input sanitization and validation
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Secure Execution
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Sandboxed agent execution environment
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Audit Logging
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Complete audit trail for all operations
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}