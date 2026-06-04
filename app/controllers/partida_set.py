from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import RequireTreinador
from app.database import get_session
from app.models.user import User, UserRole
from app.services.partida_set import PartidaSetService

router = APIRouter()


class CreateSetRequest(BaseModel):
    pontos_jogador:    int = 0
    pontos_adversario: int = 0
    tempo:             int = 0


class SetOut(BaseModel):
    id:                str
    numero:            int
    pontos_jogador:    int
    pontos_adversario: int
    tempo:             int

    @classmethod
    def from_model(cls, s) -> "SetOut":
        return cls(
            id                = str(s.id),
            numero            = s.numero,
            pontos_jogador    = s.pontos_jogador,
            pontos_adversario = s.pontos_adversario,
            tempo             = s.tempo,
        )


def _is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


@router.post("/{partida_id}/sets", status_code=201)
async def create_set(
    partida_id:   UUID,
    body:         CreateSetRequest,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaSetService(session)
    s = await svc.add(
        partida_id, current_user.id, _is_admin(current_user),
        body.pontos_jogador, body.pontos_adversario, body.tempo,
    )
    return SetOut.from_model(s)


@router.delete("/{partida_id}/sets/{set_id}", status_code=204)
async def delete_set(
    partida_id:   UUID,
    set_id:       UUID,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaSetService(session)
    await svc.delete(partida_id, set_id, current_user.id, _is_admin(current_user))
