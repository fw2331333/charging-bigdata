/** BI API 短时缓存（60s TTL），减少页面切换重复请求 */

const TTL_MS = 60_000

interface Entry<T> {
  data: T
  fetchedAt: number
}

const store = new Map<string, Entry<unknown>>()

export async function cachedBiFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const hit = store.get(key)
  if (hit && Date.now() - hit.fetchedAt < TTL_MS) {
    return hit.data as T
  }
  const data = await fetcher()
  store.set(key, { data, fetchedAt: Date.now() })
  return data
}

export function invalidateBiCache(prefix?: string): void {
  if (!prefix) {
    store.clear()
    return
  }
  for (const key of store.keys()) {
    if (key.startsWith(prefix)) store.delete(key)
  }
}
