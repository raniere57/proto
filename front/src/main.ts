import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import { css } from '@primeuix/styled'
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
  injectPrimeVueStyle('inputtext', (InputTextStyle as any).style)
  injectPrimeVueStyle('password', (PasswordStyle as any).style)
  injectPrimeVueStyle('button', (ButtonStyle as any).style)
} catch (e) {
  console.warn('PrimeVue style preload failed (non-critical):', e)
}

function injectPrimeVueStyle(name: string, rawCSS: string) {
  const resolved = (css as any)(['', ''], rawCSS) as string
  const el = document.createElement('style')
  el.setAttribute('type', 'text/css')
  el.setAttribute('data-primevue-style-id', name)
  el.textContent = resolved
  document.head.appendChild(el)
}

const theme = useTheme()
theme.initTheme()

const auth = useAuthStore()
auth.initAuth().finally(() => {
  app.mount('#app')
})
