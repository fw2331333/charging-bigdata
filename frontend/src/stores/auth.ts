/** 用户会话（双 Token + 邮箱登录） */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  applyTokenPair,
  clearTokens,
  fetchMe,
  loginApi,
  logoutApi,
  type ProfileUpdateResponse,
  type UserInfo,
} from '@/api/auth'
import { ensureValidAccessToken, getAuthToken, getRefreshToken, refreshAccessToken } from '@/api/request'

const STORAGE_KEY = 'charging_bigdata_auth'

function loadStoredUser(): UserInfo | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as UserInfo) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(loadStoredUser())
  const pendingRoute = ref<string | null>(null)
  const sessionReady = ref(false)

  const isLoggedIn = computed(() => !!user.value && (!!getAuthToken() || !!getRefreshToken()))
  const isAdmin = computed(() => user.value?.role === 'admin')

  function persistUser(u: UserInfo | null) {
    if (u) localStorage.setItem(STORAGE_KEY, JSON.stringify(u))
    else localStorage.removeItem(STORAGE_KEY)
  }

  function setPendingRoute(path: string) {
    pendingRoute.value = path
  }

  function clearPendingRoute() {
    pendingRoute.value = null
  }

  async function login(
    email: string,
    password: string,
  ): Promise<{ message: string; status?: number } | null> {
    try {
      const res = await loginApi(email, password)
      applyTokenPair(res)
      user.value = res.user
      persistUser(res.user)
      return null
    } catch (e: unknown) {
      const ax = e as { response?: { status?: number; data?: { detail?: string } } }
      const msg = ax.response?.data?.detail ?? '登录失败，请检查邮箱与密码'
      return { message: String(msg), status: ax.response?.status }
    }
  }

  async function logout() {
    const refresh = getRefreshToken()
    if (refresh) {
      try {
        await logoutApi(refresh)
      } catch {
        /* 服务端吊销失败时仍清除本地会话 */
      }
    }
    user.value = null
    persistUser(null)
    clearTokens()
    clearPendingRoute()
  }

  async function restoreSession() {
    const hasAccess = !!getAuthToken()
    const hasRefresh = !!getRefreshToken()

    if (!hasAccess && !hasRefresh) {
      user.value = null
      persistUser(null)
      clearTokens()
      sessionReady.value = true
      return
    }

    try {
      await ensureValidAccessToken()
      user.value = await fetchMe()
      persistUser(user.value)
    } catch {
      await logout()
    } finally {
      sessionReady.value = true
    }
  }

  async function handleUnauthorized() {
    const ok = await refreshAccessToken()
    if (ok) {
      try {
        user.value = await fetchMe()
        persistUser(user.value)
        return
      } catch {
        /* fall through */
      }
    }
    await logout()
    const { default: router } = await import('@/router')
    if (router.currentRoute.value.meta.requiresAuth) {
      await router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    }
  }

  async function applyProfileUpdate(res: ProfileUpdateResponse) {
    user.value = res.user
    persistUser(res.user)
    if (res.access_token && res.refresh_token) {
      applyTokenPair({
        access_token: res.access_token,
        refresh_token: res.refresh_token,
        token_type: 'bearer',
        expires_in: res.expires_in ?? 1800,
      })
    }
  }

  return {
    user,
    pendingRoute,
    sessionReady,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    restoreSession,
    setPendingRoute,
    clearPendingRoute,
    handleUnauthorized,
    applyProfileUpdate,
  }
})
