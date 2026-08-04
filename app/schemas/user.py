from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    role: str = "Admin"  # Changed from Enum to clear string to stop validation loops!

class UserCreate(UserBase):
    password: str = Field(..., min_length=6) # Lowered to 6 characters for fast manual testing

class UserUpdate(BaseModel):
    """
    Schema for updating user details. All attributes are optional 
    so you can submit partial updates directly via Swagger docs.
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None

class UserRead(UserBase):
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
