from fastapi import APIRouter
from app.core.enums import (
    TIPO_EVENTO_CHOICES,
    TIPO_REDE_CHOICES,
    STATUS_ATENDIMENTO_CHOICES,
    TIPOS_ATENDIMENTO_CHOICES,
    TIPOS_ATENDIMENTO_SUPORTE_CHOICES,
    STATUS_SUPORTE_CHOICES,
    TIPO_OS_CHOICES,
)

router = APIRouter()


@router.get("/")
async def listar_tipos():
    return {
        "tipo_evento": [{"codigo": c[0], "nome": c[1]} for c in TIPO_EVENTO_CHOICES],
        "tipo_rede": [{"codigo": c[0], "nome": c[1]} for c in TIPO_REDE_CHOICES],
        "status_atendimento": [{"codigo": c[0], "nome": c[1]} for c in STATUS_ATENDIMENTO_CHOICES],
        "tipo_atendimento": [{"codigo": c[0], "nome": c[1]} for c in TIPOS_ATENDIMENTO_CHOICES],
        "tipo_atendimento_suporte": [{"codigo": c[0], "nome": c[1]} for c in TIPOS_ATENDIMENTO_SUPORTE_CHOICES],
        "status_suporte": [{"codigo": c[0], "nome": c[1]} for c in STATUS_SUPORTE_CHOICES],
        "tipo_os": [{"codigo": c[0], "nome": c[1]} for c in TIPO_OS_CHOICES],
    }
