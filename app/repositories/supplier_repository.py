from sqlalchemy import select
from typing import Optional
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories.base import BaseRepository

class SupplierRepository(BaseRepository[Supplier]):
    def get_by_email(self, db: Session, email: str) -> Optional[Supplier]:
        return db.scalars(select(Supplier).where(Supplier.email == email)).first()

    def get_by_phone(self, db: Session, phone_number: str) -> Optional[Supplier]:
        return db.scalars(select(Supplier).where(Supplier.phone_number == phone_number)).first()

supplier_repository = SupplierRepository(Supplier)