from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class SuporteProtocoloCreate(BaseModel):
    servico_id: int
    descricao: Optional[str] = ""
    responsavel_id: Optional[int] = None
    id_tipo_atendimento: int = Field(..., description="Tipo de atendimento FTTH")
    id_atendimento_status: int = 1
    tipo_os: Optional[int] = None
    ativo: bool = True
    data_hora_falha: Optional[str] = None
    slot_pon: list[str] = []
    rotas: list[int] = []
    ctos: list[int] = []
    bairro: Optional[str] = ""
    clientes_afetados: Optional[str] = ""


class SuporteProtocoloUpdate(BaseModel):
    descricao: Optional[str] = None
    responsavel_id: Optional[int] = None
    id_tipo_atendimento: Optional[int] = None
    id_atendimento_status: Optional[int] = None
    tipo_os: Optional[int] = None
    ativo: Optional[bool] = None
    bairro: Optional[str] = None
    clientes_afetados: Optional[str] = None


class SuporteStatusUpdate(BaseModel):
    id_atendimento_status: int = Field(..., ge=1, le=5, description="1=Pendente, 2=Análise, 22=Andamento, 3=Resolvido, 4=Fechado")


class SuporteDetalhesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    protocolo_id: Optional[int] = None
    responsavel_id: Optional[int] = None
    atendimento_suporte_id: Optional[int] = None
    id_cliente_servico: int
    descricao: str
    id_tipo_atendimento: int
    id_atendimento_status: int
    tipo_os: Optional[int] = None
    ativo: bool
    data_hora_falha: Optional[datetime] = None
    protocolo_atendimento: Optional[str] = None
    slot: Optional[int] = None
    pon: Optional[int] = None
    rota: Optional[int] = None
    cto: Optional[int] = None
    bairro: Optional[str] = None
    clientes_afetados: Optional[str] = None
    informacoes_tecnicas: Optional[list] = None


class SuporteListagemItem(BaseModel):
    id: int
    id_cliente_servico: int
    id_tipo_atendimento: int
    id_atendimento_status: int
    tipo_os: Optional[int] = None
    ativo: bool
    descricao: str
    data_hora_falha: Optional[datetime] = None
    bairro: Optional[str] = None


class SuporteListagemResponse(BaseModel):
    items: list[SuporteListagemItem]
    total: int
    page: int
    per_page: int
    pages: int
