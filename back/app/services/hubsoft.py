"""
HubSoft API Integration Service

Handles:
- OAuth2 token management with auto-refresh
- Atendimento creation (NOC + Suporte)
- Message sending
- Service import from HubSoft database
"""

import httpx
import asyncio
import asyncpg
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import get_settings

settings = get_settings()

TOKEN_URL = "https://api.megalinktelecom.hubsoft.com.br/oauth/token"
API_BASE = "https://api.megalinktelecom.hubsoft.com.br/api/v1/integracao"
MAX_RETRIES = 2
RETRY_DELAY = 1.0  # seconds


class HubSoftError(Exception):
    def __init__(self, message: str, status_code: int | None = None, response: Any = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class HubSoftAuthError(HubSoftError):
    pass


class HubSoftAPIError(HubSoftError):
    pass


# ---- Token Management ----

_token_data: dict = {}  # {"token": str, "expires_at": datetime}
_token_lock = asyncio.Lock()


async def _get_token() -> str:
    async with _token_lock:
        now = datetime.now(timezone.utc)
        if _token_data.get("token") and _token_data.get("expires_at", now) > now + timedelta(minutes=5):
            return _token_data["token"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    TOKEN_URL,
                    json={
                        "client_id": settings.HUBSOFT_CLIENT_ID,
                        "client_secret": settings.HUBSOFT_CLIENT_SECRET,
                        "username": settings.HUBSOFT_USERNAME,
                        "password": settings.HUBSOFT_PASSWORD,
                        "grant_type": "password",
                    },
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise HubSoftAuthError(
                    f"Falha na autenticação HubSoft: {e.response.status_code}",
                    status_code=e.response.status_code,
                    response=e.response.text,
                )
            except httpx.RequestError as e:
                raise HubSoftAuthError(f"Falha de conexão com HubSoft: {e}")

        _token_data["token"] = data["access_token"]
        _token_data["expires_at"] = now + timedelta(seconds=data.get("expires_in", 3600))
        return _token_data["token"]


async def _headers() -> dict:
    return {"Authorization": f"Bearer {await _get_token()}"}


# ---- HTTP Client with Retry ----

async def _api_post(path: str, payload: dict, retries: int = MAX_RETRIES) -> dict:
    url = f"{API_BASE}/{path.lstrip('/')}"
    last_error = None

    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=await _headers())
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "success":
                    raise HubSoftAPIError(
                        f"HubSoft retornou status não-success: {data.get('message', str(data))}",
                        response=data,
                    )
                return data

        except httpx.HTTPStatusError as e:
            last_error = HubSoftAPIError(
                f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                status_code=e.response.status_code,
            )
            if e.response.status_code == 401 and attempt < retries:
                _token_data.clear()
                continue
            if e.response.status_code < 500 and attempt >= retries:
                break
        except httpx.RequestError as e:
            last_error = HubSoftError(f"Erro de conexão HubSoft: {e}")

        if attempt < retries:
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))

    raise last_error or HubSoftAPIError("Falha na requisição após múltiplas tentativas")


# ---- Atendimento Creation ----

async def _criar_atendimento(
    db: AsyncSession,
    id_cliente_servico: int,
    descricao: str,
    nome: str,
    telefone: str,
    id_tipo_atendimento: int,
    id_atendimento_status: int,
    id_usuario_responsavel: int | None = None,
    protocolo_atendimento_ref: Any = None,
    is_suporte: bool = False,
) -> "Atendimento":
    from app.models.atendimento import Atendimento

    payload = {
        "id_cliente_servico": id_cliente_servico,
        "descricao": descricao,
        "nome": nome or "Megalink",
        "telefone": str(telefone) or "86999998888",
        "id_tipo_atendimento": id_tipo_atendimento,
        "id_atendimento_status": id_atendimento_status or 1,
        "id_usuario_responsavel": id_usuario_responsavel,
    }

    data = await _api_post("atendimento", payload)
    a = data["atendimento"]

    atendimento = Atendimento(
        id_atendimento=a["id_atendimento"],
        protocolo_atendimento=a["protocolo"],
        descricao_abertura=a["descricao_abertura"],
        A_tipo_atendimento=a["tipo_atendimento"],
        usuario_abertura=a["usuario_abertura"],
        usuario_responsavel=a["usuario_responsavel"],
        status=a["status"],
        cliente_nome=a["cliente"]["nome_razaosocial"],
        cliente_codigo=a["cliente"]["codigo_cliente"],
        servico_id=a["servico"]["id_cliente_servico"],
        servico_nome=a["servico"]["nome"],
        data_cadastro=datetime.utcnow(),
    )
    db.add(atendimento)
    await db.commit()
    await db.refresh(atendimento)
    return atendimento


async def criar_atendimento_hubsoft(db: AsyncSession, protocolo: "Protocolo") -> "Atendimento":
    from app.models.responsavel import Responsavel

    responsavel = None
    if protocolo.responsavel_atendimento_id:
        result = await db.execute(select(Responsavel).where(Responsavel.id == protocolo.responsavel_atendimento_id))
        responsavel = result.scalar_one_or_none()

    descricao = (
        f"Titulo: {protocolo.titulo}\n"
        f"Trecho: {protocolo.trecho_id}\n"
        f"Tipo de Rede: {protocolo.tipo_rede}\n"
        f"Tipo de Evento: {protocolo.tipo_evento}\n"
        f"Data/Hora Falha: {protocolo.data_hora_falha}\n"
        f"Clientes Afetados: {protocolo.clientes_afetados}\n"
        f"Número OS: {protocolo.numero_chamado_os}"
    )

    atendimento = await _criar_atendimento(
        db=db,
        id_cliente_servico=protocolo.pop_trecho_id or 79856,
        descricao=descricao,
        nome=responsavel.nome if responsavel else "Megalink",
        telefone=str(responsavel.telefone) if responsavel else "86999998888",
        id_tipo_atendimento=protocolo.tipo_atendimento,
        id_atendimento_status=protocolo.status_atendimento,
        id_usuario_responsavel=responsavel.id_hubsoft if responsavel and responsavel.id_hubsoft else None,
    )

    protocolo.atendimento_id = atendimento.id
    protocolo.numero_chamado_interno = atendimento.protocolo_atendimento
    await db.commit()
    return atendimento


async def criar_atendimento_hubsoft_suporte(db: AsyncSession, suporte: "SuporteProtocolo") -> "Atendimento":
    from app.models.responsavel import Responsavel

    responsavel = None
    if suporte.responsavel_id:
        result = await db.execute(select(Responsavel).where(Responsavel.id == suporte.responsavel_id))
        responsavel = result.scalar_one_or_none()

    nome = responsavel.nome if responsavel else "Megalink"
    telefone = str(responsavel.telefone) if responsavel else "86999998888"

    descricao = (
        f"Protocolo de Suporte NOC FTTH\n"
        f"ID Serviço: {suporte.id_cliente_servico}\n"
        f"Data/Hora: {suporte.data_hora_falha or datetime.utcnow()}\n"
        f"Responsável: {nome}\n"
        f"Descrição: {suporte.descricao}"
    )

    atendimento = await _criar_atendimento(
        db=db,
        id_cliente_servico=suporte.id_cliente_servico,
        descricao=descricao,
        nome=nome,
        telefone=telefone,
        id_tipo_atendimento=suporte.id_tipo_atendimento,
        id_atendimento_status=suporte.id_atendimento_status or 1,
        id_usuario_responsavel=responsavel.id_hubsoft if responsavel and responsavel.id_hubsoft else None,
    )

    suporte.atendimento_suporte_id = atendimento.id
    suporte.protocolo_atendimento = atendimento.protocolo_atendimento
    await db.commit()
    return atendimento


async def adicionar_mensagem_hubsoft(id_atendimento: int, mensagem: str) -> dict:
    return await _api_post(f"atendimento/adicionar_mensagem/{id_atendimento}", {"mensagem": mensagem})


# ---- Import Services from HubSoft Database ----

async def importar_servicos(db: AsyncSession, cliente_id: int = 45418) -> dict:
    """Importa serviços do banco HubSoft para o sistema de protocolos."""
    from app.models.servico import Servico

    conn = await asyncpg.connect(
        host=settings.HUBSOFT_DB_HOST,
        port=settings.HUBSOFT_DB_PORT,
        database=settings.HUBSOFT_DB_NAME,
        user=settings.HUBSOFT_DB_USER,
        password=settings.HUBSOFT_DB_PASSWORD,
    )

    try:
        rows = await conn.fetch(
            """
            SELECT cs.id_cliente_servico, s.descricao
            FROM cliente_servico cs
            LEFT JOIN servico s ON cs.id_servico = s.id_servico
            WHERE cs.id_cliente = $1
            ORDER BY cs.id_cliente_servico
            """,
            cliente_id,
        )
    finally:
        await conn.close()

    if not rows:
        return {"inserted": 0, "updated": 0, "total": 0, "message": "Nenhum serviço encontrado"}

    inserted = 0
    updated = 0

    for row in rows:
        result = await db.execute(
            select(Servico).where(Servico.id_cliente_servico == row["id_cliente_servico"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            if existing.descricao != row["descricao"]:
                existing.descricao = row["descricao"]
                updated += 1
        else:
            db.add(Servico(id_cliente_servico=row["id_cliente_servico"], descricao=row["descricao"]))
            inserted += 1

    await db.commit()

    return {
        "inserted": inserted,
        "updated": updated,
        "total": len(rows),
        "message": f"{inserted} inseridos, {updated} atualizados de {len(rows)} serviços",
    }
