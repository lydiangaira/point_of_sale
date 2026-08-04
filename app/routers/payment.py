from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.payment import PaymentCreate, PaymentResponse
from repositories.payment_repository import PaymentRepository

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def post_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    return PaymentRepository(db).create(payment_in)
