from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.protocolo import Protocolo
from app.models.suporte_protocolo import SuporteProtocolo
from app.models.usuario import Usuario

router = APIRouter()


@router.post("/vincular")
async def vincular(body: dict, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    protocolo_id = body.get("protocolo_id")
    suporte_id = body.get("suporte_id")
    acao = body.get("acao", "adicionar")

    if not protocolo_id or not suporte_id:
        raise HTTPException(status_code=400, detail="protocolo_id e suporte_id são obrigatórios")

    p_result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = p_result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo NOC não encontrado")

    s_result = await db.execute(select(SuporteProtocolo).where(SuporteProtocolo.id == suporte_id))
    suporte = s_result.scalar_one_or_none()
    if not suporte:
        raise HTTPException(status_code=404, detail="Protocolo de suporte não encontrado")

    if acao == "adicionar":
        suporte.protocolo_id = protocolo.id
        if suporte not in protocolo.protocolos_suporte:
            protocolo.protocolos_suporte.append(suporte)
    elif acao == "remover":
        suporte.protocolo_id = None
        if suporte in protocolo.protocolos_suporte:
            protocolo.protocolos_suporte.remove(suporte)
    else:
        raise HTTPException(status_code=400, detail="Ação inválida (use 'adicionar' ou 'remover')")

    await db.commit()
    return {"status": "success", "message": "Relação atualizada com sucesso"}


@router.get("/relacoes")
async def listar_relacoes(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    p_result = await db.execute(select(Protocolo).where(Protocolo.ativo == True))
    protocolos = p_result.scalars().all()
    s_result = await db.execute(select(SuporteProtocolo).where(SuporteProtocolo.ativo == True))
    suportes = s_result.scalars().all()

    relacoes = {}
    for p in protocolos:
        relacoes[str(p.id)] = [s.id for s in p.protocolos_suporte]

    return {
        "protocolos": [{"id": p.id, "titulo": p.titulo, "numero": p.numero_chamado_interno} for p in protocolos],
        "suportes": [{"id": s.id, "descricao": (s.descricao or "")[:100], "servico": s.id_cliente_servico} for s in suportes],
        "relacoes": relacoes,
    }
