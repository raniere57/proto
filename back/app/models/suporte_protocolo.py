from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.base import Base


class SuporteProtocolo(Base):
    __tablename__ = "protocolocd_suporte_protocolo"

    id = Column(Integer, primary_key=True, index=True)
    protocolo_id = Column(Integer, ForeignKey("protocolocd_protocolo.id"), nullable=True)
    responsavel_id = Column(Integer, ForeignKey("protocolocd_responsavel.id"), nullable=True)
    atendimento_suporte_id = Column(Integer, ForeignKey("protocolocd_atendimento.id"), nullable=True)

    id_cliente_servico = Column(Integer, nullable=False)
    descricao = Column(Text, nullable=False)
    id_tipo_atendimento = Column(Integer, nullable=False)
    id_atendimento_status = Column(Integer, nullable=False)
    tipo_os = Column(Integer, nullable=True)
    ativo = Column(Boolean, default=True)
    data_hora_falha = Column(DateTime, nullable=True)
    protocolo_atendimento = Column(String(50), nullable=True)

    slot = Column(Integer, nullable=True, comment="Slot (1-15)")
    pon = Column(Integer, nullable=True, comment="PON (0-15)")
    rota = Column(Integer, nullable=True, comment="Rota (1-300)")
    cto = Column(Integer, nullable=True, comment="CTO (1-100)")
    bairro = Column(String(200), nullable=True, comment="Bairro afetado")
    clientes_afetados = Column(String(500), nullable=True, comment="Clientes afetados")
    informacoes_tecnicas = Column(JSON, nullable=True, comment="Informações técnicas FTTH")

    protocolo_rel = relationship("Protocolo", back_populates="protocolos_suporte", lazy="selectin")
    responsavel = relationship("Responsavel", lazy="selectin")
    atendimento_suporte = relationship("Atendimento", lazy="selectin")

    def __repr__(self):
        return f"SuporteProtocolo #{self.id}"
