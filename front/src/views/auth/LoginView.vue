<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <svg width="48" height="48" viewBox="0 0 52 52" fill="none">
          <rect width="52" height="52" rx="12" fill="url(#lg)"/>
          <path d="M16 32V20l10 6v-6l10 6v12l-10-6v6l-10-6z" fill="white" opacity="0.9"/>
          <path d="M26 14l8 4.8v3.2l-8-4.8-8 4.8v-3.2L26 14z" fill="white" opacity="0.5"/>
          <defs>
            <linearGradient id="lg" x1="0" y1="0" x2="52" y2="52">
              <stop stop-color="#667eea"/><stop offset="1" stop-color="#764ba2"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
      <h1>Protocolos Megalink</h1>
      <p class="subtitle">Faça login para continuar</p>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <label for="username">Usuário</label>
          <InputText id="username" v-model="username" placeholder="Digite seu usuário" fluid :disabled="auth.loading" autocomplete="username" />
        </div>
        <div class="field">
          <label for="password">Senha</label>
          <Password id="password" v-model="password" placeholder="Digite sua senha" :feedback="false" fluid :disabled="auth.loading" toggleMask autocomplete="current-password" />
        </div>
        <Button type="submit" label="Entrar" icon="pi pi-sign-in" class="w-full" :loading="auth.loading" />
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'
import { extractError } from '@/api/client'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

const auth = useAuthStore()
const toast = useToast()
const username = ref('')
const password = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    toast.add({ severity: 'warn', summary: 'Campos obrigatórios', detail: 'Preencha usuário e senha', life: 4000 })
    return
  }
  try {
    await auth.loginAction(username.value, password.value)
    toast.add({ severity: 'success', summary: 'Bem-vindo', detail: `Olá, ${username.value}`, life: 3000 })
  } catch (err) {
    const detail = extractError(err)
    toast.add({ severity: 'error', summary: 'Erro de autenticação', detail, life: 5000 })
  }
}
</script>

<style scoped>
.login-page {
  display: flex; align-items: center; justify-content: center; min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-card {
  background: white; border-radius: 20px; padding: 3rem; width: 420px; max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-logo { text-align: center; margin-bottom: 1rem; }
.login-card h1 { color: #1a1a2e; text-align: center; margin-bottom: 0.25rem; font-size: 1.8rem; }
.subtitle { color: #6c757d; text-align: center; margin-bottom: 2rem; font-size: 0.95rem; }
.field { margin-bottom: 1.5rem; }
.field label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50; font-size: 0.95rem; }
.w-full { width: 100%; }
</style>
