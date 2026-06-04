from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import BaseModel   # herda created_at / updated_at


class AtaqueTipo(str, Enum):
    CABECA = "cabeca"
    SHARK  = "shark"


class AtaqueQualidade(str, Enum):
    BOA   = "boa"
    MEDIA = "media"
    RUIM  = "ruim"


class PartidaLancamento(BaseModel):
    """Lançamento (ataque) registrado no scout: tipo, qualidade, posição e zona."""
    __tablename__ = "partidas_lancamentos"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    partida_id = Column(PG_UUID(as_uuid=True),
                        ForeignKey("partidas.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    set_id     = Column(PG_UUID(as_uuid=True),
                        ForeignKey("partidas_sets.id", ondelete="SET NULL"),
                        nullable=True, index=True)
    tipo       = Column(String(10), nullable=False)  # cabeca | shark
    qualidade  = Column(String(10), nullable=False)  # boa | media | ruim
    pos_x      = Column(Integer,    nullable=False)  # posição do atacante (0-100)
    pos_y      = Column(Integer,    nullable=False)
    zona       = Column(String(3),  nullable=False)  # Z1..Z9 (zona de destino)

    partida     = relationship("Partida", back_populates="lancamentos")
    partida_set = relationship("PartidaSet", back_populates="lancamentos")
