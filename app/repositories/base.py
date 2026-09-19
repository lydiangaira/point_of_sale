from typing import Optional, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    def get_by_id(self, db: Session, id_: UUID) -> Optional[ModelT]:
        return db.get(self.model, id_)

    def list(self, db: Session, *, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        stmt = select(self.model).offset(skip).limit(limit)
        return db.scalars(stmt).all()

    def create(self, db: Session, values: dict) -> ModelT:
        obj = self.model(**values)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, obj: ModelT, values: dict) -> ModelT:
        for key, value in values.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelT) -> None:
        db.delete(obj)
        db.commit()