from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException
from app.models.partida_set import PartidaSet
from app.services.partida import PartidaService


class PartidaSetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.partidas = PartidaService(session)

    async def add(
        self,
        partida_id:        UUID,
        user_id:           UUID,
        is_admin:          bool,
        pontos_jogador:    int = 0,
        pontos_adversario: int = 0,
        tempo:             int = 0,
    ) -> PartidaSet:
        # get_by_id também garante a posse/permissão da partida
        partida = await self.partidas.get_by_id(partida_id, user_id, is_admin)
        numero = max((s.numero for s in partida.sets), default=0) + 1
        novo = PartidaSet(
            partida_id        = partida.id,
            numero            = numero,
            pontos_jogador    = pontos_jogador,
            pontos_adversario = pontos_adversario,
            tempo             = tempo,
        )
        self.session.add(novo)
        await self.session.commit()
        await self.session.refresh(novo)
        return novo

    async def delete(
        self, partida_id: UUID, set_id: UUID, user_id: UUID, is_admin: bool
    ) -> None:
        partida = await self.partidas.get_by_id(partida_id, user_id, is_admin)
        alvo = next((s for s in partida.sets if s.id == set_id), None)
        if not alvo:
            raise NotFoundException("Set")
        await self.session.delete(alvo)
        await self.session.commit()
