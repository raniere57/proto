from pydantic import BaseModel, ConfigDict
from typing import Optional


class ServicoBase(BaseModel):
    id_cliente_servico: int
    descricao: str


class ServicoResponse(ServicoBase):
    model_config = ConfigDict(from_attributes=True)
