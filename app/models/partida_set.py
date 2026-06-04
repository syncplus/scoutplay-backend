from uuid import uuid4

from sqlalchemy import Column, Integer, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import BaseModel   # herda created_at / updated_at


class PartidaSet(BaseModel):
    """Placar e tempo de cada set da partida."""
    __tablename__ = "partidas_sets"

    id                = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    partida_id        = Column(PG_UUID(as_uuid=True),
                               ForeignKey("partidas.id", ondelete="CASCADE"),
                               nullable=False, index=True)
    numero            = Column(Integer, nullable=False)             # número do set
    pontos_jogador    = Column(Integer, nullable=False, default=0)  # "nos"
    pontos_adversario = Column(Integer, nullable=False, default=0)  # "them"
    tempo             = Column(Integer, nullable=False, default=0)  # duração do set em segundos

    partida     = relationship("Partida", back_populates="sets")
    lancamentos = relationship("PartidaLancamento", back_populates="partida_set")

    __table_args__ = (
        Index("ix_partidas_sets_partida_numero", "partida_id", "numero", unique=True),
    )
