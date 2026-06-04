import base64
import os
import re
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.user import User, UserRole
from app.services.utils.security import hash_password

AVATAR_DIR = "static/avatars"
MAX_AVATAR_BYTES = 3 * 1024 * 1024  # 3 MB
_DATA_URL_RE = re.compile(r"^data:image/(png|jpe?g|webp|gif);base64,(.+)$", re.IGNORECASE | re.DOTALL)


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
        email:    str | None = None,
        password: str | None = None,
        role:     UserRole | None = None,
        active:   bool | None = None,
        photo:    str | None = None,
    ) -> User:
        user = await self.get_by_id(user_id)
        if username is not None:
            conflict = await self.session.execute(
                select(User).where(User.username == username.lower(), User.id != user_id)
            )
            if conflict.scalar_one_or_none():
                raise ConflictException("Username já cadastrado")
            user.username = username.lower()
        if email is not None:
            conflict = await self.session.execute(
                select(User).where(User.email == email.lower(), User.id != user_id)
            )
            if conflict.scalar_one_or_none():
                raise ConflictException("E-mail já cadastrado")
            user.email = email.lower()
        if name     is not None: user.name     = name
        if password:             user.password = hash_password(password)
        if role     is not None: user.role     = role
        if active   is not None: user.active   = active
        if photo    is not None: user.photo    = photo
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def set_avatar(self, user_id: UUID, data_url: str) -> User:
        """Recebe uma data URL base64 (data:image/png;base64,...), salva em static/avatars e grava o caminho."""
        user = await self.get_by_id(user_id)
        m = _DATA_URL_RE.match((data_url or "").strip())
        if not m:
            raise BadRequestException("Imagem inválida. Envie uma imagem PNG, JPG, WEBP ou GIF.")
        ext_raw = m.group(1).lower()
        ext = "jpg" if ext_raw in ("jpeg", "jpg") else ext_raw
        try:
            raw = base64.b64decode(m.group(2), validate=True)
        except Exception:
            raise BadRequestException("Falha ao decodificar a imagem.")
        if len(raw) > MAX_AVATAR_BYTES:
            raise BadRequestException("Imagem muito grande (máx. 3 MB).")

        os.makedirs(AVATAR_DIR, exist_ok=True)
        filename = f"{user_id}.{ext}"
        with open(os.path.join(AVATAR_DIR, filename), "wb") as f:
            f.write(raw)

        user.photo = f"/api/static/avatars/{filename}"
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        await self.session.delete(user)
        await self.session.commit()