from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException, NotFoundException
from app.models.user import User, UserRole
from app.services.utils.security import hash_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, name: str, username: str, email: str, password: str, role: UserRole = UserRole.TREINADOR
    ) -> User:
        taken = await self.session.execute(
            select(User).where(
                (User.email == email.lower()) | (User.username == username.lower())
            )
        )
        existing = taken.scalar_one_or_none()
        if existing:
            if existing.email == email.lower():
                raise ConflictException("E-mail já cadastrado")
            raise ConflictException("Username já cadastrado")

        user = User(
            name     = name,
            username = username.lower(),
            email    = email.lower(),
            password = hash_password(password),
            role     = role,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def list_all(
        self, page: int = 1, page_size: int = 20, active_only: bool = False
    ) -> tuple[list[User], int]:
        q = select(User)
        if active_only:
            q = q.where(User.active == True)

        total = await self.session.scalar(
            select(func.count()).select_from(q.subquery())
        )
        rows = await self.session.execute(
            q.order_by(User.created_at.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
        )
        return list(rows.scalars()), total or 0

    async def get_by_id(self, user_id: UUID) -> User:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("Usuário")
        return user

    async def update(
        self,
        user_id:  UUID,
        name:     str | None = None,
        username: str | None = None,
        role:     UserRole | None = None,
        active:   bool | None = None,
    ) -> User:
        user = await self.get_by_id(user_id)
        if username is not None:
            conflict = await self.session.execute(
                select(User).where(User.username == username.lower(), User.id != user_id)
            )
            if conflict.scalar_one_or_none():
                raise ConflictException("Username já cadastrado")
            user.username = username.lower()
        if name   is not None: user.name   = name
        if role   is not None: user.role   = role
        if active is not None: user.active = active
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        await self.session.delete(user)
        await self.session.commit()