from pydantic import BaseModel, ConfigDict
from typing import Optional


class ResponsavelBase(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None
    ativo: bool = True
    id_hubsoft: Optional[int] = None


class ResponsavelCreate(ResponsavelBase):
    pass


class ResponsavelResponse(ResponsavelBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
