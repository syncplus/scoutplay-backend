from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.context import RequireAny, get_current_user
from app.database import get_session
from app.models.user import User
from app.services.auth import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    identifier: str  # email ou username
    password:   str

class RefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str

class UserOut(BaseModel):
    id:       str
    name:     str
    username: str
    email:    str
    role:     str
    active:   bool

    model_config = {"from_attributes": True}


@router.post("/login")
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = AuthService(session)
    return await svc.login(body.identifier, body.password)


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = AuthService(session)
    return await svc.refresh(body.refresh_token)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = RequireAny):
    return UserOut(
        id       = str(current_user.id),
        name     = current_user.name,
        username = current_user.username,
        email    = current_user.email,
        role     = current_user.role,
        active   = current_user.active,
    )


@router.post("/forgot-password", status_code=204)
async def forgot_password(
    body: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = AuthService(session)
    await svc.forgot_password(body.email)


@router.post("/reset-password", status_code=204)
async def reset_password(
    body: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = AuthService(session)
    await svc.reset_password(body.token, body.new_password)


@router.post("/logout", status_code=204)
async def logout():
    return  # frontend apaga os tokens