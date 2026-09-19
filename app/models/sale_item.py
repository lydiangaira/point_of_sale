from uuid import uuid4
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    sale_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.sale_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False)
    
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")