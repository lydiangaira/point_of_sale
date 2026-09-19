from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class SupplierBase(BaseModel):
    supplier_name: str = Field(min_length=1, max_length=100)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=255)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None

class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: UUID
    is_active: bool
    created_at: datetime
