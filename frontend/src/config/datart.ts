/** Datart BI 大屏（手册 §5.1–5.3） */

export const DATART_BASE_URL = (
  (import.meta.env.VITE_DATART_BASE_URL as string | undefined) || 'http://127.0.0.1:8088'
).replace(/\/$/, '')

/** Datart 分享 Dashboard 完整 URL（含 shareDashboard/...） */
export const DATART_DASHBOARD_URL = (
  (import.meta.env.VITE_DATART_DASHBOARD_URL as string | undefined) || ''
).trim()

export const DATART_LOGIN_HINT = 'demo / 123456'

export const hasDatartShareUrl = Boolean(DATART_DASHBOARD_URL)

export function getDatartOpenUrl(): string {
  return DATART_DASHBOARD_URL || DATART_BASE_URL
}

/** 探测 Datart 是否可访问（开发环境用） */
export async function isDatartReachable(): Promise<boolean> {
  try {
    await fetch(`${DATART_BASE_URL}/`, {
      mode: 'no-cors',
      signal: AbortSignal.timeout(3000),
    })
    return true
  } catch {
    return false
  }
}

export function openDatartDashboard(): void {
  const url = getDatartOpenUrl()
  const opened = window.open(url, '_blank', 'noopener,noreferrer')
  if (!opened) {
    window.location.assign(url)
  }
}

