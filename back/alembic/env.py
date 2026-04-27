from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models to register them in Base.metadata
from app.models.trecho import Trecho  # noqa: F401
from app.models.servico import Servico  # noqa: F401
from app.models.responsavel import Responsavel  # noqa: F401
from app.models.atendimento import Atendimento  # noqa: F401
from app.models.mensagem import Mensagem  # noqa: F401
from app.models.protocolo import Protocolo  # noqa: F401
from app.models.suporte_protocolo import SuporteProtocolo  # noqa: F401
from app.models.ordem_servico import OrdemServico  # noqa: F401
from app.models.descricao_trecho import DescricaoTrecho  # noqa: F401
from app.models.usuario import Usuario, Grupo  # noqa: F401
from app.core.base import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    try:
        run_migrations_online()
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")
        print("ℹ️  Run offline with: alembic upgrade --sql head")
        raise
