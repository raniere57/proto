from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import engine, Base
from app.routers import auth, protocolos, trechos, servicos, responsaveis, suporte, dashboard, relacionar, tipos, importacao, exportacao

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Sistema de Protocolos - Megalink",
    version="1.0.0",
    description="API para gestão de protocolos NOC TX/IP e Suporte FTTH",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(trechos.router, prefix="/trechos", tags=["Trechos"])
app.include_router(servicos.router, prefix="/servicos", tags=["Serviços"])
app.include_router(responsaveis.router, prefix="/responsaveis", tags=["Responsáveis"])
app.include_router(protocolos.router, prefix="/protocolos", tags=["Protocolos NOC"])
app.include_router(suporte.router, prefix="/suporte", tags=["Protocolos Suporte FTTH"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(relacionar.router, prefix="/relacionar", tags=["Relacionar Protocolos"])
app.include_router(tipos.router, prefix="/tipos", tags=["Tipos e Enums"])
app.include_router(importacao.router, prefix="/servicos", tags=["Importação"])
app.include_router(exportacao.router, prefix="/exportar", tags=["Exportação"])


@app.get("/health")
async def health():
    return {"status": "ok"}
