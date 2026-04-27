export interface Trecho {
  id: number
  uf_a: string
  municipio_a: string
  nome_pop_a: string
  trecho: string
  uf_b: string
  municipio_b: string
  nome_pop_b: string
  tipo_rede: string
  responsaveis: string
  equipamento_a: string
  porta_a: string
  equipamento_b: string
  porta_b: string
}

export interface TrechoJson {
  tipo_rede: string
  nome_pop_a: string
  nome_pop_b: string
  responsaveis: string
  uf_a: string
  equipamento_a: string
  porta_a: string
  equipamento_b: string
  porta_b: string
}

export interface Servico {
  id_cliente_servico: number
  descricao: string
}

export interface Responsavel {
  id: number
  nome: string
  telefone: string
  email?: string
  ativo: boolean
}

export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active: boolean
  is_staff?: boolean
  is_superuser?: boolean
  groups: string[]
  redirect_to?: string
}

export interface Mensagem {
  id: number
  usuario: string
  mensagem: string
  data_hora: string
}
