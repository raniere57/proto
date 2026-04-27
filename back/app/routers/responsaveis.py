from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.responsavel import Responsavel
from app.models.usuario import Usuario
from app.schemas.responsavel import ResponsavelResponse

router = APIRouter()


@router.get("/", response_model=list[ResponsavelResponse])
async def listar_responsaveis(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Responsavel).where(Responsavel.ativo == True).order_by(Responsavel.nome)
    )
    return result.scalars().all()
