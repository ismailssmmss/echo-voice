from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import SessionLocal

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        user_id = int(subject)
    except (JWTError, RuntimeError, TypeError, ValueError):
        raise unauthorized
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise unauthorized
    return user
