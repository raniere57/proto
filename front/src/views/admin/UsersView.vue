<template>
  <div>
    <div class="page-header">
      <h1>Gerenciar Usuários</h1>
      <p>Apenas administradores</p>
    </div>

    <div v-if="loading" class="card"><ProgressSpinner /></div>

    <div class="card" v-else>
      <div class="toolbar">
        <InputText v-model="search" placeholder="Buscar usuário..." @input="debounceSearch" fluid />
      </div>

      <DataTable :value="users" stripedRows paginator :rows="20">
        <Column field="username" header="Usuário" sortable />
        <Column field="first_name" header="Nome" sortable />
        <Column field="email" header="Email" sortable />
        <Column header="Grupos">
          <template #body="{ data }">
            <Tag v-for="g in data.groups" :key="g" :value="g" class="mr-1" severity="info" />
            <span v-if="!data.groups?.length">—</span>
          </template>
        </Column>
        <Column header="Status">
          <template #body="{ data }">
            <Tag :value="data.is_active ? 'Ativo' : 'Inativo'" :severity="data.is_active ? 'success' : 'danger'" />
          </template>
        </Column>
        <Column header="Admin">
          <template #body="{ data }">
            <i v-if="data.is_staff" class="pi pi-check" style="color: #27ae60"></i>
            <i v-else class="pi pi-times" style="color: #e74c3c"></i>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import { listUsers } from '@/api/auth'
import { extractError } from '@/api/client'
import { useToast } from 'primevue/usetoast'
import type { User } from '@/types'

const toast = useToast()
const users = ref<User[]>([])
const loading = ref(true)
const search = ref('')

let debounceTimer: ReturnType<typeof setTimeout>
function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(carregar, 400)
}

async function carregar() {
  loading.value = true
  try {
    users.value = await listUsers(search.value || undefined)
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally {
    loading.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
.toolbar { margin-bottom: 1rem; max-width: 300px; }
.mr-1 { margin-right: 0.25rem; }
</style>
