from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class ReceiptFormat(str, Enum):
    PDF = "PDF"
    SMS = "SMS"
    EMAIL = "Email"
    PRINTED = "Printed"

class ReceiptCreate(BaseModel):
    sale_id: UUID
    format: ReceiptFormat = ReceiptFormat.PRINTED

class ReceiptResponse(BaseModel):
    receipt_id: UUID
    sale_id: UUID
    receipt_number: str
    format: ReceiptFormat
    issued_date: datetime

    class Config:
        from_attributes = True
