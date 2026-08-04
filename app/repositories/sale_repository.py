from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from models.sale import Sale
from schemas.sale import SaleCreate, SaleUpdate

class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: UUID) -> Optional[Sale]:
        return self.db.query(Sale).filter(Sale.sale_id == sale_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Sale]:
        return self.db.query(Sale).offset(skip).limit(limit).all()

    def create(self, obj_in: SaleCreate) -> Sale:
        db_sale = Sale(
            customer_id=obj_in.customer_id,
            user_id=obj_in.user_id,
            subtotal=Decimal("0.00"),
            discount_amount=obj_in.discount_amount,
            tax_amount=obj_in.tax_amount,
            total_amount=Decimal("0.00"),
            status="Pending"
        )
        self.db.add(db_sale)
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def update_totals(self, sale_id: UUID, subtotal: Decimal) -> Sale:
        db_sale = self.get_by_id(sale_id)
        if not db_sale:
            raise ValueError("Sale transaction record not found")
        
        db_sale.subtotal = subtotal
        total = (subtotal - db_sale.discount_amount) + db_sale.tax_amount
        db_sale.total_amount = max(total, Decimal("0.00"))
        
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def update_status(self, db_sale: Sale, obj_in: SaleUpdate) -> Sale:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                setattr(db_sale, field, value.value)
            else:
                setattr(db_sale, field, value)
        
        # Recalculate balances if amounts change
        total = (db_sale.subtotal - db_sale.discount_amount) + db_sale.tax_amount
        db_sale.total_amount = max(total, Decimal("0.00"))
        
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale
