import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useMemo } from 'react'
import apiClient from '../services/api'
import { createStableHook, createStableProvider, enableHMR } from '../utils/hmr'

interface AuthContextType {
  isAuthenticated: boolean
  apiKey: string | null
  login: (apiKey: string) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

// Export the component with a stable reference for HMR
const AuthProviderComponent = React.memo<AuthProviderProps>(({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Use useCallback to ensure stable function references across re-renders
  const validateAndSetKey = useCallback(async (key: string) => {
    setIsLoading(true)
    try {
      console.log('Validating API key...')
      const isValid = await apiClient.validateApiKey(key)
      console.log('API key validation result:', isValid)
      
      if (isValid) {
        apiClient.setApiKey(key)
        setApiKey(key)
        setIsAuthenticated(true)
        console.log('Authentication successful')
      } else {
        // Invalid key, remove it
        console.log('Invalid API key, removing from storage')
        localStorage.removeItem('devsecops_api_key')
        apiClient.clearApiKey()
        setApiKey(null)
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Error validating API key:', error)
      localStorage.removeItem('devsecops_api_key')
      apiClient.clearApiKey()
      setApiKey(null)
      setIsAuthenticated(false)
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (key: string): Promise<boolean> => {
    setIsLoading(true)
    try {
      console.log('Attempting login with API key')
      const isValid = await apiClient.validateApiKey(key)
      console.log('Login validation result:', isValid)
      
      if (isValid) {
        apiClient.setApiKey(key)
        setApiKey(key)
        setIsAuthenticated(true)
        console.log('Login successful')
        setIsLoading(false)
        return true
      }
      console.log('Login failed - invalid key')
      setIsLoading(false)
      return false
    } catch (error) {
      console.error('Login error:', error)
      setIsLoading(false)
      return false
    }
  }, [])

  const logout = useCallback(() => {
    apiClient.clearApiKey()
    setApiKey(null)
    setIsAuthenticated(false)
  }, [])

  // Set up auth error handler for API client
  React.useEffect(() => {
    apiClient.setAuthErrorHandler(() => {
      console.log('Auth error detected, logging out')
      logout()
    })
  }, [logout])

  useEffect(() => {
    // Check for existing API key on app load
    const storedKey = localStorage.getItem('devsecops_api_key')
    if (storedKey) {
      validateAndSetKey(storedKey)
    } else {
      setIsLoading(false)
    }
  }, [validateAndSetKey])

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    isAuthenticated,
    apiKey,
    login,
    logout,
    isLoading
  }), [isAuthenticated, apiKey, login, logout, isLoading])

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
})

// Create stable provider and hook using HMR utilities
export const AuthProvider = createStableProvider(AuthProviderComponent, 'AuthProvider')

export const useAuth = createStableHook(() => {
  return (): AuthContextType => {
    const context = useContext(AuthContext)
    if (context === undefined) {
      throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
  }
}, 'useAuth')

// Enable HMR for this module
enableHMR()