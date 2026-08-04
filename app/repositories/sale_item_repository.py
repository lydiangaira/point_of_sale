from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from models.sale_item import SaleItem
from models.product import Product
from models.sale import Sale
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from repositories.sale_repository import SaleRepository

class SaleItemRepository:
    def __init__(self, db: Session):
        self.db = db
        self.sale_repo = SaleRepository(db)

    def get_by_id(self, sale_item_id: UUID) -> Optional[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.sale_item_id == sale_item_id).first()

    def get_by_sale(self, sale_id: UUID) -> List[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def _sync_parent_sale(self, sale_id: UUID):
        # Dynamically aggregate and recalculate the parent's running subtotal
        items = self.get_by_sale(sale_id)
        running_subtotal = sum((item.total_price for item in items), Decimal("0.00"))
        self.sale_repo.update_totals(sale_id, running_subtotal)

    def add_item_to_sale(self, obj_in: SaleItemCreate) -> SaleItem:
        product = self.db.query(Product).filter(Product.product_id == obj_in.product_id).first()
        if not product or not product.is_active:
            raise ValueError("Product is invalid or currently inactive")
        if product.quantity_in_stock < obj_in.quantity:
            raise ValueError(f"Insufficient stock balance for {product.product_name}")

        # Deduct warehouse stock matching transactional constraints
        product.quantity_in_stock -= obj_in.quantity

        item_total = product.price * obj_in.quantity
        db_item = SaleItem(
            sale_id=obj_in.sale_id,
            product_id=obj_in.product_id,
            quantity=obj_in.quantity,
            unit_price=product.price,
            total_price=item_total
        )
        
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        # Trigger automatic running ledger recalculation
        self._sync_parent_sale(obj_in.sale_id)
        return db_item

    def remove_item_from_sale(self, db_item: SaleItem) -> None:
        # Revert items back into the stock inventory
        product = self.db.query(Product).filter(Product.product_id == db_item.product_id).first()
        if product:
            product.quantity_in_stock += db_item.quantity

        sale_id = db_item.sale_id
        self.db.delete(db_item)
        self.db.commit()

        # Re-sync totals post-deletion
        self._sync_parent_sale(sale_id)
