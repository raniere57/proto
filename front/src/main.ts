import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import BaseStyle from '@primevue/core/base/style'
import InputTextStyle from 'primevue/inputtext/style'
import PasswordStyle from 'primevue/password/style'
import ButtonStyle from 'primevue/button/style'
import { registerPrimeVueComponents } from './plugins/primevue'
import { useTheme } from './composables/useTheme'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import 'primeicons/primeicons.css'
import './assets/base.css'
import './assets/dark.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark',
    },
  },
})
app.use(ToastService)
registerPrimeVueComponents(app)

try {
  ;(BaseStyle as any).loadCSS?.()
  ;(BaseStyle as any).loadStyle?.()
  ;(InputTextStyle as any).loadCSS?.()
  ;(InputTextStyle as any).loadStyle?.()
  ;(PasswordStyle as any).loadCSS?.()
  ;(PasswordStyle as any).loadStyle?.()
  ;(ButtonStyle as any).loadCSS?.()
  ;(ButtonStyle as any).loadStyle?.()
} catch (e) {
  console.warn('PrimeVue style preload failed (non-critical):', e)
}

const theme = useTheme()
theme.initTheme()

const auth = useAuthStore()
auth.initAuth().finally(() => {
  app.mount('#app')
})
