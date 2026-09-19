from typing import Optional

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.sale import SaleStatus

class SaleItemInput(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0, le=10_000)

class SaleCreate(BaseModel):
    customer_id: Optional[UUID] = None
    items: list[SaleItemInput] = Field(min_length=1, max_length=200)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)

class BasketCreate(BaseModel):
    customer_id: Optional[UUID] = None

class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_item_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal

class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_id: UUID
    customer_id: Optional[UUID]
    user_id: UUID
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: SaleStatus
    sale_date: datetime
    items: list[SaleItemRead]
