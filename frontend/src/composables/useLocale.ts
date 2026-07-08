import { storeToRefs } from 'pinia'
import { useLocaleStore } from '@/stores/locale'

export function useLocale() {
  const store = useLocaleStore()
  const { locale, isEn } = storeToRefs(store)
  return { locale, isEn, setLocale: store.setLocale, t: store.t }
}
