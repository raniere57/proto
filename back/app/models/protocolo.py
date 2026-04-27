from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.base import Base


class Protocolo(Base):
    __tablename__ = "protocolocd_protocolo"

    id = Column(Integer, primary_key=True, index=True)
    trecho_id = Column(Integer, ForeignKey("protocolocd_trecho.id"), nullable=True)
    pop_trecho_id = Column(Integer, ForeignKey("protocolocd_servico.id_cliente_servico"), nullable=True)
    atendimento_id = Column(Integer, ForeignKey("protocolocd_atendimento.id"), nullable=True)
    responsavel_atendimento_id = Column(Integer, ForeignKey("protocolocd_responsavel.id"), nullable=True)

    tipo_rede = Column(String(100), nullable=False)
    numero_chamado_interno = Column(String(50), default="AUTOMATICO")
    estado = Column(String(2), nullable=False)
    nome_pop_a = Column(String(100), nullable=False)
    nome_pop_b = Column(String(100), nullable=False)
    nome_responsavel = Column(String(100), default="Megalink")
    numero_chamado_os = Column(String(50), nullable=False)
    tipo_evento = Column(String(20), nullable=False)
    site_a = Column(String(100), nullable=False)
    equipamento_site_a = Column(String(100), nullable=False)
    porta_site_a = Column(String(50), nullable=False)
    site_b = Column(String(100), nullable=False)
    equipamento_site_b = Column(String(100), nullable=False)
    porta_site_b = Column(String(50), nullable=False)
    data_hora_falha = Column(DateTime, nullable=False)
    responsavel_trecho = Column(String(100), nullable=False)
    protocolo_parceiro = Column(String(100), nullable=False)
    clientes_afetados = Column(Text, nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    titulo = Column(String(255), nullable=False)
    tipo_atendimento = Column(Integer, nullable=False, default=660)
    status_atendimento = Column(Integer, nullable=False, default=2)
    ativo = Column(Boolean, default=True)

    trecho_rel = relationship("Trecho", back_populates="protocolos", lazy="selectin")
    pop_trecho_rel = relationship("Servico", back_populates="protocolos", lazy="selectin")
    atendimento = relationship("Atendimento", lazy="selectin")
    responsavel_atendimento = relationship("Responsavel", lazy="selectin")
    protocolos_suporte = relationship(
        "SuporteProtocolo",
        back_populates="protocolo_rel",
        foreign_keys="SuporteProtocolo.protocolo_id",
        lazy="selectin",
    )

    def __repr__(self):
        return f"Protocolo - {self.numero_chamado_interno} ({self.tipo_rede})"
