import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { guest: true, title: 'Login' },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Home', component: () => import('@/views/protocolos/HomeView.vue'), meta: { title: 'Protocolos NOC' } },
      { path: 'protocolos/criar', name: 'CriarProtocolo', component: () => import('@/views/protocolos/CriarProtocoloView.vue'), meta: { title: 'Novo Protocolo' } },
      { path: 'protocolos/:id', name: 'DetalhesProtocolo', component: () => import('@/views/protocolos/DetalhesProtocoloView.vue'), meta: { title: 'Detalhes do Protocolo' } },
      { path: 'gestao', name: 'GestaoProtocolos', component: () => import('@/views/protocolos/GestaoProtocolosView.vue'), meta: { title: 'Gestão NOC' } },
      { path: 'suporte/criar', name: 'CriarSuporte', component: () => import('@/views/suporte/CriarSuporteView.vue'), meta: { title: 'Novo Suporte FTTH' } },
      { path: 'suporte/:id', name: 'DetalhesSuporte', component: () => import('@/views/suporte/DetalhesSuporteView.vue'), meta: { title: 'Detalhes Suporte' } },
      { path: 'suporte', name: 'HomeSuporte', component: () => import('@/views/suporte/HomeSuporteView.vue'), meta: { title: 'Suporte FTTH' } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/DashboardView.vue'), meta: { title: 'Dashboard' } },
      { path: 'relacionar', name: 'Relacionar', component: () => import('@/views/protocolos/RelacionarView.vue'), meta: { title: 'Relacionar Protocolos' } },
      {
        path: 'admin/users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersView.vue'),
        meta: { requiresStaff: true, title: 'Usuários' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Página não encontrada' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (auth.isAuthenticated && !auth.user) {
    await auth.initAuth()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.guest && auth.isAuthenticated) {
    next('/')
    return
  }

  if (to.meta.requiresStaff && !auth.isStaff) {
    next('/')
    return
  }

  document.title = to.meta.title ? `${to.meta.title} — Megalink Protocolos` : 'Megalink Protocolos'
  next()
})

export default router
