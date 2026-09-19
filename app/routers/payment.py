from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.user import UserRole
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentStatusUpdate
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(get_current_user)])
manage = require_roles(UserRole.ADMIN, UserRole.STORE_MANAGER)

@router.post("", response_model=PaymentRead, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return payment_service.create_payment(db, data)

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: UUID, db: Session = Depends(get_db)):
    return payment_service.get_payment(db, payment_id)

@router.patch("/{payment_id}/status", response_model=PaymentRead, dependencies=[Depends(manage)])
def update_payment_status(payment_id: UUID, data: PaymentStatusUpdate, db: Session = Depends(get_db)):
    return payment_service.update_payment_status(db, payment_id, data)