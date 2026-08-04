from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas.sale import SaleCreate, SaleUpdate, SaleResponse
from repositories.sale_repository import SaleRepository

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale_ticket(sale_in: SaleCreate, db: Session = Depends(get_db)):
    return SaleRepository(db).create(sale_in)

@router.get("/", response_model=List[SaleResponse])
def read_sales_ledger(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return SaleRepository(db).get_all(skip=skip, limit=limit)

@router.get("/{sale_id}", response_model=SaleResponse)
def read_sale_by_id(sale_id: UUID, db: Session = Depends(get_db)):
    sale = SaleRepository(db).get_by_id(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale record not found")
    return sale

@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale_meta(sale_id: UUID, sale_in: SaleUpdate, db: Session = Depends(get_db)):
    repo = SaleRepository(db)
    sale = repo.get_by_id(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale record not found")
    return repo.update_status(sale, sale_in)
