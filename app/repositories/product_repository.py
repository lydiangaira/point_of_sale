from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.product import Product


class ProductRepository(BaseRepository[Product]):
    def get_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku).first()

    def list_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        stmt = select(Product).where(Product.is_active == True).offset(skip).limit(limit)
        return db.scalars(stmt).all()


product_repository = ProductRepository(Product)