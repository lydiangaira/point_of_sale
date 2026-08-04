from pydantic import BaseModel, Field, condecimal
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class ProductBase(BaseModel):
    product_name: str = Field(..., max_length=255)
    sku: str = Field(..., max_length=50)
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    size: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=50)
    price: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)
    cost_price: Decimal = Field(Decimal("0.00"), max_digits=10, decimal_places=2, ge=0)
    quantity_in_stock: int = Field(0, ge=0)
    description: Optional[str] = Field(None, max_length=500)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=255)
    sku: Optional[str] = Field(None, max_length=50)
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    size: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=50)
    price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2, ge=0)
    cost_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2, ge=0)
    quantity_in_stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    product_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
