from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import customer_repository
from app.schemas.customer import CustomerCreate, CustomerUpdate

def check_duplicates(db: Session, email: Optional[str], phone: Optional[str], exclude_id: Optional[UUID] = None) -> None:
    if email:
        existing = customer_repository.get_by_email(db, email)
        if existing and existing.customer_id != exclude_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    if phone:
        existing = customer_repository.get_by_phone(db, phone)
        if existing and existing.customer_id != exclude_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already in use")

def create_customer(db: Session, data: CustomerCreate) -> Customer:
    check_duplicates(db, data.email, data.phone_number)
    return customer_repository.create(db, data.model_dump())

def get_customer(db: Session, customer_id: UUID) -> Customer:
    customer = customer_repository.get_by_id(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

def update_customer(db: Session, customer_id: UUID, data: CustomerUpdate) -> Customer:
    customer = get_customer(db, customer_id)
    values = data.model_dump(exclude_unset=True)
    check_duplicates(db, values.get("email"), values.get("phone_number"), exclude_id=customer_id)
    return customer_repository.update(db, customer, values)

def deactivate_customer(db: Session, customer_id: UUID) -> Customer:
    customer = get_customer(db, customer_id)
    return customer_repository.update(db, customer, {"is_active": False})