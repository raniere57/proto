from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from datetime import datetime
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.suporte_protocolo import SuporteProtocolo
from app.models.servico import Servico
from app.models.usuario import Usuario
from app.schemas.suporte import (
    SuporteProtocoloCreate,
    SuporteProtocoloUpdate,
    SuporteStatusUpdate,
    SuporteDetalhesResponse,
    SuporteListagemItem,
    SuporteListagemResponse,
)
from app.services.hubsoft import criar_atendimento_hubsoft_suporte

router = APIRouter()


@router.get("/", response_model=SuporteListagemResponse)
async def listar_suporte(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=200),
    ativo: Optional[bool] = None,
    search: Optional[str] = Query(None, max_length=100),
    id_tipo_atendimento: Optional[int] = None,
    id_atendimento_status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    stmt = select(SuporteProtocolo)
    count_stmt = select(func.count(SuporteProtocolo.id))

    if ativo is not None:
        stmt = stmt.where(SuporteProtocolo.ativo == ativo)
        count_stmt = count_stmt.where(SuporteProtocolo.ativo == ativo)
    if id_tipo_atendimento:
        stmt = stmt.where(SuporteProtocolo.id_tipo_atendimento == id_tipo_atendimento)
        count_stmt = count_stmt.where(SuporteProtocolo.id_tipo_atendimento == id_tipo_atendimento)
    if id_atendimento_status:
        stmt = stmt.where(SuporteProtocolo.id_atendimento_status == id_atendimento_status)
        count_stmt = count_stmt.where(SuporteProtocolo.id_atendimento_status == id_atendimento_status)
    if search:
        stmt = stmt.where(
            or_(
                SuporteProtocolo.descricao.ilike(f"%{search}%"),
                SuporteProtocolo.bairro.ilike(f"%{search}%"),
                SuporteProtocolo.id_cliente_servico.cast(str).ilike(f"%{search}%"),
            )
        )
        count_stmt = count_stmt.where(
            or_(
                SuporteProtocolo.descricao.ilike(f"%{search}%"),
                SuporteProtocolo.bairro.ilike(f"%{search}%"),
                SuporteProtocolo.id_cliente_servico.cast(str).ilike(f"%{search}%"),
            )
        )

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.order_by(desc(SuporteProtocolo.id))
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return SuporteListagemResponse(
        items=[_to_listagem_item(p) for p in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, (total + per_page - 1) // per_page),
    )


@router.get("/{protocolo_id}", response_model=SuporteDetalhesResponse)
async def detalhes_suporte(protocolo_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(SuporteProtocolo).where(SuporteProtocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo de suporte não encontrado")
    return protocolo


@router.post("/", status_code=201)
async def criar_suporte(data: SuporteProtocoloCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    data_hora = None
    if data.data_hora_falha:
        try:
            data_hora = datetime.fromisoformat(data.data_hora_falha.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass

    informacoes_tecnicas = _build_informacoes_tecnicas(
        data.slot_pon or [], data.rotas or [], data.ctos or [],
        data.bairro or "", data.clientes_afetados or "",
    )

    protocolo = SuporteProtocolo(
        id_cliente_servico=data.servico_id,
        descricao=data.descricao or "",
        id_tipo_atendimento=data.id_tipo_atendimento,
        id_atendimento_status=data.id_atendimento_status or 1,
        tipo_os=data.tipo_os,
        ativo=True if data.ativo is None else data.ativo,
        data_hora_falha=data_hora,
        bairro=data.bairro or "",
        clientes_afetados=data.clientes_afetados or "",
        informacoes_tecnicas=informacoes_tecnicas or None,
    )
    if data.responsavel_id:
        protocolo.responsavel_id = data.responsavel_id

    if informacoes_tecnicas:
        first = informacoes_tecnicas[0]
        protocolo.slot = first["slot"]
        protocolo.pon = first["pon"]
        protocolo.rota = first["rota"]
        protocolo.cto = first["cto"]

    db.add(protocolo)
    await db.commit()
    await db.refresh(protocolo)

    try:
        await criar_atendimento_hubsoft_suporte(db, protocolo)
    except Exception as e:
        print(f"HubSoft suporte atendimento failed (non-critical): {e}")

    return {"status": "success", "message": "Protocolo de suporte criado", "id": protocolo.id}


@router.put("/{protocolo_id}")
async def atualizar_suporte(protocolo_id: int, data: SuporteProtocoloUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(SuporteProtocolo).where(SuporteProtocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo de suporte não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(protocolo, field, value)

    await db.commit()
    return {"status": "success", "message": "Protocolo de suporte atualizado"}


@router.delete("/{protocolo_id}")
async def desativar_suporte(protocolo_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(SuporteProtocolo).where(SuporteProtocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo de suporte não encontrado")
    protocolo.ativo = False
    await db.commit()
    return {"status": "success", "message": "Protocolo de suporte desativado"}


@router.patch("/{protocolo_id}/status")
async def atualizar_status(protocolo_id: int, data: SuporteStatusUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(SuporteProtocolo).where(SuporteProtocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo de suporte não encontrado")

    protocolo.id_atendimento_status = data.id_atendimento_status
    if data.id_atendimento_status in (3, 4):
        protocolo.ativo = False
    elif data.id_atendimento_status == 1:
        protocolo.ativo = True

    await db.commit()
    return {"status": "success", "message": "Status atualizado"}


def _build_informacoes_tecnicas(
    slot_pon: list[str], rotas: list[int], ctos: list[int],
    bairro: str, clientes_afetados: str,
) -> list[dict]:
    result = []
    for sp in slot_pon:
        if "/" not in sp:
            continue
        slot, pon = sp.split("/")
        for rota in (rotas or []) if rotas else [0]:
            for cto in (ctos or []) if ctos else [0]:
                result.append({
                    "slot": int(slot), "pon": int(pon),
                    "rota": rota, "cto": cto,
                    "bairro": bairro, "clientes_afetados": clientes_afetados,
                })
    return result


def _to_listagem_item(p: SuporteProtocolo) -> SuporteListagemItem:
    return SuporteListagemItem(
        id=p.id,
        id_cliente_servico=p.id_cliente_servico,
        id_tipo_atendimento=p.id_tipo_atendimento,
        id_atendimento_status=p.id_atendimento_status,
        tipo_os=p.tipo_os,
        ativo=p.ativo,
        descricao=(p.descricao or "")[:100],
        data_hora_falha=p.data_hora_falha,
        bairro=p.bairro,
    )
