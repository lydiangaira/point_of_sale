from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from typing import Optional

class SaleItemBase(BaseModel):
    sale_id: UUID
    product_id: UUID
    quantity: int = Field(..., ge=1)

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class SaleItemResponse(SaleItemBase):
    sale_item_id: UUID
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True
