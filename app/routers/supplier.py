from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.user import UserRole
from app.repositories.supplier_repository import supplier_repository
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.services import supplier_service

router = APIRouter(prefix="/suppliers", tags=["suppliers"])
manage = require_roles(UserRole.ADMIN, UserRole.STORE_MANAGER)

@router.post("", response_model=SupplierRead, status_code=201, dependencies=[Depends(manage)])
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    return supplier_service.create_supplier(db, data)

@router.get("", response_model=list[SupplierRead], dependencies=[Depends(get_current_user)])
def list_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return supplier_repository.list(db, skip=skip, limit=limit)

@router.get("/{supplier_id}", response_model=SupplierRead, dependencies=[Depends(get_current_user)])
def get_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    return supplier_service.get_supplier(db, supplier_id)

@router.patch("/{supplier_id}", response_model=SupplierRead, dependencies=[Depends(manage)])
def update_supplier(supplier_id: UUID, data: SupplierUpdate, db: Session = Depends(get_db)):
    return supplier_service.update_supplier(db, supplier_id, data)

@router.delete("/{supplier_id}", status_code=204, dependencies=[Depends(manage)])
def deactivate_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    supplier_service.deactivate_supplier(db, supplier_id)