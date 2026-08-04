from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Enum, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class UserRole(str, PyEnum):
    ADMIN = "Admin"
    STORE_MANAGER = "Manager"
    SALES_ASSOCIATE = "Sales Associate"

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="pos_user_role_enum", create_type=True), nullable=False, default=UserRole.SALES_ASSOCIATE)
    is_active = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sales = relationship("Sale", back_populates="user")
