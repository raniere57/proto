import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import { Theme } from '@primeuix/styled'
import BaseStyle from '@primevue/core/base/style'
import { registerPrimeVueComponents } from './plugins/primevue'
import { useTheme } from './composables/useTheme'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import 'primeicons/primeicons.css'
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

// Force PrimeVue CSS injection BEFORE app.mount()
// This prevents FOUC (Flash of Unstyled Content) on page refresh,
// since PrimeVue 4 normally injects CSS lazily on component mount.
try {
  if (!Theme.isStyleNameLoaded('common')) {
    const bs = BaseStyle as any
    const { primitive, semantic, global, style } = bs.getCommonTheme?.() || {}
    if (primitive?.css) bs.load(primitive.css, { name: 'primitive-variables' })
    if (semantic?.css) bs.load(semantic.css, { name: 'semantic-variables' })
    if (global?.css) bs.load(global.css, { name: 'global-variables' })
    if (style) bs.loadStyle({ name: 'global-style' }, style)
    Theme.setLoadedStyleName('common')
  }
} catch (e) {
  console.warn('PrimeVue preload CSS failed (non-critical):', e)
}

const theme = useTheme()
theme.initTheme()

const auth = useAuthStore()
auth.initAuth().finally(() => {
  app.mount('#app')
})
