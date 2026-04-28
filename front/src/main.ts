import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import BaseStyle from '@primevue/core/base/style'
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

// PrimeVue 4 injeta CSS lazy em onMounted. Forçamos o carregamento
// dos estilos base e das variáveis do tema antes do mount para
// evitar FOUC (Flash of Unstyled Content) na primeira renderização.
try {
  const bs = BaseStyle as any
  bs.loadCSS?.()
  bs.loadStyle?.()
} catch (e) {
  console.warn('PrimeVue base style preload failed (non-critical):', e)
}

const theme = useTheme()
theme.initTheme()

const auth = useAuthStore()
auth.initAuth().finally(() => {
  app.mount('#app')
})
