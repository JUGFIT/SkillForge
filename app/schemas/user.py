from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from uuid import UUID


# ============================================================
# 👤 BASE SCHEMAS
# ============================================================


class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    password: constr(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    role: Optional[str] = "user"
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
