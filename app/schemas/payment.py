from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentMethod, PaymentStatus

class PaymentCreate(BaseModel):
    sale_id: UUID
    payment_method: PaymentMethod
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID
    sale_id: UUID
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    payment_date: datetime