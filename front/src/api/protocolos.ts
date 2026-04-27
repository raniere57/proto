import api from './client'
import type { Trecho, TrechoJson, Servico, Responsavel, Mensagem } from '@/types'

export interface ProtocoloListagemItem {
  id: number
  numero_chamado_interno: string
  titulo: string
  tipo_evento: string
  tipo_rede: string
  estado: string
  data_criacao: string | null
  ativo: boolean
  responsavel_trecho: string
  color_class: string
}

export interface ProtocoloListagemResponse {
  items: ProtocoloListagemItem[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ProtocoloDetalhes {
  id: number
  numero_chamado_interno: string
  titulo: string
  tipo_evento: string
  tipo_rede: string
  estado: string
  data_criacao: string | null
  data_hora_falha: string | null
  ativo: boolean
  site_a: string
  site_b: string
  equipamento_site_a: string
  equipamento_site_b: string
  porta_site_a: string
  porta_site_b: string
  numero_chamado_os: string
  protocolo_parceiro: string
  clientes_afetados: string
  responsavel_trecho: string
  tipo_atendimento: number
  status_atendimento: number
  responsavel_atendimento_id?: number | null
  trecho_id: number
  pop_trecho_id?: number | null
  atendimento_id?: number | null
  nome_pop_a: string
  nome_pop_b: string
  nome_responsavel: string
}

export interface CreateProtocoloPayload {
  trecho_id: number | null
  pop_trecho_id?: number | null
  tipo_evento: string
  tipo_atendimento?: number
  status_atendimento?: number
  data_falha: string
  hora_falha: string
  responsavel_atendimento_id?: number | null
  numero_chamado_os: string
  protocolo_parceiro?: string
  clientes_afetados: string
  criar_os?: boolean
}

export interface UpdateProtocoloPayload {
  tipo_evento?: string
  tipo_atendimento?: number
  status_atendimento?: number
  responsavel_atendimento_id?: number | null
  numero_chamado_os?: string
  protocolo_parceiro?: string
  clientes_afetados?: string
  ativo?: boolean
}

export async function listarProtocolos(params?: Record<string, any>): Promise<ProtocoloListagemItem[]> {
  const { data } = await api.get<ProtocoloListagemResponse>('/protocolos/', { params })
  return data.items
}

export async function getTotalProtocolos(params?: Record<string, any>): Promise<number> {
  const { data } = await api.get<ProtocoloListagemResponse>('/protocolos/', { params })
  return data.total
}

export async function getProtocolo(id: number): Promise<ProtocoloDetalhes> {
  const { data } = await api.get<ProtocoloDetalhes>(`/protocolos/${id}`)
  return data
}

export async function criarProtocolo(payload: CreateProtocoloPayload): Promise<{ status: string; message: string; protocolo_id?: number }> {
  const { data } = await api.post('/protocolos/', payload)
  return data
}

export async function atualizarProtocolo(id: number, payload: UpdateProtocoloPayload): Promise<{ status: string; message: string }> {
  const { data } = await api.put(`/protocolos/${id}`, payload)
  return data
}

export async function desativarProtocolo(id: number): Promise<{ status: string; message: string }> {
  const { data } = await api.delete(`/protocolos/${id}`)
  return data
}

export async function atualizarStatusProtocolo(id: number, status_atendimento: number): Promise<{ status: string; message: string }> {
  const { data } = await api.patch(`/protocolos/${id}/status`, { status_atendimento })
  return data
}

export async function listarMensagens(protocoloId: number): Promise<Mensagem[]> {
  const { data } = await api.get(`/protocolos/${protocoloId}/mensagens`)
  return data
}

export async function enviarMensagem(protocoloId: number, mensagem: string): Promise<{ status: string; message: string }> {
  const { data } = await api.post(`/protocolos/${protocoloId}/mensagens`, { mensagem })
  return data
}

export async function listarTrechos(): Promise<Trecho[]> {
  const { data } = await api.get('/trechos/')
  return data
}

export async function getTrechoJson(id: number): Promise<TrechoJson> {
  const { data } = await api.get(`/trechos/${id}/json`)
  return data
}

export async function listarServicos(): Promise<Servico[]> {
  const { data } = await api.get('/servicos/')
  return data
}

export async function listarResponsaveis(): Promise<Responsavel[]> {
  const { data } = await api.get('/responsaveis/')
  return data
}

export async function importarServicos(clienteId: number = 45418): Promise<{ status: string; message: string; inserted: number; updated: number; total: number }> {
  const { data } = await api.post('/servicos/importar', null, { params: { cliente_id: clienteId } })
  return data
}

export function getExportCsvUrl(params?: Record<string, any>) {
  const p = new URLSearchParams()
  if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null) p.set(k, String(v)) })
  const qs = p.toString()
  return `/api/exportar/protocolos/csv${qs ? '?' + qs : ''}`
}

export function getExportExcelUrl(params?: Record<string, any>) {
  const p = new URLSearchParams()
  if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null) p.set(k, String(v)) })
  const qs = p.toString()
  return `/api/exportar/protocolos/excel${qs ? '?' + qs : ''}`
}
