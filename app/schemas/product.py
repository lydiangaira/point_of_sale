from typing import Optional

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ProductBase(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    size: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=50)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    cost_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=500)


class ProductCreate(ProductBase):
    quantity_in_stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    size: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=50)
    price: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    cost_price: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None

class StockAdjustment(BaseModel):
    delta: int = Field(description="Positive to add stock, negative to remove. Cannot be zero.")
    reason: str = Field(min_length=1, max_length=255)

    @field_validator("delta")
    @classmethod
    def not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("delta cannot be zero")
        return v

class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    quantity_in_stock: int
    is_active: bool
    created_at: datetime

ProductResponse = ProductRead
