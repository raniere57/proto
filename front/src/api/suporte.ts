import api from './client'

export interface SuporteProtocolo {
  id: number
  id_cliente_servico: number
  descricao: string
  id_tipo_atendimento: number
  id_atendimento_status: number
  tipo_os?: number | null
  ativo: boolean
  data_hora_falha?: string | null
  protocolo_atendimento?: string | null
  bairro?: string | null
  clientes_afetados?: string | null
  informacoes_tecnicas?: any[] | null
  slot?: number | null
  pon?: number | null
  rota?: number | null
  cto?: number | null
  protocolo_id?: number | null
  responsavel_id?: number | null
  atendimento_suporte_id?: number | null
}

export interface SuporteListagemResponse {
  items: SuporteProtocolo[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface CreateSuportePayload {
  servico_id: number
  descricao?: string
  responsavel_id?: number | null
  id_tipo_atendimento: number
  id_atendimento_status?: number
  tipo_os?: number | null
  ativo?: boolean
  data_hora_falha?: string | null
  slot_pon?: string[]
  rotas?: number[]
  ctos?: number[]
  bairro?: string
  clientes_afetados?: string
}

export interface UpdateSuportePayload {
  descricao?: string
  responsavel_id?: number | null
  id_tipo_atendimento?: number
  id_atendimento_status?: number
  tipo_os?: number | null
  ativo?: boolean
  bairro?: string
  clientes_afetados?: string
}

export async function listarSuporte(params?: Record<string, any>): Promise<SuporteProtocolo[]> {
  const { data } = await api.get<SuporteListagemResponse>('/suporte/', { params })
  return data.items
}

export async function getSuporte(id: number): Promise<SuporteProtocolo> {
  const { data } = await api.get<SuporteProtocolo>(`/suporte/${id}`)
  return data
}

export async function criarSuporte(payload: CreateSuportePayload): Promise<{ status: string; message: string; id?: number }> {
  const { data } = await api.post('/suporte/', payload)
  return data
}

export async function atualizarSuporte(id: number, payload: UpdateSuportePayload): Promise<{ status: string; message: string }> {
  const { data } = await api.put(`/suporte/${id}`, payload)
  return data
}

export async function desativarSuporte(id: number): Promise<{ status: string; message: string }> {
  const { data } = await api.delete(`/suporte/${id}`)
  return data
}

export async function atualizarStatusSuporte(id: number, id_atendimento_status: number): Promise<{ status: string; message: string }> {
  const { data } = await api.patch(`/suporte/${id}/status`, { id_atendimento_status })
  return data
}
