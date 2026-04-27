from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.base import Base


class Mensagem(Base):
    __tablename__ = "protocolocd_mensagem"

    id = Column(Integer, primary_key=True, index=True)
    atendimento_id = Column(Integer, ForeignKey("protocolocd_atendimento.id"), nullable=False)
    usuario = Column(String(100), nullable=False)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    mensagem = Column(Text, nullable=False)

    atendimento = relationship("Atendimento", back_populates="mensagens", lazy="selectin")

    def __repr__(self):
        return f"Mensagem de {self.usuario} em {self.data_hora}"
