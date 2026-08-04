from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: UUID) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()

    def get_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def create(self, obj_in: CustomerCreate) -> Customer:
        db_customer = Customer(**obj_in.model_dump())
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def update(self, db_customer: Customer, obj_in: CustomerUpdate) -> Customer:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def delete(self, db_customer: Customer) -> None:
        self.db.delete(db_customer)
        self.db.commit()
