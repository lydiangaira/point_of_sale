from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def list_by_sale(self, db: Session, sale_id: UUID) -> list[Payment]:
        stmt = select(Payment).where(Payment.sale_id == sale_id)
        return list(db.scalars(stmt).all())


payment_repository = PaymentRepository(Payment)