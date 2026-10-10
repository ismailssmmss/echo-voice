from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(payload: RegisterRequest) -> dict[str, str]:
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    return {"message": "User registration request accepted.", "email": payload.email}


@router.post("/login")
def login(email: EmailStr, password: str) -> dict[str, str]:
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    return {"message": "Login request accepted.", "email": str(email)}
