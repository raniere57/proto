import { ref, computed } from 'vue'

const STORAGE_KEY = 'theme'
type Theme = 'light' | 'dark'

const currentTheme = ref<Theme>((localStorage.getItem(STORAGE_KEY) as Theme) || 'light')

export function useTheme() {
  const isDark = computed(() => currentTheme.value === 'dark')

  function applyTheme(theme: Theme) {
    currentTheme.value = theme
    localStorage.setItem(STORAGE_KEY, theme)
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }

  function toggleTheme() {
    applyTheme(currentTheme.value === 'light' ? 'dark' : 'light')
  }

  function initTheme() {
    applyTheme(currentTheme.value)
  }

  return { currentTheme, isDark, toggleTheme, initTheme }
}
