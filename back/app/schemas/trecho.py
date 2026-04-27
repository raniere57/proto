from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TrechoBase(BaseModel):
    uf_a: str
    municipio_a: str
    nome_pop_a: str
    trecho: str
    uf_b: str
    municipio_b: str
    nome_pop_b: str
    tipo_rede: str
    responsaveis: str
    equipamento_a: Optional[str] = ""
    porta_a: Optional[str] = ""
    equipamento_b: Optional[str] = ""
    porta_b: Optional[str] = ""


class TrechoCreate(TrechoBase):
    pass


class TrechoResponse(TrechoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TrechoJsonResponse(BaseModel):
    tipo_rede: str
    nome_pop_a: str
    nome_pop_b: str
    responsaveis: str
    uf_a: str
    municipio_a: str
    uf_b: str
    municipio_b: str
    equipamento_a: str
    porta_a: str
    equipamento_b: str
    porta_b: str
