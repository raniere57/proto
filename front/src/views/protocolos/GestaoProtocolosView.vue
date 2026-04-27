<template>
  <div>
    <div class="page-header">
      <h1>Gestão de Protocolos NOC</h1>
      <p>Acompanhamento de protocolos ativos com indicador de tempo</p>
    </div>

    <div class="card" v-if="loading">
      <ProgressSpinner />
    </div>

    <div class="card" v-else>
      <DataTable :value="protocolos" stripedRows paginator :rows="20" sortField="data_criacao" :sortOrder="-1">
        <Column field="numero_chamado_interno" header="Nº Chamado" sortable />
        <Column field="tipo_evento" header="Evento" sortable>
          <template #body="{ data }">
            <Tag :value="data.tipo_evento" :severity="eventoColor(data.tipo_evento)" />
          </template>
        </Column>
        <Column field="tipo_rede" header="Rede" sortable />
        <Column field="estado" header="UF" sortable />
        <Column field="responsavel_trecho" header="Responsável" sortable />
        <Column header="Tempo">
          <template #body="{ data }">
            <Tag :value="tempoDecorrido(data.data_criacao)" :severity="tempoSeverity(data.data_criacao)" />
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
          <div class="empty-state"><i class="pi pi-check-circle"></i><p>Nenhum protocolo ativo no momento</p></div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listarProtocolos } from '@/api/protocolos'
import { extractError } from '@/api/client'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'

const toast = useToast()
const protocolos = ref<any[]>([])
const loading = ref(true)

function eventoColor(e: string) {
  const map: Record<string, string> = { RUPTURA: 'danger', ATENUAÇÃO: 'warn', INDISPONIBILIDADE: 'info', OSCILAÇÃO: 'warn' }
  return map[e] || 'contrast'
}

function tempoDecorrido(d: string | null | undefined) {
  if (!d) return '-'
  const diff = Date.now() - new Date(d).getTime()
  const horas = Math.floor(diff / 3600000)
  if (horas < 1) return `${Math.floor(diff / 60000)}min`
  if (horas < 24) return `${horas}h`
  return `${Math.floor(horas / 24)}d`
}

function tempoSeverity(d: string | null | undefined) {
  if (!d) return 'contrast'
  const diff = Date.now() - new Date(d).getTime()
  const horas = diff / 3600000
  if (horas < 3) return 'success'
  if (horas < 6) return 'warn'
  return 'danger'
}

onMounted(async () => {
  try {
    protocolos.value = await listarProtocolos({ ativo: true })
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally {
    loading.value = false
  }
})
</script>
