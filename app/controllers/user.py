from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import RequireAdmin
from app.database import get_session
from app.models.user import UserRole
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
    role:     UserRole | None = None
    active:   bool | None = None

class UserOut(BaseModel):
    id:       str
    name:     str
    username: str
    email:    str
    role:     str
    active:   bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, u) -> "UserOut":
        return cls(id=str(u.id), name=u.name, username=u.username, email=u.email, role=u.role, active=u.active)


@router.get("", dependencies=[RequireAdmin])
async def list_users(
    page: int = 1,
    page_size: int = 20,
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
    user = await svc.update(user_id, body.name, body.username, body.role, body.active)
    return UserOut.from_model(user)


@router.delete("/{user_id}", dependencies=[RequireAdmin], status_code=204)
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    svc = UserService(session)
    await svc.delete(user_id)