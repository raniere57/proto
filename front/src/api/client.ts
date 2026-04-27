import axios, { AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'

export interface ApiError {
  detail: string
  status: number
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError<{ detail?: string; message?: string }>) => {
    const originalRequest = err.config as any
    if (!originalRequest || err.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(err)
    }

    const auth = useAuthStore()
    if (!auth.refresh_token) {
      auth.logout()
      return Promise.reject(err)
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        pendingRequests.push((token: string) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          resolve(api(originalRequest))
        })
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      const ok = await auth.attemptTokenRefresh()
      if (ok) {
        originalRequest.headers.Authorization = `Bearer ${auth.token}`
        pendingRequests.forEach((cb) => cb(auth.token))
        pendingRequests = []
        return api(originalRequest)
      }
    } finally {
      isRefreshing = false
    }

    return Promise.reject(err)
  },
)

export function extractError(err: unknown): string {
  if (err instanceof AxiosError) {
    return err.response?.data?.detail || err.response?.data?.message || err.message
  }
  if (err instanceof Error) return err.message
  return 'Erro desconhecido'
}

export default api
