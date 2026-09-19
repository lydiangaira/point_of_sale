from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from app.repositories.sale_item_repository import SaleItemRepository
from app.schemas.sale_item import SaleItemCreate
from app.models.sale_item import SaleItem

class SaleItemService:
    def __init__(self, db: Session):
        self.repo = SaleItemRepository(db)

    def add_item_to_basket(self, obj_in: SaleItemCreate) -> SaleItem:
        try:
            return self.repo.add_item_to_sale(obj_in)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_items_by_sale_id(self, sale_id: UUID) -> List[SaleItem]:
        return self.repo.get_by_sale(sale_id)

    def remove_item_from_basket(self, sale_item_id: UUID) -> None:
        item = self.repo.get_by_id(sale_item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line checkout cart item reference missing.")
        self.repo.remove_item_from_sale(item)
