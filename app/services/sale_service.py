from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.sale_repository import sale_repository
from schemas.sale import SaleCreate, SaleUpdate

def list_sales(db: Session):
    return sale_repository.get_all(db)

def get_sale(db: Session, sale_id: int):
    sale = sale_repository.get_by_id(db, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Sale not found"
        )
    return sale

def create_sale(db: Session, data: SaleCreate):
    return sale_repository.create(db, data)

def update_sale(db: Session, sale_id: int, data: SaleUpdate):
    db_sale = get_sale(db, sale_id)
    return sale_repository.update(db, db_sale, data)

def delete_sale(db: Session, sale_id: int):
    db_sale = get_sale(db, sale_id)
    return sale_repository.delete(db, db_sale)
