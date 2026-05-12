from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthException, ConflictException
from app.models.user import User, UserRole
from app.services.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)


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
        }

    async def refresh(self, refresh_token: str) -> dict:
        from app.services.utils.security import decode_token
        from uuid import UUID

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