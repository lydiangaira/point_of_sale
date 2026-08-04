from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class ReceiptFormat(str, PyEnum):
    PDF = "PDF"
    SMS = "SMS"
    EMAIL = "Email"
    PRINTED = "Printed"

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.sale_id", ondelete="CASCADE"), nullable=False)
    receipt_number = Column(String(100), unique=True, nullable=False, index=True)
    format = Column(Enum(ReceiptFormat, name="receipt_format_enum", create_type=True), nullable=False, default=ReceiptFormat.PRINTED)
    
    issued_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sale = relationship("Sale", back_populates="receipts")
