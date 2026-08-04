import random
import string
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from models.receipt import Receipt
from schemas.receipt import ReceiptCreate

class ReceiptRepository:
    def __init__(self, db: Session):
        self.db = db

    def _generate_receipt_number(self) -> str:
        # Generates a random structured pattern tracking code (e.g., REC-20260801-X7K2)
        date_str = datetime.now().strftime("%Y%m%d")
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"REC-{date_str}-{rand_str}"

    def create_for_sale(self, obj_in: ReceiptCreate) -> Receipt:
        db_receipt = Receipt(
            sale_id=obj_in.sale_id,
            receipt_number=self._generate_receipt_number(),
            format=obj_in.format.value
        )
        self.db.add(db_receipt)
        self.db.commit()
        self.db.refresh(db_receipt)
        return db_receipt
