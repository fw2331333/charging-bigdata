import en from './en'
import zh from './zh'

export type Locale = 'zh' | 'en'

export const messages = { zh, en } as const

export type MessageTree = typeof zh

function getByPath(obj: Record<string, unknown>, path: string): string | undefined {
  const val = path.split('.').reduce<unknown>((acc, key) => {
    if (acc && typeof acc === 'object' && key in (acc as object)) {
      return (acc as Record<string, unknown>)[key]
    }
    return undefined
  }, obj)
  return typeof val === 'string' ? val : undefined
}

export function translate(
  locale: Locale,
  key: string,
  params?: Record<string, string | number>,
): string {
  const raw = getByPath(messages[locale] as unknown as Record<string, unknown>, key)
    ?? getByPath(messages.zh as unknown as Record<string, unknown>, key)
    ?? key
  if (!params) return raw
  return Object.entries(params).reduce(
    (s, [k, v]) => s.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v)),
    raw,
  )
}
