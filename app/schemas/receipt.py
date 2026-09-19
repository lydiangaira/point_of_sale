from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.receipt import ReceiptFormat

class ReceiptCreate(BaseModel):
    sale_id: UUID
    format: ReceiptFormat = ReceiptFormat.PRINTED

class ReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    receipt_id: UUID
    sale_id: UUID
    receipt_number: str
    format: ReceiptFormat
    issued_date: datetime