from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case
from sqlalchemy.sql import and_
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.protocolo import Protocolo
from app.models.suporte_protocolo import SuporteProtocolo
from app.models.trecho import Trecho
from app.models.usuario import Usuario

router = APIRouter()


async def _get_date_filter(periodo: str):
    if periodo == "todos":
        return None
    dias = int(periodo)
    return datetime.utcnow() - timedelta(days=dias)


# ---- NOC Dashboard ----

@router.get("/noc")
async def dashboard_noc(
    periodo: str = Query("30", description="Período em dias ou 'todos'"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    date_filter = await _get_date_filter(periodo)

    # Base query
    stmt = select(Protocolo)
    if date_filter:
        stmt = stmt.where(Protocolo.data_criacao >= date_filter)

    result = await db.execute(stmt)
    todos = result.scalars().all()

    # Stats
    total = len(todos)
    ativos = sum(1 for p in todos if p.ativo)
    resolvidos = total - ativos
    taxa = round((resolvidos / total * 100), 2) if total > 0 else 0

    # Eventos
    eventos = {}
    tipos_evento_order = ["RUPTURA", "ATENUAÇÃO", "INDISPONIBILIDADE", "SATURAÇÃO", "TAXA DE ERRO", "OSCILAÇÃO", "FALHA ELÉTRICA", "OUTRAS"]
    for p in todos:
        ev = p.tipo_evento or "OUTRAS"
        if ev not in eventos:
            eventos[ev] = {"tipo_evento": ev, "total": 0, "ativos": 0, "resolvidos": 0}
        eventos[ev]["total"] += 1
        if p.ativo:
            eventos[ev]["ativos"] += 1
        else:
            eventos[ev]["resolvidos"] += 1
    eventos_list = [eventos[e] for e in tipos_evento_order if e in eventos]
    outros = [v for k, v in eventos.items() if k not in tipos_evento_order]
    eventos_list.extend(outros)

    # Redes
    redes = {}
    for p in todos:
        redes[p.tipo_rede] = redes.get(p.tipo_rede, 0) + 1
    redes_list = [{"tipo": k or "N/A", "total": v} for k, v in sorted(redes.items(), key=lambda x: x[1], reverse=True)]

    # Estados
    estados = {}
    for p in todos:
        estados[p.estado] = estados.get(p.estado, 0) + 1
    estados_list = [{"estado": k or "N/A", "total": v} for k, v in sorted(estados.items(), key=lambda x: x[1], reverse=True)]

    # Responsáveis (top 15)
    responsaveis = {}
    for p in todos:
        r = p.responsavel_trecho or "Não informado"
        if r not in responsaveis:
            responsaveis[r] = {"nome": r, "total": 0, "ativos": 0}
        responsaveis[r]["total"] += 1
        if p.ativo:
            responsaveis[r]["ativos"] += 1
    responsaveis_list = sorted(responsaveis.values(), key=lambda x: x["total"], reverse=True)[:15]

    # Top trechos
    trechos_count = {}
    for p in todos:
        if p.trecho_id:
            trechos_count[p.trecho_id] = trechos_count.get(p.trecho_id, 0) + 1
    top_trecho_ids = sorted(trechos_count.keys(), key=lambda x: trechos_count[x], reverse=True)[:10]

    top_trechos_nomes = {}
    if top_trecho_ids:
        t_result = await db.execute(
            select(Trecho).where(Trecho.id.in_(top_trecho_ids))
        )
        for t in t_result.scalars().all():
            top_trechos_nomes[t.id] = t.trecho

    top_trechos = [
        {"trecho": top_trechos_nomes.get(tid, f"ID {tid}"), "total": trechos_count[tid]}
        for tid in top_trecho_ids
    ]

    # Top POPs A e B
    pops_a = {}
    pops_b = {}
    for p in todos:
        if p.nome_pop_a:
            pops_a[p.nome_pop_a] = pops_a.get(p.nome_pop_a, 0) + 1
        if p.nome_pop_b:
            pops_b[p.nome_pop_b] = pops_b.get(p.nome_pop_b, 0) + 1

    top_pops_a = [{"pop": k, "total": v} for k, v in sorted(pops_a.items(), key=lambda x: x[1], reverse=True)[:10]]
    top_pops_b = [{"pop": k, "total": v} for k, v in sorted(pops_b.items(), key=lambda x: x[1], reverse=True)[:10]]

    # Protocolos críticos (>24h ativos)
    data_critica = datetime.utcnow() - timedelta(hours=24)
    criticos = [
        {
            "id": p.id,
            "numero": p.numero_chamado_interno,
            "tipo_evento": p.tipo_evento,
            "titulo": p.titulo,
            "data_criacao": p.data_criacao.isoformat() if p.data_criacao else None,
        }
        for p in todos
        if p.ativo and p.data_criacao
        and (p.data_criacao.tzinfo and p.data_criacao.replace(tzinfo=None) or p.data_criacao) < data_critica
    ][:10]

    # Evolução temporal (últimos 12 meses)
    meses_agora = datetime.utcnow()
    meses_dados = {}
    for p in todos:
        if p.data_criacao:
            dc = p.data_criacao.tzinfo and p.data_criacao or p.data_criacao
            mes_key = dc.strftime("%Y-%m")
            if mes_key not in meses_dados:
                meses_dados[mes_key] = {"mes": mes_key, "total": 0, "rupturas": 0, "atenuacoes": 0}
            meses_dados[mes_key]["total"] += 1
            if p.tipo_evento == "RUPTURA":
                meses_dados[mes_key]["rupturas"] += 1
            elif p.tipo_evento == "ATENUAÇÃO":
                meses_dados[mes_key]["atenuacoes"] += 1

    meses_list = sorted(meses_dados.values(), key=lambda x: x["mes"])[-12:]

    return {
        "total_protocolos": total,
        "protocolos_ativos": ativos,
        "protocolos_resolvidos": resolvidos,
        "taxa_resolucao": taxa,
        "eventos": eventos_list,
        "redes": redes_list,
        "estados": estados_list,
        "responsaveis": responsaveis_list,
        "top_trechos": top_trechos,
        "top_pops_a": top_pops_a,
        "top_pops_b": top_pops_b,
        "protocolos_criticos": criticos,
        "evolucao_mensal": meses_list,
    }


# ---- Suporte Dashboard ----

@router.get("/suporte")
async def dashboard_suporte(
    periodo: str = Query("30", description="Período em dias ou 'todos'"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    date_filter = await _get_date_filter(periodo)

    stmt = select(SuporteProtocolo)
    if date_filter:
        stmt = stmt.where(SuporteProtocolo.data_hora_falha >= date_filter)

    result = await db.execute(stmt)
    todos = result.scalars().all()

    total = len(todos)
    ativos = sum(1 for p in todos if p.ativo)
    resolvidos = sum(1 for p in todos if not p.ativo)

    tipos = {}
    for p in todos:
        t = p.id_tipo_atendimento
        tipos[t] = tipos.get(t, 0) + 1
    tipos_list = [{"tipo": k, "total": v} for k, v in sorted(tipos.items(), key=lambda x: x[1], reverse=True)]

    return {
        "total_protocolos": total,
        "protocolos_ativos": ativos,
        "protocolos_resolvidos": resolvidos,
        "tipos_atendimento": tipos_list,
    }
