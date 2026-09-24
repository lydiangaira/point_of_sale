import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.models.sale import SaleStatus
from app.models.user import User
from app.repositories.receipt_repository import receipt_repository
from app.schemas.receipt import ReceiptCreate
from app.services.sale_service import get_sale

def _generate_receipt_number() -> str:
    return f"RCPT-{datetime.now(timezone.utc):%Y%m%d}-{secrets.token_hex(4).upper()}"

def create_receipt(db: Session, data: ReceiptCreate, current_user: User) -> Receipt:
    sale = get_sale(db, data.sale_id)
    if sale.status != SaleStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receipts can only be issued for completed sales")
    if receipt_repository.get_by_sale(db, sale.sale_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A receipt already exists for this sale")

    values = {
        "sale_id": sale.sale_id,
        "format": data.format,
        "receipt_number": _generate_receipt_number(),
        "issued_by_user_id": current_user.user_id,
    }
    return receipt_repository.create(db, values)

def get_receipt(db: Session, receipt_id: UUID) -> Receipt:
    receipt = receipt_repository.get_by_id(db, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    return receipt