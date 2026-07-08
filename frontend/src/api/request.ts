/** Axios 实例：统一请求后端 API（双 Token + 401 自动刷新） */
import axios, { type InternalAxiosRequestConfig } from 'axios'

const TOKEN_KEY = 'charging_bigdata_token'
const REFRESH_KEY = 'charging_bigdata_refresh'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

let onUnauthorized: (() => void) | null = null
let refreshPromise: Promise<boolean> | null = null

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean }

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler
}

export function setAuthToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setRefreshToken(token: string | null) {
  if (token) localStorage.setItem(REFRESH_KEY, token)
  else localStorage.removeItem(REFRESH_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY)
}

function isAccessTokenExpired(): boolean {
  const token = getAuthToken()
  if (!token || token.split('.').length !== 3) return true
  try {
    const payload = JSON.parse(atob(token.split('.')[1]!)) as { exp?: number }
    if (!payload.exp) return true
    return payload.exp * 1000 <= Date.now() + 30_000
  } catch {
    return true
  }
}

export function clearTokens() {
  setAuthToken(null)
  setRefreshToken(null)
}

/** 使用 Refresh Token 换取新的 Token 对（服务端轮换） */
export async function refreshAccessToken(): Promise<boolean> {
  const refresh = getRefreshToken()
  if (!refresh) return false
  try {
    const { data } = await axios.post<{
      access_token: string
      refresh_token: string
    }>('/api/v1/auth/refresh', { refresh_token: refresh }, { timeout: 30000 })
    setAuthToken(data.access_token)
    setRefreshToken(data.refresh_token)
    return true
  } catch {
    return false
  }
}

export async function ensureValidAccessToken(): Promise<boolean> {
  if (getAuthToken() && !isAccessTokenExpired()) return true
  refreshPromise ??= refreshAccessToken().finally(() => {
    refreshPromise = null
  })
  return refreshPromise
}

request.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (res) => res.data,
  async (err) => {
    const status = err.response?.status
    const config = err.config as RetriableConfig | undefined
    const url = String(config?.url ?? '')

    if (status !== 401 || !config) {
      return Promise.reject(err)
    }

    if (url.includes('/auth/login') || url.includes('/auth/refresh')) {
      onUnauthorized?.()
      return Promise.reject(err)
    }

    if (config._retried) {
      onUnauthorized?.()
      return Promise.reject(err)
    }

    config._retried = true
    refreshPromise ??= refreshAccessToken().finally(() => {
      refreshPromise = null
    })
    const ok = await refreshPromise
    if (!ok) {
      onUnauthorized?.()
      return Promise.reject(err)
    }

    config.headers.Authorization = `Bearer ${getAuthToken()}`
    return request(config)
  },
)

export default request
