from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException
from app.models.partida import PartidaStatus
from app.models.partida_lancamento import (
    AtaqueQualidade,
    AtaqueTipo,
    PartidaLancamento,
)
from app.services.partida import PartidaService


class PartidaLancamentoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.partidas = PartidaService(session)

    async def add(
        self,
        partida_id: UUID,
        user_id:    UUID,
        is_admin:   bool,
        tipo:       AtaqueTipo,
        qualidade:  AtaqueQualidade,
        pos_x:      int,
        pos_y:      int,
        zona:       str,
        set_id:     UUID | None = None,
    ) -> PartidaLancamento:
        partida = await self.partidas.get_by_id(partida_id, user_id, is_admin)
        if partida.status == PartidaStatus.FINALIZADA:
            raise ConflictException("Partida finalizada — reabra para registrar ataques")
        lancamento = PartidaLancamento(
            partida_id = partida.id,
            set_id     = set_id,
            tipo       = tipo,
            qualidade  = qualidade,
            pos_x      = pos_x,
            pos_y      = pos_y,
            zona       = zona,
        )
        self.session.add(lancamento)
        partida.ataques = (partida.ataques or 0) + 1
        await self.session.commit()
        await self.session.refresh(lancamento)
        return lancamento

    async def delete(
        self, partida_id: UUID, lancamento_id: UUID, user_id: UUID, is_admin: bool
    ) -> None:
        partida = await self.partidas.get_by_id(partida_id, user_id, is_admin)
        alvo = next((l for l in partida.lancamentos if l.id == lancamento_id), None)
        if not alvo:
            raise NotFoundException("Lançamento")
        await self.session.delete(alvo)
        partida.ataques = max(0, (partida.ataques or 0) - 1)
        await self.session.commit()
