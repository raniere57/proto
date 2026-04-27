from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.usuario import Usuario
from app.services.hubsoft import importar_servicos

router = APIRouter()


@router.post("/importar")
async def importar_servicos_endpoint(
    cliente_id: int = 45418,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Apenas administradores podem importar serviços")

    try:
        result = await importar_servicos(db, cliente_id)
        return {
            "status": "success",
            "message": result["message"],
            "inserted": result["inserted"],
            "updated": result["updated"],
            "total": result["total"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na importação: {str(e)}")
