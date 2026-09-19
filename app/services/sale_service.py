# Save as: services/sale_service.py
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.models.user import User, UserRole
from app.repositories.sale_repository import sale_repository
from app.schemas.sale import SaleCreate

TWO_PLACES = Decimal("0.01")

def _money(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def create_sale(db: Session, data: SaleCreate, current_user: User) -> Sale:
    product_ids = [item.product_id for item in data.items]
    products = (
        db.query(Product)
        .filter(Product.product_id.in_(product_ids))
        .with_for_update()
        .all()
    )
    products_by_id = {p.product_id: p for p in products}

    subtotal = Decimal("0.00")
    sale_items: list[SaleItem] = []

    for line in data.items:
        product = products_by_id.get(line.product_id)
        if product is None or not product.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {line.product_id} not found")
        if product.quantity_in_stock < line.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock for {product.product_name} (have {product.quantity_in_stock}, need {line.quantity})",
            )
        unit_price = product.price  # always the live DB price, never client-supplied
        line_total = _money(unit_price * line.quantity)
        subtotal += line_total
        product.quantity_in_stock -= line.quantity
        sale_items.append(SaleItem(product_id=product.product_id, quantity=line.quantity, unit_price=unit_price, total_price=line_total))

    if data.discount_amount > subtotal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount cannot exceed subtotal")

    taxable = subtotal - data.discount_amount
    tax_amount = _money(taxable * Decimal(str(settings.tax_rate)))
    total_amount = _money(taxable + tax_amount)

    sale = Sale(
        customer_id=data.customer_id,
        user_id=current_user.user_id,
        subtotal=subtotal,
        discount_amount=data.discount_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status=SaleStatus.COMPLETED,
        items=sale_items,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale

def create_basket(db: Session, customer_id: Optional[UUID], current_user: User) -> Sale:
    sale = Sale(
        customer_id=customer_id,
        user_id=current_user.user_id,
        status=SaleStatus.PENDING,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def checkout_sale(db: Session, sale_id: UUID, current_user: User) -> Sale:
    sale = get_sale(db, sale_id)
    authorize_sale_access(sale, current_user)
    if sale.status != SaleStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending sales can be checked out")
    if not sale.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot check out a sale with no items")
    sale.status = SaleStatus.COMPLETED
    db.commit()
    db.refresh(sale)
    return sale

def get_sale(db: Session, sale_id: UUID) -> Sale:
    sale = db.query(Sale).options(selectinload(Sale.items)).filter(Sale.sale_id == sale_id).first()
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return sale

def authorize_sale_access(sale: Sale, current_user: User) -> None:
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.STORE_MANAGER:
        return
    if sale.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def cancel_sale(db: Session, sale_id: UUID, current_user: User) -> Sale:
    sale = get_sale(db, sale_id)
    authorize_sale_access(sale, current_user)
    if sale.status != SaleStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending sales can be cancelled")
    _restock(db, sale)
    sale.status = SaleStatus.CANCELLED
    db.commit()
    db.refresh(sale)
    return sale

def refund_sale(db: Session, sale_id: UUID) -> Sale:
    sale = get_sale(db, sale_id)
    if sale.status != SaleStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only completed sales can be refunded")
    _restock(db, sale)
    sale.status = SaleStatus.REFUNDED
    db.commit()
    db.refresh(sale)
    return sale

def _restock(db: Session, sale: Sale) -> None:
    product_ids = [item.product_id for item in sale.items]
    products = db.query(Product).filter(Product.product_id.in_(product_ids)).with_for_update().all()
    products_by_id = {p.product_id: p for p in products}
    for item in sale.items:
        product = products_by_id.get(item.product_id)
        if product:
            product.quantity_in_stock += item.quantity