from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict[str, Any], expires_minutes: int | None = None) -> str:
    payload = data.copy()
    expire_delta = expires_minutes or settings.jwt_expire_minutes
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expire_delta)
    payload.update({"exp": expire_at})
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token khong hop le hoac da het han.",
        ) from exc
