<template>
  <Toast />
  <div class="layout">
    <!-- Mobile overlay -->
    <div v-if="sidebarOpen && isMobile" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <aside v-if="auth.isAuthenticated" class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <h3>Megalink</h3>
        <small>Sistema de Protocolos</small>
        <button v-if="isMobile" class="close-btn" @click="sidebarOpen = false"><i class="pi pi-times"></i></button>
      </div>
      <nav>
        <router-link v-for="item in menuItems" :key="item.to" :to="item.to" class="nav-item" @click="sidebarOpen = false">
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </router-link>
        <div v-if="auth.isStaff" class="admin-section">
          <div class="admin-title">ADMIN</div>
          <button class="nav-item nav-btn" @click="handleImportarServicos" :disabled="importando">
            <i class="pi pi-cloud-download"></i>
            <span>{{ importando ? 'Importando...' : 'Importar Serviços' }}</span>
          </button>
        </div>
      </nav>
      <div class="sidebar-footer">
        <span class="user-name">
          {{ auth.user?.first_name || auth.user?.username }}
          <span v-if="auth.isStaff" class="staff-badge">ADMIN</span>
        </span>
        <div class="footer-actions">
          <button class="btn-footer" @click="toggleTheme()" title="Alternar tema">
            <i :class="isDark ? 'pi pi-sun' : 'pi pi-moon'"></i>
          </button>
          <button class="btn-footer" @click="showPasswordDialog = true" title="Alterar senha"><i class="pi pi-key"></i></button>
          <button class="btn-footer btn-logout" @click="auth.logout()" title="Sair"><i class="pi pi-sign-out"></i></button>
        </div>
      </div>
    </aside>

    <main class="main-content" :class="{ collapsed: !sidebarOpen && isMobile }">
      <button v-if="auth.isAuthenticated && isMobile" class="hamburger" @click="sidebarOpen = !sidebarOpen">
        <i class="pi pi-bars"></i>
      </button>
      <router-view />
    </main>

    <Dialog v-model:visible="showPasswordDialog" header="Alterar Senha" modal class="password-dialog">
      <form @submit.prevent="handleChangePassword" class="password-form">
        <div class="field">
          <label>Senha Atual</label>
          <Password v-model="passwordForm.current" :feedback="false" toggleMask fluid />
        </div>
        <div class="field">
          <label>Nova Senha</label>
          <Password v-model="passwordForm.newPass" :feedback="true" toggleMask fluid
            :promptLabel="'Digite uma senha'" :weakLabel="'Fraca'" :mediumLabel="'Média'" :strongLabel="'Forte'" />
        </div>
        <div class="field">
          <label>Confirmar Nova Senha</label>
          <Password v-model="passwordForm.confirm" :feedback="false" toggleMask fluid />
        </div>
      </form>
      <template #footer>
        <Button label="Cancelar" severity="secondary" @click="showPasswordDialog = false" />
        <Button label="Salvar" icon="pi pi-check" :loading="passwordLoading" @click="handleChangePassword" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { changePassword } from '@/api/auth'
import { importarServicos } from '@/api/protocolos'
import { extractError } from '@/api/client'
import { useTheme } from '@/composables/useTheme'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import Password from 'primevue/password'
import Button from 'primevue/button'

const auth = useAuthStore()
const toast = useToast()
const { toggleTheme, isDark } = useTheme()
const sidebarOpen = ref(false)
const isMobile = ref(false)
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const importando = ref(false)

const passwordForm = reactive({ current: '', newPass: '', confirm: '' })

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) sidebarOpen.value = true
}
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))

const menuItems = computed(() => {
  const items = [
    { to: '/', icon: 'pi pi-home', label: 'Home', show: true },
    { to: '/protocolos/criar', icon: 'pi pi-plus-circle', label: 'Novo Protocolo', show: true },
    { to: '/gestao', icon: 'pi pi-list', label: 'Gestão NOC', show: true },
    { to: '/suporte', icon: 'pi pi-headphones', label: 'Suporte FTTH', show: true },
    { to: '/suporte/criar', icon: 'pi pi-plus', label: 'Novo Suporte', show: true },
    { to: '/dashboard', icon: 'pi pi-chart-bar', label: 'Dashboard', show: true },
    { to: '/relacionar', icon: 'pi pi-link', label: 'Relacionar', show: auth.isStaff },
    { to: '/admin/users', icon: 'pi pi-users', label: 'Usuários', show: auth.isStaff },
  ]
  return items.filter((i) => i.show)
})

async function handleChangePassword() {
  if (!passwordForm.current || !passwordForm.newPass || !passwordForm.confirm) {
    toast.add({ severity: 'warn', summary: 'Campos obrigatórios', detail: 'Preencha todos os campos', life: 4000 })
    return
  }
  if (passwordForm.newPass !== passwordForm.confirm) {
    toast.add({ severity: 'warn', summary: 'Senhas não conferem', detail: 'Nova senha e confirmação devem ser iguais', life: 4000 })
    return
  }
  passwordLoading.value = true
  try {
    const res = await changePassword(passwordForm.current, passwordForm.newPass)
    toast.add({ severity: 'success', summary: 'Sucesso', detail: res.message, life: 3000 })
    showPasswordDialog.value = false
    passwordForm.current = ''; passwordForm.newPass = ''; passwordForm.confirm = ''
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally { passwordLoading.value = false }
}

async function handleImportarServicos() {
  importando.value = true
  try {
    const res = await importarServicos()
    toast.add({ severity: 'success', summary: 'Importação concluída', detail: res.message, life: 5000 })
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro na importação', detail: extractError(err), life: 5000 })
  } finally { importando.value = false }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; color: #2c3e50; }

.layout { display: flex; min-height: 100vh; }

.sidebar-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 99; }

.sidebar {
  width: 250px; background: #1a1a2e; color: white; display: flex;
  flex-direction: column; position: fixed; height: 100vh; z-index: 100;
  transition: transform 0.3s ease;
}
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
}

.sidebar-header { padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); position: relative; }
.sidebar-header h3 { margin: 0; font-size: 1.3rem; }
.sidebar-header small { opacity: 0.7; font-size: 0.8rem; }
.close-btn { position: absolute; top: 1rem; right: 1rem; background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; }

.sidebar nav { flex: 1; padding: 0.5rem 0; overflow-y: auto; }

.nav-item {
  display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1.5rem;
  color: rgba(255,255,255,0.7); text-decoration: none; transition: all 0.2s;
  border-left: 3px solid transparent; font-size: 0.95rem;
}
.nav-item:hover { background: rgba(255,255,255,0.1); color: white; cursor: pointer; }
.nav-item.router-link-active {
  background: rgba(102,126,234,0.2); color: white; border-left-color: #667eea;
}
.nav-btn { background: none; border: none; width: 100%; text-align: left; font-family: inherit; font-size: 0.95rem; }
.nav-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.admin-section { border-top: 1px solid rgba(255,255,255,0.1); margin-top: 0.5rem; padding-top: 0.5rem; }
.admin-title { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; padding: 0.5rem 1.5rem 0.25rem; opacity: 0.4; }

.sidebar-footer { padding: 0.75rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); }
.user-name { font-size: 0.85rem; opacity: 0.8; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.staff-badge { font-size: 0.65rem; background: #e74c3c; color: white; padding: 0.1rem 0.4rem; border-radius: 4px; font-weight: 700; }
.footer-actions { display: flex; gap: 0.5rem; }
.btn-footer {
  flex: 1; background: transparent; border: 1px solid rgba(255,255,255,0.2); color: white;
  padding: 0.5rem; border-radius: 6px; cursor: pointer; display: flex;
  align-items: center; justify-content: center; gap: 0.4rem; transition: all 0.2s; font-size: 0.9rem;
}
.btn-footer:hover { background: rgba(255,255,255,0.1); }
.btn-logout:hover { background: rgba(231,76,60,0.3); border-color: #e74c3c; }

.main-content {
  margin-left: 250px; flex: 1; padding: 1.5rem; max-width: calc(100vw - 250px);
  transition: margin-left 0.3s ease;
}
.main-content.collapsed { margin-left: 0; max-width: 100vw; }

.hamburger {
  background: #1a1a2e; color: white; border: none; border-radius: 8px;
  padding: 0.5rem 0.75rem; font-size: 1.2rem; cursor: pointer; margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .main-content { margin-left: 0; max-width: 100vw; }
}

.page-header { margin-bottom: 1.5rem; }
.page-header h1 { color: #1a1a2e; font-size: 1.6rem; margin-bottom: 0.25rem; }
.page-header p { color: #6c757d; font-size: 0.95rem; }

.card {
  background: white; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1.5rem;
}

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.form-grid .full-width { grid-column: 1 / -1; }
.field { margin-bottom: 1.25rem; }
.field label { display: block; margin-bottom: 0.4rem; font-weight: 600; color: #2c3e50; font-size: 0.95rem; }

.password-form .field { margin-bottom: 1.25rem; }
.password-form .field label { display: block; margin-bottom: 0.4rem; font-weight: 600; color: #2c3e50; }

@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }

/* Empty states */
.empty-state { text-align: center; padding: 3rem 1rem; color: #6c757d; }
.empty-state i { font-size: 3rem; display: block; margin-bottom: 1rem; opacity: 0.4; }
.empty-state p { font-size: 1rem; }
.empty-small { text-align: center; padding: 1rem; color: #6c757d; }

/* PrimeVue overrides */
.p-dialog-header { padding: 1.25rem 1.5rem 0.5rem !important; }
.p-dialog-content { padding: 0.5rem 1.5rem !important; }
.p-dialog-footer { padding: 0.5rem 1.5rem 1.25rem !important; }
</style>
