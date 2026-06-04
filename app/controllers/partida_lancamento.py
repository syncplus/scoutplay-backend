from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import RequireTreinador
from app.database import get_session
from app.models.partida_lancamento import AtaqueQualidade, AtaqueTipo
from app.models.user import User, UserRole
from app.services.partida_lancamento import PartidaLancamentoService

router = APIRouter()


class CreateLancamentoRequest(BaseModel):
    tipo:      AtaqueTipo
    qualidade: AtaqueQualidade
    pos_x:     int
    pos_y:     int
    zona:      str
    set_id:    UUID | None = None


class LancamentoOut(BaseModel):
    id:        str
    set_id:    str | None
    tipo:      str
    qualidade: str
    pos_x:     int
    pos_y:     int
    zona:      str

    @classmethod
    def from_model(cls, l) -> "LancamentoOut":
        return cls(
            id        = str(l.id),
            set_id    = str(l.set_id) if l.set_id else None,
            tipo      = l.tipo,
            qualidade = l.qualidade,
            pos_x     = l.pos_x,
            pos_y     = l.pos_y,
            zona      = l.zona,
        )


def _is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


@router.post("/{partida_id}/lancamentos", status_code=201)
async def create_lancamento(
    partida_id:   UUID,
    body:         CreateLancamentoRequest,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaLancamentoService(session)
    lancamento = await svc.add(
        partida_id, current_user.id, _is_admin(current_user),
        body.tipo, body.qualidade, body.pos_x, body.pos_y, body.zona, body.set_id,
    )
    return LancamentoOut.from_model(lancamento)


@router.delete("/{partida_id}/lancamentos/{lancamento_id}", status_code=204)
async def delete_lancamento(
    partida_id:    UUID,
    lancamento_id: UUID,
    current_user:  User = RequireTreinador,
    session:       AsyncSession = Depends(get_session),
):
    svc = PartidaLancamentoService(session)
    await svc.delete(
        partida_id, lancamento_id, current_user.id, _is_admin(current_user)
    )
