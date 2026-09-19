from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.user import UserRole
from app.repositories.category_repository import category_repository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])
manage = require_roles(UserRole.ADMIN, UserRole.STORE_MANAGER)

@router.post("", response_model=CategoryRead, status_code=201, dependencies=[Depends(manage)])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, data)

@router.get("", response_model=list[CategoryRead], dependencies=[Depends(get_current_user)])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return category_repository.list(db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=CategoryRead, dependencies=[Depends(get_current_user)])
def get_category(category_id: UUID, db: Session = Depends(get_db)):
    return category_service.get_category(db, category_id)

@router.patch("/{category_id}", response_model=CategoryRead, dependencies=[Depends(manage)])
def update_category(category_id: UUID, data: CategoryUpdate, db: Session = Depends(get_db)):
    return category_service.update_category(db, category_id, data)

@router.delete("/{category_id}", status_code=204, dependencies=[Depends(manage)])
def delete_category(category_id: UUID, db: Session = Depends(get_db)):
    category_service.delete_category(db, category_id)