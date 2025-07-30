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
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private reconnectTimer: NodeJS.Timeout | null = null
  private eventHandlers: Map<string, EventCallback<any>[]> = new Map()

  /**
   * Helper to emit connection status updates so that React hooks can reactively
   * respond to WebSocket connectivity changes without polling the service.
   * Consumers can subscribe via `onStatusUpdate`.
   */
  private emitStatus(connected: boolean): void {
    this.emit('status', { connected })
  }

  connect(apiKey?: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return
    }

    // Use environment variable for WebSocket URL, fallback to direct backend URL for development  
    const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8001'
    let wsUrl: string
    
    if (apiBase.startsWith('/')) {
      // Relative path like "/api" - use current host with WebSocket protocol
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      wsUrl = `${protocol}//${window.location.host}${apiBase}/updates`
    } else {
      // Full URL like "http://localhost:8001"
      wsUrl = apiBase.replace('http://', 'ws://').replace('https://', 'wss://') + '/updates'
    }
    console.log('Connecting to WebSocket:', wsUrl)
    
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
        this.reconnectTimer = null
      }

      // Notify listeners that we are now connected
      this.emitStatus(true)
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('WebSocket message received:', data)
        
        // Handle different message types
        if (data.type === 'agent_update' || data.agent_name) {
          this.emit('agent_update', data)
        } else if (data.type === 'task_update' || data.task_id) {
          this.emit('task_update', data)
        } else if (data.type === 'system_update') {
          this.emit('system_update', data)
        }
        
        // Emit raw message as well
        this.emit('message', data)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason)
      // Notify listeners that we are now disconnected before attempting to reconnect
      this.emitStatus(false)
      this.attemptReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1) // Exponential backoff
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, delay)
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.reconnectAttempts = 0
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  // Agent updates
  onAgentUpdate(callback: EventCallback<AgentUpdate>): void {
    this.on('agent_update', callback)
  }

  offAgentUpdate(callback: EventCallback<AgentUpdate>): void {
    this.off('agent_update', callback)
  }

  // Task updates
  onTaskUpdate(callback: EventCallback<TaskUpdate>): void {
    this.on('task_update', callback)
  }

  offTaskUpdate(callback: EventCallback<TaskUpdate>): void {
    this.off('task_update', callback)
  }

  // System health updates
  onSystemUpdate(callback: EventCallback<{ status: string; message?: string }>): void {
    this.on('system_update', callback)
  }

  offSystemUpdate(callback: EventCallback<{ status: string; message?: string }>): void {
    this.off('system_update', callback)
  }

  // Connection status updates
  onStatusUpdate(callback: EventCallback<{ connected: boolean }>): void {
    this.on('status', callback)
  }

  offStatusUpdate(callback: EventCallback<{ connected: boolean }>): void {
    this.off('status', callback)
  }

  // Generic event listener
  on(event: string, callback: EventCallback<any>): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, [])
    }
    this.eventHandlers.get(event)!.push(callback)
  }

  off(event: string, callback: EventCallback<any>): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      const index = handlers.indexOf(callback)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  // Emit events internally
  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error)
        }
      })
    }
  }

  // Send data to server (if needed)
  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected, cannot send data')
    }
  }
}

export const websocketService = new WebSocketService()
export default websocketService
