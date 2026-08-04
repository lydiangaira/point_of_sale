from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from repositories.category_repository import CategoryRepository

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryRepository(db).create(category_in)

@router.get("/", response_model=List[CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CategoryRepository(db).get_all(skip=skip, limit=limit)
