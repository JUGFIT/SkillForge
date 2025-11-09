# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UserProfile(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {UUID: str}


class RegisterResponse(BaseModel):
    message: str
    user: UserProfile
