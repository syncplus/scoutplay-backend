from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import RequireTreinador
from app.controllers.partida_lancamento import LancamentoOut
from app.controllers.partida_set import SetOut
from app.database import get_session
from app.models.partida import PartidaLado, PartidaStatus
from app.models.user import User, UserRole
from app.services.partida import PartidaService

router = APIRouter()


# ── Request schemas ───────────────────────────────────────────────
class CreatePartidaRequest(BaseModel):
    jogador:    str
    fase:       str
    lado:       PartidaLado = PartidaLado.ESQUERDA
    adversario: str | None = None
    data:       date | None = None


class UpdatePartidaRequest(BaseModel):
    jogador:    str | None = None
    adversario: str | None = None
    fase:       str | None = None
    lado:       PartidaLado | None = None
    status:     PartidaStatus | None = None
    data:       date | None = None
    tempo:      int | None = None


# ── Response schemas ──────────────────────────────────────────────
class PartidaOut(BaseModel):
    id:         str
    user_id:    str
    user_name:  str | None
    jogador:    str
    adversario: str | None
    fase:       str
    lado:       str
    status:     str
    data:       str | None
    ataques:    int
    tempo:      int

    @classmethod
    def from_model(cls, p) -> "PartidaOut":
        return cls(
            id         = str(p.id),
            user_id    = str(p.user_id),
            user_name  = p.user.name if p.user else None,
            jogador    = p.jogador,
            adversario = p.adversario,
            fase       = p.fase,
            lado       = p.lado,
            status     = p.status,
            data       = p.data.isoformat() if p.data else None,
            ataques    = p.ataques,
            tempo      = p.tempo,
        )


class PartidaDetailOut(PartidaOut):
    sets:        list[SetOut]
    lancamentos: list[LancamentoOut]

    @classmethod
    def from_model(cls, p) -> "PartidaDetailOut":
        base = PartidaOut.from_model(p).model_dump()
        return cls(
            **base,
            sets        = [SetOut.from_model(s) for s in p.sets],
            lancamentos = [LancamentoOut.from_model(l) for l in p.lancamentos],
        )


def _is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


# ── Endpoints ─────────────────────────────────────────────────────
@router.get("")
async def list_partidas(
    status:       PartidaStatus | None = None,
    page:         int = 1,
    page_size:    int = 50,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaService(session)
    partidas, total = await svc.list_all(
        current_user.id, _is_admin(current_user), status, page, page_size
    )
    return {"data": [PartidaOut.from_model(p) for p in partidas], "total": total}


@router.post("", status_code=201)
async def create_partida(
    body:         CreatePartidaRequest,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaService(session)
    partida = await svc.create(
        current_user.id, body.jogador, body.fase, body.lado, body.adversario, body.data
    )
    # recarrega com o relacionamento `user` para popular user_name
    partida = await svc.get_by_id(partida.id, current_user.id, _is_admin(current_user))
    return PartidaOut.from_model(partida)


@router.get("/{partida_id}")
async def get_partida(
    partida_id:   UUID,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaService(session)
    partida = await svc.get_by_id(partida_id, current_user.id, _is_admin(current_user))
    return PartidaDetailOut.from_model(partida)


@router.patch("/{partida_id}")
async def update_partida(
    partida_id:   UUID,
    body:         UpdatePartidaRequest,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaService(session)
    partida = await svc.update(
        partida_id, current_user.id, _is_admin(current_user),
        jogador=body.jogador, adversario=body.adversario, fase=body.fase,
        lado=body.lado, status=body.status, data=body.data, tempo=body.tempo,
    )
    return PartidaOut.from_model(partida)


@router.delete("/{partida_id}", status_code=204)
async def delete_partida(
    partida_id:   UUID,
    current_user: User = RequireTreinador,
    session:      AsyncSession = Depends(get_session),
):
    svc = PartidaService(session)
    await svc.delete(partida_id, current_user.id, _is_admin(current_user))
