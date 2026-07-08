import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { type Locale, translate } from '@/locales'

const STORAGE_KEY = 'charging_bigdata_locale'

function loadLocale(): Locale {
  const raw = localStorage.getItem(STORAGE_KEY)
  return raw === 'en' ? 'en' : 'zh'
}

export const useLocaleStore = defineStore('locale', () => {
  const locale = ref<Locale>(loadLocale())

  const isEn = computed(() => locale.value === 'en')

  function setLocale(next: Locale) {
    locale.value = next
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.lang = next === 'en' ? 'en' : 'zh-CN'
  }

  function t(key: string, params?: Record<string, string | number>) {
    return translate(locale.value, key, params)
  }

  return { locale, isEn, setLocale, t }
})
