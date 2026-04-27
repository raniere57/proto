from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.base import Base

usuario_grupo_association = Table(
    "auth_user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("auth_user.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("auth_group.id"), primary_key=True),
)


class Usuario(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(254), nullable=True)
    first_name = Column(String(150), default="")
    last_name = Column(String(150), default="")
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    groups = relationship("Grupo", secondary=usuario_grupo_association, lazy="selectin")


class Grupo(Base):
    __tablename__ = "auth_group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
