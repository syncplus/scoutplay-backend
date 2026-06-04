from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import BaseModel   # herda created_at / updated_at


class PartidaStatus(str, Enum):
    AGUARDANDO   = "wait"   # aguardando
    EM_PROGRESSO = "prog"   # em progresso
    FINALIZADA   = "done"   # finalizada


class PartidaLado(str, Enum):
    ESQUERDA = "Esq"
    DIREITA  = "Dir"


class Partida(BaseModel):
    """Partida de futevôlei analisada por um treinador."""
    __tablename__ = "partidas"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id    = Column(PG_UUID(as_uuid=True),
                        ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    jogador    = Column(String(150), nullable=False)            # jogador / dupla analisada
    adversario = Column(String(150), nullable=True)
    fase       = Column(String(100), nullable=False)            # ex: "Semi final 1"
    lado       = Column(String(3),   nullable=False, default=PartidaLado.ESQUERDA)      # Esq | Dir
    status     = Column(String(10),  nullable=False, default=PartidaStatus.AGUARDANDO)  # wait | prog | done
    data       = Column(Date,        nullable=True)             # data da partida
    ataques    = Column(Integer,     nullable=False, default=0) # contador (cache)
    tempo      = Column(Integer,     nullable=False, default=0) # tempo total em segundos

    user        = relationship("User")   # dono da partida (treinador/admin)
    sets        = relationship("PartidaSet", back_populates="partida",
                               cascade="all, delete-orphan",
                               order_by="PartidaSet.numero")
    lancamentos = relationship("PartidaLancamento", back_populates="partida",
                               cascade="all, delete-orphan")
