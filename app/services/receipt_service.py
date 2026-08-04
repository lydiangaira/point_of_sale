from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from repositories.receipt_repository import ReceiptRepository
from repositories.sale_repository import SaleRepository
from schemas.receipt import ReceiptCreate
from models.receipt import Receipt

class ReceiptService:
    def __init__(self, db: Session):
        self.repo = ReceiptRepository(db)
        self.sale_repo = SaleRepository(db)

    def generate_receipt_for_sale(self, obj_in: ReceiptCreate) -> Receipt:
        sale = self.sale_repo.get_by_id(obj_in.sale_id)
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent transaction sale ledger tracking target missing.")
        return self.repo.create_for_sale(obj_in)
