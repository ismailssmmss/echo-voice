from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    if not settings.secret_key or len(settings.secret_key) < 32:
        raise RuntimeError("SECRET_KEY must be configured with at least 32 characters.")
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expires_at}, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    if not settings.secret_key or len(settings.secret_key) < 32:
        raise RuntimeError("SECRET_KEY must be configured with at least 32 characters.")
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


__all__ = ["JWTError", "create_access_token", "decode_access_token", "hash_password", "verify_password"]
