<template>
  <div>
    <div class="page-header">
      <h1>Detalhes do Protocolo</h1>
      <p v-if="protocolo">Protocolo {{ protocolo.numero_chamado_interno }}</p>
    </div>

    <div v-if="loading" class="card"><ProgressSpinner /></div>

    <div v-else-if="error" class="card">
      <Message severity="error">{{ error }}</Message>
    </div>

    <template v-if="protocolo">
      <div class="card">
        <div class="header-actions">
          <div class="header-tags">
            <Tag :value="protocolo.ativo ? 'Ativo' : 'Resolvido'" :severity="protocolo.ativo ? 'danger' : 'success'" />
            <Tag :value="protocolo.tipo_evento" style="margin-left: 0.5rem" />
          </div>
          <router-link to="/gestao">
            <Button label="Voltar" icon="pi pi-arrow-left" severity="secondary" />
          </router-link>
        </div>

        <h2>{{ protocolo.titulo }}</h2>

        <Divider />

        <div class="info-grid">
          <div class="info-item"><strong>Nº Chamado Interno:</strong> {{ protocolo.numero_chamado_interno }}</div>
          <div class="info-item"><strong>Nº Chamado OS:</strong> {{ protocolo.numero_chamado_os }}</div>
          <div class="info-item"><strong>Tipo de Rede:</strong> {{ protocolo.tipo_rede }}</div>
          <div class="info-item"><strong>UF:</strong> {{ protocolo.estado }}</div>
          <div class="info-item"><strong>Data/Hora Falha:</strong> {{ formatDate(protocolo.data_hora_falha) }}</div>
          <div class="info-item"><strong>Responsável Trecho:</strong> {{ protocolo.responsavel_trecho }}</div>
          <div class="info-item"><strong>Protocolo Parceiro:</strong> {{ protocolo.protocolo_parceiro || '-' }}</div>
        </div>

        <Divider />

        <h3>Sites</h3>
        <div class="info-grid">
          <div class="info-item">
            <strong>Site A:</strong> {{ protocolo.site_a }}<br>
            <small>{{ protocolo.equipamento_site_a }} / {{ protocolo.porta_site_a }}</small>
          </div>
          <div class="info-item">
            <strong>Site B:</strong> {{ protocolo.site_b }}<br>
            <small>{{ protocolo.equipamento_site_b }} / {{ protocolo.porta_site_b }}</small>
          </div>
        </div>

        <Divider />

        <div class="field">
          <label><strong>Clientes Afetados:</strong></label>
          <p class="text-block">{{ protocolo.clientes_afetados }}</p>
        </div>
      </div>

      <div class="card">
        <h3>Mensagens</h3>
        <div class="chat">
          <div v-for="msg in mensagens" :key="msg.id" class="chat-msg">
            <strong>{{ msg.usuario }}</strong>
            <small>{{ msg.data_hora }}</small>
            <p>{{ msg.mensagem }}</p>
          </div>
          <div v-if="mensagens.length === 0" class="empty"><p>Nenhuma mensagem ainda</p></div>
        </div>
        <div class="chat-input">
          <Textarea v-model="novaMensagem" rows="2" placeholder="Digite sua mensagem..." fluid />
          <Button label="Enviar" icon="pi pi-send" @click="enviar" :loading="enviando" :disabled="!novaMensagem.trim()" />
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
import { getProtocolo, listarMensagens, enviarMensagem } from '@/api/protocolos'
import { extractError } from '@/api/client'
import type { Mensagem } from '@/types'
import type { ProtocoloDetalhes } from '@/api/protocolos'

const route = useRoute()
const toast = useToast()
const protocolo = ref<ProtocoloDetalhes | null>(null)
const mensagens = ref<Mensagem[]>([])
const novaMensagem = ref('')
const loading = ref(true)
const error = ref('')
const enviando = ref(false)

function formatDate(d: string | null | undefined) {
  if (!d) return '-'
  return new Date(d).toLocaleString('pt-BR')
}

async function carregar() {
  const id = Number(route.params.id)
  loading.value = true
  error.value = ''
  try {
    const [p, msgs] = await Promise.all([getProtocolo(id), listarMensagens(id)])
    protocolo.value = p
    mensagens.value = msgs
  } catch (err) {
    error.value = extractError(err)
    toast.add({ severity: 'error', summary: 'Erro', detail: error.value, life: 5000 })
  } finally {
    loading.value = false
  }
}

async function enviar() {
  if (!novaMensagem.value.trim()) return
  enviando.value = true
  try {
    await enviarMensagem(Number(route.params.id), novaMensagem.value)
    novaMensagem.value = ''
    mensagens.value = await listarMensagens(Number(route.params.id))
    toast.add({ severity: 'success', summary: 'Enviada', detail: 'Mensagem enviada com sucesso', life: 3000 })
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally {
    enviando.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.header-tags { display: flex; align-items: center; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.info-item { background: #f8f9fa; padding: 0.75rem 1rem; border-radius: 8px; line-height: 1.6; }
.text-block { background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 0.5rem; white-space: pre-wrap; }
.chat { max-height: 400px; overflow-y: auto; margin-bottom: 1rem; }
.chat-msg { background: #f0f2f5; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; }
.chat-msg small { float: right; color: #6c757d; font-size: 0.8rem; }
.chat-msg p { margin-top: 0.5rem; }
.chat-input { display: flex; gap: 0.5rem; align-items: flex-end; }
.empty { text-align: center; color: #6c757d; padding: 2rem; }
</style>
