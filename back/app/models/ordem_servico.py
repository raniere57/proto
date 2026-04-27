from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.base import Base


class OrdemServico(Base):
    __tablename__ = "protocolocd_ordem_servico"

    id = Column(Integer, primary_key=True, index=True)
    id_ordem_servico = Column(Integer, unique=True, nullable=False)
    id_atendimento = Column(Integer, nullable=False)
    tipo_ordem_servico = Column(String(100), nullable=False)
    numero_ordem_servico = Column(String(100), nullable=False)
    descricao_abertura = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    data_cadastro = Column(DateTime, nullable=False)
    data_inicio_programado = Column(DateTime, nullable=False)
    data_termino_programado = Column(DateTime, nullable=False)
    cliente_servico_display = Column(String(755), nullable=False)
    cliente_servico_id = Column(Integer, nullable=False)
    cliente = Column(String(755), nullable=False)
    response_status = Column(String(50), nullable=False)
    response_msg = Column(String(755), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"OS {self.numero_ordem_servico} - {self.status}"
