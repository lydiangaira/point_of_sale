from typing import Optional  # Ensure this import is added at the top
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.category import Category

class CategoryRepository(BaseRepository[Category]):
    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

category_repository = CategoryRepository(Category)
