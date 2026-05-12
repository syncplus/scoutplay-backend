from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database import Base   # importe sua Base existente


class UserRole(str, Enum):
    ADMIN     = "admin"
    TREINADOR = "treinador"


class User(Base):
    __tablename__ = "users"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name       = Column(String(100), nullable=False)
    username   = Column(String(50),  nullable=False, unique=True, index=True)
    email      = Column(String(255), nullable=False, unique=True, index=True)
    password   = Column(String(255), nullable=False)
    role       = Column(String(20),  nullable=False, default=UserRole.TREINADOR)
    active     = Column(Boolean,     nullable=False, default=True)
    created_at = Column(DateTime,    default=datetime.utcnow)
    updated_at = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # helpers
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def can_manage_users(self) -> bool:
        return self.role == UserRole.ADMIN

    def can_view_all_partidas(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.TREINADOR)