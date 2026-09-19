import re
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.]+$")
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    """Only reachable by an Admin (see routers/user_router.py) — no public signup."""

    password: str = Field(min_length=10, max_length=128)
    role: UserRole = UserRole.SALES_ASSOCIATE

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not (re.search(r"[A-Z]", v) and re.search(r"[a-z]", v) and re.search(r"\d", v)):
            raise ValueError("Password must include upper case, lower case, and a digit")
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
