import api from './client'

export interface DashboardNocData {
  total_protocolos: number
  protocolos_ativos: number
  protocolos_resolvidos: number
  taxa_resolucao: number
  eventos: Array<{ tipo_evento: string; total: number; ativos: number; resolvidos: number }>
  redes: Array<{ tipo: string; total: number }>
  estados: Array<{ estado: string; total: number }>
  responsaveis: Array<{ nome: string; total: number; ativos: number }>
  top_trechos: Array<{ trecho: string; total: number }>
  top_pops_a: Array<{ pop: string; total: number }>
  top_pops_b: Array<{ pop: string; total: number }>
  protocolos_criticos: Array<{ id: number; numero: string; tipo_evento: string; titulo: string; data_criacao: string }>
  evolucao_mensal: Array<{ mes: string; total: number; rupturas: number; atenuacoes: number }>
}

export interface DashboardSuporteData {
  total_protocolos: number
  protocolos_ativos: number
  protocolos_resolvidos: number
  tipos_atendimento: Array<{ tipo: number; total: number }>
}

export async function getDashboardNoc(periodo: string = '30'): Promise<DashboardNocData> {
  const { data } = await api.get<DashboardNocData>('/dashboard/noc', { params: { periodo } })
  return data
}

export async function getDashboardSuporte(periodo: string = '30'): Promise<DashboardSuporteData> {
  const { data } = await api.get<DashboardSuporteData>('/dashboard/suporte', { params: { periodo } })
  return data
}

export async function vincularProtocolos(protocoloId: number, suporteId: number, acao: string) {
  const { data } = await api.post('/relacionar/vincular', { protocolo_id: protocoloId, suporte_id: suporteId, acao })
  return data
}

export async function listarRelacoes() {
  const { data } = await api.get('/relacionar/relacoes')
  return data
}
