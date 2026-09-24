from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user
from app.models.user import User
from app.schemas.receipt import ReceiptCreate, ReceiptRead
from app.services import receipt_service

router = APIRouter(prefix="/receipts", tags=["receipts"], dependencies=[Depends(get_current_user)])

@router.post("", response_model=ReceiptRead, status_code=201)
def create_receipt(data: ReceiptCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return receipt_service.create_receipt(db, data, current_user)

@router.get("/{receipt_id}", response_model=ReceiptRead)
def get_receipt(receipt_id: UUID, db: Session = Depends(get_db)):
    return receipt_service.get_receipt(db, receipt_id)