from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.servico import Servico
from app.models.usuario import Usuario
from app.schemas.servico import ServicoResponse

router = APIRouter()


@router.get("/", response_model=list[ServicoResponse])
async def listar_servicos(
    search: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    stmt = select(Servico)
    if search:
        stmt = stmt.where(
            or_(
                Servico.descricao.ilike(f"%{search}%"),
                Servico.id_cliente_servico.cast(str).ilike(f"%{search}%"),
            )
        )
    stmt = stmt.order_by(Servico.id_cliente_servico).limit(200)
    result = await db.execute(stmt)
    return result.scalars().all()
