from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import ForbiddenException, NotFoundException
from app.models.partida import Partida, PartidaLado, PartidaStatus


class PartidaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id:    UUID,
        jogador:    str,
        fase:       str,
        lado:       PartidaLado = PartidaLado.ESQUERDA,
        adversario: str | None = None,
        data:       date | None = None,
    ) -> Partida:
        partida = Partida(
            user_id    = user_id,
            jogador    = jogador,
            fase       = fase,
            lado       = lado,
            adversario = adversario,
            data       = data,
            status     = PartidaStatus.AGUARDANDO,
        )
        self.session.add(partida)
        await self.session.commit()
        await self.session.refresh(partida)
        return partida

    async def list_all(
        self,
        user_id:   UUID,
        is_admin:  bool,
        status:    PartidaStatus | None = None,
        page:      int = 1,
        page_size: int = 50,
    ) -> tuple[list[Partida], int]:
        q = select(Partida)
        if not is_admin:
            q = q.where(Partida.user_id == user_id)
        if status is not None:
            q = q.where(Partida.status == status)

        total = await self.session.scalar(
            select(func.count()).select_from(q.subquery())
        )
        rows = await self.session.execute(
            q.options(selectinload(Partida.user))
             .order_by(Partida.created_at.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
        )
        return list(rows.scalars()), total or 0

    async def get_by_id(
        self, partida_id: UUID, user_id: UUID, is_admin: bool
    ) -> Partida:
        result = await self.session.execute(
            select(Partida)
            .where(Partida.id == partida_id)
            .options(
                selectinload(Partida.user),
                selectinload(Partida.sets),
                selectinload(Partida.lancamentos),
            )
        )
        partida = result.scalar_one_or_none()
        if not partida:
            raise NotFoundException("Partida")
        if not is_admin and partida.user_id != user_id:
            raise ForbiddenException("Você não tem acesso a esta partida")
        return partida

    async def update(
        self,
        partida_id: UUID,
        user_id:    UUID,
        is_admin:   bool,
        jogador:    str | None = None,
        adversario: str | None = None,
        fase:       str | None = None,
        lado:       PartidaLado | None = None,
        status:     PartidaStatus | None = None,
        data:       date | None = None,
        tempo:      int | None = None,
    ) -> Partida:
        partida = await self.get_by_id(partida_id, user_id, is_admin)
        if jogador    is not None: partida.jogador    = jogador
        if adversario is not None: partida.adversario = adversario
        if fase       is not None: partida.fase       = fase
        if lado       is not None: partida.lado       = lado
        if status     is not None: partida.status     = status
        if data       is not None: partida.data       = data
        if tempo      is not None: partida.tempo      = tempo
        await self.session.commit()
        await self.session.refresh(partida)
        return partida

    async def delete(self, partida_id: UUID, user_id: UUID, is_admin: bool) -> None:
        partida = await self.get_by_id(partida_id, user_id, is_admin)
        await self.session.delete(partida)
        await self.session.commit()
