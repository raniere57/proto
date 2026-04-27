from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.base import Base


class Trecho(Base):
    __tablename__ = "protocolocd_trecho"

    id = Column(Integer, primary_key=True, index=True)
    uf_a = Column(String(2), nullable=False, comment="UF - A")
    municipio_a = Column(String(100), nullable=False, comment="Município - A")
    nome_pop_a = Column(String(100), nullable=False, comment="Nome do POP - A")
    trecho = Column(String(255), nullable=False, comment="Trecho")
    uf_b = Column(String(2), nullable=False, comment="UF - B")
    municipio_b = Column(String(100), nullable=False, comment="Município - B")
    nome_pop_b = Column(String(100), nullable=False, comment="Nome do POP - B")
    tipo_rede = Column(String(100), nullable=False, comment="Tipo de Rede")
    responsaveis = Column(String(255), nullable=False, comment="Responsáveis")
    equipamento_a = Column(String(100), default="", comment="Equipamento - A")
    porta_a = Column(String(100), default="", comment="Porta Equipamento - A")
    equipamento_b = Column(String(100), default="", comment="Equipamento - B")
    porta_b = Column(String(100), default="", comment="Porta Equipamento - B")

    protocolos = relationship("Protocolo", back_populates="trecho_rel")
    descricoes = relationship("DescricaoTrecho", back_populates="trecho_rel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.trecho} ({self.tipo_rede})"
