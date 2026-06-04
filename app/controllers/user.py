from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import RequireAdmin, RequireAny
from app.database import get_session
from app.models.user import User, UserRole
from app.services.user import UserService

router = APIRouter()


class CreateUserRequest(BaseModel):
    name:     str
    username: str
    email:    EmailStr
    password: str
    role:     UserRole = UserRole.TREINADOR

class UpdateUserRequest(BaseModel):
    name:     str | None = None
    username: str | None = None
    email:    EmailStr | None = None
    password: str | None = None
    role:     UserRole | None = None
    active:   bool | None = None
    photo:    str | None = None

class UpdateMeRequest(BaseModel):
    name:     str | None = None
    username: str | None = None
    email:    EmailStr | None = None
    password: str | None = None

class AvatarRequest(BaseModel):
    data: str   # data URL base64 (data:image/png;base64,...)

class UserOut(BaseModel):
    id:       str
    name:     str
    username: str
    email:    str
    role:     str
    active:   bool
    photo:    str | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, u) -> "UserOut":
        return cls(id=str(u.id), name=u.name, username=u.username, email=u.email,
                   role=u.role, active=u.active, photo=u.photo)


# ── Perfil do próprio usuário (qualquer role) ─────────────────────
# IMPORTANTE: declarar /me antes de /{user_id} para não colidir com o path param.
@router.patch("/me")
async def update_me(
    body: UpdateMeRequest,
    current_user: User = RequireAny,
    session: AsyncSession = Depends(get_session),
):
    svc = UserService(session)
    user = await svc.update(
        current_user.id,
        name=body.name, username=body.username, email=body.email, password=body.password,
    )
    return UserOut.from_model(user)


@router.post("/me/avatar")
async def upload_my_avatar(
    body: AvatarRequest,
    current_user: User = RequireAny,
    session: AsyncSession = Depends(get_session),
):
    svc = UserService(session)
    user = await svc.set_avatar(current_user.id, body.data)
    return UserOut.from_model(user)


# ── Gestão de usuários (admin) ────────────────────────────────────
@router.get("", dependencies=[RequireAdmin])
async def list_users(
    page: int = 1,
    page_size: int = 100,
    active_only: bool = False,
    session: AsyncSession = Depends(get_session),
):
    svc = UserService(session)
    users, total = await svc.list_all(page, page_size, active_only)
    return {"data": [UserOut.from_model(u) for u in users], "total": total}


@router.post("", dependencies=[RequireAdmin], status_code=201)
async def create_user(
    body: CreateUserRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = UserService(session)
    user = await svc.create(body.name, body.username, body.email, body.password, body.role)
    return UserOut.from_model(user)


@router.get("/{user_id}", dependencies=[RequireAdmin])
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    svc = UserService(session)
    user = await svc.get_by_id(user_id)
    return UserOut.from_model(user)


@router.patch("/{user_id}", dependencies=[RequireAdmin])
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = UserService(session)
    user = await svc.update(
        user_id,
        name=body.name, username=body.username, email=body.email, password=body.password,
        role=body.role, active=body.active, photo=body.photo,
    )
    return UserOut.from_model(user)


@router.delete("/{user_id}", dependencies=[RequireAdmin], status_code=204)
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    svc = UserService(session)
    await svc.delete(user_id)
