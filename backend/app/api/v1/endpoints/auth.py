from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter()


def _issue_token(user: User) -> str:
    try:
        return create_access_token(str(user.id))
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured. Set a strong SECRET_KEY.",
        ) from exc


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")

    email = str(payload.email).lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists.")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    token = _issue_token(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        access_token=token,
        message="User registration successful.",
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        access_token=_issue_token(user),
        message="Login successful.",
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, is_active=user.is_active)
