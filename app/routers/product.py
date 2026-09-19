from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.repositories.product_repository import ProductRepository

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.user import UserRole
from app.repositories.product_repository import product_repository
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate, StockAdjustment
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])
manage = require_roles(UserRole.ADMIN, UserRole.STORE_MANAGER)

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    if repo.get_by_sku(product_in.sku):
        raise HTTPException(status_code=400, detail="SKU already exists")
    return repo.create(product_in)

@router.get("/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ProductRepository(db).get_all(skip=skip, limit=limit)

@router.post("", response_model=ProductRead, status_code=201, dependencies=[Depends(manage)])
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, data)

@router.get("", response_model=list[ProductRead], dependencies=[Depends(get_current_user)])
def list_products(skip: int = 0, limit: int = 100, active_only: bool = True, db: Session = Depends(get_db)):
    if active_only:
        return product_repository.list_active(db, skip=skip, limit=limit)
    return product_repository.list(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead, dependencies=[Depends(get_current_user)])
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)


@router.patch("/{product_id}", response_model=ProductRead, dependencies=[Depends(manage)])
def update_product(product_id: UUID, data: ProductUpdate, db: Session = Depends(get_db)):
    return product_service.update_product(db, product_id, data)


@router.post("/{product_id}/stock-adjustment", response_model=ProductRead, dependencies=[Depends(manage)])
def adjust_stock(product_id: UUID, data: StockAdjustment, db: Session = Depends(get_db)):
    return product_service.adjust_stock(db, product_id, data)


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(manage)])
def deactivate_product(product_id: UUID, db: Session = Depends(get_db)):
    product_service.deactivate_product(db, product_id)