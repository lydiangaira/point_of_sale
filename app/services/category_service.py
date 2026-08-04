from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate, CategoryUpdate
from models.category import Category

class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def create_category(self, obj_in: CategoryCreate) -> Category:
        return self.repo.create(obj_in)

    def get_category_by_id(self, category_id: UUID) -> Category:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog class target row index missing.")
        return category

    def list_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.repo.get_all(skip=skip, limit=limit)

    def update_category(self, category_id: UUID, obj_in: CategoryUpdate) -> Category:
        category = self.get_category_by_id(category_id)
        return self.repo.update(category, obj_in)

    def delete_category(self, category_id: UUID) -> None:
        category = self.get_category_by_id(category_id)
        self.repo.delete(category)
