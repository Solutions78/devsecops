import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import apiClient from '../services/api'

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

export function AuthProvider({ children }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing API key on app load
    const storedKey = localStorage.getItem('devsecops_api_key')
    if (storedKey) {
      validateAndSetKey(storedKey)
    } else {
      setIsLoading(false)
    }
  }, [])

  const validateAndSetKey = async (key: string) => {
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
  }

  const login = async (key: string): Promise<boolean> => {
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
  }

  const logout = () => {
    apiClient.clearApiKey()
    setApiKey(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, apiKey, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}