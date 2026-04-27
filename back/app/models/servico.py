from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from app.core.base import Base


class Servico(Base):
    __tablename__ = "protocolocd_servico"

    id_cliente_servico = Column(Integer, primary_key=True, index=True)
    descricao = Column(Text, nullable=False, comment="Descrição do Serviço")

    protocolos = relationship("Protocolo", back_populates="pop_trecho_rel")

    def __repr__(self):
        return f"Serviço #{self.id_cliente_servico}"
