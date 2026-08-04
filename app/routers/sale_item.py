from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas.sale_item import SaleItemCreate, SaleItemResponse
from repositories.sale_item_repository import SaleItemRepository

router = APIRouter(prefix="/sale-items", tags=["Sale Items"])

@router.post("/", response_model=SaleItemResponse, status_code=status.HTTP_201_CREATED)
def append_item_to_basket(item_in: SaleItemCreate, db: Session = Depends(get_db)):
    try:
        return SaleItemRepository(db).add_item_to_sale(item_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sale/{sale_id}", response_model=List[SaleItemResponse])
def read_all_items_in_sale(sale_id: UUID, db: Session = Depends(get_db)):
    return SaleItemRepository(db).get_by_sale(sale_id)

@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def void_item_from_basket(sale_item_id: UUID, db: Session = Depends(get_db)):
    repo = SaleItemRepository(db)
    item = repo.get_by_id(sale_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Line item not found")
    repo.remove_item_from_sale(item)
    return None
