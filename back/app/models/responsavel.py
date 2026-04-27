from sqlalchemy import Column, Integer, String, Boolean
from app.core.base import Base


class Responsavel(Base):
    __tablename__ = "protocolocd_responsavel"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, comment="Nome do Responsável")
    telefone = Column(String(15), nullable=False, comment="Telefone")
    email = Column(String(254), nullable=True, comment="E-mail")
    ativo = Column(Boolean, default=True, comment="Ativo")
    id_hubsoft = Column(Integer, nullable=True, comment="ID Hubsoft")

    def __repr__(self):
        return f"{self.nome} ({self.telefone})"
