from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config import (
    get_access_token_expire_minutes,
    get_algorithm,
    get_refresh_token_expire_days,
    get_secret_key,
)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: UUID, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=get_access_token_expire_minutes()
    )
    return jwt.encode(
        {"sub": str(user_id), "role": role, "type": "access", "exp": expire},
        get_secret_key(),
        algorithm=get_algorithm(),
    )


def create_refresh_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=get_refresh_token_expire_days()
    )
    return jwt.encode(
        {"sub": str(user_id), "type": "refresh", "exp": expire},
        get_secret_key(),
        algorithm=get_algorithm(),
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            get_secret_key(),
            algorithms=[get_algorithm()],
        )
    except JWTError:
        return None