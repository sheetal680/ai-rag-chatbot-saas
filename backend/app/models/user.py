from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserInDB(BaseModel):
    id: str
    name: str
    email: str
    hashed_password: str
    role: Literal["admin", "viewer"] = "admin"
    client_id: str
    is_active: bool = True
    created_at: datetime


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    client_id: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str                   # user_id
    email: str
    role: str
    client_id: str
    exp: Optional[int] = None
