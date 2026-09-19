from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatus
from app.models.sale import SaleStatus
from app.repositories.payment_repository import payment_repository
from app.schemas.payment import PaymentCreate, PaymentStatusUpdate
from app.services.sale_service import get_sale

def create_payment(db: Session, data: PaymentCreate) -> Payment:
    sale = get_sale(db, data.sale_id)
    if sale.status not in (SaleStatus.PENDING, SaleStatus.COMPLETED):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale is not payable in its current state")

    already_paid = sum(p.amount for p in payment_repository.list_by_sale(db, sale.sale_id) if p.status == PaymentStatus.COMPLETED)
    remaining = sale.total_amount - already_paid
    if data.amount > remaining:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment of {data.amount} exceeds remaining balance of {remaining}",
        )

    return payment_repository.create(db, {**data.model_dump(), "status": PaymentStatus.COMPLETED})

def get_payment(db: Session, payment_id: UUID) -> Payment:
    payment = payment_repository.get_by_id(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment

def update_payment_status(db: Session, payment_id: UUID, data: PaymentStatusUpdate) -> Payment:
    payment = get_payment(db, payment_id)
    return payment_repository.update(db, payment, {"status": data.status})