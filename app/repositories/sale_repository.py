from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.repositories.base import BaseRepository


class SaleRepository(BaseRepository[Sale]):
    def list_by_user(self, db: Session, user_id: UUID, *, skip: int = 0, limit: int = 100) -> list[Sale]:
        stmt = select(Sale).where(Sale.user_id == user_id).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

sale_repository = SaleRepository(Sale)