from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    MOBILE_MONEY = "Mobile Money"
    BANK_TRANSFER = "Bank Transfer"

class PaymentStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class PaymentCreate(BaseModel):
    sale_id: UUID
    payment_method: PaymentMethod
    amount: Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)

class PaymentResponse(BaseModel):
    payment_id: UUID
    sale_id: UUID
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    payment_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
