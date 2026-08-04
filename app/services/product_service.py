from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from repositories.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate
from models.product import Product

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def create_product(self, obj_in: ProductCreate) -> Product:
        if self.repo.get_by_sku(obj_in.sku):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU catalogue duplicate footprint code found.")
        return self.repo.create(obj_in)

    def get_product_by_id(self, product_id: UUID) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product inventory item missing.")
        return product

    def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.repo.get_all(skip=skip, limit=limit)

    def update_product(self, product_id: UUID, obj_in: ProductUpdate) -> Product:
        product = self.get_product_by_id(product_id)
        return self.repo.update(product, obj_in)

    def delete_product(self, product_id: UUID) -> None:
        product = self.get_product_by_id(product_id)
        self.repo.delete(product)
