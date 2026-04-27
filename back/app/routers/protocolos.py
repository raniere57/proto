from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from datetime import datetime, timezone
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.protocolo import Protocolo
from app.models.trecho import Trecho
from app.models.atendimento import Atendimento
from app.models.mensagem import Mensagem
from app.models.usuario import Usuario
from app.schemas.protocolo import (
    ProtocoloCreate,
    ProtocoloUpdate,
    ProtocoloStatusUpdate,
    ProtocoloDetalhesResponse,
    ProtocoloListagemItem,
    ProtocoloListagemResponse,
)
from app.schemas.common import MensagemCreate, MensagemResponse
from app.services.hubsoft import criar_atendimento_hubsoft, adicionar_mensagem_hubsoft
from app.core.enums import SIGLAS_EVENTOS

router = APIRouter()


@router.get("/", response_model=ProtocoloListagemResponse)
async def listar_protocolos(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=200),
    tipo_evento: Optional[str] = None,
    tipo_rede: Optional[str] = None,
    estado: Optional[str] = None,
    ativo: Optional[bool] = None,
    search: Optional[str] = None,
    tipo_protocolo: Optional[str] = Query(None, description="NOC-TX, NOC-IP ou OUTROS"),
    data_inicio: Optional[str] = Query(None, description="YYYY-MM-DD"),
    data_fim: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    stmt = select(Protocolo)
    count_stmt = select(func.count(Protocolo.id))

    if tipo_evento:
        stmt = stmt.where(Protocolo.tipo_evento == tipo_evento)
        count_stmt = count_stmt.where(Protocolo.tipo_evento == tipo_evento)
    if tipo_rede:
        stmt = stmt.where(Protocolo.tipo_rede == tipo_rede)
        count_stmt = count_stmt.where(Protocolo.tipo_rede == tipo_rede)
    if estado:
        stmt = stmt.where(Protocolo.estado == estado)
        count_stmt = count_stmt.where(Protocolo.estado == estado)
    if ativo is not None:
        stmt = stmt.where(Protocolo.ativo == ativo)
        count_stmt = count_stmt.where(Protocolo.ativo == ativo)
    if search:
        stmt = stmt.where(
            or_(
                Protocolo.numero_chamado_interno.ilike(f"%{search}%"),
                Protocolo.titulo.ilike(f"%{search}%"),
                Protocolo.responsavel_trecho.ilike(f"%{search}%"),
            )
        )
        count_stmt = count_stmt.where(
            or_(
                Protocolo.numero_chamado_interno.ilike(f"%{search}%"),
                Protocolo.titulo.ilike(f"%{search}%"),
                Protocolo.responsavel_trecho.ilike(f"%{search}%"),
            )
        )

    if tipo_protocolo:
        noc_tx_ids = [660, 661, 662, 663, 664, 666, 667, 668, 669, 670, 671, 723]
        noc_ip_ids = [690, 691, 692, 693, 694, 695, 696, 933, 934]
        if tipo_protocolo == "NOC-TX":
            stmt = stmt.where(Protocolo.tipo_atendimento.in_(noc_tx_ids))
            count_stmt = count_stmt.where(Protocolo.tipo_atendimento.in_(noc_tx_ids))
        elif tipo_protocolo == "NOC-IP":
            stmt = stmt.where(Protocolo.tipo_atendimento.in_(noc_ip_ids))
            count_stmt = count_stmt.where(Protocolo.tipo_atendimento.in_(noc_ip_ids))
        elif tipo_protocolo == "OUTROS":
            todos_ids = noc_tx_ids + noc_ip_ids
            stmt = stmt.where(~Protocolo.tipo_atendimento.in_(todos_ids))
            count_stmt = count_stmt.where(~Protocolo.tipo_atendimento.in_(todos_ids))

    if data_inicio:
        try:
            dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            stmt = stmt.where(Protocolo.data_criacao >= dt)
            count_stmt = count_stmt.where(Protocolo.data_criacao >= dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="data_inicio inválida. Use YYYY-MM-DD")

    if data_fim:
        try:
            dt = datetime.strptime(data_fim + " 23:59:59", "%Y-%m-%d %H:%M:%S")
            stmt = stmt.where(Protocolo.data_criacao <= dt)
            count_stmt = count_stmt.where(Protocolo.data_criacao <= dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="data_fim inválida. Use YYYY-MM-DD")

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.order_by(desc(Protocolo.data_criacao))
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    protocolos = result.scalars().all()

    return ProtocoloListagemResponse(
        items=_build_listagem(protocolos),
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, (total + per_page - 1) // per_page),
    )


@router.get("/{protocolo_id}", response_model=ProtocoloDetalhesResponse)
async def detalhes_protocolo(protocolo_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado")
    return protocolo


@router.post("/", status_code=201)
async def criar_protocolo(data: ProtocoloCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    trecho = None
    if data.trecho_id:
        t_result = await db.execute(select(Trecho).where(Trecho.id == data.trecho_id))
        trecho = t_result.scalar_one_or_none()

    datetime_str = f"{data.data_falha} {data.hora_falha}"
    try:
        data_hora_falha = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido. Use YYYY-MM-DD e HH:MM")

    protocolo = Protocolo(
        trecho_id=data.trecho_id,
        pop_trecho_id=data.pop_trecho_id,
        tipo_evento=data.tipo_evento,
        tipo_atendimento=data.tipo_atendimento or 660,
        status_atendimento=data.status_atendimento or 2,
        data_hora_falha=data_hora_falha,
        responsavel_atendimento_id=data.responsavel_atendimento_id,
        numero_chamado_os=data.numero_chamado_os or "",
        protocolo_parceiro=data.protocolo_parceiro or "",
        clientes_afetados=data.clientes_afetados or "",
        tipo_rede=trecho.tipo_rede if trecho else "",
        estado=trecho.uf_a if trecho else "",
        nome_pop_a=trecho.nome_pop_a if trecho else "",
        nome_pop_b=trecho.nome_pop_b if trecho else "",
        site_a=trecho.nome_pop_a if trecho else "",
        site_b=trecho.nome_pop_b if trecho else "",
        equipamento_site_a=trecho.equipamento_a or "" if trecho else "",
        equipamento_site_b=trecho.equipamento_b or "" if trecho else "",
        porta_site_a=trecho.porta_a or "" if trecho else "",
        porta_site_b=trecho.porta_b or "" if trecho else "",
        responsavel_trecho=trecho.responsaveis if trecho else "",
        titulo=_gerar_titulo(trecho, data.tipo_evento) if trecho else f"AUTOMATICO-{data.tipo_evento}",
    )
    db.add(protocolo)
    await db.commit()
    await db.refresh(protocolo)

    if data.criar_os:
        try:
            await criar_atendimento_hubsoft(db, protocolo)
        except Exception as e:
            print(f"HubSoft atendimento creation failed (non-critical): {e}")

    return {"status": "success", "message": f"Protocolo {protocolo.numero_chamado_interno} criado", "protocolo_id": protocolo.id}


@router.put("/{protocolo_id}")
async def atualizar_protocolo(protocolo_id: int, data: ProtocoloUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(protocolo, field, value)

    await db.commit()
    await db.refresh(protocolo)
    return {"status": "success", "message": "Protocolo atualizado", "protocolo_id": protocolo.id}


@router.delete("/{protocolo_id}")
async def desativar_protocolo(protocolo_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado")
    protocolo.ativo = False
    await db.commit()
    return {"status": "success", "message": "Protocolo desativado"}


@router.patch("/{protocolo_id}/status")
async def atualizar_status(protocolo_id: int, data: ProtocoloStatusUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado")
    protocolo.status_atendimento = data.status_atendimento
    await db.commit()
    return {"status": "success", "message": "Status atualizado"}


@router.get("/{protocolo_id}/mensagens", response_model=list[MensagemResponse])
async def listar_mensagens(protocolo_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo or not protocolo.atendimento_id:
        return []
    msgs = await db.execute(
        select(Mensagem)
        .where(Mensagem.atendimento_id == protocolo.atendimento_id)
        .order_by(Mensagem.data_hora)
    )
    return [
        MensagemResponse(
            id=m.id,
            usuario=m.usuario,
            mensagem=m.mensagem,
            data_hora=m.data_hora.strftime("%d/%m/%Y %H:%M") if m.data_hora else "",
        )
        for m in msgs.scalars().all()
    ]


@router.post("/{protocolo_id}/mensagens")
async def enviar_mensagem(protocolo_id: int, data: MensagemCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(Protocolo).where(Protocolo.id == protocolo_id))
    protocolo = result.scalar_one_or_none()
    if not protocolo or not protocolo.atendimento_id:
        raise HTTPException(status_code=400, detail="Protocolo sem atendimento associado")
    atend_result = await db.execute(select(Atendimento).where(Atendimento.id == protocolo.atendimento_id))
    atendimento = atend_result.scalar_one_or_none()
    if not atendimento:
        raise HTTPException(status_code=400, detail="Atendimento não encontrado")

    mensagem = Mensagem(atendimento_id=atendimento.id, usuario=current_user.username, mensagem=data.mensagem)
    db.add(mensagem)
    await db.commit()

    try:
        await adicionar_mensagem_hubsoft(atendimento.id_atendimento, f"{current_user.username}: {data.mensagem}")
    except Exception as e:
        print(f"HubSoft message send failed: {e}")

    return {"status": "success", "message": "Mensagem enviada"}


def _gerar_titulo(trecho: Trecho | None, tipo_evento: str, numero_interno: str = "AUTOMATICO") -> str:
    sigla = SIGLAS_EVENTOS.get(tipo_evento, "OUT")
    if not trecho:
        return f"{numero_interno}-{sigla}"
    titulo = f"{numero_interno}-{trecho.uf_a}:{sigla}:{trecho.tipo_rede}:{trecho.nome_pop_a}"
    if trecho.nome_pop_b:
        titulo += f" <> {trecho.nome_pop_b}"
    titulo += f" - {trecho.responsaveis}"
    return titulo


def _build_listagem(protocolos: list[Protocolo]) -> list[ProtocoloListagemItem]:
    now = datetime.now(timezone.utc)
    result = []
    for p in protocolos:
        diff_h = 0
        if p.data_criacao:
            dc = p.data_criacao
            if dc.tzinfo is None:
                dc = dc.replace(tzinfo=timezone.utc)
            diff_h = (now - dc).total_seconds() / 3600
        color = "green-row" if diff_h < 3 else "yellow-row" if diff_h < 6 else "red-row"
        result.append(ProtocoloListagemItem(
            id=p.id,
            numero_chamado_interno=p.numero_chamado_interno,
            titulo=p.titulo,
            tipo_evento=p.tipo_evento,
            tipo_rede=p.tipo_rede,
            estado=p.estado,
            data_criacao=p.data_criacao.isoformat() if p.data_criacao else None,
            ativo=p.ativo,
            responsavel_trecho=p.responsavel_trecho,
            color_class=color,
        ))
    return result
