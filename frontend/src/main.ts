import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElLoading } from 'element-plus'

import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler } from './api/request'
import { useAuthStore } from './stores/auth'
import { useLocaleStore } from './stores/locale'
import './lib/gsap'
import './styles/main.css'
import './styles/now-ui-theme.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.directive('loading', ElLoading.directive)

const localeStore = useLocaleStore(pinia)
document.documentElement.lang = localeStore.locale === 'en' ? 'en' : 'zh-CN'

const auth = useAuthStore(pinia)
setUnauthorizedHandler(() => auth.handleUnauthorized())

app.mount('#app')
