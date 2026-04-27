from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.trecho import Trecho
from app.schemas.trecho import TrechoResponse, TrechoJsonResponse
from app.models.usuario import Usuario

router = APIRouter()


@router.get("/", response_model=list[TrechoResponse])
async def listar_trechos(
    search: Optional[str] = Query(None, max_length=100),
    tipo_rede: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    stmt = select(Trecho)
    if search:
        stmt = stmt.where(
            or_(
                Trecho.trecho.ilike(f"%{search}%"),
                Trecho.nome_pop_a.ilike(f"%{search}%"),
                Trecho.nome_pop_b.ilike(f"%{search}%"),
                Trecho.municipio_a.ilike(f"%{search}%"),
                Trecho.municipio_b.ilike(f"%{search}%"),
                Trecho.responsaveis.ilike(f"%{search}%"),
            )
        )
    if tipo_rede:
        stmt = stmt.where(Trecho.tipo_rede.ilike(f"%{tipo_rede}%"))
    stmt = stmt.order_by(Trecho.trecho).limit(500)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{trecho_id}", response_model=TrechoResponse)
async def detalhes_trecho(trecho_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Trecho).where(Trecho.id == trecho_id))
    trecho = result.scalar_one_or_none()
    if not trecho:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return trecho


@router.get("/{trecho_id}/json", response_model=TrechoJsonResponse)
async def trecho_json(trecho_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Trecho).where(Trecho.id == trecho_id))
    trecho = result.scalar_one_or_none()
    if not trecho:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return TrechoJsonResponse(
        tipo_rede=trecho.tipo_rede,
        nome_pop_a=trecho.nome_pop_a,
        nome_pop_b=trecho.nome_pop_b,
        responsaveis=trecho.responsaveis,
        uf_a=trecho.uf_a,
        municipio_a=trecho.municipio_a,
        uf_b=trecho.uf_b,
        municipio_b=trecho.municipio_b,
        equipamento_a=trecho.equipamento_a or "",
        porta_a=trecho.porta_a or "",
        equipamento_b=trecho.equipamento_b or "",
        porta_b=trecho.porta_b or "",
    )
