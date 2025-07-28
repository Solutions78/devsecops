import { useEffect, useCallback, useRef } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import websocketService, { AgentUpdate, TaskUpdate } from '../services/websocket'
import apiClient from '../services/api'

export function useWebSocket() {
  const queryClient = useQueryClient()
  const isConnectedRef = useRef(false)

  const connect = useCallback(() => {
    if (!isConnectedRef.current && apiClient.isAuthenticated()) {
      const apiKey = localStorage.getItem('devsecops_api_key')
      websocketService.connect(apiKey || undefined)
      isConnectedRef.current = true
    }
  }, [])

  const disconnect = useCallback(() => {
    if (isConnectedRef.current) {
      websocketService.disconnect()
      isConnectedRef.current = false
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
    // Set up event listeners
    websocketService.onAgentUpdate(handleAgentUpdate)
    websocketService.onTaskUpdate(handleTaskUpdate)

    // Cleanup
    return () => {
      websocketService.offAgentUpdate(handleAgentUpdate)
      websocketService.offTaskUpdate(handleTaskUpdate)
    }
  }, [handleAgentUpdate, handleTaskUpdate])

  return {
    connect,
    disconnect,
    isConnected: websocketService.isConnected(),
  }
}

export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => apiClient.getAgents(),
    refetchInterval: 10000, // Fallback polling every 10 seconds
    enabled: apiClient.isAuthenticated(),
  })
}

export function useAgent(agentName: string) {
  return useQuery({
    queryKey: ['agents', agentName],
    queryFn: () => apiClient.getAgentStatus(agentName),
    refetchInterval: 5000,
    enabled: !!agentName && apiClient.isAuthenticated(),
  })
}

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiClient.getTasks(),
    refetchInterval: 5000,
    enabled: apiClient.isAuthenticated(),
  })
}

export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => apiClient.getTask(taskId),
    refetchInterval: 2000,
    enabled: !!taskId && apiClient.isAuthenticated(),
  })
}