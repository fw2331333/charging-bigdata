/** JWT 双 Token 认证 API */
import request, { clearTokens, setAuthToken, setRefreshToken } from './request'

export interface UserInfo {
  username: string
  email?: string | null
  role: string
  display_name: string
}

export interface TokenPairResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginResponse extends TokenPairResponse {
  user: UserInfo
}

export function applyTokenPair(pair: TokenPairResponse) {
  setAuthToken(pair.access_token)
  setRefreshToken(pair.refresh_token)
}

export const loginApi = (email: string, password: string) =>
  request.post<unknown, LoginResponse>('/auth/login', { email, password })

export const refreshApi = (refreshToken: string) =>
  request.post<unknown, TokenPairResponse>('/auth/refresh', { refresh_token: refreshToken })

export const logoutApi = (refreshToken: string) =>
  request.post<unknown, { ok: boolean }>('/auth/logout', { refresh_token: refreshToken })

export const fetchMe = () => request.get<unknown, UserInfo>('/auth/me')

export interface MessageResponse {
  message: string
  email_sent?: boolean
}

export interface RegisterResponse extends MessageResponse {
  email: string
}

export interface InspectTokenResponse {
  valid: boolean
  purpose: string
  email_masked: string
}

export interface CompleteTokenResponse {
  message: string
  email: string
}

export const registerApi = (email: string, username: string) =>
  request.post<unknown, RegisterResponse>('/auth/register', { email, username })

export const resendVerificationApi = (email: string) =>
  request.post<unknown, MessageResponse>('/auth/resend-verification', { email })

export const forgotPasswordApi = (email: string) =>
  request.post<unknown, MessageResponse>('/auth/forgot-password', { email })

export const inspectEmailTokenApi = (token: string) =>
  request.post<unknown, InspectTokenResponse>('/auth/inspect-email-token', { token })

export const completeEmailTokenApi = (token: string, password: string) =>
  request.post<unknown, CompleteTokenResponse>('/auth/complete-email-token', { token, password })

export interface ProfileCodeResponse {
  message: string
  email_sent?: boolean
}

export interface ProfileUpdateResponse {
  user: UserInfo
  access_token?: string | null
  refresh_token?: string | null
  expires_in?: number | null
}

export const sendProfileCodeApi = () =>
  request.post<unknown, ProfileCodeResponse>('/auth/profile/send-code')

export const changeProfilePasswordApi = (code: string, newPassword: string) =>
  request.patch<unknown, ProfileUpdateResponse>('/auth/profile/password', {
    code,
    new_password: newPassword,
  })

export const updateProfileUsernameApi = (username: string) =>
  request.patch<unknown, ProfileUpdateResponse>('/auth/profile/username', { username })

export { clearTokens }

export interface ChartViewConfig {
  chart_key: string
  title: string
  chart_type: string
  data_source: string
  drill_route: string | null
  grid_area: string | null
  sort_order: number
  enabled: boolean
}

export const fetchViewConfigs = () =>
  request.get<unknown, ChartViewConfig[]>('/views')
