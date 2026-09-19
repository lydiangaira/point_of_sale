# Save as: repositories/sale_item_repository.py
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.schemas.sale_item import SaleItemCreate

TWO_PLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


class SaleItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_item_id: UUID) -> Optional[SaleItem]:
        return self.db.get(SaleItem, sale_item_id)

    def get_by_sale(self, sale_id: UUID) -> list[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def add_item_to_sale(self, obj_in: SaleItemCreate) -> SaleItem:
        sale = self.db.get(Sale, obj_in.sale_id)
        if sale is None:
            raise ValueError(f"Sale {obj_in.sale_id} not found")
        if sale.status != SaleStatus.PENDING:
            raise ValueError("Items can only be added to a sale that is still pending")

        product = (
            self.db.query(Product)
            .filter(Product.product_id == obj_in.product_id)
            .with_for_update()
            .first()
        )
        if product is None or not product.is_active:
            raise ValueError(f"Product {obj_in.product_id} not found")
        if product.quantity_in_stock < obj_in.quantity:
            raise ValueError(
                f"Insufficient stock for {product.product_name} "
                f"(have {product.quantity_in_stock}, need {obj_in.quantity})"
            )

        unit_price = product.price
        total_price = _money(unit_price * obj_in.quantity)

        product.quantity_in_stock -= obj_in.quantity
        item = SaleItem(
            sale_id=obj_in.sale_id,
            product_id=obj_in.product_id,
            quantity=obj_in.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        self.db.add(item)
        self.db.flush()
        self._recalculate_totals(sale)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_item_from_sale(self, item: SaleItem) -> None:
        sale = self.db.get(Sale, item.sale_id)

        product = (
            self.db.query(Product)
            .filter(Product.product_id == item.product_id)
            .with_for_update()
            .first()
        )
        if product:
            product.quantity_in_stock += item.quantity

        self.db.delete(item)
        self.db.flush()
        if sale:
            self._recalculate_totals(sale)
        self.db.commit()

    def _recalculate_totals(self, sale: Sale) -> None:
        items = self.db.query(SaleItem).filter(SaleItem.sale_id == sale.sale_id).all()
        subtotal = sum((i.total_price for i in items), Decimal("0.00"))
        taxable = subtotal - sale.discount_amount
        if taxable < 0:
            taxable = Decimal("0.00")
        tax_amount = _money(taxable * Decimal(str(settings.tax_rate)))
        sale.subtotal = subtotal
        sale.tax_amount = tax_amount
        sale.total_amount = _money(taxable + tax_amount)