<template>
  <div>
    <div class="page-header">
      <h1>Detalhes do Protocolo de Suporte</h1>
      <p v-if="protocolo">Protocolo #{{ protocolo.id }}</p>
    </div>

    <div v-if="loading" class="card"><ProgressSpinner /></div>

    <div v-else-if="error" class="card">
      <Message severity="error">{{ error }}</Message>
    </div>

    <template v-if="protocolo">
      <div class="card">
        <div class="header-actions">
          <Tag :value="protocolo.ativo ? 'Ativo' : 'Inativo'" :severity="protocolo.ativo ? 'danger' : 'info'" />
          <router-link to="/suporte"><Button label="Voltar" icon="pi pi-arrow-left" severity="secondary" /></router-link>
        </div>

        <Divider />

        <div class="info-grid">
          <div class="info-item"><strong>Serviço:</strong> {{ protocolo.id_cliente_servico }}</div>
          <div class="info-item"><strong>Tipo Atendimento:</strong> {{ protocolo.id_tipo_atendimento }}</div>
          <div class="info-item"><strong>Status:</strong> {{ protocolo.id_atendimento_status }}</div>
          <div class="info-item"><strong>Protocolo Atendimento:</strong> {{ protocolo.protocolo_atendimento || '-' }}</div>
          <div class="info-item"><strong>Data Falha:</strong> {{ formatDate(protocolo.data_hora_falha) }}</div>
          <div class="info-item"><strong>Bairro:</strong> {{ protocolo.bairro || '-' }}</div>
          <div class="info-item"><strong>Clientes Afetados:</strong> {{ protocolo.clientes_afetados || '-' }}</div>
        </div>

        <Divider />

        <div class="field">
          <label><strong>Descrição:</strong></label>
          <p class="descricao">{{ protocolo.descricao || 'Sem descrição' }}</p>
        </div>

        <div v-if="protocolo.informacoes_tecnicas?.length" class="tech-section">
          <Divider />
          <h3>Informações Técnicas ({{ protocolo.informacoes_tecnicas.length }} registros)</h3>
          <DataTable :value="protocolo.informacoes_tecnicas.slice(0, 50)" stripedRows>
            <Column field="slot" header="Slot" />
            <Column field="pon" header="PON" />
            <Column field="rota" header="Rota" />
            <Column field="cto" header="CTO" />
            <template #empty><p class="empty-small">Nenhum registro técnico</p></template>
          </DataTable>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import { getSuporte } from '@/api/suporte'
import { extractError } from '@/api/client'
import type { SuporteProtocolo } from '@/api/suporte'

const route = useRoute()
const toast = useToast()
const protocolo = ref<SuporteProtocolo | null>(null)
const loading = ref(true)
const error = ref('')

function formatDate(d: string | null | undefined) {
  if (!d) return '-'
  return new Date(d).toLocaleString('pt-BR')
}

onMounted(async () => {
  try {
    protocolo.value = await getSuporte(Number(route.params.id))
  } catch (err) {
    error.value = extractError(err)
    toast.add({ severity: 'error', summary: 'Erro', detail: error.value, life: 5000 })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.header-actions { display: flex; justify-content: space-between; align-items: center; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.info-item { background: #f8f9fa; padding: 0.75rem 1rem; border-radius: 8px; }
.descricao { white-space: pre-wrap; background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 0.5rem; }
</style>
