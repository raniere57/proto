<template>
  <div>
    <div class="page-header">
      <h1>Protocolos NOC</h1>
      <p>Listagem de protocolos de atendimento</p>
    </div>

    <div class="card">
      <div class="filters">
        <InputText v-model="search" placeholder="Buscar por número..." @input="debounceSearch" />
        <Select v-model="filtroEvento" :options="tiposEvento" optionLabel="nome" optionValue="codigo" placeholder="Tipo de Evento" clearable @change="carregar" />
        <Select v-model="filtroRede" :options="tiposRede" optionLabel="nome" optionValue="codigo" placeholder="Tipo de Rede" clearable @change="carregar" />
        <Select v-model="filtroAtivo" :options="filtroStatus" optionLabel="label" optionValue="value" placeholder="Status" clearable @change="carregar" />
        <div class="export-buttons">
          <Button icon="pi pi-file-excel" label="XLSX" severity="success" size="small" @click="exportar('excel')" />
          <Button icon="pi pi-file" label="CSV" severity="info" size="small" @click="exportar('csv')" />
        </div>
      </div>
    </div>

    <div class="card" v-if="loading">
      <ProgressSpinner />
    </div>

    <DataTable v-else :value="protocolos" stripedRows paginator :rows="12" sortField="data_criacao" :sortOrder="-1" :loading="loading">
      <Column field="numero_chamado_interno" header="Número" sortable />
      <Column field="tipo_evento" header="Evento" sortable>
        <template #body="{ data }">
          <Tag :value="data.tipo_evento" :severity="eventoColor(data.tipo_evento)" />
        </template>
      </Column>
      <Column field="tipo_rede" header="Rede" sortable />
      <Column field="estado" header="UF" sortable />
      <Column field="responsavel_trecho" header="Responsável" sortable />
      <Column field="data_criacao" header="Criado em" sortable>
        <template #body="{ data }">
          {{ formatDate(data.data_criacao) }}
        </template>
      </Column>
      <Column header="Status">
        <template #body="{ data }">
          <Tag :value="data.ativo ? 'Ativo' : 'Resolvido'" :severity="data.ativo ? 'danger' : 'success'" />
        </template>
      </Column>
      <Column header="Ações">
        <template #body="{ data }">
          <router-link :to="`/protocolos/${data.id}`">
            <Button icon="pi pi-eye" text rounded />
          </router-link>
        </template>
      </Column>
      <template #empty>
        <div class="empty-state"><i class="pi pi-inbox"></i><p>Nenhum protocolo encontrado</p></div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listarProtocolos, getExportCsvUrl, getExportExcelUrl } from '@/api/protocolos'
import { extractError } from '@/api/client'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'

const toast = useToast()
const protocolos = ref<any[]>([])
const loading = ref(true)
const search = ref('')
const filtroEvento = ref()
const filtroRede = ref()
const filtroAtivo = ref()

const filtroStatus = [
  { label: 'Ativos', value: true },
  { label: 'Inativos', value: false },
]

const tiposEvento = [
  { codigo: 'RUPTURA', nome: 'Ruptura' }, { codigo: 'ATENUAÇÃO', nome: 'Atenuação' },
  { codigo: 'INDISPONIBILIDADE', nome: 'Indisponibilidade' }, { codigo: 'SATURAÇÃO', nome: 'Saturação' },
  { codigo: 'TAXA DE ERRO', nome: 'Taxa de Erro' }, { codigo: 'OSCILAÇÃO', nome: 'Oscilação' },
  { codigo: 'FALHA ELÉTRICA', nome: 'Falha Elétrica' }, { codigo: 'OUTRAS', nome: 'Outros' },
]
const tiposRede = [
  { codigo: 'METRO', nome: 'Rede Metro' }, { codigo: 'DWDM', nome: 'Rede DWDM' },
  { codigo: 'CAPACIDADE', nome: 'Capacidade' },
]

let debounceTimer: ReturnType<typeof setTimeout>
function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(carregar, 400)
}

function eventoColor(evento: string) {
  const map: Record<string, string> = { RUPTURA: 'danger', ATENUAÇÃO: 'warn', INDISPONIBILIDADE: 'info', SATURAÇÃO: 'warn', OSCILAÇÃO: 'warn', 'FALHA ELÉTRICA': 'danger' }
  return map[evento] || 'contrast'
}

function formatDate(d: string | null | undefined) {
  if (!d) return '-'
  return new Date(d).toLocaleString('pt-BR')
}

function exportar(formato: 'csv' | 'excel') {
  const params: Record<string, any> = {}
  if (filtroEvento.value) params.tipo_evento = filtroEvento.value
  if (filtroRede.value) params.tipo_rede = filtroRede.value
  if (filtroAtivo.value !== undefined && filtroAtivo.value !== null) params.ativo = filtroAtivo.value
  const url = formato === 'csv' ? getExportCsvUrl(params) : getExportExcelUrl(params)
  window.open(url, '_blank')
}

async function carregar() {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (search.value) params.search = search.value
    if (filtroEvento.value) params.tipo_evento = filtroEvento.value
    if (filtroRede.value) params.tipo_rede = filtroRede.value
    if (filtroAtivo.value !== undefined && filtroAtivo.value !== null) params.ativo = filtroAtivo.value
    protocolos.value = await listarProtocolos(params)
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally {
    loading.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
.filters { display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; }
.export-buttons { display: flex; gap: 0.4rem; margin-left: auto; }
</style>
