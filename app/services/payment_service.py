from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from repositories.payment_repository import PaymentRepository
from repositories.sale_repository import SaleRepository
from schemas.payment import PaymentCreate
from models.payment import Payment

class PaymentService:
    def __init__(self, db: Session):
        self.repo = PaymentRepository(db)
        self.sale_repo = SaleRepository(db)

    def process_payment(self, obj_in: PaymentCreate) -> Payment:
        sale = self.sale_repo.get_by_id(obj_in.sale_id)
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent sale voucher target match missing.")
        if sale.status == "Cancelled":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prohibited transaction block against a cancelled invoice.")
        return self.repo.create(obj_in)

    def get_payment_by_id(self, payment_id: UUID) -> Payment:
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment clearance record sequence missing.")
        return payment
