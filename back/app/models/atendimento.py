from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import Base


class Atendimento(Base):
    __tablename__ = "protocolocd_atendimento"

    id = Column(Integer, primary_key=True, index=True)
    id_atendimento = Column(Integer, nullable=True)
    protocolo_atendimento = Column(String(50), nullable=False)
    descricao_abertura = Column(Text, nullable=False)
    A_tipo_atendimento = Column(String(50), nullable=False)
    usuario_abertura = Column(String(100), nullable=False)
    usuario_responsavel = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    cliente_nome = Column(String(255), nullable=False)
    cliente_codigo = Column(Integer, nullable=False)
    servico_id = Column(Integer, nullable=False)
    servico_nome = Column(String(255), nullable=False)
    data_cadastro = Column(DateTime, nullable=False)
    data_fechamento = Column(DateTime, nullable=True)

    mensagens = relationship("Mensagem", back_populates="atendimento", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"Atendimento {self.protocolo_atendimento} - {self.status}"
