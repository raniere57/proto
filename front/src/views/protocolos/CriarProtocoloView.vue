<template>
  <div>
    <div class="page-header">
      <h1>Criar Protocolo de Atendimento</h1>
      <p>Preencha os dados para criar um novo protocolo NOC</p>
    </div>

    <div class="card">
      <form @submit.prevent="salvar">
        <div class="form-grid">
          <div class="full-width">
            <div class="titulo-preview" v-if="tituloPreview">
              <strong>🏷️ Título:</strong> {{ tituloPreview }}
            </div>
          </div>

          <div class="field">
            <label>Trecho <span class="required">*</span></label>
            <Select v-model="form.trecho_id" :options="trechos" optionLabel="trecho" optionValue="id" placeholder="Selecione um trecho..." filter @change="onTrechoChange" fluid />
          </div>

          <div class="field">
            <label>POP/Trecho (Serviço)</label>
            <Select v-model="form.pop_trecho_id" :options="servicos" optionLabel="descricao" optionValue="id_cliente_servico" placeholder="Selecione..." filter fluid />
          </div>

          <div class="field">
            <label>Tipo de Evento <span class="required">*</span></label>
            <Select v-model="form.tipo_evento" :options="tiposEvento" optionLabel="nome" optionValue="codigo" placeholder="Selecione..." fluid @change="onTrechoChange" />
          </div>

          <div class="field">
            <label>Tipo de Atendimento <span class="required">*</span></label>
            <Select v-model="form.tipo_atendimento" :options="tiposAtendimento" optionLabel="nome" optionValue="codigo" placeholder="Selecione..." fluid />
          </div>

          <div class="field">
            <label>Data da Falha <span class="required">*</span></label>
            <DatePicker v-model="form.data_falha" dateFormat="yy-mm-dd" :manualInput="false" fluid />
          </div>

          <div class="field">
            <label>Hora da Falha <span class="required">*</span></label>
            <InputText v-model="form.hora_falha" placeholder="HH:MM" maxlength="5" fluid @input="formatarHora" />
          </div>

          <div class="field">
            <label>Responsável pelo Atendimento</label>
            <Select v-model="form.responsavel_atendimento_id" :options="responsaveis" optionLabel="nome" optionValue="id" placeholder="Selecione..." fluid />
          </div>

          <div class="field">
            <label>Nº Chamado OS <span class="required">*</span></label>
            <InputText v-model="form.numero_chamado_os" placeholder="Ex: OS123456" fluid />
          </div>

          <div class="field">
            <label>Protocolo Parceiro</label>
            <InputText v-model="form.protocolo_parceiro" placeholder="Opcional" fluid />
          </div>

          <div class="field full-width">
            <label>Clientes Afetados <span class="required">*</span></label>
            <Textarea v-model="form.clientes_afetados" rows="3" fluid />
          </div>
        </div>

        <div class="actions">
          <Button type="submit" label="Criar Protocolo" icon="pi pi-check" :loading="loading" />
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
import { criarProtocolo, listarTrechos, listarServicos, listarResponsaveis, getTrechoJson } from '@/api/protocolos'
import type { Trecho, Servico, Responsavel } from '@/types'

const router = useRouter()
const toast = useToast()
const trechos = ref<Trecho[]>([])
const servicos = ref<Servico[]>([])
const responsaveis = ref<Responsavel[]>([])
const loading = ref(false)
const tituloPreview = ref('')

const form = reactive({
  trecho_id: null as number | null,
  pop_trecho_id: null as number | null,
  tipo_evento: null as string | null,
  tipo_atendimento: null as number | null,
  status_atendimento: 2,
  data_falha: null as Date | null,
  hora_falha: '',
  responsavel_atendimento_id: null as number | null,
  numero_chamado_os: '',
  protocolo_parceiro: '',
  clientes_afetados: '',
})

const tiposEvento = [
  { codigo: 'RUPTURA', nome: 'Ruptura' }, { codigo: 'ATENUAÇÃO', nome: 'Atenuação' },
  { codigo: 'INDISPONIBILIDADE', nome: 'Indisponibilidade' }, { codigo: 'SATURAÇÃO', nome: 'Saturação' },
  { codigo: 'TAXA DE ERRO', nome: 'Taxa de Erro' }, { codigo: 'OSCILAÇÃO', nome: 'Oscilação' },
  { codigo: 'FALHA ELÉTRICA', nome: 'Falha Elétrica' }, { codigo: 'OUTRAS', nome: 'Outros' },
]

const tiposAtendimento = [
  { codigo: 660, nome: 'NOC TX' }, { codigo: 661, nome: 'NOC TX > ATENUAÇÃO PARCEIRO' },
  { codigo: 664, nome: 'NOC TX > RUPTURA PARCEIRO' }, { codigo: 671, nome: 'NOC TX > RUPTURA MEGALINK' },
  { codigo: 690, nome: 'NOC IP > LATÊNCIA ALTA DST' }, { codigo: 696, nome: 'NOC IP > OUTROS' },
]

function formatarHora() {
  let v = form.hora_falha.replace(/\D/g, '')
  if (v.length > 2) v = v.slice(0, 2) + ':' + v.slice(2, 4)
  form.hora_falha = v.slice(0, 5)
}

const siglas: Record<string, string> = {
  RUPTURA: 'RUP', ATENUAÇÃO: 'ATN', INDISPONIBILIDADE: 'IND',
  SATURAÇÃO: 'SAT', OSCILAÇÃO: 'OSC', 'FALHA ELÉTRICA': 'RGE', OUTRAS: 'OUT',
}

async function onTrechoChange() {
  if (!form.trecho_id || !form.tipo_evento) { tituloPreview.value = ''; return }
  try {
    const data = await getTrechoJson(form.trecho_id)
    const sigla = siglas[form.tipo_evento] || 'OUT'
    tituloPreview.value = `AUTOMATICO-${data.uf_a}:${sigla}:${data.tipo_rede}:${data.nome_pop_a}${data.nome_pop_b ? ' <> ' + data.nome_pop_b : ''} - ${data.responsaveis}`
  } catch { tituloPreview.value = '' }
}

async function salvar() {
  if (!form.trecho_id || !form.tipo_evento || !form.tipo_atendimento || !form.data_falha || !form.numero_chamado_os) {
    toast.add({ severity: 'warn', summary: 'Campos obrigatórios', detail: 'Preencha todos os campos marcados com *', life: 4000 })
    return
  }
  loading.value = true
  try {
    if (!form.tipo_evento) return
    const data_falha = form.data_falha instanceof Date
      ? form.data_falha.toISOString().split('T')[0]
      : String(form.data_falha)
    const res = await criarProtocolo({
      trecho_id: form.trecho_id,
      pop_trecho_id: form.pop_trecho_id,
      tipo_evento: form.tipo_evento,
      tipo_atendimento: form.tipo_atendimento ?? 660,
      status_atendimento: form.status_atendimento,
      data_falha,
      hora_falha: form.hora_falha,
      responsavel_atendimento_id: form.responsavel_atendimento_id,
      numero_chamado_os: form.numero_chamado_os,
      protocolo_parceiro: form.protocolo_parceiro,
      clientes_afetados: form.clientes_afetados,
      criar_os: true,
    })
    toast.add({ severity: 'success', summary: 'Sucesso', detail: res.message, life: 3000 })
    if (res.protocolo_id) router.push(`/protocolos/${res.protocolo_id}`)
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || 'Erro ao criar protocolo'
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 5000 })
  } finally { loading.value = false }
}

function limpar() {
  form.trecho_id = null
  form.pop_trecho_id = null
  form.tipo_evento = null
  form.tipo_atendimento = null
  form.status_atendimento = 2
  form.responsavel_atendimento_id = null
  form.numero_chamado_os = ''
  form.protocolo_parceiro = ''
  form.clientes_afetados = ''
  form.data_falha = new Date()
  form.hora_falha = new Date().toTimeString().slice(0, 5)
  tituloPreview.value = ''
}

onMounted(async () => {
  try {
    const [t, s, r] = await Promise.all([listarTrechos(), listarServicos(), listarResponsaveis()])
    trechos.value = t
    servicos.value = s
    responsaveis.value = r
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Falha ao carregar dados iniciais', life: 5000 })
  }
  limpar()
})
</script>

<style scoped>
.titulo-preview {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
  padding: 1rem 1.5rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;
}
.required { color: #e74c3c; }
.actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
</style>
