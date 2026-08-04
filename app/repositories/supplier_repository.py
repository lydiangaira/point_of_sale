from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from models.supplier import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate

class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]:
        return self.db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        return self.db.query(Supplier).offset(skip).limit(limit).all()

    def create(self, obj_in: SupplierCreate) -> Supplier:
        db_supplier = Supplier(**obj_in.model_dump())
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def update(self, db_supplier: Supplier, obj_in: SupplierUpdate) -> Supplier:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_supplier, field, value)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier
