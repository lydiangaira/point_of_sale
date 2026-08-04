from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from enum import Enum

class SaleStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

class SaleCreate(BaseModel):
    customer_id: Optional[UUID] = None
    user_id: UUID
    discount_amount: Decimal = Field(Decimal("0.00"), ge=0)
    tax_amount: Decimal = Field(Decimal("0.00"), ge=0)

class SaleUpdate(BaseModel):
    status: Optional[SaleStatus] = None
    customer_id: Optional[UUID] = None
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    tax_amount: Optional[Decimal] = Field(None, ge=0)

class SaleResponse(BaseModel):
    sale_id: UUID
    customer_id: Optional[UUID]
    user_id: UUID
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: SaleStatus
    sale_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
