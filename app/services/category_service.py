from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import category_repository
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, data: CategoryCreate) -> Category:
    if category_repository.get_by_name(db, data.category_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    return category_repository.create(db, data.model_dump())

def get_category(db: Session, category_id: UUID) -> Category:
    category = category_repository.get_by_id(db, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

def update_category(db: Session, category_id: UUID, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    values = data.model_dump(exclude_unset=True)
    if "category_name" in values:
        existing = category_repository.get_by_name(db, values["category_name"])
        if existing and existing.category_id != category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already in use")
    return category_repository.update(db, category, values)

def delete_category(db: Session, category_id: UUID) -> None:
    category = get_category(db, category_id)
    category_repository.delete(db, category)