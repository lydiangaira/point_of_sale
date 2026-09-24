from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.sale import Sale
from app.models.user import User, UserRole
from app.repositories.sale_repository import sale_repository
from app.schemas.sale import SaleCreate, SaleRead
from app.services import sale_service

router = APIRouter(prefix="/sales", tags=["sales"], dependencies=[Depends(get_current_user)])
manage = require_roles(UserRole.ADMIN, UserRole.STORE_MANAGER)


@router.post("", response_model=SaleRead, status_code=201)
def create_sale(data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return sale_service.create_sale(db, data, current_user)


@router.get("", response_model=list[SaleRead])
def list_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role in (UserRole.ADMIN, UserRole.STORE_MANAGER):
        return db.query(Sale).offset(skip).limit(limit).all()
    return sale_repository.list_by_user(db, current_user.user_id, skip=skip, limit=limit)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sale = sale_service.get_sale(db, sale_id)
    sale_service.authorize_sale_access(sale, current_user)
    return sale


@router.post("/{sale_id}/cancel", response_model=SaleRead)
def cancel_sale(sale_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return sale_service.cancel_sale(db, sale_id, current_user)


@router.post("/{sale_id}/refund", response_model=SaleRead, dependencies=[Depends(manage)])
def refund_sale(sale_id: UUID, db: Session = Depends(get_db)):
    return sale_service.refund_sale(db, sale_id)