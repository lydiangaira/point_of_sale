from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from repositories.supplier_repository import SupplierRepository

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier_in: SupplierCreate, db: Session = Depends(get_db)):
    return SupplierRepository(db).create(supplier_in)

@router.get("/", response_model=List[SupplierResponse])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return SupplierRepository(db).get_all(skip=skip, limit=limit)

@router.get("/{supplier_id}", response_model=SupplierResponse)
def read_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    supplier = SupplierRepository(db).get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier
