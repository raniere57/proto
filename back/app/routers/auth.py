from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    verify_password,
    generate_password_hash,
    password_meets_requirements,
)
from app.core.dependencies import get_current_active_user
from app.models.usuario import Usuario, Grupo
from app.schemas.common import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ChangePasswordRequest,
    UsuarioResponse,
    UsuarioDetailResponse,
    MessageResponse,
)

router = APIRouter()


def _build_user_response(user: Usuario) -> UsuarioDetailResponse:
    return UsuarioDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email or "",
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        is_active=user.is_active,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        groups=[g.name for g in user.groups],
        redirect_to="/suporte" if any(g.name == "Suporte-Cliente" for g in user.groups) else "/",
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).where(Usuario.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo. Contate o administrador.")

    user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_build_user_response(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido ou expirado")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    result = await db.execute(select(Usuario).where(Usuario.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado ou inativo")

    new_access = create_access_token(data={"sub": user.username, "user_id": user.id})
    new_refresh = create_refresh_token(data={"sub": user.username, "user_id": user.id})

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user=_build_user_response(user),
    )


@router.get("/me", response_model=UsuarioDetailResponse)
async def me(current_user: Usuario = Depends(get_current_active_user)):
    return _build_user_response(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")

    valid, msg = password_meets_requirements(data.new_password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    if data.new_password == data.current_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nova senha deve ser diferente da atual")

    current_user.password = generate_password_hash(data.new_password)
    await db.commit()

    return MessageResponse(message="Senha alterada com sucesso")


@router.get("/users", response_model=list[UsuarioDetailResponse])
async def list_users(
    search: str | None = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem listar usuários")

    stmt = select(Usuario)
    if search:
        stmt = stmt.where(
            or_(
                Usuario.username.ilike(f"%{search}%"),
                Usuario.email.ilike(f"%{search}%"),
            )
        )
    stmt = stmt.order_by(Usuario.username)
    result = await db.execute(stmt)
    return [_build_user_response(u) for u in result.scalars().all()]
