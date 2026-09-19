from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, DateTime, ForeignKey, Enum, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class PaymentMethod(str, PyEnum):
    CASH = "Cash"
    CARD = "Card"
    MOBILE_MONEY = "Mobile Money"
    BANK_TRANSFER = "Bank Transfer"

class PaymentStatus(str, PyEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.sale_id", ondelete="RESTRICT"), nullable=False)
    payment_method = Column(Enum(PaymentMethod, name="payment_method_enum", create_type=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus, name="payment_status_enum", create_type=True), nullable=False, default=PaymentStatus.PENDING)
    
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sale = relationship("Sale", back_populates="payments")
