<template>
  <div>
    <div class="page-header">
      <h1>Relacionar Protocolos</h1>
      <p>Vincule protocolos NOC com protocolos de suporte FTTH</p>
    </div>

    <div v-if="loading" class="card"><ProgressSpinner /></div>

    <template v-if="relacoes">
      <div class="card">
        <div class="form-grid">
          <div class="field">
            <label>Protocolo NOC</label>
            <Select v-model="protocoloSelecionado" :options="relacoes.protocolos" optionLabel="numero" optionValue="id" placeholder="Selecione..." filter fluid />
          </div>
          <div class="field">
            <label>Protocolo Suporte FTTH</label>
            <Select v-model="suporteSelecionado" :options="relacoes.suportes" optionLabel="descricao" optionValue="id" placeholder="Selecione..." filter fluid />
          </div>
        </div>
        <div class="actions">
          <Button label="Vincular" icon="pi pi-link" @click="vincular('adicionar')" :disabled="!protocoloSelecionado || !suporteSelecionado" />
          <Button label="Remover Vínculo" icon="pi pi-unlink" severity="danger" @click="vincular('remover')" :disabled="!protocoloSelecionado || !suporteSelecionado" />
        </div>
      </div>

      <div class="card">
        <h3>Vínculos Atuais</h3>
        <DataTable :value="vinculosLista" stripedRows>
          <Column field="protocolo" header="Protocolo NOC" />
          <Column field="suportes" header="Suportes Vinculados" />
          <template #empty>
            <div class="empty-state"><i class="pi pi-link"></i><p>Nenhum vínculo encontrado</p></div>
          </template>
        </DataTable>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'
import { useToast } from 'primevue/usetoast'
import { listarRelacoes, vincularProtocolos } from '@/api/dashboard'
import { extractError } from '@/api/client'

const toast = useToast()
const loading = ref(true)
const relacoes = ref<any>(null)
const protocoloSelecionado = ref<number | null>(null)
const suporteSelecionado = ref<number | null>(null)

const vinculosLista = computed(() => {
  if (!relacoes.value) return []
  return Object.entries(relacoes.value.relacoes || {}).map(([id, suportes]: [string, any]) => ({
    protocolo: relacoes.value.protocolos?.find((p: any) => p.id === Number(id))?.numero || id,
    suportes: (suportes as number[]).length || 0,
  }))
})

async function vincular(acao: string) {
  if (!protocoloSelecionado.value || !suporteSelecionado.value) return
  try {
    await vincularProtocolos(protocoloSelecionado.value, suporteSelecionado.value, acao)
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Operação realizada', life: 3000 })
    relacoes.value = await listarRelacoes()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  }
}

onMounted(async () => {
  try {
    relacoes.value = await listarRelacoes()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.actions { display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem; }

</style>
