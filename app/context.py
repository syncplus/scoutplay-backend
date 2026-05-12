from contextvars import ContextVar
from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session       # sua função existente
from app.exceptions import AuthException, ForbiddenException
from app.models.user import User, UserRole
from app.services.utils.security import decode_token

security = HTTPBearer()
correlationId: ContextVar[str] = ContextVar('correlationId', default=None)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    payload = decode_token(credentials.credentials)

    if not payload or payload.get("type") != "access":
        raise AuthException()

    result = await session.execute(
        select(User).where(User.id == UUID(payload["sub"]))
    )
    user = result.scalar_one_or_none()

    if not user or not user.active:
        raise AuthException("Usuário inativo ou não encontrado")

    return user


def require_roles(*roles: UserRole):
    async def guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Acesso restrito a: {', '.join(r.value for r in roles)}"
            )
        return current_user
    return guard


# Atalhos prontos
RequireAdmin     = Depends(require_roles(UserRole.ADMIN))
RequireTreinador = Depends(require_roles(UserRole.ADMIN, UserRole.TREINADOR))
RequireAny       = Depends(get_current_user)