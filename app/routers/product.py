from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from repositories.product_repository import ProductRepository

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
