from datetime import datetime
from contextlib import asynccontextmanager

from urllib.parse import quote_plus

from sqlalchemy import Column, DateTime, inspect, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, ColumnProperty
from sqlalchemy.sql import func

from config import get_db_type, get_pg_configs

session_name = 'scoutplay-api'
db_type = get_db_type()

# ── Engine ────────────────────────────────────────────────────────
pg_config = get_pg_configs()
_host = pg_config['host']
# IPv6 addresses must be wrapped in brackets in the connection URL
if ':' in _host and not _host.startswith('['):
    _host = f'[{_host}]'
postgres_connection_string = (
    f"postgresql+asyncpg://{pg_config['user']}:{quote_plus(pg_config['pwd'])}"
    f"@{_host}:{pg_config['port']}/{pg_config['dbname']}"
)
engine = create_async_engine(
    postgres_connection_string,
    pool_size=20,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=30,
    pool_pre_ping=True,
)

Base = declarative_base()

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


def init_db():
    return engine


# ── BaseModel ─────────────────────────────────────────────────────
class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    async def save(self, db: AsyncSession):
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self

    def to_dict(self, exclude=None, datetime_format='%Y-%m-%d %H:%M:%S'):
        if exclude is None:
            exclude = set()

        result = {}
        for prop in inspect(self.__class__).attrs:
            if isinstance(prop, ColumnProperty) and prop.key not in exclude:
                value = getattr(self, prop.key)
                if isinstance(value, datetime):
                    value = value.strftime(datetime_format)
                result[prop.key] = value
        return result


# ── Session helpers ───────────────────────────────────────────────
@asynccontextmanager
async def get_db(_db: AsyncSession = None):
    if _db is not None:
        try:
            yield _db
        finally:
            pass
    else:
        async with AsyncSessionLocal() as db:
            try:
                yield db
            finally:
                await db.close()


@asynccontextmanager
async def get_or_create_db(existing_db: AsyncSession = None):
    if existing_db is not None:
        try:
            yield existing_db
        finally:
            pass
    else:
        async with get_db() as db:
            yield db
