import { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, CircularProgress, Typography } from '@mui/material'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { useWebSocket } from './hooks/useWebSocket'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Tasks from './pages/Tasks'
import Security from './pages/Security'
import Monitoring from './pages/Monitoring'
import Settings from './pages/Settings'

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth()
  const { connect, disconnect } = useWebSocket()

  useEffect(() => {
    if (isAuthenticated) {
      connect()
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [isAuthenticated, connect, disconnect])

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body1" color="text.secondary">
          Connecting to DevSecOps Orchestrator...
        </Typography>
      </Box>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/security" element={<Security />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Box>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App