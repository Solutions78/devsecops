import { io, Socket } from 'socket.io-client'

export interface AgentUpdate {
  agent_name: string
  status: 'idle' | 'running' | 'complete' | 'error'
  task_id?: string
  progress?: number
  message?: string
  timestamp: string
}

export interface TaskUpdate {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number
  result?: any
  error?: string
  timestamp: string
}

type EventCallback<T> = (data: T) => void

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(apiKey?: string): void {
    if (this.socket?.connected) {
      return
    }

    this.socket = io('/updates', {
      transports: ['websocket'],
      auth: apiKey ? { token: apiKey } : undefined,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached')
        this.disconnect()
      }
    })

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`WebSocket reconnected after ${attemptNumber} attempts`)
      this.reconnectAttempts = 0
    })
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false
  }

  // Agent updates
  onAgentUpdate(callback: EventCallback<AgentUpdate>): void {
    this.socket?.on('agent_update', callback)
  }

  offAgentUpdate(callback: EventCallback<AgentUpdate>): void {
    this.socket?.off('agent_update', callback)
  }

  // Task updates
  onTaskUpdate(callback: EventCallback<TaskUpdate>): void {
    this.socket?.on('task_update', callback)
  }

  offTaskUpdate(callback: EventCallback<TaskUpdate>): void {
    this.socket?.off('task_update', callback)
  }

  // System health updates
  onSystemUpdate(callback: EventCallback<{ status: string; message?: string }>): void {
    this.socket?.on('system_update', callback)
  }

  offSystemUpdate(callback: EventCallback<{ status: string; message?: string }>): void {
    this.socket?.off('system_update', callback)
  }

  // Generic event listener
  on(event: string, callback: EventCallback<any>): void {
    this.socket?.on(event, callback)
  }

  off(event: string, callback: EventCallback<any>): void {
    this.socket?.off(event, callback)
  }

  // Emit events (if needed for bidirectional communication)
  emit(event: string, data?: any): void {
    this.socket?.emit(event, data)
  }
}

export const websocketService = new WebSocketService()
export default websocketService