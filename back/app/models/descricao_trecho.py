from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.base import Base


class DescricaoTrecho(Base):
    __tablename__ = "protocolocd_descricao_trecho"

    id = Column(Integer, primary_key=True, index=True)
    trecho_id = Column(Integer, ForeignKey("protocolocd_trecho.id"), nullable=False)
    descricao = Column(Text, nullable=False, comment="Descrição do Trecho")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trecho_rel = relationship("Trecho", back_populates="descricoes", lazy="selectin")

    def __repr__(self):
        return f"Descrição de {self.trecho_id} em {self.data_criacao}"
