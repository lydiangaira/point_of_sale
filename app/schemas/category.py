from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class CategoryBase(BaseModel):
    category_name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    category_id: UUID
    created_at: datetime
