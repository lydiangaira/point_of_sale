from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from repositories.customer_repository import CustomerRepository
from schemas.customer import CustomerCreate, CustomerUpdate
from models.customer import Customer

class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def create_customer(self, obj_in: CustomerCreate) -> Customer:
        if obj_in.email and self.repo.get_by_email(obj_in.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer email profile record registered already.")
        return self.repo.create(obj_in)

    def get_customer_by_id(self, customer_id: UUID) -> Customer:
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile context missing.")
        return customer

    def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.repo.get_all(skip=skip, limit=limit)

    def update_customer(self, customer_id: UUID, obj_in: CustomerUpdate) -> Customer:
        customer = self.get_customer_by_id(customer_id)
        return self.repo.update(customer, obj_in)

    def delete_customer(self, customer_id: UUID) -> None:
        customer = self.get_customer_by_id(customer_id)
        self.repo.delete(customer)
