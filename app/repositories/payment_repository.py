from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from models.payment import Payment
from schemas.payment import PaymentCreate

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.payment_id == payment_id).first()

    def create(self, obj_in: PaymentCreate) -> Payment:
        db_payment = Payment(
            sale_id=obj_in.sale_id,
            payment_method=obj_in.payment_method.value,
            amount=obj_in.amount,
            status="Completed" # Default processed transition logic state
        )
        self.db.add(db_payment)
        self.db.commit()
        self.db.refresh(db_payment)
        return db_payment
