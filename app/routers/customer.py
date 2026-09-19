from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.user import UserRole
from app.repositories.customer_repository import customer_repository
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import customer_service

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(get_current_user)])
manage = require_roles(UserRole.ADMIN, UserRole.STORE_MANAGER)

@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)

@router.get("", response_model=list[CustomerRead])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return customer_repository.list(db, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    return customer_service.get_customer(db, customer_id)

@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: UUID, data: CustomerUpdate, db: Session = Depends(get_db)):
    return customer_service.update_customer(db, customer_id, data)

@router.delete("/{customer_id}", status_code=204, dependencies=[Depends(manage)])
def deactivate_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer_service.deactivate_customer(db, customer_id)