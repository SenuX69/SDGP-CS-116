from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ─── User Schemas ────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ─── Token Schemas ───────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

# ─── Profile Schemas ─────────────────────────────────────────

class ProfileUpdate(BaseModel):
    current_skills: Optional[List[str]] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None


class ProfileOut(BaseModel):
    id: int
    user_id: int
    current_skills: List[str]
    target_role: Optional[str]
    experience_years: int
    education_level: Optional[str]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
