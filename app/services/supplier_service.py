from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.models.supplier import Supplier
from app.repositories.supplier_repository import supplier_repository
from app.schemas.supplier import SupplierCreate, SupplierUpdate

def _check_duplicates(db: Session, email: Optional[str], phone: Optional[str], exclude_id: Optional[UUID]):
    if email:
        existing = supplier_repository.get_by_email(db, email)
        if existing and existing.supplier_id != exclude_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    if phone:
        existing = supplier_repository.get_by_phone(db, phone)
        if existing and existing.supplier_id != exclude_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already in use")

def create_supplier(db: Session, data: SupplierCreate) -> Supplier:
    _check_duplicates(db, data.email, data.phone_number)
    return supplier_repository.create(db, data.model_dump())

def get_supplier(db: Session, supplier_id: UUID) -> Supplier:
    supplier = supplier_repository.get_by_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier

def update_supplier(db: Session, supplier_id: UUID, data: SupplierUpdate) -> Supplier:
    supplier = get_supplier(db, supplier_id)
    values = data.model_dump(exclude_unset=True)
    _check_duplicates(db, values.get("email"), values.get("phone_number"), exclude_id=supplier_id)
    return supplier_repository.update(db, supplier, values)

def deactivate_supplier(db: Session, supplier_id: UUID) -> Supplier:
    supplier = get_supplier(db, supplier_id)
    return supplier_repository.update(db, supplier, {"is_active": False})