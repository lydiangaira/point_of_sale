from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from repositories.customer_repository import CustomerRepository

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer_in: CustomerCreate, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    if customer_in.email and repo.get_by_email(customer_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return repo.create(customer_in)

@router.get("/", response_model=List[CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CustomerRepository(db).get_all(skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = CustomerRepository(db).get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: UUID, customer_in: CustomerUpdate, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    customer = repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return repo.update(customer, customer_in)
