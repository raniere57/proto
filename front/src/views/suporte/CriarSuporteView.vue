<template>
  <div>
    <div class="page-header">
      <h1>Criar Protocolo de Suporte FTTH</h1>
      <p>Preencha os dados para criar um protocolo de suporte</p>
    </div>

    <div class="card">
      <form @submit.prevent="salvar">
        <div class="form-grid">
          <div class="field">
            <label>Serviço <span class="required">*</span></label>
            <Select v-model="form.servico_id" :options="servicos" optionLabel="descricao" optionValue="id_cliente_servico" placeholder="Selecione..." filter fluid />
          </div>

          <div class="field">
            <label>Responsável</label>
            <Select v-model="form.responsavel_id" :options="responsaveis" optionLabel="nome" optionValue="id" placeholder="Selecione..." fluid />
          </div>

          <div class="field full-width">
            <label>Tipo de Atendimento <span class="required">*</span></label>
            <Select v-model="form.id_tipo_atendimento" :options="tiposAtendimento" optionLabel="nome" optionValue="codigo" placeholder="Selecione..." fluid />
          </div>

          <div class="field">
            <label>Status do Atendimento</label>
            <Select v-model="form.id_atendimento_status" :options="statusOptions" optionLabel="label" optionValue="value" fluid />
          </div>

          <div class="field">
            <label>Tipo de OS</label>
            <Select v-model="form.tipo_os" :options="tiposOs" optionLabel="nome" optionValue="codigo" placeholder="Selecione..." filter fluid />
          </div>

          <div class="field">
            <label>Data/Hora Falha</label>
            <DatePicker v-model="form.data_hora_falha" showTime hourFormat="24" fluid />
          </div>

          <div class="field">
            <label>Bairro</label>
            <InputText v-model="form.bairro" placeholder="Bairro afetado" fluid />
          </div>

          <div class="field">
            <label>Clientes Afetados</label>
            <InputText v-model="form.clientes_afetados" placeholder="Ex: 5 clientes" fluid />
          </div>
        </div>

        <Divider />
        <h3>Informações Técnicas</h3>

        <div class="form-grid">
          <div class="field">
            <label>Slot/PON <span class="required">*</span></label>
            <MultiSelect v-model="form.slot_pon" :options="slotPonOptions" placeholder="Selecione Slot/PON" filter fluid display="chip" />
          </div>

          <div class="field">
            <label>Rotas <span class="required">*</span></label>
            <MultiSelect v-model="form.rotas" :options="rotaOptions" placeholder="Selecione Rotas" filter fluid display="chip" />
          </div>

          <div class="field">
            <label>CTOs <span class="required">*</span></label>
            <MultiSelect v-model="form.ctos" :options="ctoOptions" placeholder="Selecione CTOs" filter fluid display="chip" />
          </div>
        </div>

        <Divider />

        <div class="field full-width">
          <label>Descrição</label>
          <Textarea v-model="form.descricao" rows="4" :autoResize="true" fluid />
        </div>

        <div class="actions">
          <Button type="submit" label="Criar Protocolo de Suporte" icon="pi pi-check" :loading="loading" />
          <Button label="Limpar" icon="pi pi-refresh" severity="secondary" @click="limpar" />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { criarSuporte, type CreateSuportePayload } from '@/api/suporte'
import { listarServicos, listarResponsaveis } from '@/api/protocolos'
import { extractError } from '@/api/client'

const router = useRouter()
const toast = useToast()
const servicos = ref<any[]>([])
const responsaveis = ref<any[]>([])
const loading = ref(false)

const form = reactive({
  servico_id: null as number | null,
  responsavel_id: null as number | null,
  id_tipo_atendimento: null as number | null,
  id_atendimento_status: 1,
  tipo_os: null as number | null,
  data_hora_falha: null as Date | null,
  descricao: '',
  bairro: '',
  clientes_afetados: '',
  slot_pon: [] as string[],
  rotas: [] as number[],
  ctos: [] as number[],
})

const statusOptions = [
  { label: 'PENDENTE (Abertura de OS)', value: 1 },
  { label: 'AGUARDANDO ANÁLISE', value: 2 },
]

const tiposAtendimento = [
  { codigo: 938, nome: 'NOC FTTH' }, { codigo: 939, nome: 'NOC FTTH > ATENUAÇÃO EM CTO' },
  { codigo: 940, nome: 'NOC FTTH > ROTA ATENUADA' }, { codigo: 941, nome: 'NOC FTTH > RUPTURA' },
  { codigo: 942, nome: 'NOC FTTH > OLT INDISPONIVEL' }, { codigo: 946, nome: 'NOC FTTH > CTO SEM SINAL' },
  { codigo: 957, nome: 'NOC FTTH > AMPLIAÇÃO DE CTO' }, { codigo: 958, nome: 'NOC FTTH > CONCENTRADOR INDISPONIVEL' },
  { codigo: 959, nome: 'NOC FTTH > CGNAT INDISPONIVEL' },
]

const tiposOs = [
  { codigo: 616, nome: 'OPE.BKB-DESLOCAMENTO AVARIA' }, { codigo: 617, nome: 'OPE.BKB-RUPTURA' },
  { codigo: 624, nome: 'OPE.BKB-ATENUAÇÃO EM CTO' }, { codigo: 634, nome: 'OPE.BKB-CTO SEM SINAL' },
  { codigo: 643, nome: 'OPE.BKB-AMPLIAÇÃO DE CTO' }, { codigo: 655, nome: 'OPE BKB - CTO ATENUADA' },
  { codigo: 656, nome: 'OPE BKB - CTO SEM SINAL' },
]

const slotPonOptions = Array.from({ length: 15 * 15 }, (_, i) => {
  const slot = Math.floor(i / 15) + 1
  const pon = i % 15
  return { label: `${slot}/${pon}`, value: `${slot}/${pon}` }
})

const rotaOptions = Array.from({ length: 300 }, (_, i) => ({ label: `Rota ${i + 1}`, value: i + 1 }))
const ctoOptions = Array.from({ length: 100 }, (_, i) => ({ label: `CTO ${i + 1}`, value: i + 1 }))

async function salvar() {
  if (!form.servico_id || !form.id_tipo_atendimento) {
    toast.add({ severity: 'warn', summary: 'Campos obrigatórios', detail: 'Preencha Serviço e Tipo de Atendimento', life: 4000 })
    return
  }
  loading.value = true
  try {
    const payload: CreateSuportePayload = {
      servico_id: form.servico_id,
      responsavel_id: form.responsavel_id,
      id_tipo_atendimento: form.id_tipo_atendimento,
      id_atendimento_status: form.id_atendimento_status,
      tipo_os: form.tipo_os,
      descricao: form.descricao,
      bairro: form.bairro,
      clientes_afetados: form.clientes_afetados,
      slot_pon: form.slot_pon,
      rotas: form.rotas,
      ctos: form.ctos,
      data_hora_falha: form.data_hora_falha?.toISOString() || null,
    }
    const res = await criarSuporte(payload)
    toast.add({ severity: 'success', summary: 'Sucesso', detail: res.message || 'Protocolo criado', life: 3000 })
    router.push('/suporte')
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally { loading.value = false }
}

function limpar() {
  form.servico_id = null
  form.responsavel_id = null
  form.id_tipo_atendimento = null
  form.id_atendimento_status = 1
  form.tipo_os = null
  form.descricao = ''
  form.bairro = ''
  form.clientes_afetados = ''
  form.slot_pon = []
  form.rotas = []
  form.ctos = []
  form.data_hora_falha = new Date()
}

onMounted(async () => {
  try {
    const [s, r] = await Promise.all([listarServicos(), listarResponsaveis()])
    servicos.value = s
    responsaveis.value = r
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  }
  limpar()
})
</script>

<style scoped>
.required { color: #e74c3c; }
.actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
</style>
