import { useEffect, useCallback, useState, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import websocketService, { AgentUpdate, TaskUpdate } from '../services/websocket'
import apiClient from '../services/api'
import { createStableHook, enableHMR } from '../utils/hmr'

// Export stable hook references using HMR utilities
export const useWebSocket = createStableHook(() => {
  return () => {
    const queryClient = useQueryClient()
    const [isConnected, setIsConnected] = useState<boolean>(
      websocketService.isConnected()
    )

    const connect = useCallback(() => {
      // Avoid attempting to connect if we are already connected or not authenticated
      if (websocketService.isConnected() || !apiClient.isAuthenticated()) {
        return
      }

      const apiKey = localStorage.getItem('devsecops_api_key') || undefined
      websocketService.connect(apiKey)
    }, [])

    const disconnect = useCallback(() => {
      if (websocketService.isConnected()) {
        websocketService.disconnect()
      }
    }, [])

    // Agent update handler
    const handleAgentUpdate = useCallback((update: AgentUpdate) => {
      // Update the agents query cache
      queryClient.setQueryData(['agents'], (oldData: any) => {
        if (!oldData) return oldData
        
        return oldData.map((agent: any) => 
          agent.name === update.agent_name 
            ? { ...agent, ...update }
            : agent
        )
      })

      // Invalidate specific agent query
      queryClient.invalidateQueries({ 
        queryKey: ['agents', update.agent_name] 
      })
    }, [queryClient])

    // Task update handler
    const handleTaskUpdate = useCallback((update: TaskUpdate) => {
      // Update the tasks query cache
      queryClient.setQueryData(['tasks'], (oldData: any) => {
        if (!oldData) return oldData
        
        return oldData.map((task: any) => 
          task.id === update.task_id 
            ? { ...task, ...update }
            : task
        )
      })

      // Update specific task query
      queryClient.setQueryData(['tasks', update.task_id], (oldData: any) => {
        if (!oldData) return oldData
        return { ...oldData, ...update }
      })
    }, [queryClient])

    useEffect(() => {
      // Reactively update connection status
      const handleStatus = (data: { connected: boolean }) => {
        setIsConnected(data.connected)
      }

      websocketService.onStatusUpdate(handleStatus)

      // Set up event listeners
      websocketService.onAgentUpdate(handleAgentUpdate)
      websocketService.onTaskUpdate(handleTaskUpdate)

      // Cleanup
      return () => {
        websocketService.offStatusUpdate(handleStatus)
        websocketService.offAgentUpdate(handleAgentUpdate)
        websocketService.offTaskUpdate(handleTaskUpdate)
      }
    }, [handleAgentUpdate, handleTaskUpdate])

    // Automatically connect/disconnect based on auth status
    useEffect(() => {
      if (apiClient.isAuthenticated()) {
        connect()
      } else {
        disconnect()
      }
    }, [connect, disconnect])

    return useMemo(
      () => ({
        connect,
        disconnect,
        isConnected,
      }),
      [connect, disconnect, isConnected]
    )
  }
}, 'useWebSocket')

export const useAgents = createStableHook(() => {
  return () => {
    return useQuery({
      queryKey: ['agents'],
      queryFn: () => apiClient.getAgents(),
      refetchInterval: 10000, // Fallback polling every 10 seconds
      enabled: apiClient.isAuthenticated(),
    })
  }
}, 'useAgents')

export const useAgent = createStableHook(() => {
  return (agentName: string) => {
    return useQuery({
      queryKey: ['agents', agentName],
      queryFn: () => apiClient.getAgentStatus(agentName),
      refetchInterval: 5000,
      enabled: !!agentName && apiClient.isAuthenticated(),
    })
  }
}, 'useAgent')

export const useTasks = createStableHook(() => {
  return () => {
    return useQuery({
      queryKey: ['tasks'],
      queryFn: () => apiClient.getTasks(),
      refetchInterval: 5000,
      enabled: apiClient.isAuthenticated(),
    })
  }
}, 'useTasks')

export const useTask = createStableHook(() => {
  return (taskId: string) => {
    return useQuery({
      queryKey: ['tasks', taskId],
      queryFn: () => apiClient.getTask(taskId),
      refetchInterval: 2000,
      enabled: !!taskId && apiClient.isAuthenticated(),
    })
  }
}, 'useTask')

// Enable HMR for this module
enableHMR()
