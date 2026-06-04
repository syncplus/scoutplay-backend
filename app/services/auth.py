from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthException, NotFoundException
from app.models.user import User
from app.services.utils.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.utils.email import send_password_reset_email


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def login(self, identifier: str, password: str) -> dict:
        identifier = identifier.strip()
        if "@" in identifier:
            condition = User.email == identifier.lower()
        else:
            condition = User.username == identifier.lower()

        result = await self.session.execute(select(User).where(condition))
        user = result.scalar_one_or_none()

        if not user:
            raise AuthException("Credenciais inválidas")

        if not user.active:
            raise AuthException("Conta desativada. Contate o administrador.")

        if not verify_password(password, user.password):
            raise AuthException("Credenciais inválidas")

        return {
            "access_token":  create_access_token(user.id, user.role),
            "refresh_token": create_refresh_token(user.id),
            "token_type":    "bearer",
            "user_id":       str(user.id),
            "name":          user.name,
            "username":      user.username,
            "role":          user.role,
            "email":         user.email,
            "photo":         user.photo,
        }

    async def forgot_password(self, email: str) -> None:
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        # Responde sem revelar se o e-mail existe ou não
        if not user or not user.active:
            return

        token = create_password_reset_token(user.id)
        await send_password_reset_email(user.email, user.name, token)

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = decode_token(token)
        if not payload or payload.get("type") != "password_reset":
            raise AuthException("Token inválido ou expirado")

        result = await self.session.execute(
            select(User).where(User.id == UUID(payload["sub"]))
        )
        user = result.scalar_one_or_none()
        if not user or not user.active:
            raise AuthException("Usuário não encontrado ou inativo")

        user.password = hash_password(new_password)
        await self.session.commit()

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthException("Refresh token inválido")

        result = await self.session.execute(
            select(User).where(User.id == UUID(payload["sub"]))
        )
        user = result.scalar_one_or_none()

        if not user or not user.active:
            raise AuthException("Usuário não encontrado ou inativo")

        return {
            "access_token": create_access_token(user.id, user.role),
            "token_type":   "bearer",
        }