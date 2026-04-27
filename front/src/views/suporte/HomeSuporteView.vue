<template>
  <div>
    <div class="page-header">
      <h1>Suporte FTTH</h1>
      <p>Protocolos de suporte técnico</p>
    </div>

    <div class="card">
      <div class="filters">
        <Select v-model="filtroAtivo" :options="filtroStatus" optionLabel="label" optionValue="value" placeholder="Status" clearable @change="carregar" />
      </div>
    </div>

    <div class="card" v-if="loading"><ProgressSpinner /></div>

    <DataTable v-else :value="protocolos" stripedRows paginator :rows="15">
      <Column field="id" header="#" sortable />
      <Column field="id_cliente_servico" header="Serviço" />
      <Column field="id_tipo_atendimento" header="Tipo">
        <template #body="{ data }">
          <Tag :value="tipoNome(data.id_tipo_atendimento)" />
        </template>
      </Column>
      <Column header="Status">
        <template #body="{ data }">
          <Tag :value="data.ativo ? 'Ativo' : 'Inativo'" :severity="data.ativo ? 'danger' : 'info'" />
        </template>
      </Column>
      <Column field="data_hora_falha" header="Data Falha">
        <template #body="{ data }">{{ formatDate(data.data_hora_falha) }}</template>
      </Column>
      <Column header="Ações">
        <template #body="{ data }">
          <router-link :to="`/suporte/${data.id}`">
            <Button icon="pi pi-eye" text rounded />
          </router-link>
        </template>
      </Column>
      <template #empty>
        <div class="empty-state"><i class="pi pi-inbox"></i><p>Nenhum protocolo de suporte encontrado</p></div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'
import { listarSuporte, type SuporteProtocolo } from '@/api/suporte'
import { extractError } from '@/api/client'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const protocolos = ref<SuporteProtocolo[]>([])
const loading = ref(true)
const filtroAtivo = ref()

const filtroStatus = [
  { label: 'Ativos', value: true },
  { label: 'Inativos', value: false },
]

function formatDate(d: string | null | undefined) {
  if (!d) return '-'
  return new Date(d).toLocaleString('pt-BR')
}

function tipoNome(id: number) {
  const map: Record<number, string> = {
    938: 'NOC FTTH', 939: 'FTTH ATENUAÇÃO CTO', 940: 'FTTH ROTA ATENUADA',
    941: 'FTTH RUPTURA', 942: 'FTTH OLT INDISPONIVEL', 946: 'FTTH CTO SEM SINAL',
    957: 'FTTH AMPLIAÇÃO CTO', 958: 'FTTH CONCENTRADOR INDISP',
  }
  return map[id] || `Tipo ${id}`
}

async function carregar() {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filtroAtivo.value !== undefined && filtroAtivo.value !== null) params.ativo = filtroAtivo.value
    protocolos.value = await listarSuporte(params)
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally {
    loading.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
.filters { display: flex; gap: 1rem; }
</style>
