from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class ProtocoloCreate(BaseModel):
    trecho_id: Optional[int] = None
    pop_trecho_id: Optional[int] = None
    tipo_evento: str = Field(..., min_length=2, max_length=20)
    tipo_atendimento: int = 660
    status_atendimento: int = 2
    data_falha: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    hora_falha: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM")
    responsavel_atendimento_id: Optional[int] = None
    numero_chamado_os: str = ""
    protocolo_parceiro: Optional[str] = ""
    clientes_afetados: str = ""
    criar_os: bool = True


class ProtocoloUpdate(BaseModel):
    tipo_evento: Optional[str] = Field(None, min_length=2, max_length=20)
    tipo_atendimento: Optional[int] = None
    status_atendimento: Optional[int] = None
    responsavel_atendimento_id: Optional[int] = None
    numero_chamado_os: Optional[str] = None
    protocolo_parceiro: Optional[str] = None
    clientes_afetados: Optional[str] = None
    ativo: Optional[bool] = None


class ProtocoloStatusUpdate(BaseModel):
    status_atendimento: int = Field(..., ge=1, le=4)


class ProtocoloDetalhesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    trecho_id: Optional[int] = None
    pop_trecho_id: Optional[int] = None
    atendimento_id: Optional[int] = None
    responsavel_atendimento_id: Optional[int] = None
    tipo_rede: str
    numero_chamado_interno: str
    estado: str
    nome_pop_a: str
    nome_pop_b: str
    nome_responsavel: str
    numero_chamado_os: str
    tipo_evento: str
    tipo_atendimento: int
    status_atendimento: int
    data_hora_falha: Optional[datetime] = None
    data_criacao: Optional[datetime] = None
    titulo: str
    ativo: bool
    site_a: str
    site_b: str
    equipamento_site_a: str
    equipamento_site_b: str
    porta_site_a: str
    porta_site_b: str
    responsavel_trecho: str
    protocolo_parceiro: str
    clientes_afetados: str


class ProtocoloListagemItem(BaseModel):
    id: int
    numero_chamado_interno: str
    titulo: str
    tipo_evento: str
    tipo_rede: str
    estado: str
    data_criacao: Optional[str] = None
    ativo: bool
    responsavel_trecho: str
    color_class: str = "green-row"


class ProtocoloListagemResponse(BaseModel):
    items: list[ProtocoloListagemItem]
    total: int
    page: int
    per_page: int
    pages: int
