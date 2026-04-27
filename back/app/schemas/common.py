from pydantic import BaseModel, Field
from typing import Optional


class MensagemCreate(BaseModel):
    mensagem: str


class MensagemResponse(BaseModel):
    id: int
    usuario: str
    mensagem: str
    data_hora: str


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=150, description="Nome de usuário")
    password: str = Field(..., min_length=1, max_length=128, description="Senha")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token para obter novo access token")


class UsuarioDetailResponse(BaseModel):
    id: int
    username: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    is_active: bool
    is_staff: bool = False
    is_superuser: bool = False
    groups: list[str] = []
    redirect_to: str = "/"


class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str = ""
    is_active: bool
    groups: list[str] = []


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str = "bearer"
    user: Optional[UsuarioDetailResponse] = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, description="Senha atual")
    new_password: str = Field(..., min_length=6, max_length=128, description="Nova senha")


class MessageResponse(BaseModel):
    message: str
