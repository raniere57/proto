import api from './client'
import type { User } from '@/types'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user?: User
}

export async function login(username: string, password: string) {
  const { data } = await api.post<LoginResponse>('/auth/login', { username, password })
  return data
}

export async function refreshToken(refresh_token: string) {
  const { data } = await api.post<LoginResponse>('/auth/refresh', { refresh_token })
  return data
}

export async function getMe() {
  const { data } = await api.get<User>('/auth/me')
  return data
}

export async function changePassword(current_password: string, new_password: string) {
  const { data } = await api.post<{ message: string }>('/auth/change-password', { current_password, new_password })
  return data
}

export async function listUsers(search?: string) {
  const { data } = await api.get<User[]>('/auth/users', { params: { search } })
  return data
}
