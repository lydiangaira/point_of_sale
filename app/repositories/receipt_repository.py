from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.receipt import Receipt

class ReceiptRepository(BaseRepository[Receipt]):
    def get_by_sale(self, db: Session, sale_id: UUID) -> Optional[Receipt]:
        return db.query(Receipt).filter(Receipt.sale_id == sale_id).first()

receipt_repository = ReceiptRepository(Receipt)
