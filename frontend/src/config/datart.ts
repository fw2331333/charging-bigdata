/** Datart BI 大屏（手册 §5.1–5.3） */

export const DATART_BASE_URL = (
  (import.meta.env.VITE_DATART_BASE_URL as string | undefined) || 'http://127.0.0.1:8088'
).replace(/\/$/, '')

/** Datart 分享 Dashboard 完整 URL（含 shareDashboard/...） */
export const DATART_DASHBOARD_URL = (
  (import.meta.env.VITE_DATART_DASHBOARD_URL as string | undefined) || ''
).trim()

export const DATART_LOGIN_HINT = 'admin / 123456'

export const hasDatartShareUrl = Boolean(DATART_DASHBOARD_URL)

/** 构建时若写死 127.0.0.1，公网访问时改为当前主机名（:8088） */
function resolveDatartHost(url: string): string {
  if (!url || typeof window === 'undefined') return url
  try {
    const parsed = new URL(url)
    const builtForLocal =
      parsed.hostname === '127.0.0.1' || parsed.hostname === 'localhost'
    const onRemote =
      window.location.hostname !== '127.0.0.1' &&
      window.location.hostname !== 'localhost'
    if (builtForLocal && onRemote) {
      parsed.hostname = window.location.hostname
      return parsed.toString().replace(/\/$/, '')
    }
  } catch {
    /* ignore malformed url */
  }
  return url.replace(/\/$/, '')
}

export function getDatartOpenUrl(): string {
  const configured = DATART_DASHBOARD_URL || DATART_BASE_URL
  return resolveDatartHost(configured)
}

/** 探测 Datart 是否可访问（开发环境用） */
export async function isDatartReachable(): Promise<boolean> {
  try {
    await fetch(`${getDatartOpenUrl()}/`, {
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

