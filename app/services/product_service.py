from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import product_repository
from app.schemas.product import ProductCreate, ProductUpdate, StockAdjustment

def create_product(db: Session, data: ProductCreate) -> Product:
    if product_repository.get_by_sku(db, data.sku):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
    return product_repository.create(db, data.model_dump())

def get_product(db: Session, product_id: UUID) -> Product:
    product = product_repository.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

def update_product(db: Session, product_id: UUID, data: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    return product_repository.update(db, product, data.model_dump(exclude_unset=True))

def adjust_stock(db: Session, product_id: UUID, data: StockAdjustment) -> Product:
    product = get_product(db, product_id)
    new_quantity = product.quantity_in_stock + data.delta
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Adjustment would drop stock below zero (current: {product.quantity_in_stock})",
        )
    return product_repository.update(db, product, {"quantity_in_stock": new_quantity})

def deactivate_product(db: Session, product_id: UUID) -> Product:
    product = get_product(db, product_id)
    return product_repository.update(db, product, {"is_active": False})