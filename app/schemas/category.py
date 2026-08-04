from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    category_name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryResponse(CategoryBase):
    category_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
