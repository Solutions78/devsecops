import axios, { AxiosInstance, AxiosResponse } from 'axios'

export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface AgentStatus {
  name: string
  status: 'idle' | 'running' | 'complete' | 'error'
  last_updated: string
  tasks_completed: number
  current_task?: string
}

export interface TaskSubmission {
  intent: string
  params: Record<string, any>
}

export interface TaskResult {
  id: string
  intent: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  agent_name: string
  created_at: string
  updated_at: string
  result?: any
  error?: string
}

class ApiClient {
  private client: AxiosInstance
  private apiKey: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 30000,
    })

    this.setupInterceptors()
    this.loadApiKey()
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth header
    this.client.interceptors.request.use(
      (config) => {
        if (this.apiKey) {
          config.headers.Authorization = `Bearer ${this.apiKey}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearApiKey()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  private loadApiKey(): void {
    this.apiKey = localStorage.getItem('devsecops_api_key')
  }

  public setApiKey(key: string): void {
    this.apiKey = key
    localStorage.setItem('devsecops_api_key', key)
  }

  public clearApiKey(): void {
    this.apiKey = null
    localStorage.removeItem('devsecops_api_key')
  }

  public isAuthenticated(): boolean {
    return !!this.apiKey
  }

  // Authentication
  async validateApiKey(key: string): Promise<boolean> {
    try {
      await this.client.get('/health', {
        headers: { Authorization: `Bearer ${key}` }
      })
      return true
    } catch {
      return false
    }
  }

  // Agent endpoints
  async getAgents(): Promise<AgentStatus[]> {
    const response = await this.client.get<ApiResponse<AgentStatus[]>>('/agents')
    return response.data.data
  }

  async getAgentStatus(agentName: string): Promise<AgentStatus> {
    const response = await this.client.get<ApiResponse<AgentStatus>>(`/agents/${agentName}`)
    return response.data.data
  }

  // Task endpoints
  async submitTask(task: TaskSubmission): Promise<TaskResult> {
    const response = await this.client.post<ApiResponse<TaskResult>>('/task', task)
    return response.data.data
  }

  async getTasks(): Promise<TaskResult[]> {
    const response = await this.client.get<ApiResponse<TaskResult[]>>('/tasks')
    return response.data.data
  }

  async getTask(taskId: string): Promise<TaskResult> {
    const response = await this.client.get<ApiResponse<TaskResult>>(`/tasks/${taskId}`)
    return response.data.data
  }

  async cancelTask(taskId: string): Promise<void> {
    await this.client.delete(`/tasks/${taskId}`)
  }

  // Health check
  async getHealth(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get<ApiResponse<{ status: string; timestamp: string }>>('/health')
    return response.data.data
  }

  // Metrics
  async getMetrics(): Promise<any> {
    const response = await this.client.get('/metrics')
    return response.data
  }
}

export const apiClient = new ApiClient()
export default apiClient