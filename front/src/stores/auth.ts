import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getMe, refreshToken } from '@/api/auth'
import type { User } from '@/types'
import router from '@/router'

const STORAGE_KEY_TOKEN = 'token'
const STORAGE_KEY_REFRESH = 'refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(STORAGE_KEY_TOKEN) || '')
  const refresh_token = ref(localStorage.getItem(STORAGE_KEY_REFRESH) || '')
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const userGroups = computed(() => user.value?.groups || [])
  const isSuporte = computed(() => userGroups.value.includes('Suporte-Cliente'))
  const isNocIp = computed(() => userGroups.value.includes('Noc-IP'))
  const isStaff = computed(() => user.value?.is_staff || false)

  function _saveTokens(access: string, refresh: string) {
    token.value = access
    refresh_token.value = refresh
    localStorage.setItem(STORAGE_KEY_TOKEN, access)
    localStorage.setItem(STORAGE_KEY_REFRESH, refresh)
  }

  function _clearTokens() {
    token.value = ''
    refresh_token.value = ''
    user.value = null
    localStorage.removeItem(STORAGE_KEY_TOKEN)
    localStorage.removeItem(STORAGE_KEY_REFRESH)
  }

  async function loginAction(username: string, password: string) {
    loading.value = true
    try {
      const res = await login(username, password)
      _saveTokens(res.access_token, res.refresh_token || '')
      if (res.user) {
        user.value = res.user
      } else {
        await fetchUser()
      }
      const redirect = res.user?.redirect_to || '/'
      router.push(redirect)
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await getMe()
    } catch {
      await attemptTokenRefresh()
    }
  }

  async function attemptTokenRefresh(): Promise<boolean> {
    if (!refresh_token.value) {
      _clearTokens()
      router.push('/login')
      return false
    }
    try {
      const res = await refreshToken(refresh_token.value)
      _saveTokens(res.access_token, res.refresh_token)
      if (res.user) user.value = res.user
      return true
    } catch {
      _clearTokens()
      router.push('/login')
      return false
    }
  }

  async function initAuth() {
    if (!token.value) return
    loading.value = true
    try {
      user.value = await getMe()
    } catch {
      await attemptTokenRefresh()
    } finally {
      loading.value = false
    }
  }

  function logout() {
    _clearTokens()
    router.push('/login')
  }

  return {
    token, refresh_token, user, loading,
    isAuthenticated, userGroups, isSuporte, isNocIp, isStaff,
    loginAction, fetchUser, attemptTokenRefresh, initAuth, logout,
  }
})
