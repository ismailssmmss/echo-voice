from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: str
    message: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
