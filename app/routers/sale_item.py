# Save as: routers/sale_item.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user
from app.schemas.sale_item import SaleItemCreate, SaleItemResponse
from app.services.sale_item_service import SaleItemService

router = APIRouter(prefix="/sale-items", tags=["Sale Items"], dependencies=[Depends(get_current_user)])

def get_service(db: Session = Depends(get_db)) -> SaleItemService:
    return SaleItemService(db)

@router.post("", response_model=SaleItemResponse, status_code=status.HTTP_201_CREATED)
def append_item_to_basket(item_in: SaleItemCreate, service: SaleItemService = Depends(get_service)):
    return service.add_item_to_basket(item_in)

@router.get("/sale/{sale_id}", response_model=List[SaleItemResponse])
def read_all_items_in_sale(sale_id: UUID, service: SaleItemService = Depends(get_service)):
    return service.get_items_by_sale_id(sale_id)

@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def void_item_from_basket(sale_item_id: UUID, service: SaleItemService = Depends(get_service)):
    service.remove_item_from_basket(sale_item_id)
    return None