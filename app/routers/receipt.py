from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.receipt import ReceiptCreate, ReceiptResponse
from repositories.receipt_repository import ReceiptRepository

router = APIRouter(prefix="/receipts", tags=["Receipts"])

@router.post("/", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def issue_receipt(receipt_in: ReceiptCreate, db: Session = Depends(get_db)):
    return ReceiptRepository(db).create_for_sale(receipt_in)
