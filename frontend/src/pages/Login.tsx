import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Security as SecurityIcon,
  CloudQueue as AzureIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const [apiKey, setApiKey] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const { login, isLoading, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Get the intended destination from state or default to dashboard
  const from = location.state?.from?.pathname || '/'

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!apiKey.trim()) {
      setError('Please enter your API key')
      return
    }

    const success = await login(apiKey.trim())
    if (!success) {
      setError('Invalid API key. Please check your credentials and try again.')
    }
    // Navigation will be handled by the useEffect above when isAuthenticated changes
  }

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0d1117 0%, #161b22 100%)',
        p: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 480,
          width: '100%',
          background: 'rgba(22, 27, 34, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid #30363d',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <SecurityIcon
              sx={{
                fontSize: 64,
                color: 'primary.main',
                mb: 2,
              }}
            />
            <Typography variant="h4" gutterBottom>
              DevSecOps Orchestrator
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Secure AI-powered development operations platform
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
              mb: 3,
              p: 2,
              backgroundColor: 'primary.main',
              borderRadius: 1,
              color: 'white',
            }}
          >
            <AzureIcon />
            <Typography variant="body2" fontWeight={600}>
              Azure Active Directory Integration
            </Typography>
          </Box>

          <form onSubmit={handleSubmit}>
            <Tooltip
              title="Enter your API key to authenticate with the DevSecOps Orchestrator backend"
              arrow
              placement="top"
            >
              <TextField
                fullWidth
                label="API Key"
                type={showPassword ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key..."
                disabled={isLoading}
                error={!!error}
                sx={{ mb: 2 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Tooltip title={showPassword ? 'Hide API key' : 'Show API key'}>
                        <IconButton
                          onClick={handleTogglePasswordVisibility}
                          edge="end"
                          disabled={isLoading}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </Tooltip>
                    </InputAdornment>
                  ),
                }}
              />
            </Tooltip>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Tooltip title="Authenticate and access the DevSecOps dashboard" arrow>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isLoading || !apiKey.trim()}
                sx={{ mb: 2 }}
              >
                {isLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Sign In'
                )}
              </Button>
            </Tooltip>
          </form>

          <Box sx={{ mt: 3, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              <strong>Security Features:</strong>
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              • Bearer token authentication
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              • Azure Key Vault integration
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              • Encrypted secret management
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              • Real-time agent monitoring
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}