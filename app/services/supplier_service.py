from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from repositories.supplier_repository import SupplierRepository
from schemas.supplier import SupplierCreate, SupplierUpdate
from models.supplier import Supplier

class SupplierService:
    def __init__(self, db: Session):
        self.repo = SupplierRepository(db)

    def create_supplier(self, obj_in: SupplierCreate) -> Supplier:
        return self.repo.create(obj_in)

    def get_supplier_by_id(self, supplier_id: UUID) -> Supplier:
        supplier = self.repo.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier logistics index entity missing.")
        return supplier

    def list_suppliers(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        return self.repo.get_all(skip=skip, limit=limit)

    def update_supplier(self, supplier_id: UUID, obj_in: SupplierUpdate) -> Supplier:
        supplier = self.get_supplier_by_id(supplier_id)
        return self.repo.update(supplier, obj_in)

    def delete_supplier(self, supplier_id: UUID) -> None:
        supplier = self.get_supplier_by_id(supplier_id)
        self.repo.delete(supplier)
